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


def enhance_single_chunk(
    chunk_content: str,
    category: str,
    chunk_num: int,
    total_chunks: int,
    provider
) -> str:
    """
    Enhance a single chunk using LLM CLI provider.

    Args:
        chunk_content: Content to enhance
        category: Tax category
        chunk_num: Current chunk number
        total_chunks: Total number of chunks
        provider: LLM CLI provider instance

    Returns:
        Enhanced content
    """
    chunk_info = f" (chunk {chunk_num}/{total_chunks})" if total_chunks > 1 else ""

    prompt = f"""Please optimize this CRA tax content for the '{category}' category{chunk_info}.

Requirements:
1. Keep all factual information accurate and complete
2. Add practical examples where appropriate
3. Improve clarity and structure
4. Use professional Canadian tax terminology
5. Format as clean Markdown with proper headers (##, ###)
6. Make it actionable for developers building tax applications

IMPORTANT: Output ONLY the enhanced Markdown content, nothing else. No meta-commentary.

Content to enhance:
{chunk_content}

Enhanced content (Markdown only):"""

    try:
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

            # Execute
            if provider.uses_stdin():
                result = subprocess.run(
                    command,
                    input=prompt,
                    capture_output=True,
                    text=True,
                    timeout=timeout
                )
            else:
                result = subprocess.run(
                    command,
                    capture_output=True,
                    text=True,
                    timeout=timeout
                )

            if result.returncode == 0:
                enhanced = provider.parse_output(result.stdout, result.stderr)
                return enhanced
            else:
                logger.error(f"Enhancement failed for chunk {chunk_num}: code {result.returncode}")
                raise Exception(f"Provider returned error code {result.returncode}")

    except subprocess.TimeoutExpired:
        logger.error(f"Enhancement timed out for chunk {chunk_num}")
        raise
    except Exception as e:
        logger.error(f"Enhancement failed for chunk {chunk_num}: {e}")
        raise


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
    """
    start_time = time.time()

    try:
        # Initialize provider in this subprocess
        provider = get_provider(provider_name)
        if not provider:
            return (chunk_num, False, f"Provider '{provider_name}' not available", 0.0)

        # Enhance the chunk
        enhanced_content = enhance_single_chunk(
            chunk_data['content'],
            category,
            chunk_num,
            total_chunks,
            provider
        )

        # Save enhanced chunk immediately
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

        processing_time = time.time() - start_time
        return (chunk_num, True, f"Success ({processing_time:.1f}s)", processing_time)

    except Exception as e:
        processing_time = time.time() - start_time
        error_msg = f"Failed: {str(e)}"
        logger.error(f"Chunk {chunk_num} failed: {e}")
        return (chunk_num, False, error_msg, processing_time)


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

    # Check existing progress
    progress = pipeline.get_enhancement_progress(chunks_id)

    if force and progress:
        print(f"\n⚠️  Force mode: Ignoring existing progress")
        progress = None
    elif progress and not resume and not retry_failed:
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

                        # Update progress
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
                            failed += 1
                            if result_chunk_num not in progress.get("failed_chunks", []):
                                progress["failed_chunks"].append(result_chunk_num)

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
                        failed += 1
                        completed_count += 1
                        if chunk_num not in progress.get("failed_chunks", []):
                            progress["failed_chunks"].append(chunk_num)
                        progress["last_update"] = datetime.now().isoformat()
                        pipeline.save_enhancement_progress(chunks_id, progress)
                        print(f"❌ Chunk {chunk_num}/{total_chunks}: Exception: {e}")

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

            # Update progress
            if success:
                successful += 1
                if result_chunk_num in progress.get("failed_chunks", []):
                    progress["failed_chunks"].remove(result_chunk_num)
                progress["completed_chunks"] = max(
                    progress.get("completed_chunks", 0),
                    result_chunk_num
                )
            else:
                failed += 1
                if result_chunk_num not in progress.get("failed_chunks", []):
                    progress["failed_chunks"].append(result_chunk_num)

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

    if failed > 0:
        print(f"\n⚠️  Some chunks failed. Retry with:")
        print(f"   uv run python stage4_enhance_chunks.py --chunks-id {chunks_id} --retry-failed --workers {workers}")

    if successful > 0:
        print(f"\n💡 Next step: uv run python stage5_generate_skill.py --enhanced-id {chunks_id}")

    return failed == 0


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
