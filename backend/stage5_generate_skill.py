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
from app.document_processor.dynamic_classifier import DynamicSemanticClassifier

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def convert_dynamic_to_skill_metadata(dynamic_classification, source_file: str) -> ClassificationResult:
    """
    Convert dynamic classification result to existing system's ClassificationResult format.

    Args:
        dynamic_classification: DynamicClassification result from semantic classifier
        source_file: Original source file path

    Returns:
        ClassificationResult compatible with existing skill generation system
    """
    # Extract primary category information
    primary_name = dynamic_classification.primary_category.name
    primary_type = dynamic_classification.primary_category.category_type

    # Generate skill ID from primary category
    import re
    skill_id = f"{primary_type.value.lower()}-{primary_name.lower()}"
    skill_id = re.sub(r'[^a-z0-9-]', '-', skill_id)
    skill_id = re.sub(r'-+', '-', skill_id).strip('-')
    skill_id = skill_id[:50]  # Limit length

    # Map dynamic category types to existing TaxCategory
    from app.document_processor.content_classifier import TaxCategory

    # Simple mapping - can be enhanced
    category_mapping = {
        "domain": TaxCategory.UNKNOWN,
        "purpose": TaxCategory.UNKNOWN,
        "topic": TaxCategory.UNKNOWN,
        "level": TaxCategory.UNKNOWN,
        "temporal": TaxCategory.UNKNOWN,
        "geographic": TaxCategory.UNKNOWN,
        "audience": TaxCategory.UNKNOWN,
        "format": TaxCategory.UNKNOWN
    }

    mapped_category = category_mapping.get(primary_type.value, TaxCategory.UNKNOWN)

    # Determine confidence and quality based on primary category
    confidence = dynamic_classification.primary_category.confidence

    # Create quality metrics
    quality_metrics = QualityMetrics(
        relevance_score=confidence,
        clarity_score=confidence,
        completeness_score=confidence,
        accuracy_score=confidence,
        overall_score=confidence
    )

    # Create ClassificationResult
    result = ClassificationResult(
        primary_category=mapped_category,
        confidence=confidence,
        secondary_categories=[],  # Can be mapped more intelligently later
        quality_metrics=quality_metrics,
        matched_keywords=list(dynamic_classification.primary_category.keywords)
    )

    return result


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

    # Initialize glm_analysis variable
    glm_analysis = None

    # Check if we have dynamic classification to override the standard skill metadata
    if glm_analysis and hasattr(glm_analysis, 'primary_category') and hasattr(glm_analysis.primary_category, 'name'):
        # This is a DynamicClassification result
        print(f"🧠 Using dynamic semantic classification for skill metadata...")

        # Convert dynamic classification to standard format
        dynamic_classification = convert_dynamic_to_skill_metadata(glm_analysis, pdf_path)

        # Generate new skill with dynamic classification
        skill = generator.generate_skill(
            content=total_text,
            classification=dynamic_classification,
            source_file=pdf_path
        )

        print(f"✅ Dynamic skill metadata generated:")
        print(f"   Primary: {glm_analysis.primary_category.name}")
        print(f"   Confidence: {glm_analysis.primary_category.confidence:.2f}")
        print(f"   Secondary: {[cat.name for cat in glm_analysis.secondary_categories[:3]]}")
    else:
        # Generate standard skill metadata
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

    # Use enhanced provider based on selection
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
    elif provider == "dynamic-semantic":
        print(f"🧠 Using Dynamic Semantic Classification provider...")
        try:
            from app.document_processor.glm_claude_processor import DocumentChunk, DocumentSplitter

            # Use existing enhanced chunks as TOC entries for dynamic classification
            toc_entries = []
            for chunk in enhanced_chunks:
                toc_entries.append({
                    'title': chunk.get('original_title', f'Section {chunk.get("chunk_id")}'),
                    'level': 1,
                    'page_number': 1,
                    'char_start': 0,
                    'char_end': 1000
                })

            # Create dynamic classifier
            dynamic_classifier = DynamicSemanticClassifier(provider_name="glm-claude")

            print(f"📊 Performing dynamic semantic classification...")
            # Since we're in sync context, we'll use a synchronous approach
            import asyncio

            # Create an event loop for the async call
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            try:
                dynamic_classification = loop.run_until_complete(
                    dynamic_classifier.classify_document(total_text, Path(pdf_path).stem, toc_entries)
                )
                print(f"✅ Dynamic classification completed:")
                print(f"   Primary: {dynamic_classification.primary_category.name}")
                print(f"   Confidence: {dynamic_classification.primary_category.confidence:.2f}")
                print(f"   Secondary: {[cat.name for cat in dynamic_classification.secondary_categories[:3]]}")
                print(f"   Tags: {[tag.tag for tag in dynamic_classification.semantic_tags[:5]]}")

                # Store for later use
                glm_analysis = dynamic_classification
            finally:
                loop.close()

        except Exception as e:
            print(f"⚠️ Dynamic classification failed: {e}")
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

    # 3. Improve titles using TOC if available
    if glm_analysis:
        if hasattr(glm_analysis, 'toc') and glm_analysis.toc.entries:
            # Standard GLM-Claude analysis with TOC
            print(f"🏷️  Improving chapter titles using GLM TOC...")
            reference_chunks = generator._improve_chapter_titles_with_toc(reference_chunks, glm_analysis.toc.entries)
        elif hasattr(glm_analysis, 'semantic_tags'):
            # Dynamic classification - use semantic information for title improvement
            print(f"🏷️  Improving chapter titles using dynamic classification insights...")
            # For now, we'll skip title improvement as the dynamic classifier doesn't generate TOC
            # In the future, we could use semantic tags to improve titles
        else:
            print(f"🏷️  No TOC information available for title improvement")
    else:
        print(f"🏷️  No analysis results available for title improvement")

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
        choices=['gemini', 'glm-claude', 'dynamic-semantic'],
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
