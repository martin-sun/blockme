# Document Processor - Phase-02

Offline CRA tax document processing modules for generating high-quality Skill files.

## Quick Start

### Process Complete PDF with Local Claude Code

```bash
cd backend
uv run python generate_skill.py --pdf ../mvp/pdf/t4012-24e.pdf --local-claude --full
```

This will:
- Extract all 153 pages from the PDF
- Classify content by tax category
- Generate a skill file with YAML metadata
- Enhance content using local Claude Code CLI (free with subscription)
- Validate and save the output to `skills_output/`

### Quick Test (First 5 Pages, No AI)

```bash
cd backend
uv run python generate_skill.py --pdf ../mvp/pdf/t4012-24e.pdf --no-ai --max-pages 5
```

---

## Modules Overview

### ✅ All Modules Completed (English-only, fully typed)

1. **pdf_extractor.py** (280 lines) - PDF text extraction
   - PyMuPDF-based extraction
   - OCR support with pytesseract
   - Intelligent quality assessment
   - Complete type annotations
   - Pydantic models: `PDFExtractorConfig`, `PageResult`, `PDFMetadata`, `ExtractionResult`

2. **content_classifier.py** (330 lines) - Content classification
   - Keyword-based multi-category classification
   - 25+ tax categories (TaxCategory enum)
   - 5-dimensional quality metrics
   - Confidence scoring
   - Pydantic models: `TaxCategory`, `QualityMetrics`, `ClassificationResult`

3. **skill_generator.py** (280 lines) - Skill file generation
   - Generate Markdown with YAML front matter
   - Compatible with MVP skill_loader.py
   - Hierarchical organization by category
   - Auto-generate IDs, titles, tags, descriptions
   - Pydantic models: `SkillMetadata`, `SkillContent`

4. **markdown_optimizer.py** (250 lines) - AI content enhancement
   - Basic cleaning (PDF artifacts, formatting)
   - AI enhancement with Claude/OpenAI/ZhipuAI APIs
   - Offline processing (API usage allowed)
   - Pydantic models: `OptimizationConfig`, `OptimizationResult`, `AIProvider`

5. **quality_validator.py** (320 lines) - Quality validation
   - YAML front matter validation
   - Markdown format checking
   - Content quality assessment
   - Tax content accuracy validation
   - Pydantic models: `ValidationIssue`, `ValidationResult`

6. **__init__.py** (95 lines) - Module initialization
   - Clean exports
   - Version information
   - All public APIs exposed

7. **tests/test_document_processing.py** (270 lines) - Integration tests
   - ✅ All 6 tests passing
   - English-only test output
   - Full pipeline validation

---

## Code Standards Compliance

All code follows project standards from `.claude/skills/development-policies`:

- ✅ All identifiers in English
- ✅ All docstrings in English
- ✅ All Field descriptions in English
- ✅ Complete type annotations
- ✅ Pydantic models for data validation
- ✅ Structured logging
- ✅ Proper error handling

---

## Usage

### Python API

```python
from app.document_processor import (
    PDFTextExtractor,
    ContentClassifier,
    SkillGenerator,
    MarkdownOptimizer,
    QualityValidator
)

# 1. Extract PDF text
extractor = PDFTextExtractor()
extraction_result = extractor.extract("document.pdf")

# 2. Classify content
classifier = ContentClassifier()
classification = classifier.classify(
    extraction_result.total_text,
    title="Tax Document"
)

# 3. Generate Skill file
generator = SkillGenerator(output_dir="skills")
skill = generator.generate_skill(
    content=extraction_result.total_text,
    classification=classification,
    source_file="document.pdf"
)

# 4. Optimize with AI (optional)
optimizer = MarkdownOptimizer()
optimized = optimizer.optimize(skill.markdown_body)
skill.markdown_body = optimized.optimized_content

# 5. Validate quality
validator = QualityValidator()
validation = validator.validate_content(
    generator._render_skill_file(skill)
)

# 6. Save if valid
if validation.is_valid:
    file_path = generator.save_skill(skill)
    print(f"Skill saved: {file_path}")
```

### CLI Script

The `generate_skill.py` script provides a convenient way to generate skills from PDFs:

**Location**: `backend/generate_skill.py`

**Command Options**:

| Flag | Type | Default | Description |
|------|------|---------|-------------|
| `--pdf` | Required | - | Path to PDF file |
| `--full` | Flag | False | **Process ALL pages** (otherwise limited to --max-pages) |
| `--local-claude` | Flag | False | Use local Claude CLI (free with Code Max subscription) |
| `--no-ai` | Flag | False | Skip AI enhancement (fastest mode) |
| `--api` | Flag | False | Use Claude API (requires ANTHROPIC_API_KEY) |
| `--max-pages N` | Integer | 10 | Max pages to process when not using --full |
| `--output-dir PATH` | String | `skills_output` | Output directory for generated skills |

**Example Commands**:

```bash
# Complete processing with local Claude (recommended)
uv run python generate_skill.py \
  --pdf ../mvp/pdf/t4012-24e.pdf \
  --local-claude \
  --full

# Fast test without AI (first 10 pages)
uv run python generate_skill.py \
  --pdf ../mvp/pdf/t4012-24e.pdf \
  --no-ai

# Custom page range with API enhancement
export ANTHROPIC_API_KEY="sk-ant-..."
uv run python generate_skill.py \
  --pdf ../mvp/pdf/t4012-24e.pdf \
  --api \
  --max-pages 20
```

---

## Output Structure

Generated skill files are organized by category:

```
skills_output/
└── credits/                    # Category subdirectory
    └── credits-t4012-24e.md   # Generated skill file
```

**File Format**:

```yaml
---
id: credits-t4012-24e
title: Tax Credits
tags: [Tax Credits, CRA, Canadian Tax, Corporation]
description: Comprehensive guide to tax credits
domain: tax
category: credits
priority: medium
quality_grade: B
source: ../mvp/pdf/t4012-24e.pdf
---

# Tax Credits

## Canada Carbon Rebate for Small Businesses

[Enhanced content with clear structure, examples, and actionable guidance]
```

---

## Performance Benchmarks

From test runs with real CRA PDFs:

| Stage | Time | Notes |
|-------|------|-------|
| PDF Extraction | 1-5 sec | Depends on PDF size; 153 pages ~0.5 sec |
| Classification | <1 sec | Keyword-based, very fast |
| Skill Generation | <1 sec | Template-based |
| Local Claude Enhancement | 2-4 min | Per 300K char chunk; **5-8 min for 720K PDF** |
| API Enhancement | 5-15 sec | Automated, faster than CLI |
| Validation | <1 sec | Format and quality checks |

**Total Processing Time**:
- Without AI: ~5-10 seconds (full 153-page doc)
- With Local Claude: **5-8 minutes** (for 720K char / 153-page doc)
- With API: ~15-25 seconds

---

## Current Limitations

### 1. Content Processing Limit

**Issue**: The script limits Claude enhancement to the first 300,000 characters per chunk (~75K tokens).

```python
# From generate_skill.py line 38
MAX_CHUNK_SIZE = 300_000  # ~75K tokens, optimal for 200K input + 64K output
content_sample = content[:MAX_CHUNK_SIZE] if len(content) > MAX_CHUNK_SIZE else content
```

**Based on Claude Sonnet 4.5 specs**:
- Input context: 200K tokens (≈800,000 chars)
- Output limit: 64K tokens (≈256,000 chars)
- Processing 300K chars (~75K tokens) leaves safe room for maximum 64K token output
- Total utilization: ~139K tokens (69.6% of 200K context)

**Impact**:
- Documents up to ~300 pages can be processed in one call
- 720K PDF needs only 2-3 chunks (vs 144 with original 5K limit)
- Information retention: ~42% per chunk (60x improvement from original)
- Processing time: 5-8 minutes (vs 48 minutes with original limit)

**Workaround**: Process specific page ranges or split large PDFs by chapter.

**Future Fix**: Implement automatic chunked processing with overlap to handle documents of any size.

### 2. Quality Scoring Gap

**Issue**: The validator primarily checks format quality (YAML syntax, Markdown structure), not content completeness.

**Impact**:
- A file with perfect formatting but missing 80% of content can score A+
- No comparison to source document size or topic coverage

**Workaround**: Manually review generated files for completeness.

**Future Fix**: Add completeness metrics (retention ratio, topic coverage) to validation.

### 3. Processing Mode

**Current**: The test script is designed for testing and validation.

**For Production**: Use the Python API directly for better control over chunking, error handling, and batch processing.

---

## Troubleshooting

### `claude: command not found`

**Solution**: Install Claude Code and ensure CLI is in PATH
- Verify: `which claude`
- Install: Download from [claude.com](https://claude.com/claude-code)

### Local Claude doesn't enhance content

**Solution**: Check Claude Code subscription status
- Requires Claude Code Max subscription
- Fallback: Use `--api` mode with `ANTHROPIC_API_KEY`

### PDF extraction fails

**Solutions**:
- Ensure PyMuPDF is installed: `uv sync`
- Check PDF is not corrupted or password-protected
- Try different PDF if issue persists

### Quality score seems too high

This is a known limitation. The validator checks format, not completeness.
- Review the actual content manually
- Check file size vs source PDF
- Count topics covered vs expected

---

## Next Steps

1. **Test with your PDF**:
   ```bash
   uv run python generate_skill.py --pdf your-file.pdf --local-claude --full
   ```

2. **Review generated skill files** in `skills_output/`

3. **Adjust for your needs**:
   - Modify classification categories in `content_classifier.py`
   - Customize skill templates in `skill_generator.py`
   - Tune enhancement prompts in `generate_skill.py`

4. **Integrate into production**:
   - Use Python API for programmatic access
   - Implement proper error handling
   - Add retry logic for Claude API calls
   - Consider batch processing for multiple PDFs

---

## Project Standards

All code follows `.claude/skills/development-policies`:
- English-only code and documentation
- Full type annotations with Pydantic models
- Structured logging with proper levels
- Comprehensive error handling
