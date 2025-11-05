#!/usr/bin/env python3
"""
Generate skill files from CRA tax PDFs using multi-stage pipeline.

This script orchestrates the 5-stage processing pipeline:
1. PDF Extraction (with caching)
2. Content Classification
3. Content Chunking
4. AI Enhancement (resumable)
5. Skill Directory Generation
6. SKILL.md Enhancement (optional)

Usage:
    # Basic processing (no AI enhancement)
    uv run python generate_skill.py --pdf ../mvp/pdf/t4012-24e.pdf --no-ai

    # With local Codex (recommended)
    uv run python generate_skill.py --pdf ../mvp/pdf/t4012-24e.pdf --local-codex

    # With local Claude
    uv run python generate_skill.py --pdf ../mvp/pdf/t4012-24e.pdf --local-claude

    # Process full document (all 151 pages, ~7-11 hours with AI)
    uv run python generate_skill.py --pdf ../mvp/pdf/t4012-24e.pdf --local-codex --full

    # With SKILL.md enhancement
    uv run python generate_skill.py --pdf ../mvp/pdf/t4012-24e.pdf --local-codex --enhance-skill
"""

import argparse
import logging
import subprocess
import sys
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Add backend to Python path
sys.path.insert(0, str(Path(__file__).parent))

from app.document_processor.pipeline_manager import CacheManager, PipelineManager, PipelineStage
from app.document_processor.llm_cli_providers import get_provider


def run_stage_script(script_name: str, args: list, description: str) -> bool:
    """
    Run a stage script.

    Args:
        script_name: Script filename (e.g., "stage1_extract_pdf.py")
        args: Command-line arguments list
        description: Human-readable description

    Returns:
        True if successful, False otherwise
    """
    script_path = Path(__file__).parent / script_name
    command = [sys.executable, str(script_path)] + args

    print(f"\n{'='*60}")
    print(f"{description}")
    print(f"{'='*60}")
    print(f"Running: {' '.join(command)}")
    print()

    try:
        result = subprocess.run(
            command,
            check=True,
            capture_output=False,  # Show output directly
            text=True
        )
        return True

    except subprocess.CalledProcessError as e:
        logger.error(f"Stage failed: {script_name}")
        return False


def main():
    parser = argparse.ArgumentParser(
        description='Generate skill files from CRA tax PDFs using multi-stage pipeline',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Pipeline Stages:
  1. PDF Extraction     - Extract text from PDF (cached)
  2. Classification     - Classify tax category (cached)
  3. Chunking          - Split into chapters (cached)
  4. AI Enhancement    - Enhance with LLM (resumable)
  5. Skill Generation  - Create skill directory
  6. SKILL Enhancement - Enhance SKILL.md (optional)

Caching & Resumability:
  - Stages 1-3 are cached automatically
  - Stage 4 supports resume after interruption (Ctrl+C)
  - Re-running with same PDF will skip completed stages
  - Use different --max-pages to force re-extraction

Examples:
  # Quick test (10 pages, no AI)
  python generate_skill.py --pdf FILE.pdf --no-ai

  # Full processing with AI (151 pages, 7-11 hours)
  python generate_skill.py --pdf FILE.pdf --local-codex --full

  # Resume interrupted enhancement
  python generate_skill.py --pdf FILE.pdf --local-codex --full
  (automatically resumes from last completed chunk)
        """
    )

    # Required arguments
    parser.add_argument(
        '--pdf',
        required=True,
        type=Path,
        help='Path to PDF file'
    )

    # Output configuration
    parser.add_argument(
        '--output-dir',
        default='skills_output',
        help='Output directory for generated skills (default: skills_output)'
    )

    # PDF extraction options
    parser.add_argument(
        '--full',
        action='store_true',
        help='Process full document (default: first 10 pages only)'
    )

    parser.add_argument(
        '--max-pages',
        type=int,
        default=10,
        help='Maximum pages to process if not --full (default: 10)'
    )

    # LLM provider options
    parser.add_argument(
        '--no-ai',
        action='store_true',
        help='Skip AI enhancement (stages 4-6 use original content)'
    )

    parser.add_argument(
        '--local-claude',
        action='store_true',
        help='Use local Claude CLI for enhancement'
    )

    parser.add_argument(
        '--local-gemini',
        action='store_true',
        help='Use local Gemini CLI for enhancement'
    )

    parser.add_argument(
        '--local-codex',
        action='store_true',
        help='Use local Codex CLI for enhancement'
    )

    parser.add_argument(
        '--glm-api',
        action='store_true',
        help='Use GLM API for enhancement (requires GLM_API_KEY)'
    )

    # Enhancement options
    parser.add_argument(
        '--enhance-skill',
        action='store_true',
        help='Enhance SKILL.md with AI after generation (adds 3-5 minutes)'
    )

    parser.add_argument(
        '--workers',
        type=int,
        default=1,
        choices=range(1, 9),
        metavar='N',
        help='Number of parallel workers for AI enhancement (1-8, default: 1). Use 4 for optimal speed.'
    )

    # Cache options
    parser.add_argument(
        '--force-extract',
        action='store_true',
        help='Force re-extraction of PDF (ignore cache)'
    )

    parser.add_argument(
        '--cache-dir',
        type=Path,
        help='Cache directory (default: backend/cache/)'
    )

    args = parser.parse_args()

    # Validate PDF
    if not args.pdf.exists():
        print(f"❌ PDF file not found: {args.pdf}")
        return 1

    print(f"\n{'='*60}")
    print("PDF Document Processing Pipeline")
    print(f"{'='*60}\n")
    print(f"📄 PDF: {args.pdf.name}")
    print(f"📁 Output: {args.output_dir}")
    print(f"📦 Pages: {'All' if args.full else f'First {args.max_pages}'}")

    # Determine provider
    provider_name = None
    if not args.no_ai:
        if args.local_claude:
            provider_name = 'claude'
        elif args.local_gemini:
            provider_name = 'gemini'
        elif args.local_codex:
            provider_name = 'codex'
        elif args.glm_api:
            provider_name = 'glm-api'
        else:
            print("\n❌ Error: Must specify LLM provider or use --no-ai")
            print("   Options: --local-claude, --local-gemini, --local-codex, --glm-api, --no-ai")
            return 1

        # Verify provider available
        provider = get_provider(provider_name)
        if not provider:
            print(f"\n❌ Error: Provider '{provider_name}' not available")
            print(f"   Check that the CLI is installed and in PATH")
            return 1

        print(f"🤖 Provider: {provider_name}")
    else:
        print(f"🤖 Provider: None (--no-ai)")

    # Calculate PDF hash for cache
    cache_mgr = CacheManager(args.cache_dir)
    pdf_hash = cache_mgr.hash_file(args.pdf)
    print(f"🔑 PDF hash: {pdf_hash}")

    # Check existing cache
    pipeline = PipelineManager(args.cache_dir)
    cache_status = pipeline.get_stage_status(pdf_hash)

    print(f"\n📊 Cache Status:")
    print(f"   Stage 1 (Extraction):    {'✅ Cached' if cache_status.get(PipelineStage.EXTRACTION) else '⏳ Not cached'}")
    print(f"   Stage 2 (Classification): {'✅ Cached' if cache_status.get(PipelineStage.CLASSIFICATION) else '⏳ Not cached'}")
    print(f"   Stage 3 (Chunking):       {'✅ Cached' if cache_status.get(PipelineStage.CHUNKING) else '⏳ Not cached'}")
    print(f"   Stage 4 (Enhancement):    {'✅ Cached' if cache_status.get(PipelineStage.ENHANCEMENT) else '⏳ Not cached'}")

    # Check enhancement progress
    if cache_status.get(PipelineStage.ENHANCEMENT):
        progress = pipeline.get_enhancement_progress(pdf_hash)
        if progress:
            completed = progress.get("completed_chunks", 0)
            total = progress.get("total_chunks", 0)
            failed = len(progress.get("failed_chunks", []))
            print(f"   Enhancement progress: {completed}/{total} chunks")
            if failed > 0:
                print(f"   Failed chunks: {failed}")

    # ========================================
    # Stage 1: PDF Extraction
    # ========================================
    stage1_args = [
        '--pdf', str(args.pdf)
    ]

    if args.full:
        stage1_args.append('--full')
    else:
        stage1_args.extend(['--max-pages', str(args.max_pages)])

    if args.force_extract:
        stage1_args.append('--force')

    if args.cache_dir:
        stage1_args.extend(['--cache-dir', str(args.cache_dir)])

    success = run_stage_script(
        'stage1_extract_pdf.py',
        stage1_args,
        'Stage 1: PDF Extraction'
    )

    if not success:
        print("\n❌ Pipeline failed at Stage 1")
        return 1

    # ========================================
    # Stage 2: Content Classification
    # ========================================
    stage2_args = [
        '--extraction-id', pdf_hash
    ]

    if args.cache_dir:
        stage2_args.extend(['--cache-dir', str(args.cache_dir)])

    success = run_stage_script(
        'stage2_classify_content.py',
        stage2_args,
        'Stage 2: Content Classification'
    )

    if not success:
        print("\n❌ Pipeline failed at Stage 2")
        return 1

    # ========================================
    # Stage 3: Content Chunking
    # ========================================
    stage3_args = [
        '--extraction-id', pdf_hash
    ]

    if args.cache_dir:
        stage3_args.extend(['--cache-dir', str(args.cache_dir)])

    success = run_stage_script(
        'stage3_chunk_content.py',
        stage3_args,
        'Stage 3: Content Chunking'
    )

    if not success:
        print("\n❌ Pipeline failed at Stage 3")
        return 1

    # ========================================
    # Stage 4: AI Enhancement (optional)
    # ========================================
    if not args.no_ai:
        stage4_args = [
            '--chunks-id', pdf_hash,
            '--provider', provider_name,
            '--workers', str(args.workers)
        ]

        # Check if we should resume
        if cache_status.get(PipelineStage.ENHANCEMENT):
            progress = pipeline.get_enhancement_progress(pdf_hash)
            if progress:
                completed = progress.get("completed_chunks", 0)
                total = progress.get("total_chunks", 0)
                if completed > 0 and completed < total:
                    print(f"\n💡 Detected incomplete enhancement ({completed}/{total} chunks)")
                    print(f"   Will resume from chunk {completed + 1}")
                    stage4_args.append('--resume')

        if args.cache_dir:
            stage4_args.extend(['--cache-dir', str(args.cache_dir)])

        success = run_stage_script(
            'stage4_enhance_chunks.py',
            stage4_args,
            'Stage 4: AI Enhancement'
        )

        if not success:
            print("\n❌ Pipeline failed at Stage 4")
            print("\n💡 You can resume enhancement later with:")
            print(f"   uv run python stage4_enhance_chunks.py --chunks-id {pdf_hash} --resume")
            return 1
    else:
        print(f"\n{'='*60}")
        print("Stage 4: AI Enhancement")
        print(f"{'='*60}")
        print("⏭️  Skipped (--no-ai)")
        print("   Will use original content without enhancement")

    # ========================================
    # Stage 5: Generate Skill Directory
    # ========================================
    stage5_args = [
        '--enhanced-id', pdf_hash,
        '--output-dir', args.output_dir
    ]

    if args.cache_dir:
        stage5_args.extend(['--cache-dir', str(args.cache_dir)])

    success = run_stage_script(
        'stage5_generate_skill.py',
        stage5_args,
        'Stage 5: Generate Skill Directory'
    )

    if not success:
        print("\n❌ Pipeline failed at Stage 5")
        return 1

    # Find the generated skill directory
    # Load extraction to get skill_id
    extraction_data = cache_mgr.load_cache(PipelineStage.EXTRACTION, pdf_hash)
    classification_data = cache_mgr.load_cache(PipelineStage.CLASSIFICATION, pdf_hash)

    if extraction_data and classification_data:
        from app.document_processor.skill_generator import SkillGenerator
        generator = SkillGenerator(output_dir=args.output_dir)

        # Generate skill_id
        pdf_path = Path(extraction_data.get("pdf_path", ""))
        from app.document_processor.content_classifier import TaxCategory
        category = TaxCategory(classification_data.get("primary_category"))

        skill_id = generator._generate_skill_id(category, str(pdf_path))
        skill_dir = Path(args.output_dir) / skill_id

        # ========================================
        # Stage 6: SKILL.md Enhancement (optional)
        # ========================================
        if args.enhance_skill and provider_name:
            print(f"\n{'='*60}")
            print("Stage 6: SKILL.md Enhancement")
            print(f"{'='*60}")

            enhance_args = [
                'python',
                'enhance_skill.py',
                '--skill-dir', str(skill_dir),
                '--provider', provider_name
            ]

            success = run_stage_script(
                'enhance_skill.py',
                ['--skill-dir', str(skill_dir), '--provider', provider_name],
                'Stage 6: SKILL.md Enhancement'
            )

            if not success:
                print("\n⚠️  SKILL.md enhancement failed (using basic version)")

        # ========================================
        # Final Summary
        # ========================================
        print(f"\n{'='*60}")
        print("✅ Pipeline Complete!")
        print(f"{'='*60}\n")

        print(f"📁 Skill directory: {skill_dir}")
        print(f"   ├── SKILL.md")
        print(f"   ├── references/")
        print(f"   │   ├── index.md")
        print(f"   │   └── *.md")
        print(f"   └── raw/")
        print(f"       └── full-extract.txt")

        # Show cache location
        print(f"\n💾 Cache: {cache_mgr.cache_dir}")
        print(f"   Intermediate results saved for re-use")

        # Show manual stage commands
        print(f"\n💡 Manual Stage Commands:")
        print(f"   Stage 1: uv run python stage1_extract_pdf.py --pdf {args.pdf}")
        print(f"   Stage 2: uv run python stage2_classify_content.py --extraction-id {pdf_hash}")
        print(f"   Stage 3: uv run python stage3_chunk_content.py --extraction-id {pdf_hash}")
        if provider_name:
            print(f"   Stage 4: uv run python stage4_enhance_chunks.py --chunks-id {pdf_hash} --provider {provider_name}")
        print(f"   Stage 5: uv run python stage5_generate_skill.py --enhanced-id {pdf_hash}")

        return 0
    else:
        print("\n❌ Failed to load cache data for final summary")
        return 1


if __name__ == '__main__':
    sys.exit(main())
