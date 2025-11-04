#!/usr/bin/env python3
"""
Generate skill files from CRA tax PDFs with local Claude Code enhancement.

Usage:
    # Basic processing (no AI)
    uv run python generate_skill.py --pdf ../mvp/pdf/t4012-24e.pdf --no-ai

    # With local Claude (free with Claude Code subscription)
    uv run python generate_skill.py --pdf ../mvp/pdf/t4012-24e.pdf --local-claude

    # Process full document (all pages)
    uv run python generate_skill.py --pdf ../mvp/pdf/t4012-24e.pdf --local-claude --full
"""

import argparse
import re
import subprocess
import tempfile
import shutil
import sys
from pathlib import Path

# Add backend to Python path
sys.path.insert(0, str(Path(__file__).parent))

from app.document_processor import (
    PDFTextExtractor,
    ContentClassifier,
    SkillGenerator,
    QualityValidator,
    MarkdownOptimizer,
    OptimizationConfig
)
from app.document_processor.llm_cli_providers import (
    LLMCLIProvider,
    ClaudeCLIProvider,
    GeminiCLIProvider,
    CodexCLIProvider,
    get_provider,
    detect_available_providers
)

# Claude processing configuration
# Based on Claude Sonnet 4.5 specs: 200K token input, 64K token output (≈800K chars)
# Using 300K chars (75K tokens) leaves safe margin for 64K token responses
MAX_CHUNK_SIZE = 300_000      # ~75K tokens, optimal for 200K input + 64K output
MIN_TIMEOUT = 90              # Minimum timeout in seconds
TIMEOUT_PER_1K_CHARS = 1      # Scale timeout: 1 second per 1,000 chars


def split_content_into_chunks(content: str, max_chunk_size: int = MAX_CHUNK_SIZE) -> list[str]:
    """
    Split content into chunks at paragraph boundaries.

    Ensures chunks don't exceed max_chunk_size while preferring to split at
    paragraph breaks (double newlines) to maintain context.

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

    # Split by paragraphs (double newline or more)
    paragraphs = re.split(r'\n\n+', content)

    for paragraph in paragraphs:
        # If single paragraph exceeds limit, split by sentences
        if len(paragraph) > max_chunk_size:
            # Split by sentences
            sentences = re.split(r'(?<=[.!?])\s+', paragraph)
            for sentence in sentences:
                if len(current_chunk) + len(sentence) + 2 <= max_chunk_size:
                    current_chunk += sentence + " "
                else:
                    if current_chunk:
                        chunks.append(current_chunk.strip())
                    current_chunk = sentence + " "
        else:
            # Try adding paragraph to current chunk
            if len(current_chunk) + len(paragraph) + 2 <= max_chunk_size:
                current_chunk += paragraph + "\n\n"
            else:
                # Save current chunk and start new one
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = paragraph + "\n\n"

    # Add remaining content
    if current_chunk:
        chunks.append(current_chunk.strip())

    return chunks


def merge_enhanced_chunks(chunks: list[str]) -> str:
    """
    Merge enhanced chunks back together.

    Args:
        chunks: List of enhanced content chunks

    Returns:
        Merged content
    """
    # Join chunks with double newlines for clean separation
    return "\n\n".join(chunk.strip() for chunk in chunks if chunk.strip())


def detect_chapters(content: str) -> list[dict]:
    """
    Detect chapter structure in content based on markdown headings.

    Identifies main chapters (# and ## headings) to intelligently split content.
    Similar to Skill_Seekers' chapter detection pattern.

    Args:
        content: Full document content

    Returns:
        List of chapter dicts with {title, start_pos, level, slug}
    """
    chapters = []

    # Match H1 (# ) and H2 (## ) headings at line start
    heading_pattern = re.compile(r'^(#{1,2})\s+(.+)$', re.MULTILINE)

    for match in heading_pattern.finditer(content):
        level = len(match.group(1))  # Number of # symbols
        title = match.group(2).strip()
        start_pos = match.start()

        # Generate slug from title (kebab-case)
        slug = re.sub(r'[^a-zA-Z0-9\s-]', '', title.lower())
        slug = re.sub(r'\s+', '-', slug)
        slug = re.sub(r'-+', '-', slug).strip('-')

        chapters.append({
            'title': title,
            'level': level,
            'start_pos': start_pos,
            'slug': slug
        })

    return chapters


def split_by_chapters(content: str, max_chunk_size: int = MAX_CHUNK_SIZE) -> list[dict]:
    """
    Split content by chapter boundaries with smart chunking.

    Prioritizes splitting at chapter headings, but respects max_chunk_size.
    Returns structured chunks with metadata.

    Args:
        content: Full content to split
        max_chunk_size: Maximum size per chunk

    Returns:
        List of chunk dicts with {content, title, slug, chapter_num}
    """
    chapters = detect_chapters(content)

    if not chapters:
        # No chapters detected, fall back to paragraph-based splitting
        chunks_list = split_content_into_chunks(content, max_chunk_size)
        return [{
            'content': chunk,
            'title': f'Section {i+1}',
            'slug': f'section-{i+1}',
            'chapter_num': i + 1
        } for i, chunk in enumerate(chunks_list)]

    # Split by chapters
    structured_chunks = []

    for i, chapter in enumerate(chapters):
        # Determine chunk boundaries
        start_pos = chapter['start_pos']
        end_pos = chapters[i + 1]['start_pos'] if i + 1 < len(chapters) else len(content)

        chapter_content = content[start_pos:end_pos].strip()

        # If chapter exceeds max size, split further
        if len(chapter_content) > max_chunk_size:
            # Split this chapter into sub-chunks
            sub_chunks = split_content_into_chunks(chapter_content, max_chunk_size)
            for j, sub_chunk in enumerate(sub_chunks):
                structured_chunks.append({
                    'content': sub_chunk,
                    'title': f"{chapter['title']} (Part {j+1})",
                    'slug': f"{chapter['slug']}-part-{j+1}",
                    'chapter_num': len(structured_chunks) + 1
                })
        else:
            structured_chunks.append({
                'content': chapter_content,
                'title': chapter['title'],
                'slug': chapter['slug'],
                'chapter_num': len(structured_chunks) + 1
            })

    return structured_chunks


def generate_chapter_name(title: str, fallback_num: int = 1) -> str:
    """
    Generate a clean filename from chapter title.

    Args:
        title: Chapter title
        fallback_num: Number to use if title is empty

    Returns:
        Clean filename (kebab-case, no extension)
    """
    if not title or title.strip() == '':
        return f'section-{fallback_num}'

    # Clean and convert to kebab-case
    clean = re.sub(r'[^a-zA-Z0-9\s-]', '', title.lower())
    clean = re.sub(r'\s+', '-', clean)
    clean = re.sub(r'-+', '-', clean).strip('-')

    # Limit length
    if len(clean) > 50:
        clean = clean[:50].rstrip('-')

    return clean or f'section-{fallback_num}'


def enhance_single_chunk(
    chunk: str,
    category: str,
    chunk_num: int,
    total_chunks: int,
    provider: LLMCLIProvider
) -> str:
    """
    Enhance a single chunk using any LLM CLI provider.

    Args:
        chunk: Content chunk to enhance
        category: Tax category
        chunk_num: Current chunk number (1-indexed)
        total_chunks: Total number of chunks
        provider: LLM CLI provider instance to use

    Returns:
        Enhanced chunk content
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
{chunk}

Enhanced content (Markdown only):"""

    try:
        # Get provider-specific timeout
        timeout = provider.get_timeout(len(chunk))

        # Build provider-specific command
        command = provider.build_command(prompt)

        # Execute command (with or without stdin based on provider)
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
            try:
                enhanced = provider.parse_output(result.stdout, result.stderr)
                return enhanced
            except ValueError as e:
                print(f"    ⚠️  Invalid output for chunk {chunk_num}: {e}, using original")
                return chunk
        else:
            print(f"    ⚠️  Failed for chunk {chunk_num} (code {result.returncode}), using original")
            if result.stderr:
                print(f"    Error: {result.stderr[:200]}")
            return chunk

    except subprocess.TimeoutExpired:
        print(f"    ⚠️  Timeout for chunk {chunk_num}, using original")
        return chunk
    except Exception as e:
        print(f"    ⚠️  Error for chunk {chunk_num}: {e}, using original")
        return chunk


def main():
    parser = argparse.ArgumentParser(description='Generate skill files from CRA tax PDFs with LLM enhancement')
    parser.add_argument('--pdf', required=True, help='Path to PDF file')
    parser.add_argument('--output-dir', default='skills_output', help='Output directory for generated skills')
    parser.add_argument('--no-ai', action='store_true', help='Skip AI enhancement')
    parser.add_argument('--local-claude', action='store_true', help='Use local Claude CLI for enhancement')
    parser.add_argument('--local-gemini', action='store_true', help='Use local Gemini CLI for enhancement')
    parser.add_argument('--local-codex', action='store_true', help='Use local Codex CLI for enhancement')
    parser.add_argument('--api', action='store_true', help='Use API for enhancement (requires ANTHROPIC_API_KEY)')
    parser.add_argument('--full', action='store_true', help='Process full document (default: first 10 pages)')
    parser.add_argument('--max-pages', type=int, default=10, help='Max pages to process if not --full')

    args = parser.parse_args()

    # Validate PDF path
    pdf_path = Path(args.pdf)
    if not pdf_path.exists():
        print(f"❌ PDF file not found: {pdf_path}")
        return 1

    print(f"\n{'='*60}")
    print("PDF Document Processing with Local LLM")
    print(f"{'='*60}\n")
    print(f"📄 PDF: {pdf_path.name}")
    print(f"📁 Output: {args.output_dir}")

    # Determine which LLM CLI provider to use
    llm_provider = None
    provider_name = None

    if args.local_claude:
        provider_name = 'claude'
        llm_provider = ClaudeCLIProvider()
    elif args.local_gemini:
        provider_name = 'gemini'
        llm_provider = GeminiCLIProvider()
    elif args.local_codex:
        provider_name = 'codex'
        llm_provider = CodexCLIProvider()

    # Check provider availability
    if llm_provider and not llm_provider.is_available():
        print(f"\n⚠️  Warning: '{provider_name}' CLI not found in PATH")
        print(f"Please ensure {llm_provider.name} is installed and the CLI is available")
        print("Falling back to basic processing without AI enhancement\n")
        llm_provider = None
        args.no_ai = True
        args.local_claude = False
        args.local_gemini = False
        args.local_codex = False
    elif llm_provider:
        print(f"✅ Using {llm_provider.name} for enhancement\n")

    # Step 1: Extract PDF
    print("\n" + "="*60)
    print("Step 1: Extracting PDF Text")
    print("="*60)

    extractor = PDFTextExtractor()
    extraction = extractor.extract(str(pdf_path))

    print(f"✅ Extracted {extraction.total_pages} pages")
    print(f"✅ Total characters: {len(extraction.total_text):,}")
    print(f"✅ Average quality: {extraction.average_quality:.2f}")
    print(f"✅ Pages needing OCR: {extraction.pages_needing_ocr}")

    # Limit pages if not processing full document
    if not args.full and extraction.total_pages > args.max_pages:
        print(f"\n⚠️  Processing only first {args.max_pages} pages (use --full for complete document)")
        # Truncate content to first N pages
        limited_text = "\n".join([
            f"=== Page {r.page_number} ===\n{r.text}"
            for r in extraction.pages[:args.max_pages]
        ])
        extraction.total_text = limited_text

    # Step 2: Classify Content
    print("\n" + "="*60)
    print("Step 2: Classifying Content")
    print("="*60)

    classifier = ContentClassifier()
    classification = classifier.classify(
        extraction.total_text,
        title=pdf_path.stem
    )

    print(f"✅ Primary category: {classification.primary_category.value}")
    print(f"✅ Confidence: {classification.confidence:.2%}")
    print(f"✅ Quality grade: {classification.quality_metrics.quality_grade}")
    print(f"✅ Completeness: {classification.quality_metrics.completeness:.1f}/10")
    print(f"✅ Clarity: {classification.quality_metrics.clarity:.1f}/10")

    if classification.secondary_categories:
        print(f"✅ Secondary categories: {', '.join(c.value for c in classification.secondary_categories[:3])}")

    # Step 3: Detect Chapters and Split Content
    print("\n" + "="*60)
    print("Step 3: Detecting Chapters and Splitting Content")
    print("="*60)

    # Determine optimal chunk size based on LLM provider
    if llm_provider:
        chunk_size = llm_provider.get_max_chunk_size()
        print(f"📏 Using {llm_provider.name}-optimized chunk size: {chunk_size:,} chars")
    else:
        chunk_size = MAX_CHUNK_SIZE
        print(f"📏 Using default chunk size: {chunk_size:,} chars")

    # Detect chapter structure
    chapters_detected = detect_chapters(extraction.total_text)
    print(f"✅ Detected {len(chapters_detected)} chapters")

    # Split content by chapters with provider-specific chunk size
    structured_chunks = split_by_chapters(extraction.total_text, chunk_size)
    print(f"✅ Split into {len(structured_chunks)} structured chunks")

    for i, chunk_info in enumerate(structured_chunks[:3], 1):
        print(f"   {i}. {chunk_info['title']} ({len(chunk_info['content']):,} chars)")
    if len(structured_chunks) > 3:
        print(f"   ... and {len(structured_chunks) - 3} more")

    # Step 4: Generate Skill Metadata
    print("\n" + "="*60)
    print("Step 4: Generating Skill Metadata")
    print("="*60)

    generator = SkillGenerator(output_dir=args.output_dir)
    skill = generator.generate_skill(
        content=extraction.total_text,
        classification=classification,
        source_file=str(pdf_path)
    )

    print(f"✅ Skill ID: {skill.metadata.id}")
    print(f"✅ Title: {skill.metadata.title}")
    print(f"✅ Tags: {', '.join(skill.metadata.tags)}")
    print(f"✅ Category: {skill.metadata.category}")

    # Step 5: AI Enhancement of Chunks (optional)
    enhanced_chunks = []

    if not args.no_ai:
        print("\n" + "="*60)
        print("Step 5: AI Content Enhancement (Chapter-by-Chapter)")
        print("="*60)

        if llm_provider:
            print(f"Using {llm_provider.name} for {len(structured_chunks)} chunks")
            print(f"Estimated time: {len(structured_chunks) * 5}-{len(structured_chunks) * 8} minutes\n")

            for i, chunk_info in enumerate(structured_chunks, 1):
                print(f"\n--- Chunk {i}/{len(structured_chunks)}: {chunk_info['title']} ---")
                enhanced_content = enhance_single_chunk(
                    chunk_info['content'],
                    classification.primary_category.value,
                    i,
                    len(structured_chunks),
                    llm_provider
                )

                enhanced_chunks.append({
                    'content': enhanced_content,
                    'title': chunk_info['title'],
                    'slug': chunk_info['slug'],
                    'chapter_num': chunk_info['chapter_num']
                })

                print(f"✅ Chunk {i} enhanced ({len(enhanced_content):,} chars)")

        elif args.api:
            print("Using Claude API (requires ANTHROPIC_API_KEY)")
            optimizer = MarkdownOptimizer(
                OptimizationConfig(enable_ai_enhancement=True)
            )

            for i, chunk_info in enumerate(structured_chunks, 1):
                print(f"Enhancing chunk {i}/{len(structured_chunks)}: {chunk_info['title']}")
                try:
                    optimized = optimizer.optimize(
                        chunk_info['content'],
                        classification.primary_category.value
                    )
                    enhanced_chunks.append({
                        'content': optimized.optimized_content,
                        'title': chunk_info['title'],
                        'slug': chunk_info['slug'],
                        'chapter_num': chunk_info['chapter_num']
                    })
                    print(f"✅ Chunk {i} enhanced")
                except Exception as e:
                    print(f"⚠️  Chunk {i} enhancement failed: {e}, using original")
                    enhanced_chunks.append(chunk_info)
        else:
            print("No enhancement method specified, using original content")
            enhanced_chunks = structured_chunks
    else:
        print("\n" + "="*60)
        print("Step 5: Skipping AI Enhancement (--no-ai)")
        print("="*60)
        enhanced_chunks = structured_chunks

    # Step 6: Save Skill Directory Structure
    print("\n" + "="*60)
    print("Step 6: Saving Skill Directory Structure")
    print("="*60)

    skill_dir = generator.save_skill_directory(
        skill_id=skill.metadata.id,
        raw_text=extraction.total_text,
        reference_chunks=enhanced_chunks,
        metadata=skill.metadata,
        subdirectory=None  # Create at root of output_dir
    )

    print(f"✅ Skill directory created: {skill_dir}")
    print(f"   ├── SKILL.md")
    print(f"   ├── references/")
    print(f"   │   ├── index.md")
    for chunk in enhanced_chunks[:3]:
        print(f"   │   ├── {chunk['slug']}.md")
    if len(enhanced_chunks) > 3:
        print(f"   │   └── ... {len(enhanced_chunks) - 3} more")
    print(f"   └── raw/")
    print(f"       └── full-extract.txt ({len(extraction.total_text):,} chars)")

    # Calculate total size
    total_size = sum(
        f.stat().st_size
        for f in skill_dir.rglob('*')
        if f.is_file()
    )
    print(f"\n✅ Total directory size: {total_size:,} bytes")

    # Summary
    print("\n" + "="*60)
    print("✅ Processing Complete!")
    print("="*60)
    print(f"PDF: {pdf_path.name}")
    print(f"Category: {classification.primary_category.value}")
    print(f"Skill ID: {skill.metadata.id}")
    print(f"Output: {skill_dir}")
    print(f"Chapters: {len(enhanced_chunks)}")

    # Determine enhancement method used
    if llm_provider:
        enhancement_method = llm_provider.name
    elif args.api:
        enhancement_method = "Claude API"
    else:
        enhancement_method = "No"

    print(f"AI Enhanced: {enhancement_method}")
    print(f"Total Size: {total_size:,} bytes")
    print("="*60 + "\n")

    return 0


if __name__ == "__main__":
    sys.exit(main())
