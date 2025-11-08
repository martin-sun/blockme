#!/usr/bin/env python3
"""
Stage 5: Generate Skill Directory

Generates final skill directory from cached enhanced chunks.

Usage:
    # Basic usage
    uv run python stage5_generate_skill.py --enhanced-id abc123

    # Custom output directory
    uv run python stage5_generate_skill.py --enhanced-id abc123 --output-dir my_skills

    # Force overwrite existing skill
    uv run python stage5_generate_skill.py --enhanced-id abc123 --force
"""

import argparse
import logging
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from app.document_processor.pipeline_manager import PipelineManager, CacheManager, PipelineStage
from app.document_processor.skill_generator import SkillGenerator
from app.document_processor.content_classifier import ClassificationResult, TaxCategory
from app.document_processor.glm_claude_processor import GLMClaudeProcessor

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def generate_skill_directory(
    enhanced_id: str,
    output_dir: str = "skills_output",
    force: bool = False,
    cache_dir: Path = None,
    provider: str = "gemini"
) -> Path:
    """
    Generate skill directory from cached enhanced chunks.

    Args:
        enhanced_id: Enhanced chunks cache hash ID
        output_dir: Output directory for skills
        force: Force overwrite if skill exists
        cache_dir: Cache directory path
        provider: LLM provider to use (gemini, glm-claude)

    Returns:
        Path to generated skill directory
    """
    # Initialize managers
    pipeline = PipelineManager(cache_dir)
    cache_mgr = CacheManager(cache_dir)

    print(f"\n{'='*60}")
    print(f"Stage 5: Generate Skill Directory")
    print(f"{'='*60}")
    print(f"Enhanced ID: {enhanced_id}")

    # Load all required caches
    print(f"\n📦 Loading cached data...")

    # 1. Load extraction
    extraction_data = cache_mgr.load_cache(PipelineStage.EXTRACTION, enhanced_id)
    if not extraction_data:
        print(f"❌ Error: Extraction cache not found")
        return None

    total_text = extraction_data.get("total_text", "")
    pdf_path = extraction_data.get("pdf_path", "")
    print(f"✓ Extraction: {len(total_text):,} chars")

    # 2. Load classification
    classification_data = cache_mgr.load_cache(PipelineStage.CLASSIFICATION, enhanced_id)
    if not classification_data:
        print(f"❌ Error: Classification cache not found")
        return None

    category_str = classification_data.get("primary_category")
    category = TaxCategory(category_str)
    print(f"✓ Classification: {category.value}")

    # Reconstruct ClassificationResult for SkillGenerator
    from app.document_processor.content_classifier import ClassificationResult, QualityMetrics

    classification = ClassificationResult(
        primary_category=category,
        confidence=classification_data.get("confidence", 0.85),
        secondary_categories=[
            TaxCategory(sc["category"])
            for sc in classification_data.get("secondary_categories", [])
        ],
        quality_metrics=QualityMetrics(**classification_data.get("quality_metrics", {})),
        matched_keywords=classification_data.get("matched_keywords", [])
    )

    # 3. Load original chunks
    chunks_data = cache_mgr.load_cache(PipelineStage.CHUNKING, enhanced_id)
    if not chunks_data:
        print(f"❌ Error: Chunks cache not found")
        return None

    print(f"✓ Chunks: {chunks_data.get('total_chunks')} chunks")

    # 4. Load enhanced chunks
    enhanced_chunks = pipeline.load_enhanced_chunks(enhanced_id)
    if not enhanced_chunks:
        print(f"❌ Error: No enhanced chunks found")
        print(f"   Run stage4_enhance_chunks.py first")
        return None

    print(f"✓ Enhanced chunks: {len(enhanced_chunks)}")

    # Check progress
    progress = pipeline.get_enhancement_progress(enhanced_id)
    if progress:
        completed = progress.get("completed_chunks", 0)
        total = progress.get("total_chunks", len(enhanced_chunks))
        failed = len(progress.get("failed_chunks", []))

        if completed < total or failed > 0:
            print(f"\n⚠️  Warning: Enhancement incomplete")
            print(f"   Completed: {completed}/{total}")
            print(f"   Failed: {failed}")
            print(f"   Continue anyway? Some references may be missing.")

    # Generate skill
    print(f"\n🔨 Generating skill...")

    generator = SkillGenerator(output_dir=output_dir)

    # Generate skill metadata
    skill = generator.generate_skill(
        content=total_text,
        classification=classification,
        source_file=pdf_path
    )

    print(f"✅ Skill metadata generated")
    print(f"   ID: {skill.metadata.id}")
    print(f"   Title: {skill.metadata.title}")
    print(f"   Category: {skill.metadata.category}")
    print(f"   Tags: {', '.join(skill.metadata.tags[:5])}")

    # Check if skill already exists
    skill_dir = Path(output_dir) / skill.metadata.id
    if skill_dir.exists() and not force:
        print(f"\n⚠️  Skill directory already exists: {skill_dir}")
        print(f"   Use --force to overwrite")
        return None

    print(f"🔧 Processing {len(enhanced_chunks)} enhanced chunks...")

    # If using GLM-Claude provider, enhance metadata with its analysis capabilities
    if provider == "glm-claude":
        print(f"🤖 Using GLM-Claude provider for enhanced analysis...")
        try:
            glm_processor = GLMClaudeProcessor(provider_name="glm-claude")

            # Analyze the full document to get better metadata
            print(f"📊 Performing GLM analysis for skill generation...")
            glm_analysis = glm_processor.analyze_full_document(total_text, Path(pdf_path).stem)

            print(f"✅ GLM analysis completed:")
            print(f"   Category: {glm_analysis.classification.primary_category.value}")
            print(f"   Confidence: {glm_analysis.classification.confidence:.2f}")
            print(f"   TOC entries: {glm_analysis.toc.total_entries}")

        except Exception as e:
            print(f"⚠️ GLM-Claude analysis failed: {e}")
            print(f"   Falling back to standard processing...")
            glm_analysis = None
    else:
        glm_analysis = None

    # Prepare reference chunks for save_skill_directory
    reference_chunks = []
    for enhanced_chunk in enhanced_chunks:
        reference_chunks.append({
            'content': enhanced_chunk.get('enhanced_content', ''),
            'title': enhanced_chunk.get('original_title', f'Section {enhanced_chunk.get("chunk_id")}'),
            'slug': enhanced_chunk.get('slug', f'section-{enhanced_chunk.get("chunk_id")}'),
            'chapter_num': enhanced_chunk.get('chunk_id', 0)
        })

    # Apply optimizations
    print(f"🧹 Applying optimizations...")

    # 1. Remove duplicate content
    reference_chunks = generator._deduplicate_content_chunks(reference_chunks)
    print(f"   Removed duplicates: {len(enhanced_chunks) - len(reference_chunks)} chunks")

    # 2. Ensure continuous chapter numbering
    reference_chunks = generator._generate_continuous_chapters(reference_chunks)
    print(f"   Ensured continuous numbering: {len(reference_chunks)} chapters")

    # 3. Improve titles using GLM TOC if available
    if glm_analysis and glm_analysis.toc.entries:
        print(f"🏷️  Improving chapter titles using GLM TOC...")
        reference_chunks = generator._improve_chapter_titles_with_toc(reference_chunks, glm_analysis.toc.entries)

    # Sort by chapter_num (final sort)
    reference_chunks.sort(key=lambda x: x['chapter_num'])

    # Save skill directory
    print(f"\n💾 Saving skill directory...")

    skill_dir = generator.save_skill_directory(
        skill_id=skill.metadata.id,
        raw_text=total_text,
        reference_chunks=reference_chunks,
        metadata=skill.metadata,
        subdirectory=None
    )

    print(f"\n✅ Skill directory created!")
    print(f"   Path: {skill_dir}")
    print(f"   ├── SKILL.md")
    print(f"   ├── references/")
    print(f"   │   ├── index.md")
    print(f"   │   └── *.md ({len(reference_chunks)} files)")
    print(f"   └── raw/")
    print(f"       └── full-extract.txt")

    # Show file sizes
    skill_md_size = (skill_dir / "SKILL.md").stat().st_size
    full_extract_size = (skill_dir / "raw" / "full-extract.txt").stat().st_size

    print(f"\n📊 File Sizes:")
    print(f"   SKILL.md: {skill_md_size:,} bytes")
    print(f"   full-extract.txt: {full_extract_size:,} bytes")

    # Calculate total references size
    refs_size = sum(
        f.stat().st_size
        for f in (skill_dir / "references").glob("*.md")
    )
    print(f"   references/*.md: {refs_size:,} bytes ({len(reference_chunks)} files)")
    print(f"   Total: {skill_md_size + full_extract_size + refs_size:,} bytes")

    print(f"\n💡 Next step (optional): uv run python enhance_skill.py --skill-dir {skill_dir}")

    return skill_dir


def main():
    parser = argparse.ArgumentParser(
        description='Stage 5: Generate skill directory from enhanced chunks',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate skill directory
  python stage5_generate_skill.py --enhanced-id abc123

  # Custom output directory
  python stage5_generate_skill.py --enhanced-id abc123 --output-dir my_skills

  # Force overwrite
  python stage5_generate_skill.py --enhanced-id abc123 --force
        """
    )

    parser.add_argument(
        '--enhanced-id',
        type=str,
        required=True,
        help='Enhanced chunks cache hash ID (from stage4)'
    )

    parser.add_argument(
        '--output-dir',
        type=str,
        default='skills_output',
        help='Output directory for skills (default: skills_output)'
    )

    parser.add_argument(
        '--force',
        action='store_true',
        help='Force overwrite if skill exists'
    )

    parser.add_argument(
        '--cache-dir',
        type=Path,
        help='Cache directory (default: backend/cache/)'
    )

    parser.add_argument(
        '--provider',
        type=str,
        default='gemini',
        choices=['gemini', 'glm-claude'],
        help='LLM provider to use for enhanced processing (default: gemini)'
    )

    args = parser.parse_args()

    # Generate skill directory
    try:
        skill_dir = generate_skill_directory(
            args.enhanced_id,
            output_dir=args.output_dir,
            force=args.force,
            cache_dir=args.cache_dir,
            provider=args.provider
        )

        if skill_dir is None:
            return 1

        return 0

    except Exception as e:
        print(f"\n❌ Skill generation failed: {e}")
        logger.exception("Skill generation failed")
        return 1


if __name__ == '__main__':
    sys.exit(main())
