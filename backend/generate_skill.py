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

# Claude processing configuration
# Based on Claude Sonnet 4.5 specs: 200K token input, 64K token output (≈800K chars)
# Using 300K chars (75K tokens) leaves safe margin for 64K token responses
MAX_CHUNK_SIZE = 300_000      # ~75K tokens, optimal for 200K input + 64K output
MIN_TIMEOUT = 90              # Minimum timeout in seconds
TIMEOUT_PER_1K_CHARS = 1      # Scale timeout: 1 second per 1,000 chars


def is_claude_available() -> bool:
    """Check if claude CLI is available."""
    return shutil.which('claude') is not None


def enhance_with_local_claude(content: str, category: str) -> str:
    """
    Enhance content using local claude CLI.

    No API key required - uses Claude Code subscription.
    """
    print("  Using local Claude Code CLI for enhancement...")

    # Build enhancement prompt - limit to MAX_CHUNK_SIZE for Claude context
    content_sample = content[:MAX_CHUNK_SIZE] if len(content) > MAX_CHUNK_SIZE else content

    prompt = f"""Please optimize this CRA tax content for the '{category}' category.

Requirements:
1. Keep all factual information accurate and complete
2. Add practical examples where appropriate
3. Improve clarity and structure
4. Use professional Canadian tax terminology
5. Format as clean Markdown with proper headers (##, ###)
6. Make it actionable for developers building tax applications

IMPORTANT: Output ONLY the enhanced Markdown content, nothing else. No meta-commentary.

Content to enhance:
{content_sample}

Enhanced content (Markdown only):"""

    try:
        # Call claude CLI with --print mode for non-interactive output
        # --tools "" disables all tools for faster text-only processing
        print(f"  Calling Claude CLI (processing {len(content_sample):,} / {len(content):,} chars)...")

        # Dynamic timeout based on content size (1 sec per 1K chars, minimum 90s)
        timeout = max(MIN_TIMEOUT, len(content_sample) // 1000)

        result = subprocess.run(
            ['claude', '--print', '--tools', ''],
            input=prompt,
            capture_output=True,
            text=True,
            timeout=timeout
        )

        if result.returncode == 0 and result.stdout:
            enhanced = result.stdout.strip()
            # Filter out any system messages or errors
            if enhanced and len(enhanced) > 50 and not enhanced.startswith("Error"):
                print(f"  ✅ Enhanced content received ({len(enhanced)} chars)")
                return enhanced
            else:
                print(f"  ⚠️  Claude returned invalid output, using original content")
                return content
        else:
            print(f"  ⚠️  Claude CLI failed (code {result.returncode}), using original content")
            if result.stderr:
                print(f"  Error: {result.stderr[:300]}")
            return content

    except subprocess.TimeoutExpired:
        print("  ⚠️  Claude CLI timeout (90s), using original content")
        return content
    except Exception as e:
        print(f"  ⚠️  Claude CLI error: {e}, using original content")
        return content


def main():
    parser = argparse.ArgumentParser(description='Generate skill files from CRA tax PDFs with Claude enhancement')
    parser.add_argument('--pdf', required=True, help='Path to PDF file')
    parser.add_argument('--output-dir', default='skills_output', help='Output directory for generated skills')
    parser.add_argument('--no-ai', action='store_true', help='Skip AI enhancement')
    parser.add_argument('--local-claude', action='store_true', help='Use local Claude CLI for enhancement')
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
    print("PDF Document Processing with Local Claude Test")
    print(f"{'='*60}\n")
    print(f"📄 PDF: {pdf_path.name}")
    print(f"📁 Output: {args.output_dir}")

    # Check Claude availability if needed
    if args.local_claude and not is_claude_available():
        print("\n⚠️  Warning: 'claude' CLI not found in PATH")
        print("Please ensure Claude Code is installed and the CLI is available")
        print("Falling back to basic processing without AI enhancement\n")
        args.local_claude = False
        args.no_ai = True

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

    # Step 3: Generate Skill
    print("\n" + "="*60)
    print("Step 3: Generating Skill File")
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
    print(f"✅ Content length: {len(skill.markdown_body):,} chars")

    # Step 4: AI Enhancement (optional)
    if not args.no_ai:
        print("\n" + "="*60)
        print("Step 4: AI Content Enhancement")
        print("="*60)

        if args.local_claude:
            print("Using local Claude Code CLI (free with subscription)")
            enhanced_content = enhance_with_local_claude(
                skill.markdown_body,
                classification.primary_category.value
            )
            if enhanced_content != skill.markdown_body:
                skill.markdown_body = enhanced_content
                print(f"✅ Content enhanced via Claude CLI")

        elif args.api:
            print("Using Claude API (requires ANTHROPIC_API_KEY)")
            try:
                optimizer = MarkdownOptimizer(
                    OptimizationConfig(enable_ai_enhancement=True)
                )
                optimized = optimizer.optimize(
                    skill.markdown_body,
                    classification.primary_category.value
                )
                skill.markdown_body = optimized.optimized_content
                print(f"✅ Content enhanced via API")
                print(f"✅ API provider: {optimized.provider or 'default'}")
            except Exception as e:
                print(f"⚠️  API enhancement failed: {e}")
        else:
            print("No enhancement method specified")
    else:
        print("\n" + "="*60)
        print("Step 4: Skipping AI Enhancement (--no-ai)")
        print("="*60)

    # Step 5: Validate Quality
    print("\n" + "="*60)
    print("Step 5: Validating Quality")
    print("="*60)

    validator = QualityValidator()
    full_content = generator._render_skill_file(skill)
    validation = validator.validate_content(full_content)

    print(f"✅ Valid: {validation.is_valid}")
    print(f"✅ Score: {validation.score:.1f}/100")
    print(f"✅ Grade: {validation.quality_grade}")

    if validation.errors:
        print(f"\n⚠️  Errors ({len(validation.errors)}):")
        for error in validation.errors[:5]:
            print(f"  - {error.message}")

    if validation.warnings:
        print(f"\n⚠️  Warnings ({len(validation.warnings)}):")
        for warning in validation.warnings[:5]:
            print(f"  - {warning.message}")

    if validation.info:
        print(f"\nℹ️  Info ({len(validation.info)}):")
        for info in validation.info[:3]:
            print(f"  - {info.message}")

    # Step 6: Save Skill File
    print("\n" + "="*60)
    print("Step 6: Saving Skill File")
    print("="*60)

    if validation.is_valid or validation.score >= 60:
        file_path = generator.save_skill(
            skill,
            subdirectory=classification.primary_category.value
        )
        print(f"✅ Saved to: {file_path}")
        print(f"✅ File size: {Path(file_path).stat().st_size:,} bytes")
    else:
        print(f"❌ Skill quality too low (score: {validation.score:.1f}), not saving")
        print("Consider using AI enhancement to improve quality")

    # Summary
    print("\n" + "="*60)
    print("✅ Test Complete!")
    print("="*60)
    print(f"PDF: {pdf_path.name}")
    print(f"Category: {classification.primary_category.value}")
    print(f"Quality: {validation.quality_grade} ({validation.score:.1f}/100)")
    print(f"AI Enhanced: {'Yes' if args.local_claude or args.api else 'No'}")
    print("="*60 + "\n")

    return 0


if __name__ == "__main__":
    sys.exit(main())
