#!/usr/bin/env python3
"""
BeanFlow-CRA: One-Click Pipeline Runner

Runs all 5 stages of the PDF processing pipeline in sequence.

Usage:
    # Basic usage with GLM API
    uv run python run_pipeline.py --pdf ../mvp/pdf/rc4022-24e.pdf --provider glm-api

    # Full document processing
    uv run python run_pipeline.py --pdf ../mvp/pdf/rc4022-24e.pdf --provider glm-api --full

    # With parallel workers for Stage 4
    uv run python run_pipeline.py --pdf ../mvp/pdf/rc4022-24e.pdf --provider glm-api --full --workers 4

    # Skip AI enhancement (Stage 4)
    uv run python run_pipeline.py --pdf ../mvp/pdf/rc4022-24e.pdf --provider glm-api --skip-enhance
"""

import argparse
import sys
import time
from datetime import timedelta
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from stage1_extract_pdf import extract_pdf
from stage2_classify_content import classify_content
from stage3_chunk_content import chunk_content
from stage4_enhance_chunks import enhance_chunks
from stage5_generate_skill import generate_skill_directory


def run_pipeline(
    pdf_path: Path,
    provider: str,
    max_pages: int = None,
    output_dir: str = "skills_output",
    cache_dir: Path = None,
    force: bool = False,
    skip_enhance: bool = False,
    workers: int = 1
) -> bool:
    """
    Run the complete PDF processing pipeline.

    Args:
        pdf_path: Path to PDF file
        provider: LLM provider name (glm-api, claude, gemini, codex)
        max_pages: Maximum pages to process (None for all)
        output_dir: Output directory for skills
        cache_dir: Cache directory path
        force: Force re-process all stages
        skip_enhance: Skip Stage 4 (AI enhancement)
        workers: Number of parallel workers for Stage 4

    Returns:
        True if successful
    """
    start_time = time.time()

    print(f"\n{'='*70}")
    print(f"BeanFlow-CRA: PDF Processing Pipeline")
    print(f"{'='*70}")
    print(f"📄 PDF: {pdf_path}")
    print(f"🤖 Provider: {provider}")
    print(f"📦 Pages: {'All' if max_pages is None else f'First {max_pages}'}")
    print(f"📁 Output: {output_dir}")
    if skip_enhance:
        print(f"⏭️  Stage 4 (AI Enhancement): SKIPPED")
    else:
        print(f"👷 Workers: {workers}")
    print(f"{'='*70}")

    # ========================================
    # Stage 1: PDF Extraction
    # ========================================
    print(f"\n🔹 Stage 1/5: PDF Extraction")
    try:
        extraction_data = extract_pdf(
            pdf_path=pdf_path,
            max_pages=max_pages,
            force=force,
            cache_dir=cache_dir
        )
        extraction_id = extraction_data["pdf_hash"]
        print(f"   ✅ Extraction ID: {extraction_id}")
    except Exception as e:
        print(f"   ❌ Stage 1 failed: {e}")
        return False

    # ========================================
    # Stage 2: Content Classification
    # ========================================
    print(f"\n🔹 Stage 2/5: Content Classification")
    try:
        classification_data = classify_content(
            extraction_id=extraction_id,
            force=force,
            cache_dir=cache_dir,
            provider=provider
        )
        if classification_data is None:
            print(f"   ❌ Stage 2 failed: No classification data")
            return False
        print(f"   ✅ Category: {classification_data.get('primary_category')}")
    except Exception as e:
        print(f"   ❌ Stage 2 failed: {e}")
        return False

    # ========================================
    # Stage 3: Content Chunking
    # ========================================
    print(f"\n🔹 Stage 3/5: Content Chunking")
    try:
        chunking_data = chunk_content(
            extraction_id=extraction_id,
            force=force,
            cache_dir=cache_dir
        )
        if chunking_data is None:
            print(f"   ❌ Stage 3 failed: No chunking data")
            return False
        print(f"   ✅ Chunks: {chunking_data.get('total_chunks')}")
    except Exception as e:
        print(f"   ❌ Stage 3 failed: {e}")
        return False

    # ========================================
    # Stage 4: AI Enhancement (optional)
    # ========================================
    if skip_enhance:
        print(f"\n🔹 Stage 4/5: AI Enhancement [SKIPPED]")
    else:
        print(f"\n🔹 Stage 4/5: AI Enhancement")
        try:
            success = enhance_chunks(
                chunks_id=extraction_id,
                provider_name=provider,
                force=force,
                cache_dir=cache_dir,
                workers=workers
            )
            if not success:
                print(f"   ❌ Stage 4 failed")
                return False
            print(f"   ✅ Enhancement complete")
        except Exception as e:
            print(f"   ❌ Stage 4 failed: {e}")
            return False

    # ========================================
    # Stage 5: Generate Skill Directory
    # ========================================
    print(f"\n🔹 Stage 5/5: Generate Skill Directory")
    try:
        skill_dir = generate_skill_directory(
            enhanced_id=extraction_id,
            output_dir=output_dir,
            force=force,
            cache_dir=cache_dir
        )
        if skill_dir is None:
            print(f"   ❌ Stage 5 failed: No skill directory")
            return False
        print(f"   ✅ Skill: {skill_dir}")
    except Exception as e:
        print(f"   ❌ Stage 5 failed: {e}")
        return False

    # ========================================
    # Summary
    # ========================================
    elapsed = time.time() - start_time
    elapsed_str = str(timedelta(seconds=int(elapsed)))

    print(f"\n{'='*70}")
    print(f"✅ Pipeline Complete!")
    print(f"{'='*70}")
    print(f"📁 Skill Directory: {skill_dir}")
    print(f"⏱️  Total Time: {elapsed_str}")
    print(f"{'='*70}")

    return True


def main():
    parser = argparse.ArgumentParser(
        description='BeanFlow-CRA: One-Click PDF Processing Pipeline',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Process with GLM API (recommended)
  uv run python run_pipeline.py --pdf ../mvp/pdf/rc4022-24e.pdf --provider glm-api

  # Full document with parallel processing
  uv run python run_pipeline.py --pdf ../mvp/pdf/t4012-24e.pdf --provider glm-api --full --workers 4

  # Quick test without AI enhancement
  uv run python run_pipeline.py --pdf ../mvp/pdf/rc4022-24e.pdf --provider glm-api --skip-enhance

  # Process first 30 pages
  uv run python run_pipeline.py --pdf ../mvp/pdf/t4012-24e.pdf --provider glm-api --max-pages 30

Available Providers:
  glm-api     GLM-4 via Direct API (recommended, requires GLM_API_KEY)
  claude      Claude Code CLI (requires claude login)
  gemini      Gemini CLI (requires gemini login)
  codex       Codex CLI (requires codex login)
        """
    )

    parser.add_argument(
        '--pdf',
        type=Path,
        required=True,
        help='Path to PDF file'
    )

    parser.add_argument(
        '--provider',
        type=str,
        required=True,
        choices=['glm-api', 'claude', 'gemini', 'gemini-api', 'codex'],
        help='LLM provider to use'
    )

    parser.add_argument(
        '--full',
        action='store_true',
        help='Process full document (default: first 10 pages)'
    )

    parser.add_argument(
        '--max-pages',
        type=int,
        default=10,
        help='Maximum pages to process if not --full (default: 10)'
    )

    parser.add_argument(
        '--output-dir',
        type=str,
        default='skills_output',
        help='Output directory for skills (default: skills_output)'
    )

    parser.add_argument(
        '--cache-dir',
        type=Path,
        help='Cache directory (default: backend/cache/)'
    )

    parser.add_argument(
        '--force',
        action='store_true',
        help='Force re-process all stages (ignore cache)'
    )

    parser.add_argument(
        '--skip-enhance',
        action='store_true',
        help='Skip Stage 4 (AI enhancement) for quick testing'
    )

    parser.add_argument(
        '--workers',
        type=int,
        default=1,
        choices=range(1, 9),
        metavar='N',
        help='Number of parallel workers for Stage 4 (1-8, default: 1)'
    )

    args = parser.parse_args()

    # Validate PDF exists
    if not args.pdf.exists():
        print(f"❌ Error: PDF file not found: {args.pdf}")
        return 1

    # Determine max_pages
    max_pages = None if args.full else args.max_pages

    # Run pipeline
    try:
        success = run_pipeline(
            pdf_path=args.pdf,
            provider=args.provider,
            max_pages=max_pages,
            output_dir=args.output_dir,
            cache_dir=args.cache_dir,
            force=args.force,
            skip_enhance=args.skip_enhance,
            workers=args.workers
        )
        return 0 if success else 1

    except KeyboardInterrupt:
        print(f"\n\n⏸️  Pipeline interrupted by user")
        print(f"💡 Progress has been saved. Re-run the same command to resume.")
        return 130

    except Exception as e:
        print(f"\n❌ Pipeline failed: {e}")
        return 1


if __name__ == '__main__':
    sys.exit(main())
