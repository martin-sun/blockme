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
import logging
import subprocess
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path

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


def enhance_chunks(
    chunks_id: str,
    provider_name: str = None,
    resume: bool = False,
    retry_failed: bool = False,
    force: bool = False,
    cache_dir: Path = None
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
        failed = len(progress.get("failed_chunks", []))
        print(f"\n⚠️  Found existing progress:")
        print(f"   Completed: {completed}/{total_chunks}")
        print(f"   Failed: {failed}")
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
    print(f"Estimated time: {len(chunks_to_process) * 5}-{len(chunks_to_process) * 8} minutes")
    print(f"\n{'='*60}")

    # Process chunks
    start_time = time.time()
    successful = 0
    failed = 0

    for i, chunk_num in enumerate(chunks_to_process, 1):
        chunk_index = chunk_num - 1  # 0-indexed for array access
        chunk = chunks[chunk_index]

        print(f"\n--- Chunk {chunk_num}/{total_chunks}: {chunk['title'][:50]} ---")
        print(f"Progress: {i}/{len(chunks_to_process)} ({i*100//len(chunks_to_process)}%)")
        print(f"Size: {chunk['char_count']:,} chars")

        # Check if already completed
        existing_chunk_file = pipeline.cache_manager.get_cache_path(
            PipelineStage.ENHANCEMENT,
            chunks_id
        ) / f"chunk-{chunk_num:03d}.json"

        if existing_chunk_file.exists() and not retry_failed:
            print(f"✓ Already enhanced, skipping")
            continue

        try:
            # Enhance chunk
            print(f"🤖 Enhancing with {provider_name}...")
            chunk_start = time.time()

            enhanced_content = enhance_single_chunk(
                chunk['content'],
                category,
                chunk_num,
                total_chunks,
                provider
            )

            chunk_elapsed = time.time() - chunk_start

            # Save chunk immediately
            chunk_data = {
                "chunk_id": chunk_num,
                "original_title": chunk['title'],
                "slug": chunk['slug'],
                "enhanced_content": enhanced_content,
                "enhancement_time": datetime.now().isoformat(),
                "provider": provider_name,
                "status": "completed",
                "elapsed_seconds": int(chunk_elapsed)
            }

            pipeline.save_enhanced_chunk(chunks_id, chunk_num, chunk_data)

            # Update progress
            if chunk_num not in progress.get("failed_chunks", []):
                progress["completed_chunks"] = max(
                    progress.get("completed_chunks", 0),
                    chunk_num
                )
            else:
                # Remove from failed list
                progress["failed_chunks"].remove(chunk_num)

            progress["last_update"] = datetime.now().isoformat()

            # Calculate ETA
            elapsed = time.time() - start_time
            avg_time_per_chunk = elapsed / i
            remaining_chunks = len(chunks_to_process) - i
            eta_seconds = remaining_chunks * avg_time_per_chunk
            eta = str(timedelta(seconds=int(eta_seconds)))

            progress["estimated_remaining"] = eta

            pipeline.save_enhancement_progress(chunks_id, progress)

            print(f"✅ Enhanced ({int(chunk_elapsed)}s)")
            print(f"📊 ETA: {eta} | Avg: {int(avg_time_per_chunk)}s/chunk")

            successful += 1

        except Exception as e:
            print(f"❌ Failed: {e}")

            # Mark as failed
            if chunk_num not in progress.get("failed_chunks", []):
                progress["failed_chunks"].append(chunk_num)

            progress["last_update"] = datetime.now().isoformat()
            pipeline.save_enhancement_progress(chunks_id, progress)

            failed += 1

            # Continue with next chunk
            continue

    # Final summary
    total_elapsed = time.time() - start_time
    print(f"\n{'='*60}")
    print(f"Enhancement Complete!")
    print(f"{'='*60}")
    print(f"Successful: {successful}/{len(chunks_to_process)}")
    print(f"Failed: {failed}/{len(chunks_to_process)}")
    print(f"Total time: {str(timedelta(seconds=int(total_elapsed)))}")

    if failed > 0:
        print(f"\n⚠️  Some chunks failed. Retry with:")
        print(f"   uv run python stage4_enhance_chunks.py --chunks-id {chunks_id} --retry-failed")

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
        choices=['claude', 'gemini', 'codex'],
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

    args = parser.parse_args()

    # Enhance chunks
    try:
        success = enhance_chunks(
            args.chunks_id,
            provider_name=args.provider,
            resume=args.resume,
            retry_failed=args.retry_failed,
            force=args.force,
            cache_dir=args.cache_dir
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
