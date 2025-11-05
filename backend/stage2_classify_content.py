#!/usr/bin/env python3
"""
Stage 2: Content Classification

Classifies extracted content using smart multi-signal algorithm.

Usage:
    # Basic usage
    uv run python stage2_classify_content.py --extraction-id abc123

    # Force re-classification (ignore cache)
    uv run python stage2_classify_content.py --extraction-id abc123 --force

    # Custom cache directory
    uv run python stage2_classify_content.py --extraction-id abc123 --cache-dir /path/to/cache
"""

import argparse
import logging
import sys
from datetime import datetime
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from app.document_processor.content_classifier import ContentClassifier
from app.document_processor.pipeline_manager import CacheManager, PipelineStage

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def classify_content(
    extraction_id: str,
    force: bool = False,
    cache_dir: Path = None
) -> dict:
    """
    Classify extracted content with caching.

    Args:
        extraction_id: Extraction cache hash ID
        force: Force re-classification even if cached
        cache_dir: Cache directory path

    Returns:
        Classification data dict
    """
    # Initialize cache manager
    cache_mgr = CacheManager(cache_dir)

    print(f"\n{'='*60}")
    print(f"Stage 2: Content Classification")
    print(f"{'='*60}")
    print(f"Extraction ID: {extraction_id}")

    # Load extraction data
    extraction_data = cache_mgr.load_cache(PipelineStage.EXTRACTION, extraction_id)
    if not extraction_data:
        print(f"❌ Error: Extraction cache not found for ID: {extraction_id}")
        print(f"   Expected: {cache_mgr.get_cache_path(PipelineStage.EXTRACTION, extraction_id)}")
        print(f"\n💡 Run stage1_extract_pdf.py first")
        return None

    total_text = extraction_data.get("total_text", "")
    print(f"Loaded extraction: {len(total_text):,} chars from {extraction_data.get('processed_pages')} pages")

    # Check classification cache
    if not force:
        cached_classification = cache_mgr.load_cache(PipelineStage.CLASSIFICATION, extraction_id)
        if cached_classification:
            print(f"\n✅ Found cached classification: {cache_mgr.get_cache_path(PipelineStage.CLASSIFICATION, extraction_id)}")
            print(f"   Category: {cached_classification.get('primary_category')}")
            print(f"   Confidence: {cached_classification.get('confidence'):.2f}")
            print(f"   Cached at: {cached_classification.get('classification_time')}")
            print("\n💡 Use --force to re-classify")
            return cached_classification

    # Classify content
    print(f"\n🏷️  Classifying content...")

    classifier = ContentClassifier()

    try:
        classification = classifier.classify(total_text)
    except Exception as e:
        logger.error(f"Failed to classify content: {e}")
        raise

    # Prepare classification data
    classification_data = {
        "primary_category": classification.primary_category.value,
        "confidence": classification.confidence,
        "secondary_categories": [
            {
                "category": cat.value,
                "confidence": classification.confidence
            }
            for cat in classification.secondary_categories
        ],
        "quality_metrics": {
            "completeness": classification.quality_metrics.completeness,
            "accuracy": classification.quality_metrics.accuracy,
            "relevance": classification.quality_metrics.relevance,
            "clarity": classification.quality_metrics.clarity,
            "practicality": classification.quality_metrics.practicality,
            "overall_score": classification.quality_metrics.overall_score,
            "quality_grade": classification.quality_metrics.quality_grade
        },
        "matched_keywords": classification.matched_keywords,
        "classification_time": datetime.now().isoformat()
    }

    # Save to cache
    print(f"\n💾 Saving classification to cache...")
    cache_path = cache_mgr.save_cache(
        PipelineStage.CLASSIFICATION,
        extraction_id,
        classification_data,
        metadata={
            "primary_category": classification.primary_category.value,
            "confidence": classification.confidence
        }
    )

    print(f"\n✅ Classification complete!")
    print(f"   Primary category: {classification.primary_category.value}")
    print(f"   Confidence: {classification.confidence:.2f}")
    print(f"   Secondary categories: {len(classification.secondary_categories)}")
    print(f"   Matched keywords: {len(classification.matched_keywords)}")
    print(f"   Cache: {cache_path}")

    # Show quality metrics
    print(f"\n📊 Quality Metrics:")
    print(f"   Completeness: {classification.quality_metrics.completeness:.2f}")
    print(f"   Accuracy: {classification.quality_metrics.accuracy:.2f}")
    print(f"   Relevance: {classification.quality_metrics.relevance:.2f}")
    print(f"   Clarity: {classification.quality_metrics.clarity:.2f}")
    print(f"   Practicality: {classification.quality_metrics.practicality:.2f}")
    print(f"   Overall score: {classification.quality_metrics.overall_score:.2f} ({classification.quality_metrics.quality_grade})")

    print(f"\n💡 Next step: uv run python stage3_chunk_content.py --extraction-id {extraction_id}")

    return classification_data


def main():
    parser = argparse.ArgumentParser(
        description='Stage 2: Classify extracted content',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Classify content
  python stage2_classify_content.py --extraction-id abc123

  # Force re-classification
  python stage2_classify_content.py --extraction-id abc123 --force

  # List available extractions
  python -c "from app.document_processor.pipeline_manager import CacheManager; \\
             [print(f'{p[\"content_hash\"]}: {p[\"pdf_path\"]}') \\
              for p in CacheManager().list_cached_pdfs()]"
        """
    )

    parser.add_argument(
        '--extraction-id',
        type=str,
        required=True,
        help='Extraction cache hash ID (from stage1)'
    )

    parser.add_argument(
        '--force',
        action='store_true',
        help='Force re-classification even if cached'
    )

    parser.add_argument(
        '--cache-dir',
        type=Path,
        help='Cache directory (default: backend/cache/)'
    )

    args = parser.parse_args()

    # Classify content
    try:
        classification_data = classify_content(
            args.extraction_id,
            force=args.force,
            cache_dir=args.cache_dir
        )

        if classification_data is None:
            return 1

        return 0

    except Exception as e:
        print(f"\n❌ Classification failed: {e}")
        logger.exception("Classification failed")
        return 1


if __name__ == '__main__':
    sys.exit(main())
