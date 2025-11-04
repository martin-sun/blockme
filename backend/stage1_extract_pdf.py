#!/usr/bin/env python3
"""
Stage 1: PDF Text Extraction

Extracts text from PDF and caches the result.

Usage:
    # Basic usage
    uv run python stage1_extract_pdf.py --pdf ../mvp/pdf/t4012-24e.pdf

    # Process full document
    uv run python stage1_extract_pdf.py --pdf PATH --full

    # Limit pages
    uv run python stage1_extract_pdf.py --pdf PATH --max-pages 30

    # Force re-extraction (ignore cache)
    uv run python stage1_extract_pdf.py --pdf PATH --force

    # Custom cache directory
    uv run python stage1_extract_pdf.py --pdf PATH --cache-dir /path/to/cache
"""

import argparse
import logging
import sys
from datetime import datetime
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from app.document_processor.pdf_extractor import PDFTextExtractor, PDFExtractorConfig
from app.document_processor.pipeline_manager import CacheManager, PipelineStage

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def extract_pdf(
    pdf_path: Path,
    max_pages: int = None,
    force: bool = False,
    cache_dir: Path = None
) -> dict:
    """
    Extract text from PDF with caching.

    Args:
        pdf_path: Path to PDF file
        max_pages: Maximum pages to process (None for all)
        force: Force re-extraction even if cached
        cache_dir: Cache directory path

    Returns:
        Extraction data dict
    """
    # Initialize cache manager
    cache_mgr = CacheManager(cache_dir)

    # Calculate PDF hash
    print(f"\n{'='*60}")
    print(f"Stage 1: PDF Text Extraction")
    print(f"{'='*60}")
    print(f"PDF: {pdf_path}")
    print(f"Size: {pdf_path.stat().st_size:,} bytes")
    print(f"Max pages: {max_pages or 'All'}")

    pdf_hash = cache_mgr.hash_file(pdf_path)
    print(f"PDF hash: {pdf_hash}")

    # Check cache
    if not force:
        cached_data = cache_mgr.load_cache(PipelineStage.EXTRACTION, pdf_hash)
        if cached_data:
            # Check if cached max_pages matches requested
            cached_max_pages = cached_data.get("config", {}).get("max_pages")

            if cached_max_pages == max_pages:
                print(f"\n✅ Found cached extraction: {cache_mgr.get_cache_path(PipelineStage.EXTRACTION, pdf_hash)}")
                print(f"   Total pages: {cached_data.get('total_pages')}")
                print(f"   Total text: {len(cached_data.get('total_text', '')):,} chars")
                print(f"   Cached at: {cached_data.get('extraction_time')}")
                print("\n💡 Use --force to re-extract")
                return cached_data
            else:
                print(f"\n⚠️  Cached extraction found but page limit differs:")
                print(f"   Cached: {cached_max_pages}, Requested: {max_pages}")
                print(f"   Re-extracting...")

    # Extract PDF
    print(f"\n📄 Extracting PDF text...")

    config = PDFExtractorConfig(max_pages=max_pages)
    extractor = PDFTextExtractor(config)

    try:
        extraction = extractor.extract(pdf_path)
    except Exception as e:
        logger.error(f"Failed to extract PDF: {e}")
        raise

    # Prepare extraction data
    extraction_data = {
        "pdf_path": str(pdf_path),
        "pdf_hash": pdf_hash,
        "total_pages": extraction.total_pages,
        "processed_pages": len(extraction.pages),
        "total_text": extraction.total_text,
        "pages": [
            {
                "page_number": page.page_number,
                "text": page.text,
                "char_count": page.char_count,
                "line_count": page.line_count
            }
            for page in extraction.pages
        ],
        "metadata": extraction.metadata.model_dump(),
        "config": {
            "max_pages": max_pages
        },
        "extraction_time": datetime.now().isoformat()
    }

    # Save to cache
    print(f"\n💾 Saving extraction to cache...")
    cache_path = cache_mgr.save_cache(
        PipelineStage.EXTRACTION,
        pdf_hash,
        extraction_data,
        metadata={
            "pdf_path": str(pdf_path),
            "total_pages": extraction.total_pages,
            "processed_pages": len(extraction.pages)
        }
    )

    print(f"\n✅ Extraction complete!")
    print(f"   Total pages: {extraction.total_pages}")
    print(f"   Processed pages: {len(extraction.pages)}")
    print(f"   Total text: {len(extraction.total_text):,} chars")
    print(f"   Cache: {cache_path}")
    print(f"\n💡 Next step: uv run python stage2_classify_content.py --extraction-id {pdf_hash}")

    return extraction_data


def main():
    parser = argparse.ArgumentParser(
        description='Stage 1: Extract text from PDF',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Extract first 10 pages (default)
  python stage1_extract_pdf.py --pdf ../mvp/pdf/t4012-24e.pdf

  # Extract full document
  python stage1_extract_pdf.py --pdf ../mvp/pdf/t4012-24e.pdf --full

  # Extract specific number of pages
  python stage1_extract_pdf.py --pdf ../mvp/pdf/t4012-24e.pdf --max-pages 30

  # Force re-extraction
  python stage1_extract_pdf.py --pdf ../mvp/pdf/t4012-24e.pdf --force
        """
    )

    parser.add_argument(
        '--pdf',
        type=Path,
        required=True,
        help='Path to PDF file'
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
        '--force',
        action='store_true',
        help='Force re-extraction even if cached'
    )

    parser.add_argument(
        '--cache-dir',
        type=Path,
        help='Cache directory (default: backend/cache/)'
    )

    args = parser.parse_args()

    # Validate PDF exists
    if not args.pdf.exists():
        print(f"❌ Error: PDF file not found: {args.pdf}")
        return 1

    # Determine max_pages
    max_pages = None if args.full else args.max_pages

    # Extract PDF
    try:
        extraction_data = extract_pdf(
            args.pdf,
            max_pages=max_pages,
            force=args.force,
            cache_dir=args.cache_dir
        )
        return 0

    except Exception as e:
        print(f"\n❌ Extraction failed: {e}")
        logger.exception("Extraction failed")
        return 1


if __name__ == '__main__':
    sys.exit(main())
