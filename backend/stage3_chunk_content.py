#!/usr/bin/env python3
"""
Stage 3: Content Chunking

Executes TOC-based chunking using Stage 2 analysis (if available) or
falls back to pattern matching chapter detection.

Features:
- TOC-based chunking with hierarchy support (level, hierarchy_path, parent_title)
- Smart merging of small chunks
- Pattern matching fallback for documents without TOC
- Supports Claude Skills best practices with hierarchical structure

Usage:
    # Basic usage (uses TOC from Stage 2)
    uv run python stage3_chunk_content.py --extraction-id abc123

    # Force re-chunking (ignore cache)
    uv run python stage3_chunk_content.py --extraction-id abc123 --force

    # Skip TOC and use pattern matching
    uv run python stage3_chunk_content.py --extraction-id abc123 --no-toc

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

# Claude Skills best practices: smaller chunks for better organization
# 30K chars (~500 lines) per chunk for optimal skill file generation
MAX_CHUNK_SIZE = 30_000


def _estimate_toc_end_position(content: str, toc_entries: list[dict]) -> int:
    """
    Estimate where the Table of Contents block ends in the document.

    Uses heuristics to find the end of TOC:
    1. Look for common TOC end markers
    2. Estimate based on number of TOC entries (each entry ~50-100 chars in TOC listing)
    3. Cap at reasonable percentage of document (TOC rarely exceeds 10%)

    Args:
        content: Full document content
        toc_entries: List of TOC entries

    Returns:
        Estimated character position where TOC block ends
    """
    # Heuristic 1: Look for common patterns that indicate end of TOC
    # e.g., "Chapter 1", "Part 1", "Introduction" at start of line after some content
    toc_end_patterns = [
        r'\n\s*#{1,2}\s+',  # Markdown heading (# or ##)
        r'\n\s*Chapter\s+\d',  # Chapter N
        r'\n\s*Part\s+\d',  # Part N
        r'\n\s*Section\s+\d',  # Section N
        r'\n-{3,}\n',  # Horizontal rule (---)
        r'\n\*{3,}\n',  # Horizontal rule (***)
        r'\n_{3,}\n',  # Horizontal rule (___)
    ]

    # Start searching after a minimum offset (TOC needs some space)
    min_toc_size = min(500, len(content) // 20)

    for pattern in toc_end_patterns:
        matches = list(re.finditer(pattern, content))
        for match in matches:
            # Skip matches too early (likely still in TOC header)
            if match.start() > min_toc_size:
                return match.start()

    # Heuristic 2: Estimate based on TOC entry count
    # Each TOC entry typically takes ~80 chars in the listing
    estimated_toc_size = len(toc_entries) * 80

    # Heuristic 3: Cap at 10% of document
    max_toc_size = len(content) // 10

    # Use the smaller of estimated and max, but at least min_toc_size
    toc_end = max(min_toc_size, min(estimated_toc_size, max_toc_size))

    return toc_end


def _find_title_with_heading_context(content: str, title: str, search_start: int = 0) -> re.Match | None:
    """
    Find a title in content, preferring matches that look like section headings.

    Prioritizes matches that:
    1. Are preceded by newline + optional # (markdown heading)
    2. Are preceded by newline + whitespace (start of paragraph)
    3. Any match as fallback

    Args:
        content: Document content to search
        title: Title to find
        search_start: Position to start searching from

    Returns:
        Match object or None
    """
    search_content = content[search_start:]

    # Strategy 1: Look for markdown heading format (# Title or ## Title)
    heading_pattern = r'(?:^|\n)\s*#{1,3}\s*' + re.escape(title)
    match = re.search(heading_pattern, search_content, re.IGNORECASE)
    if match:
        # Adjust position to actual title start (skip the # prefix)
        title_match = re.search(re.escape(title), search_content[match.start():], re.IGNORECASE)
        if title_match:
            return re.Match.__new__(re.Match) if False else \
                   type('Match', (), {
                       'start': lambda: search_start + match.start() + title_match.start(),
                       'end': lambda: search_start + match.start() + title_match.end()
                   })()

    # Strategy 2: Look for title at start of line (after newline)
    line_start_pattern = r'(?:^|\n)\s*' + re.escape(title)
    match = re.search(line_start_pattern, search_content, re.IGNORECASE)
    if match:
        title_match = re.search(re.escape(title), search_content[match.start():], re.IGNORECASE)
        if title_match:
            return type('Match', (), {
                'start': lambda s=search_start, m=match, tm=title_match: s + m.start() + tm.start(),
                'end': lambda s=search_start, m=match, tm=title_match: s + m.start() + tm.end()
            })()

    # Strategy 3: Fallback to simple search
    pattern = re.escape(title)
    match = re.search(pattern, search_content, re.IGNORECASE)
    if match:
        return type('Match', (), {
            'start': lambda s=search_start, m=match: s + m.start(),
            'end': lambda s=search_start, m=match: s + m.end()
        })()

    return None


def locate_toc_entries_in_content(content: str, toc_entries: list[dict]) -> list[dict]:
    """
    Locate TOC entries in document content by searching for titles.

    Stage 2's TOC only has page_number, not char_start.
    This function searches for title text to determine character positions,
    skipping the TOC block itself to find actual section headings.

    Search strategy:
    1. Estimate TOC block end position to skip TOC listings
    2. Search for titles with heading context (# prefix, line start)
    3. Fallback to fuzzy matching if exact match fails

    Args:
        content: Full document content
        toc_entries: List of TOC entries from Stage 2

    Returns:
        List of TOC entries with char_start and char_end populated
    """
    located_entries = []

    # Estimate where TOC block ends to avoid matching TOC listings
    toc_end_pos = _estimate_toc_end_position(content, toc_entries)
    logger.debug(f"Estimated TOC block ends at position {toc_end_pos} (doc length: {len(content)})")

    for entry in toc_entries:
        title = entry.get('title', '')
        if not title:
            continue

        # Skip if already has char_start
        if entry.get('char_start') is not None:
            located_entries.append(entry.copy())
            continue

        # Search after TOC block for actual section heading
        match = _find_title_with_heading_context(content, title, toc_end_pos)

        if not match:
            # Try fuzzy match: remove special characters, keep alphanumeric
            simplified_title = re.sub(r'[^\w\s]', '', title)
            if simplified_title and simplified_title != title:
                match = _find_title_with_heading_context(content, simplified_title, toc_end_pos)

        if not match:
            # Try matching first few significant words (for long titles)
            words = [w for w in title.split() if len(w) > 2][:4]
            if len(words) >= 2:
                partial_title = ' '.join(words)
                match = _find_title_with_heading_context(content, partial_title, toc_end_pos)

        if not match:
            # Last resort: search entire document (including TOC area)
            # This handles edge cases where content starts before our estimated TOC end
            match = _find_title_with_heading_context(content, title, 0)
            if match:
                logger.debug(f"Found '{title[:30]}...' in TOC area (pos {match.start()}), using anyway")

        if match:
            located_entry = entry.copy()
            located_entry['char_start'] = match.start()
            located_entries.append(located_entry)
        else:
            logger.warning(f"Could not locate TOC entry: {title[:50]}")

    # Sort by position
    located_entries.sort(key=lambda x: x.get('char_start', 0))

    # Calculate char_end (next entry's char_start)
    for i, entry in enumerate(located_entries):
        if i + 1 < len(located_entries):
            entry['char_end'] = located_entries[i + 1]['char_start']
        else:
            entry['char_end'] = len(content)

    logger.info(f"Located {len(located_entries)} of {len(toc_entries)} TOC entries in content")
    return located_entries


def assign_content_region(chunk: dict, content_regions: list[dict], total_chars: int) -> str:
    """
    Assign content_region to a chunk based on its position in the document.

    Uses content_regions' estimated_start_percent/estimated_end_percent
    to determine which region a chunk belongs to.

    Args:
        chunk: Chunk dict with char_start
        content_regions: List of content regions from Stage 2
        total_chars: Total document character count

    Returns:
        Region name (e.g., "federal", "ontario", "manitoba")
    """
    if not content_regions:
        return "general"

    chunk_start = chunk.get('char_start', 0)
    chunk_percent = (chunk_start / total_chars) * 100 if total_chars > 0 else 0

    for region in content_regions:
        start_pct = region.get('estimated_start_percent', 0)
        end_pct = region.get('estimated_end_percent', 100)

        if start_pct <= chunk_percent <= end_pct:
            return region.get('region', 'general')

    return "general"


def split_large_chunk_by_headings(
    content: str,
    max_size: int,
    base_title: str = "",
    char_offset: int = 0
) -> list[dict]:
    """
    Split a large chunk by ## headings into smaller chunks.

    Used to process large chunks (like chunk-080) that contain multiple ## headings.

    Args:
        content: Chunk content to split
        max_size: Maximum chunk size in characters
        base_title: Base title for sub-chunks (used in part naming)
        char_offset: Character offset in original document

    Returns:
        List of sub-chunk dicts
    """
    # Find all ## and ### headings
    heading_pattern = re.compile(r'^(#{2,3})\s+(.+)$', re.MULTILINE)
    headings = list(heading_pattern.finditer(content))

    if not headings:
        # No ## headings, split by paragraphs
        sub_contents = split_content_into_chunks(content, max_size)
        return [{
            'content': sub_content,
            'title': f"{base_title} (Part {j+1})" if base_title else f"Section Part {j+1}",
            'slug': _slugify(f"{base_title}-part-{j+1}" if base_title else f"section-part-{j+1}"),
            'char_count': len(sub_content),
            'char_start': char_offset,  # Approximate
            'char_end': char_offset + len(sub_content)
        } for j, sub_content in enumerate(sub_contents)]

    chunks = []
    for i, match in enumerate(headings):
        start_pos = match.start()
        end_pos = headings[i + 1].start() if i + 1 < len(headings) else len(content)

        section_content = content[start_pos:end_pos].strip()
        section_title = match.group(2).strip()

        # If single section is still too large, recursively split
        if len(section_content) > max_size:
            sub_contents = split_content_into_chunks(section_content, max_size)
            for j, sub_content in enumerate(sub_contents):
                chunks.append({
                    'content': sub_content,
                    'title': f"{section_title} (Part {j+1})",
                    'slug': _slugify(f"{section_title}-part-{j+1}"),
                    'char_count': len(sub_content),
                    'char_start': char_offset + start_pos,
                    'char_end': char_offset + start_pos + len(sub_content)
                })
        else:
            chunks.append({
                'content': section_content,
                'title': section_title,
                'slug': _slugify(section_title),
                'char_count': len(section_content),
                'char_start': char_offset + start_pos,
                'char_end': char_offset + end_pos
            })

    return chunks


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
    Split content by chapter boundaries with smart chunking (pattern matching fallback).

    Args:
        content: Full content to split
        max_chunk_size: Maximum size per chunk

    Returns:
        List of chunk dicts with metadata (includes basic hierarchy fields)
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
            'char_count': len(chunk),
            'toc_level': 1,
            'hierarchy_path': f'Section {i+1}',
            'parent_title': None,
            'chunking_method': 'pattern'
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
                    'char_count': len(sub_chunk),
                    'toc_level': chapter['level'],
                    'hierarchy_path': f"{chapter['title']} (Part {j+1})",
                    'parent_title': None,
                    'chunking_method': 'pattern'
                })
        else:
            structured_chunks.append({
                'content': chapter_content,
                'title': chapter['title'],
                'slug': chapter['slug'],
                'chapter_num': len(structured_chunks) + 1,
                'char_count': len(chapter_content),
                'toc_level': chapter['level'],
                'hierarchy_path': chapter['title'],
                'parent_title': None,
                'chunking_method': 'pattern'
            })

    return structured_chunks


def chunk_by_toc(
    content: str,
    toc_entries: list[dict],
    content_regions: list[dict] = None,
    max_level: int = 2,
    min_chunk_size: int = 2000,
    max_chunk_size: int = MAX_CHUNK_SIZE
) -> list[dict]:
    """
    Chunk content based on TOC entries with hierarchy support.

    Strategy:
    - First locate TOC entries in content (calculate char_start)
    - Use TOC entries with level <= max_level as chunk boundaries
    - Split large chunks by ## headings
    - Merge adjacent small chunks
    - Assign content_region to each chunk
    - Add hierarchy path information (e.g., "Chapter 3 > Section 3.1")

    Args:
        content: Full document content
        toc_entries: List of TOC entries from Stage 2
        content_regions: List of content regions from Stage 2 (for province tagging)
        max_level: Maximum level to use for chunking (default: 2)
        min_chunk_size: Minimum chunk size in characters (default: 2000)
        max_chunk_size: Maximum chunk size in characters (default: MAX_CHUNK_SIZE)

    Returns:
        List of chunk dicts with hierarchy metadata and content_region
    """
    chunks = []
    total_chars = len(content)

    # Step 1: Locate TOC entries in content (calculate char_start)
    located_entries = locate_toc_entries_in_content(content, toc_entries)

    # Filter by max_level
    valid_entries = [
        entry for entry in located_entries
        if entry.get('level', 1) <= max_level
    ]

    if not valid_entries:
        logger.warning("No valid TOC entries found for chunking")
        return []

    logger.info(f"Processing {len(valid_entries)} TOC entries (max_level={max_level})")

    # Build hierarchy paths
    # Track parent titles at each level
    level_stack = {}  # {level: title}

    for i, entry in enumerate(valid_entries):
        level = entry.get('level', 1)
        title = entry.get('title', f'Section {i+1}')
        char_start = entry.get('char_start', 0)
        char_end = entry.get('char_end', len(content))

        # Update level stack (remove deeper levels)
        level_stack = {k: v for k, v in level_stack.items() if k < level}
        level_stack[level] = title

        # Build hierarchy path
        hierarchy_parts = [level_stack[l] for l in sorted(level_stack.keys())]
        hierarchy_path = ' > '.join(hierarchy_parts)

        # Find parent title (immediate parent level)
        parent_title = None
        if level > 1:
            parent_level = level - 1
            while parent_level >= 1:
                if parent_level in level_stack:
                    parent_title = level_stack[parent_level]
                    break
                parent_level -= 1

        # Extract content
        chunk_content = content[char_start:char_end].strip()

        if not chunk_content:
            continue

        # Step 2: Split large chunks by ## headings
        if len(chunk_content) > max_chunk_size:
            logger.info(f"Splitting large chunk '{title[:30]}...' ({len(chunk_content):,} chars) by headings")
            sub_chunks = split_large_chunk_by_headings(
                chunk_content,
                max_chunk_size,
                base_title=title,
                char_offset=char_start
            )
            for sub_chunk in sub_chunks:
                # Assign content region
                sub_chunk['content_region'] = assign_content_region(
                    sub_chunk, content_regions, total_chars
                )
                sub_chunk['toc_level'] = level
                sub_chunk['hierarchy_path'] = hierarchy_path
                sub_chunk['parent_title'] = parent_title
                sub_chunk['chunking_method'] = 'toc'
                sub_chunk['chapter_num'] = len(chunks) + 1
                chunks.append(sub_chunk)
        else:
            chunk = {
                'content': chunk_content,
                'title': title,
                'slug': _slugify(title),
                'chapter_num': len(chunks) + 1,
                'char_count': len(chunk_content),
                'toc_level': level,
                'hierarchy_path': hierarchy_path,
                'parent_title': parent_title,
                'chunking_method': 'toc',
                'char_start': char_start,
                'char_end': char_end
            }
            # Assign content region
            chunk['content_region'] = assign_content_region(
                chunk, content_regions, total_chars
            )
            chunks.append(chunk)

    # Step 3: Merge small chunks
    if min_chunk_size > 0:
        merged_chunks = []
        pending_merge = None

        for chunk in chunks:
            if chunk['char_count'] < min_chunk_size:
                if pending_merge is None:
                    pending_merge = chunk.copy()
                else:
                    # Merge with pending
                    pending_merge['content'] += '\n\n' + chunk['content']
                    pending_merge['title'] += f" + {chunk['title']}"
                    pending_merge['slug'] = _slugify(pending_merge['title'])
                    pending_merge['char_count'] = len(pending_merge['content'])
                    pending_merge['char_end'] = chunk.get('char_end', pending_merge.get('char_end'))
                    pending_merge['hierarchy_path'] += f" / {chunk['hierarchy_path']}"
                    # Mark as merged for later content_region recomputation
                    pending_merge['_merged'] = True
            else:
                # Chunk is large enough
                if pending_merge is not None:
                    # Flush pending merge
                    merged_chunks.append(pending_merge)
                    pending_merge = None
                merged_chunks.append(chunk)

        # Flush final pending merge
        if pending_merge is not None:
            merged_chunks.append(pending_merge)

        # Renumber chapters and recompute content_region for merged chunks
        for i, chunk in enumerate(merged_chunks, 1):
            chunk['chapter_num'] = i
            # Recompute content_region for merged chunks based on new char_start/char_end
            if chunk.get('_merged'):
                chunk['content_region'] = assign_content_region(
                    chunk, content_regions, total_chars
                )
                del chunk['_merged']  # Clean up internal flag

        logger.info(f"TOC chunking: {len(chunks)} initial chunks, {len(merged_chunks)} after merging small chunks")
        chunks = merged_chunks

    logger.info(f"Generated {len(chunks)} chunks from TOC entries")
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

    # Load classification data (contains TOC and content_regions from Stage 2)
    classification_data = None
    toc_data = None
    content_regions = None
    chunking_strategy = "pattern_matching"

    if use_semantic:
        classification_data = cache_mgr.load_cache(PipelineStage.CLASSIFICATION, extraction_id)
        if classification_data:
            # Load TOC
            if 'toc' in classification_data:
                toc_data = classification_data['toc']
                if toc_data.get('has_toc') and toc_data.get('entries'):
                    print(f"\n📋 Found TOC from Stage 2")
                    print(f"   Source: {toc_data.get('source', 'unknown')}")
                    print(f"   Max level: {toc_data.get('max_level', 'unknown')}")
                    print(f"   TOC entries: {len(toc_data['entries'])}")

            # Load content_regions
            content_regions = classification_data.get('content_regions', [])
            if content_regions:
                print(f"\n🗺️  Found {len(content_regions)} content regions from Stage 2")
                for region in content_regions:
                    region_name = region.get('region', 'unknown')
                    region_title = region.get('title', '')
                    start_pct = region.get('estimated_start_percent', 0)
                    end_pct = region.get('estimated_end_percent', 100)
                    print(f"   - {region_name}: {region_title} ({start_pct}%-{end_pct}%)")

    # Split into chunks
    if toc_data and toc_data.get('has_toc') and toc_data.get('entries'):
        print(f"\n✂️  Executing TOC-based chunking...")
        chunks = chunk_by_toc(
            cleaned_content,
            toc_data['entries'],
            content_regions=content_regions,
            max_level=2,
            min_chunk_size=2000,
            max_chunk_size=max_chunk_size
        )
        chunking_strategy = "toc_based"

        # Fallback to pattern matching if TOC chunking failed
        if not chunks:
            print(f"\n⚠️  TOC chunking produced no chunks, falling back to pattern matching")
            chunks = split_by_chapters(cleaned_content, max_chunk_size)
            chunking_strategy = "pattern_matching"
    else:
        if use_semantic:
            print(f"\n⚠️  No TOC found in Stage 2, falling back to pattern matching")
        print(f"\n✂️  Splitting by pattern matching...")
        chunks = split_by_chapters(cleaned_content, max_chunk_size)
        chunking_strategy = "pattern_matching"

    # Prepare chunking data
    chunking_data = {
        "total_chunks": len(chunks),
        "chunks": chunks,
        "max_chunk_size": max_chunk_size,
        "chunking_strategy": chunking_strategy,
        "used_toc": toc_data is not None and toc_data.get('has_toc', False),
        "toc_source": toc_data.get('source') if toc_data else None,
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
    sizes = [c['char_count'] for c in chunks]
    print(f"   Chunk sizes: min={min(sizes):,}, max={max(sizes):,}, avg={sum(sizes)//len(sizes):,} chars")
    print(f"   Cache: {cache_path}")

    # Show content region distribution
    if any(c.get('content_region') for c in chunks):
        region_counts = {}
        for c in chunks:
            r = c.get('content_region', 'unknown')
            region_counts[r] = region_counts.get(r, 0) + 1
        print(f"\n🗺️  Content Region Distribution:")
        for region, count in sorted(region_counts.items()):
            print(f"   - {region}: {count} chunks")

    # Show chunk summary
    print(f"\n📊 Chunk Summary:")
    for i, chunk in enumerate(chunks[:5], 1):
        hierarchy_info = ""
        if 'toc_level' in chunk:
            hierarchy_info = f" [L{chunk['toc_level']}]"
        region_info = ""
        if chunk.get('content_region'):
            region_info = f" [{chunk['content_region']}]"
        print(f"   {i}. {chunk['title'][:35]:<35} ({chunk['char_count']:>8,} chars){hierarchy_info}{region_info}")
    if len(chunks) > 5:
        print(f"   ... and {len(chunks) - 5} more")

    print(f"\n💡 Next step: uv run python stage4_enhance_chunks.py --chunks-id {extraction_id}")

    return chunking_data


def main():
    parser = argparse.ArgumentParser(
        description='Stage 3: Execute TOC-based chunking or fall back to pattern matching',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # TOC-based chunking (uses Stage 2 TOC)
  python stage3_chunk_content.py --extraction-id abc123

  # Force re-chunking
  python stage3_chunk_content.py --extraction-id abc123 --force

  # Pattern matching (ignore Stage 2 TOC)
  python stage3_chunk_content.py --extraction-id abc123 --no-toc

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
        '--no-toc',
        action='store_true',
        help='Use pattern matching chapter detection (ignore TOC from Stage 2)'
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
            use_semantic=not args.no_toc
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
