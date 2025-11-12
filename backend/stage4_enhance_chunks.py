#!/usr/bin/env python3
"""
Stage 4: AI Enhancement of Chunks

Enhances content chunks with AI, saving progress incrementally.

Features:
- Progressive saving (each chunk saved immediately)
- Resume capability (continue from last completed chunk)
- Failure retry (retry only failed chunks)
- Progress tracking (real-time ETA)

Usage:
    # Basic usage
    uv run python stage4_enhance_chunks.py --chunks-id abc123 --provider codex

    # Resume from last position
    uv run python stage4_enhance_chunks.py --chunks-id abc123 --resume

    # Retry failed chunks
    uv run python stage4_enhance_chunks.py --chunks-id abc123 --retry-failed

    # Force restart from beginning
    uv run python stage4_enhance_chunks.py --chunks-id abc123 --provider codex --force
"""

import argparse
import json
import logging
import subprocess
import sys
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Tuple

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from app.document_processor.pipeline_manager import PipelineManager, CacheManager, PipelineStage
from app.document_processor.llm_cli_providers import get_provider

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def validate_progress_file(progress: Dict, expected_total_chunks: int, chunks_id: str) -> bool:
    """
    Validate progress file integrity and consistency.

    Args:
        progress: Progress dictionary to validate
        expected_total_chunks: Expected total number of chunks
        chunks_id: Chunks ID for logging

    Returns:
        True if progress file is valid, False otherwise
    """
    logger.info(f"Starting progress file validation for {chunks_id}")
    logger.debug(f"Progress file content: {progress}")

    # Check required fields
    required_fields = ["total_chunks", "completed_chunks", "failed_chunks", "provider"]
    for field in required_fields:
        if field not in progress:
            logger.error(f"Progress file missing required field: {field}")
            return False
        else:
            logger.debug(f"  - {field}: {progress[field]}")

    # Validate total_chunks
    if progress["total_chunks"] != expected_total_chunks:
        logger.warning(
            f"Progress file total_chunks ({progress['total_chunks']}) "
            f"doesn't match expected ({expected_total_chunks})"
        )
        # Update total_chunks to match expected
        progress["total_chunks"] = expected_total_chunks
        logger.info(f"Updated total_chunks to {expected_total_chunks}")
    else:
        logger.debug(f"Total chunks validation passed: {expected_total_chunks}")

    # Validate completed_chunks
    completed = progress.get("completed_chunks", 0)
    if not isinstance(completed, int) or completed < 0:
        logger.error(f"Invalid completed_chunks value: {completed}")
        return False

    if completed > expected_total_chunks:
        logger.warning(
            f"completed_chunks ({completed}) exceeds total_chunks ({expected_total_chunks})"
        )
        progress["completed_chunks"] = min(completed, expected_total_chunks)
        logger.info(f"Adjusted completed_chunks to {progress['completed_chunks']}")

    logger.debug(f"Completed chunks validation passed: {completed}")

    # Validate failed_chunks
    failed_chunks = progress.get("failed_chunks", [])
    if not isinstance(failed_chunks, list):
        logger.error(f"Invalid failed_chunks type: {type(failed_chunks)}")
        return False

    logger.debug(f"Failed chunks before validation: {failed_chunks}")

    # Check for invalid chunk numbers in failed_chunks
    valid_failed_chunks = [c for c in failed_chunks if 1 <= c <= expected_total_chunks]
    if len(valid_failed_chunks) != len(failed_chunks):
        invalid_count = len(failed_chunks) - len(valid_failed_chunks)
        logger.warning(f"Removed {invalid_count} invalid failed chunk numbers")
        progress["failed_chunks"] = valid_failed_chunks
        logger.debug(f"Invalid chunks removed: {[c for c in failed_chunks if c not in valid_failed_chunks]}")

    # Check for duplicate chunks in failed_chunks
    if len(set(failed_chunks)) != len(failed_chunks):
        duplicates = len(failed_chunks) - len(set(failed_chunks))
        logger.warning(f"Removed {duplicates} duplicate entries from failed_chunks")
        progress["failed_chunks"] = list(set(failed_chunks))

    # Validate completed_chunks doesn't overlap with failed_chunks
    if completed in failed_chunks:
        logger.warning(f"Chunk {completed} marked as both completed and failed, removing from failed")
        progress["failed_chunks"].remove(completed)

    logger.debug(f"Failed chunks after validation: {progress['failed_chunks']}")
    logger.info("Progress file validation completed successfully")
    return True


def check_cache_consistency(chunks_id: str, total_chunks: int, cache_dir: Path) -> Dict:
    """
    Check consistency between chunks cache and enhanced chunks cache.

    Args:
        chunks_id: Chunks ID to check
        total_chunks: Expected total number of chunks
        cache_dir: Cache directory path

    Returns:
        Dictionary with consistency check results
    """
    logger.info(f"Starting cache consistency check for {chunks_id}")

    pipeline = PipelineManager(cache_dir)

    # Check chunks cache
    chunks_cache_path = pipeline.cache_manager.get_cache_path(PipelineStage.CHUNKING, chunks_id)
    enhanced_cache_path = pipeline.cache_manager.get_cache_path(PipelineStage.ENHANCEMENT, chunks_id)

    results = {
        "chunks_cache_exists": False,
        "enhanced_cache_exists": False,
        "missing_chunks": [],
        "orphaned_chunks": [],
        "consistency_issues": [],
        "total_chunks_in_cache": 0,
        "enhanced_chunks_count": 0
    }

    # Check chunks cache
    if chunks_cache_path.exists():
        results["chunks_cache_exists"] = True
        chunks_data = pipeline.cache_manager.load_cache(PipelineStage.CHUNKING, chunks_id)
        if chunks_data and "chunks" in chunks_data:
            chunks_list = chunks_data["chunks"]
            results["total_chunks_in_cache"] = len(chunks_list)

            logger.debug(f"Chunks cache contains {results['total_chunks_in_cache']} chunks")

            if results["total_chunks_in_cache"] != total_chunks:
                results["consistency_issues"].append(
                    f"Chunks cache has {results['total_chunks_in_cache']} chunks, expected {total_chunks}"
                )
    else:
        results["consistency_issues"].append("Chunks cache file not found")
        logger.warning("Chunks cache file not found")

    # Check enhanced chunks cache
    if enhanced_cache_path.exists():
        results["enhanced_cache_exists"] = True

        # Count enhanced chunk files
        enhanced_files = list(enhanced_cache_path.glob("chunk-*.json"))
        results["enhanced_chunks_count"] = len(enhanced_files)

        logger.debug(f"Enhanced chunks cache contains {results['enhanced_chunks_count']} chunk files")

        # Parse chunk numbers from filenames
        enhanced_chunk_numbers = []
        for file_path in enhanced_files:
            try:
                # Extract chunk number from filename like "chunk-001.json"
                chunk_num = int(file_path.stem.split('-')[1])
                enhanced_chunk_numbers.append(chunk_num)
            except (ValueError, IndexError):
                results["consistency_issues"].append(f"Invalid chunk filename: {file_path.name}")

        enhanced_chunk_numbers.sort()

        # Check for missing chunks (1 to total_chunks)
        for chunk_num in range(1, total_chunks + 1):
            if chunk_num not in enhanced_chunk_numbers:
                results["missing_chunks"].append(chunk_num)

        # Check for orphaned chunks (chunk numbers beyond expected range)
        for chunk_num in enhanced_chunk_numbers:
            if chunk_num < 1 or chunk_num > total_chunks:
                results["orphaned_chunks"].append(chunk_num)

        # Log consistency issues
        if results["missing_chunks"]:
            logger.warning(f"Missing enhanced chunks: {results['missing_chunks']}")
            results["consistency_issues"].append(f"Missing {len(results['missing_chunks'])} enhanced chunks")

        if results["orphaned_chunks"]:
            logger.warning(f"Orphaned enhanced chunks: {results['orphaned_chunks']}")
            results["consistency_issues"].append(f"Found {len(results['orphaned_chunks'])} orphaned chunks")

    else:
        logger.debug("Enhanced chunks cache does not exist yet")

    # Summary
    if not results["consistency_issues"]:
        logger.info("Cache consistency check passed - no issues found")
    else:
        logger.warning(f"Cache consistency check found {len(results['consistency_issues'])} issues")
        for issue in results["consistency_issues"]:
            logger.warning(f"  - {issue}")

    logger.info(f"Cache consistency check completed: {results['enhanced_chunks_count']}/{total_chunks} chunks enhanced")
    return results


def enhance_single_chunk(
    chunk_content: str,
    category: str,
    chunk_num: int,
    total_chunks: int,
    provider,
    max_retries: int = 2
) -> str:
    """
    Enhance a single chunk using LLM CLI provider.

    Args:
        chunk_content: Content to enhance
        category: Tax category
        chunk_num: Current chunk number
        total_chunks: Total number of chunks
        provider: LLM CLI provider instance
        max_retries: Maximum number of retry attempts

    Returns:
        Enhanced content

    Raises:
        Exception: If all retry attempts fail
    """
    chunk_info = f" (chunk {chunk_num}/{total_chunks})" if total_chunks > 1 else ""

    prompt = f"""Please enhance this CRA tax content for the '{category}' category{chunk_info}.

Requirements:
1. Keep all factual information accurate and complete
2. Add practical examples where appropriate
3. Improve clarity and structure
4. Use professional Canadian tax terminology
5. Format as clean Markdown with proper headers (##, ###)
6. Make it actionable for developers building tax applications
7. IMPORTANT: Maintain at least 70% of the original content length
8. Preserve detailed explanations and legal nuances
9. Do not over-summarize complex tax provisions

IMPORTANT: Output ONLY the enhanced Markdown content, nothing else. No meta-commentary.

Content to enhance:
{chunk_content}

Enhanced content (Markdown only):"""

    last_error = None

    for attempt in range(max_retries + 1):
        try:
            if attempt > 0:
                logger.info(f"Retry attempt {attempt}/{max_retries} for chunk {chunk_num}")
                # Add small delay between retries
                time.sleep(2 ** attempt)  # Exponential backoff

            # Get timeout
            timeout = provider.get_timeout(len(chunk_content))

            # Check if provider is API-based
            if hasattr(provider, 'is_api_based') and provider.is_api_based():
                # API-based provider: call parse_output directly with prompt
                # For API providers, parse_output expects the prompt as stdout parameter
                enhanced = provider.parse_output(prompt, "")
                return enhanced
            else:
                # CLI-based provider: use subprocess
                command = provider.build_command(prompt)

                # Get provider-specific environment variables (e.g., GLM configuration)
                provider_env = provider.get_env()

                # Execute
                if provider.uses_stdin():
                    result = subprocess.run(
                        command,
                        input=prompt,
                        capture_output=True,
                        text=True,
                        timeout=timeout,
                        env=provider_env
                    )
                else:
                    result = subprocess.run(
                        command,
                        capture_output=True,
                        text=True,
                        timeout=timeout,
                        env=provider_env
                    )

                if result.returncode == 0:
                    enhanced = provider.parse_output(result.stdout, result.stderr)
                    if enhanced.strip():  # Check if result is not empty
                        return enhanced
                    else:
                        raise Exception("Provider returned empty content")
                else:
                    error_msg = f"Provider returned error code {result.returncode}"
                    if result.stderr:
                        error_msg += f": {result.stderr.strip()}"
                    raise Exception(error_msg)

        except subprocess.TimeoutExpired:
            last_error = f"Enhancement timed out for chunk {chunk_num} (attempt {attempt + 1})"
            logger.error(last_error)
            if attempt == max_retries:
                break
        except Exception as e:
            last_error = f"Enhancement failed for chunk {chunk_num} (attempt {attempt + 1}): {str(e)}"
            logger.error(last_error)
            if attempt == max_retries:
                break

    # All retries failed
    raise Exception(f"All retry attempts failed for chunk {chunk_num}. Last error: {last_error}")


def process_chunk_worker(
    chunk_num: int,
    chunk_data: Dict,
    category: str,
    total_chunks: int,
    provider_name: str,
    chunks_id: str,
    cache_dir: Path
) -> Tuple[int, bool, str, float]:
    """
    Worker function to process a single chunk in a subprocess.

    Args:
        chunk_num: Chunk number (1-indexed)
        chunk_data: Chunk data dictionary
        category: Tax category
        total_chunks: Total number of chunks
        provider_name: LLM provider name
        chunks_id: Chunks cache ID
        cache_dir: Cache directory path

    Returns:
        Tuple of (chunk_num, success, message, processing_time)

    Raises:
        Exception: If chunk processing fails (fast-fail behavior)
    """
    start_time = time.time()

    try:
        logger.debug(f"Starting processing for chunk {chunk_num}")
        logger.debug(f"  - Provider: {provider_name}")
        logger.debug(f"  - Category: {category}")
        logger.debug(f"  - Content length: {chunk_data.get('char_count', 'unknown')}")

        # Initialize provider in this subprocess
        provider = get_provider(provider_name)

        if not provider:
            raise Exception(f"Provider '{provider_name}' not available")

        logger.debug(f"Provider '{provider_name}' initialized successfully")

        # Enhance the chunk
        enhanced_content = enhance_single_chunk(
            chunk_data['content'],
            category,
            chunk_num,
            total_chunks,
            provider
        )

        logger.debug(f"Enhancement completed for chunk {chunk_num}")

        # Validate enhanced content length
        original_char_count = chunk_data.get('char_count', 0)
        enhanced_char_count = len(enhanced_content)
        length_ratio = enhanced_char_count / original_char_count if original_char_count > 0 else 0

        logger.debug(f"Content length validation for chunk {chunk_num}:")
        logger.debug(f"  - Original: {original_char_count} chars")
        logger.debug(f"  - Enhanced: {enhanced_char_count} chars")
        logger.debug(f"  - Ratio: {length_ratio:.2f}")

        if length_ratio < 0.6:
            logger.warning(
                f"Chunk {chunk_num}: Enhanced content significantly shorter "
                f"({enhanced_char_count} vs {original_char_count} chars, ratio: {length_ratio:.2f})"
            )
            # Note: We still save the result but log the warning for monitoring

        # Save enhanced chunk immediately
        logger.debug(f"Saving enhanced chunk {chunk_num} to cache")
        pipeline = PipelineManager(cache_dir)
        output_dir = pipeline.cache_manager.get_cache_path(
            PipelineStage.ENHANCEMENT,
            chunks_id
        )
        output_dir.mkdir(parents=True, exist_ok=True)

        chunk_file = output_dir / f"chunk-{chunk_num:03d}.json"
        chunk_output = {
            "chunk_id": chunk_num,
            "title": chunk_data.get('title', ''),
            "slug": chunk_data.get('slug', ''),
            "enhanced_content": enhanced_content,
            "original_char_count": chunk_data.get('char_count', 0),
            "enhanced_char_count": len(enhanced_content),
            "enhanced_at": datetime.now().isoformat(),
            "provider": provider_name
        }

        with open(chunk_file, 'w', encoding='utf-8') as f:
            json.dump(chunk_output, f, ensure_ascii=False, indent=2)

        logger.debug(f"Successfully saved chunk {chunk_num} to {chunk_file}")
        logger.debug(f"Chunk {chunk_num} output summary:")
        logger.debug(f"  - Title: {chunk_data.get('title', 'No title')}")
        logger.debug(f"  - Provider: {provider_name}")
        logger.debug(f"  - File size: {chunk_file.stat().st_size} bytes")

        processing_time = time.time() - start_time
        logger.debug(f"Chunk {chunk_num} processing completed in {processing_time:.1f}s")
        return (chunk_num, True, f"Success ({processing_time:.1f}s)", processing_time)

    except Exception as e:
        processing_time = time.time() - start_time
        error_msg = f"Failed: {str(e)}"

        # Enhanced error logging
        logger.error(f"Chunk {chunk_num} processing failed after {processing_time:.1f}s: {e}")
        logger.error(f"  - Provider: {provider_name}")
        logger.error(f"  - Category: {category}")
        logger.error(f"  - Original content length: {chunk_data.get('char_count', 'unknown')}")

        # Provide helpful error messages for common issues
        error_str = str(e).lower()
        if "timeout" in error_str:
            logger.error(f"  - Suggestion: Consider increasing timeout or reducing chunk size")
            raise Exception(f"Chunk {chunk_num} processing timed out after {processing_time:.1f}s")
        elif "provider" in error_str and "not available" in error_str:
            logger.error(f"  - Suggestion: Check if {provider_name} CLI tool is properly installed and accessible")
            raise Exception(f"Provider '{provider_name}' not available for chunk {chunk_num}")
        elif "return code" in error_str:
            logger.error(f"  - Suggestion: Provider CLI tool failed, check system resources and tool configuration")
            raise Exception(f"Provider CLI tool failed for chunk {chunk_num}: {str(e)}")
        else:
            raise Exception(f"Chunk {chunk_num} processing failed: {str(e)}")


def enhance_chunks(
    chunks_id: str,
    provider_name: str = None,
    resume: bool = False,
    retry_failed: bool = False,
    force: bool = False,
    cache_dir: Path = None,
    workers: int = 1
) -> bool:
    """
    Enhance all chunks with AI, saving progressively.

    Args:
        chunks_id: Chunks cache hash ID
        provider_name: LLM provider name (claude/gemini/codex/glm-api)
        resume: Resume from last completed chunk
        retry_failed: Retry only failed chunks
        force: Force restart from beginning
        cache_dir: Cache directory path

    Returns:
        True if successful
    """
    # Initialize managers
    pipeline = PipelineManager(cache_dir)
    cache_mgr = CacheManager(cache_dir)

    print(f"\n{'='*60}")
    print(f"Stage 4: AI Enhancement of Chunks")
    print(f"{'='*60}")
    print(f"Chunks ID: {chunks_id}")

    # Load chunks
    chunks_data = cache_mgr.load_cache(PipelineStage.CHUNKING, chunks_id)
    if not chunks_data:
        print(f"❌ Error: Chunks cache not found for ID: {chunks_id}")
        return False

    chunks = chunks_data.get("chunks", [])
    total_chunks = len(chunks)
    print(f"Total chunks: {total_chunks}")

    # Load classification
    classification_data = cache_mgr.load_cache(PipelineStage.CLASSIFICATION, chunks_id)
    if not classification_data:
        print(f"❌ Error: Classification cache not found for ID: {chunks_id}")
        return False

    category = classification_data.get("primary_category", "unknown")
    print(f"Category: {category}")

    # Perform cache consistency check
    consistency_results = check_cache_consistency(chunks_id, total_chunks, cache_dir or Path('cache'))

    # Log consistency results at info level if there are issues
    if consistency_results["consistency_issues"]:
        print(f"\n⚠️  Cache consistency issues detected:")
        for issue in consistency_results["consistency_issues"]:
            print(f"   - {issue}")

    # Check existing progress
    progress = pipeline.get_enhancement_progress(chunks_id)

    if force and progress:
        print(f"\n⚠️  Force mode: Ignoring existing progress")
        progress = None
    elif progress:
        # Validate progress file integrity
        if not validate_progress_file(progress, total_chunks, chunks_id):
            print(f"\n❌ Error: Progress file validation failed")
            print(f"   Use --force to restart or --resume to attempt recovery")
            return False

        # Save corrected progress if validation made changes
        pipeline.save_enhancement_progress(chunks_id, progress)

        if not resume and not retry_failed:
            completed = progress.get("completed_chunks", 0)
            failed_count = len(progress.get("failed_chunks", []))

            # Check if all chunks are already completed
            if completed == total_chunks and failed_count == 0:
                print(f"\n✅ All chunks already enhanced ({completed}/{total_chunks})")
                print(f"   Skipping enhancement stage")
                return True  # Success - all work is done
            else:
                # Incomplete progress - require explicit resume
                print(f"\n⚠️  Found incomplete progress:")
                print(f"   Completed: {completed}/{total_chunks}")
                print(f"   Failed: {failed_count}")
                print(f"   Use --resume to continue or --force to restart")
                return False

    # Determine provider
    if provider_name:
        print(f"\nProvider: {provider_name}")
        provider = get_provider(provider_name)
        if not provider:
            print(f"❌ Error: Provider '{provider_name}' not available")
            return False
    elif resume and progress:
        provider_name = progress.get("provider")
        print(f"\nResuming with provider: {provider_name}")
        provider = get_provider(provider_name)
        if not provider:
            print(f"❌ Error: Provider '{provider_name}' not available")
            return False
    else:
        print(f"❌ Error: Provider required (use --provider)")
        return False

    # Determine which chunks to process
    if retry_failed and progress:
        failed_chunks = progress.get("failed_chunks", [])
        chunks_to_process = [i for i in failed_chunks if 1 <= i <= total_chunks]
        print(f"\n🔄 Retrying {len(chunks_to_process)} failed chunks")
    elif resume and progress:
        completed_chunks = progress.get("completed_chunks", 0)
        chunks_to_process = list(range(completed_chunks + 1, total_chunks + 1))
        print(f"\n▶️  Resuming from chunk {completed_chunks + 1}")
    else:
        chunks_to_process = list(range(1, total_chunks + 1))
        print(f"\n🚀 Starting fresh enhancement")

    if not chunks_to_process:
        print(f"\n✅ All chunks already completed!")
        return True

    # Initialize progress
    if not progress or force:
        progress = {
            "total_chunks": total_chunks,
            "completed_chunks": 0,
            "failed_chunks": [],
            "start_time": datetime.now().isoformat(),
            "provider": provider_name
        }

    print(f"\nChunks to process: {len(chunks_to_process)}")
    print(f"Workers: {workers}")
    est_time_per_chunk = 6  # average minutes per chunk
    est_total = len(chunks_to_process) * est_time_per_chunk / workers
    print(f"Estimated time: {int(est_total)} minutes ({len(chunks_to_process)} chunks ÷ {workers} workers)")
    print(f"\n{'='*60}")

    # Initialize provider for performance monitoring
    print(f"\nInitializing provider: {provider_name}")
    provider_init_start = time.time()

    provider = get_provider(provider_name)

    if not provider:
        raise Exception(f"Provider '{provider_name}' not available")

    provider_init_time = time.time() - provider_init_start
    print(f"Provider initialized in {provider_init_time:.2f}s")

    # Process chunks
    start_time = time.time()
    successful = 0
    failed = 0
    completed_count = 0
    active_chunks = set()

    # Filter chunks that need processing
    chunks_needing_processing = []
    for chunk_num in chunks_to_process:
        chunk_index = chunk_num - 1
        existing_chunk_file = pipeline.cache_manager.get_cache_path(
            PipelineStage.ENHANCEMENT,
            chunks_id
        ) / f"chunk-{chunk_num:03d}.json"

        if existing_chunk_file.exists() and not retry_failed and not force:
            # Already completed, skip
            completed_count += 1
            successful += 1
            continue

        chunks_needing_processing.append((chunk_num, chunks[chunk_index]))

    if not chunks_needing_processing:
        print("\n✅ All chunks already completed!")
        print(f"\n💡 Next step: uv run python stage5_generate_skill.py --enhanced-id {chunks_id}")
        return True

    print(f"\n🔄 Processing {len(chunks_needing_processing)} chunks with {workers} workers...")

    # Use ProcessPoolExecutor for parallel processing
    if workers > 1:
        with ProcessPoolExecutor(max_workers=workers) as executor:
            # Submit all chunks
            future_to_chunk = {}
            for chunk_num, chunk_data in chunks_needing_processing:
                future = executor.submit(
                    process_chunk_worker,
                    chunk_num,
                    chunk_data,
                    category,
                    total_chunks,
                    provider_name,
                    chunks_id,
                    cache_dir or Path('cache')
                )
                future_to_chunk[future] = chunk_num
                active_chunks.add(chunk_num)

            # Process completed chunks as they finish
            try:
                for future in as_completed(future_to_chunk):
                    chunk_num = future_to_chunk[future]
                    active_chunks.discard(chunk_num)

                    try:
                        result_chunk_num, success, message, proc_time = future.result()
                        completed_count += 1

                        # Update progress - fast-fail mode: no failure handling expected
                        if success:
                            successful += 1
                            # Remove from failed list if present
                            if result_chunk_num in progress.get("failed_chunks", []):
                                progress["failed_chunks"].remove(result_chunk_num)
                            # Update completed count
                            progress["completed_chunks"] = max(
                                progress.get("completed_chunks", 0),
                                result_chunk_num
                            )
                        else:
                            # This should not happen in fast-fail mode, but handle it gracefully
                            error_msg = f"Chunk {result_chunk_num} returned failure status"
                            executor.shutdown(wait=False, cancel_futures=True)
                            print(f"\n❌ {error_msg}")
                            print("🛑 Processing stopped due to failure (fast-fail mode)")
                            raise Exception(f"Fast-fail: {error_msg}")

                        # Calculate ETA
                        elapsed = time.time() - start_time
                        avg_time = elapsed / completed_count if completed_count > 0 else 0
                        remaining = len(chunks_needing_processing) - completed_count
                        eta_seconds = (remaining / workers) * avg_time if avg_time > 0 else 0
                        eta = str(timedelta(seconds=int(eta_seconds)))

                        progress["last_update"] = datetime.now().isoformat()
                        progress["estimated_remaining"] = eta
                        pipeline.save_enhancement_progress(chunks_id, progress)

                        # Status display
                        status_symbol = "✅" if success else "❌"
                        print(f"{status_symbol} Chunk {result_chunk_num}/{total_chunks}: {message}")
                        print(f"   Progress: {completed_count}/{len(chunks_needing_processing)} ({completed_count*100//len(chunks_needing_processing)}%) | "
                              f"Active: {len(active_chunks)} | ETA: {eta}")

                    except Exception as e:
                        # Fast-fail: immediately terminate processing and raise exception
                        executor.shutdown(wait=False, cancel_futures=True)
                        error_msg = f"❌ Chunk {chunk_num}/{total_chunks} failed: {str(e)}"
                        print(f"\n{error_msg}")
                        print("🛑 Processing stopped due to error (fast-fail mode)")
                        print(f"\n💡 To retry this chunk, run: uv run python stage4_enhance_chunks.py --chunks-id {chunks_id} --retry-failed")
                        raise Exception(f"Fast-fail: Chunk {chunk_num} processing failed: {str(e)}")

            except KeyboardInterrupt:
                print("\n\n⚠️  Interrupted! Shutting down workers...")
                executor.shutdown(wait=False, cancel_futures=True)
                print("✓ Workers stopped. Progress has been saved.")
                print(f"\n💡 Resume with: uv run python stage4_enhance_chunks.py --chunks-id {chunks_id} --resume")
                return False

    else:
        # Serial processing (workers=1)
        for i, (chunk_num, chunk_data) in enumerate(chunks_needing_processing, 1):
            print(f"\n--- Chunk {chunk_num}/{total_chunks} ({i}/{len(chunks_needing_processing)}) ---")
            result_chunk_num, success, message, proc_time = process_chunk_worker(
                chunk_num,
                chunk_data,
                category,
                total_chunks,
                provider_name,
                chunks_id,
                cache_dir or Path('cache')
            )

            completed_count += 1

            # Update progress - fast-fail mode
            if success:
                successful += 1
                if result_chunk_num in progress.get("failed_chunks", []):
                    progress["failed_chunks"].remove(result_chunk_num)
                progress["completed_chunks"] = max(
                    progress.get("completed_chunks", 0),
                    result_chunk_num
                )
            else:
                # Fast-fail: immediately stop processing
                error_msg = f"Chunk {result_chunk_num} failed: {message}"
                print(f"\n❌ {error_msg}")
                print("🛑 Processing stopped due to failure (fast-fail mode)")
                print(f"\n💡 To retry this chunk, run: uv run python stage4_enhance_chunks.py --chunks-id {chunks_id} --retry-failed")
                raise Exception(f"Fast-fail: {error_msg}")

            # Calculate ETA
            elapsed = time.time() - start_time
            avg_time = elapsed / completed_count
            remaining = len(chunks_needing_processing) - completed_count
            eta_seconds = remaining * avg_time
            eta = str(timedelta(seconds=int(eta_seconds)))

            progress["last_update"] = datetime.now().isoformat()
            progress["estimated_remaining"] = eta
            pipeline.save_enhancement_progress(chunks_id, progress)

            # Status display
            status_symbol = "✅" if success else "❌"
            print(f"{status_symbol} {message}")
            print(f"   Progress: {completed_count}/{len(chunks_needing_processing)} | ETA: {eta}")

    # Final summary
    total_elapsed = time.time() - start_time

    print(f"\n{'='*60}")
    print(f"Enhancement Complete!")
    print(f"{'='*60}")
    print(f"Successful: {successful}/{len(chunks_needing_processing)}")
    print(f"Failed: {failed}/{len(chunks_needing_processing)}")
    print(f"Total time: {str(timedelta(seconds=int(total_elapsed)))}")
    if workers > 1:
        print(f"Workers: {workers} (avg {total_elapsed/len(chunks_needing_processing):.1f}s per chunk)")
    print(f"Provider initialization: {provider_init_time:.2f}s")

    # In fast-fail mode, we should not have any failures
    if failed > 0:
        print(f"\n⚠️  Unexpected failures in fast-fail mode")
        print(f"   This indicates a potential issue with the error handling")
        return False

    if successful > 0:
        print(f"\n💡 Next step: uv run python stage5_generate_skill.py --enhanced-id {chunks_id}")

    return True  # In fast-fail mode, if we reached here, all chunks succeeded


def main():
    parser = argparse.ArgumentParser(
        description='Stage 4: Enhance chunks with AI',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Enhance all chunks
  python stage4_enhance_chunks.py --chunks-id abc123 --provider codex

  # Resume from last position
  python stage4_enhance_chunks.py --chunks-id abc123 --resume

  # Retry failed chunks
  python stage4_enhance_chunks.py --chunks-id abc123 --retry-failed

  # Force restart
  python stage4_enhance_chunks.py --chunks-id abc123 --provider codex --force

  # Using GLM through Direct API
  python stage4_enhance_chunks.py --chunks-id abc123 --provider glm-api
        """
    )

    parser.add_argument(
        '--chunks-id',
        type=str,
        required=True,
        help='Chunks cache hash ID (from stage3)'
    )

    parser.add_argument(
        '--provider',
        type=str,
        choices=['claude', 'gemini', 'codex', 'glm-api'],
        help='LLM provider to use (required unless --resume)'
    )

    parser.add_argument(
        '--resume',
        action='store_true',
        help='Resume from last completed chunk'
    )

    parser.add_argument(
        '--retry-failed',
        action='store_true',
        help='Retry only failed chunks'
    )

    parser.add_argument(
        '--force',
        action='store_true',
        help='Force restart from beginning (ignore progress)'
    )

    parser.add_argument(
        '--cache-dir',
        type=Path,
        help='Cache directory (default: backend/cache/)'
    )

    parser.add_argument(
        '--workers',
        type=int,
        default=1,
        choices=range(1, 9),
        metavar='N',
        help='Number of parallel workers (1-8, default: 1)'
    )

    args = parser.parse_args()

    # Enhance chunks
    try:
        success = enhance_chunks(
            args.chunks_id,
            provider_name=args.provider,
            resume=args.resume,
            retry_failed=args.retry_failed,
            force=args.force,
            cache_dir=args.cache_dir,
            workers=args.workers
        )

        return 0 if success else 1

    except KeyboardInterrupt:
        print(f"\n\n⏸️  Enhancement interrupted by user")
        print(f"💡 Resume with: uv run python stage4_enhance_chunks.py --chunks-id {args.chunks_id} --resume")
        return 130  # Standard exit code for Ctrl+C

    except Exception as e:
        print(f"\n❌ Enhancement failed: {e}")
        logger.exception("Enhancement failed")
        return 1


if __name__ == '__main__':
    sys.exit(main())
