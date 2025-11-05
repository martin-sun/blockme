#!/usr/bin/env python3
"""
Stage 3: Content Chunking

Executes semantic chunking based on Stage 2 analysis (if available) or
falls back to traditional chapter detection.

Usage:
    # Basic usage (uses Gemini semantic boundaries from Stage 2)
    uv run python stage3_chunk_content.py --extraction-id abc123

    # Force re-chunking (ignore cache)
    uv run python stage3_chunk_content.py --extraction-id abc123 --force

    # Force legacy chapter detection (ignore semantic boundaries)
    uv run python stage3_chunk_content.py --extraction-id abc123 --legacy

    # Custom chunk size
    uv run python stage3_chunk_content.py --extraction-id abc123 --max-chunk-size 500000

    # Custom cache directory
    uv run python stage3_chunk_content.py --extraction-id abc123 --cache-dir /path/to/cache
"""

import argparse
import logging
import re
import sys
from datetime import datetime
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from app.document_processor.pipeline_manager import CacheManager, PipelineStage

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Claude Sonnet 4.5 specs: 200K token input, 64K token output
# Using 300K chars (75K tokens) for optimal chunking
MAX_CHUNK_SIZE = 300_000


def clean_content(content: str) -> str:
    """
    Clean extracted content by removing artifacts and page markers.

    Args:
        content: Raw extracted content

    Returns:
        Cleaned content
    """
    # Remove page markers
    content = re.sub(r'={3,}\s*Page\s+\d+\s*={3,}', '', content, flags=re.IGNORECASE)
    content = re.sub(r'\[Page\s+\d+\]', '', content, flags=re.IGNORECASE)
    content = re.sub(r'Page\s+\d+\s+of\s+\d+', '', content, flags=re.IGNORECASE)

    # Remove excessive whitespace
    content = re.sub(r'\n{4,}', '\n\n\n', content)
    content = content.strip()

    return content


def _slugify(title: str) -> str:
    """
    Convert title to URL-friendly slug.

    Args:
        title: Chapter title

    Returns:
        Lowercase slug with hyphens
    """
    slug = re.sub(r'[^a-zA-Z0-9\s-]', '', title.lower())
    slug = re.sub(r'\s+', '-', slug)
    slug = re.sub(r'-+', '-', slug).strip('-')
    return slug[:50]


def detect_chapters(content: str, min_confidence: float = 0.6) -> list[dict]:
    """
    Detect chapter structure using multi-method algorithm.

    Detection methods:
    1. Markdown headings (# and ##)
    2. Pattern matching ("Chapter N", "Part N", etc.)
    3. All-caps headings

    Args:
        content: Full document content
        min_confidence: Minimum confidence score (0-1)

    Returns:
        List of chapter dicts
    """
    chapters = []

    # Method 1: Markdown headings
    heading_pattern = re.compile(r'^(#{1,2})\s+(.+)$', re.MULTILINE)
    for match in heading_pattern.finditer(content):
        level = len(match.group(1))
        title = match.group(2).strip()
        start_pos = match.start()

        if re.match(r'^={3,}\s*Page\s+\d+\s*={3,}$', title, re.IGNORECASE):
            continue

        chapters.append({
            'title': title,
            'level': level,
            'start_pos': start_pos,
            'slug': _slugify(title),
            'confidence': 1.0,
            'method': 'markdown'
        })

    # Method 2: Pattern matching
    chapter_patterns = [
        (r'^Chapter\s+(\d+)[:\-\s](.+)$', 'Chapter {0}: {1}'),
        (r'^Part\s+(\d+)[:\-\s](.+)$', 'Part {0}: {1}'),
        (r'^Section\s+(\d+(?:\.\d+)?)[:\-\s](.+)$', 'Section {0}: {1}'),
        (r'^(\d+)\.\s+([A-Z][^\n]{5,50})$', '{0}. {1}'),
        (r'^([IVXLCDM]+)\.\s+([A-Z][^\n]{5,50})$', '{0}. {1}'),
    ]

    for pattern, title_template in chapter_patterns:
        for match in re.finditer(pattern, content, re.MULTILINE | re.IGNORECASE):
            start_pos = match.start()

            if any(abs(ch['start_pos'] - start_pos) < 10 for ch in chapters):
                continue

            if len(match.groups()) == 2:
                number, title_part = match.groups()
                title = title_template.format(number, title_part.strip())
            else:
                title = match.group(0).strip()

            chapters.append({
                'title': title,
                'level': 1,
                'start_pos': start_pos,
                'slug': _slugify(title),
                'confidence': 0.9,
                'method': 'pattern'
            })

    # Method 3: All-caps headings
    allcaps_pattern = re.compile(r'^([A-Z][A-Z\s]{5,50})$', re.MULTILINE)
    for match in allcaps_pattern.finditer(content):
        start_pos = match.start()

        if any(abs(ch['start_pos'] - start_pos) < 10 for ch in chapters):
            continue

        title = match.group(1).strip()

        false_positives = ['PDF', 'CRA', 'GST', 'HST', 'RRSP', 'TFSA', 'HTTP', 'HTTPS']
        if title in false_positives or len(title) < 6:
            continue

        title_cased = title.title()
        chapters.append({
            'title': title_cased,
            'level': 2,
            'start_pos': start_pos,
            'slug': _slugify(title_cased),
            'confidence': 0.7,
            'method': 'allcaps'
        })

    # Filter and sort
    chapters = [ch for ch in chapters if ch['confidence'] >= min_confidence]
    chapters.sort(key=lambda x: x['start_pos'])

    # Remove duplicates
    deduplicated = []
    for chapter in chapters:
        if not any(abs(ch['start_pos'] - chapter['start_pos']) < 100 for ch in deduplicated):
            deduplicated.append(chapter)

    logger.info(f"Detected {len(deduplicated)} chapters")

    return deduplicated


def split_content_into_chunks(content: str, max_chunk_size: int) -> list[str]:
    """
    Split content into chunks at paragraph boundaries.

    Args:
        content: Full content to split
        max_chunk_size: Maximum characters per chunk

    Returns:
        List of content chunks
    """
    if len(content) <= max_chunk_size:
        return [content]

    chunks = []
    current_chunk = ""

    paragraphs = re.split(r'\n\n+', content)

    for paragraph in paragraphs:
        if len(paragraph) > max_chunk_size:
            sentences = re.split(r'(?<=[.!?])\s+', paragraph)
            for sentence in sentences:
                if len(current_chunk) + len(sentence) + 2 <= max_chunk_size:
                    current_chunk += sentence + " "
                else:
                    if current_chunk:
                        chunks.append(current_chunk.strip())
                    current_chunk = sentence + " "
        else:
            if len(current_chunk) + len(paragraph) + 2 <= max_chunk_size:
                current_chunk += paragraph + "\n\n"
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = paragraph + "\n\n"

    if current_chunk:
        chunks.append(current_chunk.strip())

    return chunks


def split_by_chapters(content: str, max_chunk_size: int) -> list[dict]:
    """
    Split content by chapter boundaries with smart chunking.

    Args:
        content: Full content to split
        max_chunk_size: Maximum size per chunk

    Returns:
        List of chunk dicts with metadata
    """
    chapters = detect_chapters(content)

    if not chapters:
        # No chapters detected, fall back to paragraph splitting
        chunks_list = split_content_into_chunks(content, max_chunk_size)
        return [{
            'content': chunk,
            'title': f'Section {i+1}',
            'slug': f'section-{i+1}',
            'chapter_num': i + 1,
            'char_count': len(chunk)
        } for i, chunk in enumerate(chunks_list)]

    # Split by chapters
    structured_chunks = []

    for i, chapter in enumerate(chapters):
        start_pos = chapter['start_pos']
        end_pos = chapters[i + 1]['start_pos'] if i + 1 < len(chapters) else len(content)

        chapter_content = content[start_pos:end_pos].strip()

        # If chapter exceeds max size, split further
        if len(chapter_content) > max_chunk_size:
            sub_chunks = split_content_into_chunks(chapter_content, max_chunk_size)
            for j, sub_chunk in enumerate(sub_chunks):
                structured_chunks.append({
                    'content': sub_chunk,
                    'title': f"{chapter['title']} (Part {j+1})",
                    'slug': f"{chapter['slug']}-part-{j+1}",
                    'chapter_num': len(structured_chunks) + 1,
                    'char_count': len(sub_chunk)
                })
        else:
            structured_chunks.append({
                'content': chapter_content,
                'title': chapter['title'],
                'slug': chapter['slug'],
                'chapter_num': len(structured_chunks) + 1,
                'char_count': len(chapter_content)
            })

    return structured_chunks


def execute_semantic_chunking(content: str, chunks_preview: list[dict]) -> list[dict]:
    """
    Execute chunking based on semantic boundaries from Stage 2 (Gemini analysis).

    Args:
        content: Full document content
        chunks_preview: List of chunk boundaries from Stage 2

    Returns:
        List of chunk dicts with content and metadata
    """
    chunks = []

    for preview in chunks_preview:
        start_pos = preview['start_pos']
        end_pos = preview['end_pos']

        # Extract actual content
        chunk_content = content[start_pos:end_pos].strip()

        chunks.append({
            'content': chunk_content,
            'title': preview['title'],
            'slug': _slugify(preview['title']),
            'chapter_num': preview['chunk_id'],
            'char_count': len(chunk_content),
            'primary_topic': preview.get('primary_topic', ''),
            'semantic_coherence': preview.get('semantic_coherence', 0.85)
        })

    logger.info(f"Executed semantic chunking: {len(chunks)} chunks")
    return chunks


def chunk_content(
    extraction_id: str,
    max_chunk_size: int = MAX_CHUNK_SIZE,
    force: bool = False,
    cache_dir: Path = None,
    use_semantic: bool = True
) -> dict:
    """
    Chunk extracted content with caching.

    Args:
        extraction_id: Extraction cache hash ID
        max_chunk_size: Maximum characters per chunk
        force: Force re-chunking even if cached
        cache_dir: Cache directory path
        use_semantic: Use semantic boundaries from Stage 2 if available (default: True)

    Returns:
        Chunking data dict
    """
    # Initialize cache manager
    cache_mgr = CacheManager(cache_dir)

    print(f"\n{'='*60}")
    print(f"Stage 3: Content Chunking")
    print(f"{'='*60}")
    print(f"Extraction ID: {extraction_id}")
    print(f"Max chunk size: {max_chunk_size:,} chars")

    # Load extraction data
    extraction_data = cache_mgr.load_cache(PipelineStage.EXTRACTION, extraction_id)
    if not extraction_data:
        print(f"❌ Error: Extraction cache not found for ID: {extraction_id}")
        return None

    total_text = extraction_data.get("total_text", "")
    print(f"Loaded extraction: {len(total_text):,} chars")

    # Check chunking cache
    if not force:
        cached_chunks = cache_mgr.load_cache(PipelineStage.CHUNKING, extraction_id)
        if cached_chunks:
            print(f"\n✅ Found cached chunks: {cache_mgr.get_cache_path(PipelineStage.CHUNKING, extraction_id)}")
            print(f"   Total chunks: {cached_chunks.get('total_chunks')}")
            print(f"   Cached at: {cached_chunks.get('chunking_time')}")
            print("\n💡 Use --force to re-chunk")
            return cached_chunks

    # Clean content
    print(f"\n🧹 Cleaning content...")
    cleaned_content = clean_content(total_text)
    print(f"   Cleaned: {len(cleaned_content):,} chars")

    # Check for semantic boundaries from Stage 2
    classification_data = None
    chunks_preview = None
    chunking_strategy = "chapter_detection"

    if use_semantic:
        classification_data = cache_mgr.load_cache(PipelineStage.CLASSIFICATION, extraction_id)
        if classification_data and 'chunks_preview' in classification_data:
            chunks_preview = classification_data['chunks_preview']
            print(f"\n🔮 Found semantic boundaries from Stage 2")
            print(f"   Method: {classification_data.get('method', 'unknown')}")
            print(f"   Chunks identified: {len(chunks_preview)}")

    # Split into chunks
    if chunks_preview:
        print(f"\n✂️  Executing semantic chunking...")
        chunks = execute_semantic_chunking(cleaned_content, chunks_preview)
        chunking_strategy = "semantic_boundaries"
    else:
        if use_semantic:
            print(f"\n⚠️  No semantic boundaries found, falling back to chapter detection")
        print(f"\n✂️  Splitting by chapter detection...")
        chunks = split_by_chapters(cleaned_content, max_chunk_size)
        chunking_strategy = "chapter_detection"

    # Prepare chunking data
    chunking_data = {
        "total_chunks": len(chunks),
        "chunks": chunks,
        "max_chunk_size": max_chunk_size,
        "chunking_strategy": chunking_strategy,
        "used_semantic_boundaries": chunks_preview is not None,
        "chunking_time": datetime.now().isoformat()
    }

    # Save to cache
    print(f"\n💾 Saving chunks to cache...")
    cache_path = cache_mgr.save_cache(
        PipelineStage.CHUNKING,
        extraction_id,
        chunking_data,
        metadata={
            "total_chunks": len(chunks),
            "total_chars": len(cleaned_content)
        }
    )

    print(f"\n✅ Chunking complete!")
    print(f"   Strategy: {chunking_strategy}")
    print(f"   Total chunks: {len(chunks)}")
    print(f"   Avg chunk size: {len(cleaned_content) // len(chunks):,} chars")
    print(f"   Cache: {cache_path}")

    # Show chunk summary
    print(f"\n📊 Chunk Summary:")
    for i, chunk in enumerate(chunks[:5], 1):
        semantic_info = ""
        if 'semantic_coherence' in chunk:
            semantic_info = f" [coherence: {chunk['semantic_coherence']:.2f}]"
        print(f"   {i}. {chunk['title'][:50]:<50} ({chunk['char_count']:>8,} chars){semantic_info}")
    if len(chunks) > 5:
        print(f"   ... and {len(chunks) - 5} more")

    print(f"\n💡 Next step: uv run python stage4_enhance_chunks.py --chunks-id {extraction_id}")

    return chunking_data


def main():
    parser = argparse.ArgumentParser(
        description='Stage 3: Execute semantic chunking or fall back to chapter detection',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Semantic chunking (uses Stage 2 analysis)
  python stage3_chunk_content.py --extraction-id abc123

  # Force re-chunking
  python stage3_chunk_content.py --extraction-id abc123 --force

  # Legacy chapter detection (ignore Stage 2)
  python stage3_chunk_content.py --extraction-id abc123 --legacy

  # Custom chunk size
  python stage3_chunk_content.py --extraction-id abc123 --max-chunk-size 500000
        """
    )

    parser.add_argument(
        '--extraction-id',
        type=str,
        required=True,
        help='Extraction cache hash ID (from stage1)'
    )

    parser.add_argument(
        '--max-chunk-size',
        type=int,
        default=MAX_CHUNK_SIZE,
        help=f'Maximum characters per chunk (default: {MAX_CHUNK_SIZE:,})'
    )

    parser.add_argument(
        '--force',
        action='store_true',
        help='Force re-chunking even if cached'
    )

    parser.add_argument(
        '--legacy',
        action='store_true',
        help='Use legacy chapter detection (ignore semantic boundaries from Stage 2)'
    )

    parser.add_argument(
        '--cache-dir',
        type=Path,
        help='Cache directory (default: backend/cache/)'
    )

    args = parser.parse_args()

    # Chunk content
    try:
        chunking_data = chunk_content(
            args.extraction_id,
            max_chunk_size=args.max_chunk_size,
            force=args.force,
            cache_dir=args.cache_dir,
            use_semantic=not args.legacy
        )

        if chunking_data is None:
            return 1

        return 0

    except Exception as e:
        print(f"\n❌ Chunking failed: {e}")
        logger.exception("Chunking failed")
        return 1


if __name__ == '__main__':
    sys.exit(main())
