"""
Gemini Smart Processor

Uses Gemini CLI with 1.5M context window to perform intelligent document analysis:
- Semantic classification (vs keyword matching)
- Topic-based chunking (vs chapter detection)

This replaces Stage 2 (classification) and Stage 3 (chunking) with a single,
unified LLM-powered analysis that understands the document holistically.
"""

import logging
import re
from typing import Dict, List, Optional, Tuple
from pydantic import BaseModel, Field

from .content_classifier import TaxCategory, QualityMetrics
from .llm_cli_providers import get_provider

logger = logging.getLogger(__name__)


class TOCEntry(BaseModel):
    """Table of Contents entry."""

    level: int = Field(..., ge=1, description="Hierarchy level (1=chapter, 2=section, 3=subsection)")
    title: str = Field(..., description="Chapter/section title")
    page_number: int = Field(..., ge=1, description="Page number where this section starts")
    char_start: Optional[int] = Field(None, ge=0, description="Character start position in full text")
    char_end: Optional[int] = Field(None, gt=0, description="Character end position in full text")


class DocumentTOC(BaseModel):
    """Document Table of Contents structure."""

    has_toc: bool = Field(..., description="Whether document has identifiable TOC")
    source: str = Field(..., description="TOC source: 'document_page' | 'generated' | 'embedded'")
    entries: List[TOCEntry] = Field(default_factory=list, description="List of TOC entries")
    max_level: int = Field(default=1, ge=1, description="Maximum hierarchy level in TOC")

    @property
    def total_entries(self) -> int:
        """Total number of TOC entries."""
        return len(self.entries)


class SmartClassification(BaseModel):
    """Classification result from Gemini semantic analysis."""

    primary_category: TaxCategory = Field(..., description="Primary tax category")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Classification confidence")
    secondary_categories: List[TaxCategory] = Field(default_factory=list,
                                                      description="Secondary categories")
    reasoning: str = Field(..., description="Explanation for the classification")
    method: str = Field(default="gemini_semantic", description="Classification method used")

    # Quality metrics (can be optionally filled by LLM or computed)
    quality_metrics: Optional[QualityMetrics] = None


class DocumentAnalysis(BaseModel):
    """Complete document analysis result from Gemini."""

    classification: SmartClassification
    toc: DocumentTOC
    total_chars: int
    processing_time: float
    model: str = "gemini-2.5-pro"


class GeminiSmartProcessor:
    """
    Intelligent document processor using Gemini CLI.

    Capabilities:
    - 1.5M character context window (can process 721K CRA documents in one call)
    - Semantic understanding (vs keyword matching)
    - Topic-aware chunking (vs structural detection)
    - Unified analysis (classification + chunking in one pass)
    """

    # Maximum input size supported by Gemini
    MAX_INPUT_SIZE = 1_500_000  # 1.5M chars (~375K tokens)

    # Chunk size limits
    # For Gemini API: use maximum possible size to leverage full context window
    DEFAULT_MAX_CHUNK_SIZE = 1_500_000  # 1.5M chars (full Gemini context)

    def __init__(self, provider_name: str = 'gemini'):
        """
        Initialize the Gemini smart processor.

        Args:
            provider_name: Name of the LLM provider (default: 'gemini')
        """
        self.provider = get_provider(provider_name)

        if not self.provider.is_available():
            raise RuntimeError(
                f"Gemini CLI is not available. Please install:\n"
                f"  npm install -g @google/gemini-cli\n"
                f"Then authenticate:\n"
                f"  gemini login"
            )

        logger.info(f"Initialized GeminiSmartProcessor with provider: {provider_name}")

    def analyze_full_document(
        self,
        content: str,
        title: str = "",
        max_chunk_size: Optional[int] = None
    ) -> DocumentAnalysis:
        """
        Analyze the full document in one pass using Gemini's large context window.

        This is the main entry point that performs:
        1. Document classification (tax category)
        2. TOC identification or generation (document structure)

        Args:
            content: Full document text
            title: Document title (optional, helps with classification)
            max_chunk_size: Maximum chunk size in characters (default: 1.5M)

        Returns:
            DocumentAnalysis: Complete analysis including classification and TOC

        Raises:
            ValueError: If content is too large or empty
            RuntimeError: If Gemini API call fails
        """
        import time

        # Validate input
        if not content or not content.strip():
            raise ValueError("Content cannot be empty or whitespace-only")

        content_length = len(content)

        if content_length > self.MAX_INPUT_SIZE:
            raise ValueError(
                f"Content too large ({content_length} chars > {self.MAX_INPUT_SIZE} limit). "
                f"Consider using chunked processing instead."
            )

        max_chunk_size = max_chunk_size or self.DEFAULT_MAX_CHUNK_SIZE

        logger.info(f"Analyzing document: {content_length} chars, max_chunk={max_chunk_size}")
        logger.info(f"Title: {title or '(untitled)'}")

        # Build the analysis prompt
        prompt = self._build_analysis_prompt(content, title, max_chunk_size)

        # Call Gemini
        start_time = time.time()
        try:
            logger.info("Calling Gemini CLI for document analysis...")
            enhanced_content = self._call_gemini(prompt, content_length)
            processing_time = time.time() - start_time
            logger.info(f"Gemini analysis completed in {processing_time:.1f}s")
        except Exception as e:
            logger.error(f"Gemini API call failed: {e}")
            raise RuntimeError(f"Failed to analyze document with Gemini: {e}")

        # Parse the response
        try:
            analysis = self._parse_analysis_result(enhanced_content, content_length, processing_time)
            logger.info(f"Parsed result: {analysis.classification.primary_category}, "
                       f"TOC: {len(analysis.toc.entries)} entries")
            return analysis
        except Exception as e:
            logger.error(f"Failed to parse Gemini response: {e}")
            logger.debug(f"Raw response:\n{enhanced_content[:500]}...")
            raise RuntimeError(f"Failed to parse Gemini response: {e}")

    def _build_analysis_prompt(self, content: str, title: str, max_chunk_size: int) -> str:
        """
        Build the comprehensive analysis prompt for Gemini.

        The prompt instructs Gemini to:
        1. Classify the document into tax categories
        2. Identify major topics
        3. Suggest semantic chunk boundaries
        """
        # Get list of available categories
        categories = [cat.value for cat in TaxCategory if cat != TaxCategory.UNKNOWN]
        categories_str = ", ".join(categories)

        # Build enhanced prompt with domain expertise
        prompt = f"""You are a specialized AI assistant for analyzing CRA (Canada Revenue Agency) tax documents. You have deep expertise in Canadian tax law, accounting practices, and document classification.

**Document Information:**
- Title: {title or "(untitled)"}
- Length: {len(content):,} characters
- Target chunk size: {max_chunk_size:,} characters

**Your Task:**

Perform a comprehensive semantic analysis of this CRA tax document and provide:

1. **Classification**: Identify the primary tax category using domain knowledge
2. **Topic Analysis**: Identify major topics/sections with semantic understanding
3. **Chunking Strategy**: Create semantically coherent chunks for downstream processing

---

## PART 1: CATEGORY CLASSIFICATION

**Available Tax Categories:**
{categories_str}

**Classification Guidelines:**

When classifying, look for these key signals:

1. **Document Form Numbers**: T1 (personal income), T2 (corporate), T4 (employment), T4A (self-employment), T5 (investment income), T1135 (foreign property), etc.

2. **Topic-Specific Keywords**:
   - Personal/Employment: salary, wages, employee benefits, T4 slip
   - Business: business income, expenses, fiscal period, GST/HST registration
   - Capital Gains: disposition, ACB (adjusted cost base), principal residence
   - Credits: tax credit, non-refundable, refundable, eligible
   - Deductions: RRSP, child care, moving expenses, medical
   - GST/HST: input tax credit (ITC), supply, registrant, rebate

3. **Context Clues**:
   - Target audience (individuals vs businesses vs corporations)
   - Referenced legislation (Income Tax Act sections)
   - Document purpose (guide, form instructions, technical interpretation)

4. **Multi-Category Documents**:
   - If document covers multiple topics, choose the PRIMARY focus
   - List other significant topics as secondary categories
   - Confidence should reflect clarity of primary focus

**Confidence Scoring:**
- 0.95-1.0: Crystal clear, single focused topic with strong signals
- 0.85-0.94: Clear primary focus, may have minor secondary topics
- 0.70-0.84: Primary topic identifiable, significant secondary content
- 0.50-0.69: Mixed content, primary topic requires interpretation
- Below 0.50: Unclear or general content (use 'general' category)

---

## PART 2: TOC (TABLE OF CONTENTS) IDENTIFICATION/GENERATION

Your task is to identify or generate a structured Table of Contents for this document.

**Priority 1: Look for existing TOC in the document**
- Check if the document contains a "Table of Contents" page or section
- Usually found in the first few pages
- Common formats:
  - "Table of contents" or "Contents" heading
  - List of chapters/sections with page numbers
  - May use Roman numerals for front matter
- If found: Extract ALL entries with their hierarchy levels and page numbers

**Priority 2: Generate TOC based on document structure (if no explicit TOC page)**
- Analyze the document structure to identify major divisions
- Look for structural indicators:
  - **Heading styles**: Larger fonts, bold text, all-caps headings
  - **Section markers**: "Chapter N", "Section N", "Part N", "Appendix"
  - **Page markers**: Look for "=== Page N ===" in the text
  - **Visual breaks**: Page breaks before major sections
  - **Numbering patterns**: 1.0, 1.1, 1.2 or I, II, III
- Generate a hierarchical TOC with logical divisions

**TOC Structure Requirements:**
- **Level 1**: Major chapters/parts (e.g., "Chapter 1 - Page 1 of T2 return")
- **Level 2**: Major sections within chapters (e.g., "Identification", "Attachments")
- **Level 3**: Subsections if clearly present (e.g., "Corporation information", "Tax year")
- Each entry MUST include: level (int), title (str), page_number (int)

**Character Position Estimation:**
- For each TOC entry, estimate its character position in the full text
- Use page markers "=== Page N ===" to calculate positions
- Assume average page ~5,000-10,000 characters
- Entries should sequentially cover the entire document
- No gaps or overlaps allowed

**Special Instructions for CRA Tax Documents:**
- T-series forms often have structured sections (T1, T2, T4, etc.)
- Common patterns: "Page 1 of Form", "Page 2 of Form", "Schedule X"
- Respect form-based structure as primary hierarchy
- Group related schedules and attachments together

---

## OUTPUT FORMAT

Structure your response EXACTLY as follows:

## CLASSIFICATION

**Primary Category:** [category_name]
**Confidence:** [0.00-1.00]
**Secondary Categories:** [cat1, cat2] or (none)
**Reasoning:** [2-3 sentences explaining: (1) key signals found, (2) why this category best fits, (3) confidence justification]

## TOC

**Has TOC:** [yes/no]
**Source:** [document_page | generated | hybrid]
**Max Level:** [1-3]

### Entry 1
- **Level:** 1
- **Title:** Chapter 1 - Page 1 of T2 return
- **Page Number:** 24
- **Character Start:** 0
- **Character End:** 50000

### Entry 2
- **Level:** 2
- **Title:** Identification
- **Page Number:** 24
- **Character Start:** 0
- **Character End:** 25000

### Entry 3
- **Level:** 2
- **Title:** Attachments
- **Page Number:** 25
- **Character Start:** 25000
- **Character End:** 50000

[... continue for all entries ...]

---

**CRITICAL REMINDERS:**
- Use EXACT category names from the list above (case-sensitive)
- ALL TOC entries must have: level (int), title (str), page_number (int), char_start (int), char_end (int)
- Character ranges must be sequential and non-overlapping
- Total coverage should be close to 100% of document length ({len(content)} characters)
- Provide 5-30 entries depending on document structure
- If document truly has no structure, create at least 3-5 logical divisions
- Each entry title should be concise and descriptive

---

**Document Content:**

{content}

---

Now provide your analysis following the format above. Focus on accuracy, semantic understanding, and practical usefulness for downstream AI processing.
"""
        return prompt

    def _call_gemini(self, prompt: str, content_length: int) -> str:
        """
        Call Gemini provider (CLI or API) with the analysis prompt.

        Args:
            prompt: The complete analysis prompt
            content_length: Length of content (for timeout calculation)

        Returns:
            str: Raw response from Gemini
        """
        import subprocess

        # Check if this is an API-based provider
        if self.provider.is_api_based():
            # For API-based providers, call parse_output directly with prompt
            # The parse_output method will handle the API call
            logger.info(f"Calling Gemini API for document analysis...")
            try:
                enhanced_content = self.provider.parse_output(prompt, "")
                return enhanced_content
            except Exception as e:
                raise RuntimeError(f"Gemini API call failed: {e}")

        # CLI-based provider logic
        # Build command
        command = self.provider.build_command(prompt)

        # Calculate timeout (generous for large documents)
        timeout = self.provider.get_timeout(content_length)

        logger.debug(f"Executing command: {' '.join(command[:3])}... (timeout: {timeout}s)")

        # Execute
        try:
            if self.provider.uses_stdin():
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

            # Check return code before parsing output
            if result.returncode != 0:
                error_msg = result.stderr.strip() or result.stdout.strip() or "Unknown error"
                raise RuntimeError(f"Gemini CLI failed (exit code {result.returncode}): {error_msg}")

            # Parse output
            enhanced_content = self.provider.parse_output(result.stdout, result.stderr)
            return enhanced_content

        except subprocess.TimeoutExpired:
            raise RuntimeError(f"Gemini CLI timed out after {timeout}s")
        except Exception as e:
            raise RuntimeError(f"Gemini CLI execution failed: {e}")

    def _parse_analysis_result(
        self,
        response: str,
        content_length: int,
        processing_time: float
    ) -> DocumentAnalysis:
        """
        Parse Gemini's structured response into DocumentAnalysis.

        Expected format:
        ## CLASSIFICATION
        **Primary Category:** credits
        **Confidence:** 0.95
        ...

        ## TOC
        **Has TOC:** yes
        **Source:** document_page
        ### Entry 1
        ...
        """
        # Extract classification section
        classification = self._parse_classification_section(response)

        # Extract TOC section
        toc = self._parse_toc_section(response, content_length)

        # Build DocumentAnalysis
        analysis = DocumentAnalysis(
            classification=classification,
            toc=toc,
            total_chars=content_length,
            processing_time=processing_time
        )

        return analysis

    def _parse_classification_section(self, response: str) -> SmartClassification:
        """
        Parse the CLASSIFICATION section from Gemini's response.
        """
        # Extract the classification section
        class_match = re.search(
            r'## CLASSIFICATION\s*\n(.*?)(?=## TOC|$)',
            response,
            re.DOTALL | re.IGNORECASE
        )

        if not class_match:
            raise ValueError("Could not find CLASSIFICATION section in response")

        class_section = class_match.group(1)

        # Parse primary category
        primary_match = re.search(
            r'\*\*Primary Category:\*\*\s*([a-z_]+)',
            class_section,
            re.IGNORECASE
        )
        if not primary_match:
            raise ValueError("Could not find Primary Category")

        primary_str = primary_match.group(1).strip()

        # Convert to TaxCategory enum
        try:
            primary_category = TaxCategory(primary_str)
        except ValueError:
            logger.warning(f"Unknown category '{primary_str}', defaulting to GENERAL")
            primary_category = TaxCategory.GENERAL

        # Parse confidence
        conf_match = re.search(
            r'\*\*Confidence:\*\*\s*(0?\.\d+|1\.0|0|1)',
            class_section,
            re.IGNORECASE
        )
        confidence = float(conf_match.group(1)) if conf_match else 0.85

        # Parse secondary categories
        secondary_match = re.search(
            r'\*\*Secondary Categories:\*\*\s*([^\n]+)',
            class_section,
            re.IGNORECASE
        )
        secondary_categories = []
        if secondary_match and secondary_match.group(1).strip() not in ['(none)', 'none', 'N/A', '']:
            secondary_str = secondary_match.group(1).strip()
            # Split by comma and convert to enum
            for cat_str in re.split(r'[,;]', secondary_str):
                cat_str = cat_str.strip()
                try:
                    secondary_categories.append(TaxCategory(cat_str))
                except ValueError:
                    logger.warning(f"Unknown secondary category '{cat_str}', skipping")

        # Parse reasoning
        reasoning_match = re.search(
            r'\*\*Reasoning:\*\*\s*([^\n]+(?:\n(?!\*\*)[^\n]+)*)',
            class_section,
            re.IGNORECASE
        )
        reasoning = reasoning_match.group(1).strip() if reasoning_match else "No reasoning provided"

        return SmartClassification(
            primary_category=primary_category,
            confidence=confidence,
            secondary_categories=secondary_categories,
            reasoning=reasoning
        )

    def _parse_toc_section(self, response: str, total_chars: int) -> DocumentTOC:
        """
        Parse the TOC section from Gemini's response.

        Expected format:
        ## TOC
        **Has TOC:** yes
        **Source:** document_page
        **Max Level:** 2

        ### Entry 1
        - **Level:** 1
        - **Title:** Chapter 1
        - **Page Number:** 24
        - **Character Start:** 0
        - **Character End:** 50000
        """
        # Extract the TOC section
        toc_match = re.search(
            r'## TOC\s*\n(.*?)$',
            response,
            re.DOTALL | re.IGNORECASE
        )

        if not toc_match:
            raise ValueError("Could not find TOC section in response")

        toc_section = toc_match.group(1)

        # Parse Has TOC
        has_toc_match = re.search(
            r'\*\*Has TOC:\*\*\s*(yes|no)',
            toc_section,
            re.IGNORECASE
        )
        has_toc = has_toc_match and has_toc_match.group(1).lower() == 'yes' if has_toc_match else False

        # Parse Source
        source_match = re.search(
            r'\*\*Source:\*\*\s*([^\n]+)',
            toc_section,
            re.IGNORECASE
        )
        source = source_match.group(1).strip() if source_match else "generated"

        # Parse Max Level
        max_level_match = re.search(
            r'\*\*Max Level:\*\*\s*(\d+)',
            toc_section,
            re.IGNORECASE
        )
        max_level = int(max_level_match.group(1)) if max_level_match else 1

        # Find all TOC entry definitions
        # Pattern: ### Entry N
        entry_patterns = re.finditer(
            r'### Entry (\d+)\s*\n(.*?)(?=### Entry \d+|$)',
            toc_section,
            re.DOTALL | re.IGNORECASE
        )

        entries = []
        for match in entry_patterns:
            entry_num = int(match.group(1))
            entry_body = match.group(2)

            # Parse Level
            level_match = re.search(
                r'\*\*Level:\*\*\s*(\d+)',
                entry_body,
                re.IGNORECASE
            )
            if not level_match:
                logger.warning(f"Entry {entry_num}: Could not find Level, skipping")
                continue
            level = int(level_match.group(1))

            # Parse Title
            title_match = re.search(
                r'\*\*Title:\*\*\s*([^\n]+)',
                entry_body,
                re.IGNORECASE
            )
            if not title_match:
                logger.warning(f"Entry {entry_num}: Could not find Title, skipping")
                continue
            title = title_match.group(1).strip()

            # Parse Page Number
            page_match = re.search(
                r'\*\*Page Number:\*\*\s*(\d+)',
                entry_body,
                re.IGNORECASE
            )
            if not page_match:
                logger.warning(f"Entry {entry_num}: Could not find Page Number, skipping")
                continue
            page_number = int(page_match.group(1))

            # Parse Character Start
            char_start_match = re.search(
                r'\*\*Character Start:\*\*\s*(\d+)',
                entry_body,
                re.IGNORECASE
            )
            char_start = int(char_start_match.group(1)) if char_start_match else None

            # Parse Character End
            char_end_match = re.search(
                r'\*\*Character End:\*\*\s*(\d+)',
                entry_body,
                re.IGNORECASE
            )
            char_end = int(char_end_match.group(1)) if char_end_match else None

            # Validate character range if provided
            if char_start is not None and char_end is not None:
                if char_start < 0 or char_end > total_chars or char_start >= char_end:
                    logger.warning(f"Entry {entry_num}: Invalid character range {char_start}-{char_end}, adjusting")
                    char_start = max(0, char_start)
                    char_end = min(total_chars, char_end)
                    if char_start >= char_end:
                        char_start = None
                        char_end = None

            # Create TOCEntry
            entry = TOCEntry(
                level=level,
                title=title,
                page_number=page_number,
                char_start=char_start,
                char_end=char_end
            )
            entries.append(entry)

        # If no entries found but has_toc is True, warn
        if not entries and has_toc:
            logger.warning("No TOC entries found despite has_toc=True")

        # Sort entries by char_start or page_number
        if entries:
            entries.sort(key=lambda e: (e.char_start if e.char_start is not None else e.page_number * 10000))

        # Build DocumentTOC
        doc_toc = DocumentTOC(
            has_toc=has_toc,
            source=source,
            entries=entries,
            max_level=max_level
        )

        logger.info(f"Parsed TOC: has_toc={has_toc}, source={source}, {len(entries)} entries, max_level={max_level}")

        return doc_toc


def test_gemini_smart_processor():
    """Quick test function for development."""
    import time

    # Sample CRA content
    test_content = """
    CANADA REVENUE AGENCY - TAX CREDITS GUIDE

    Climate Action Incentive Payment

    The Climate Action Incentive (CAI) payment is a tax-free amount paid to help
    individuals and families offset the cost of federal pollution pricing. It is
    available to residents of Alberta, Saskatchewan, Manitoba, and Ontario.

    Eligibility Requirements:
    - You must be a resident of a participating province
    - You must be 19 years or older, or have a spouse or common-law partner
    - You must file a tax return to receive the payment

    Payment Amounts:
    - Base amount: $386 (varies by province)
    - Additional amount for spouse: $193
    - Additional amount per child under 19: $96.50

    How to Claim:
    You don't need to apply. The CRA will automatically determine your eligibility
    when you file your tax return. The payment will be issued quarterly.
    """ * 20  # Repeat to make it longer

    try:
        processor = GeminiSmartProcessor()

        print(f"Testing with {len(test_content)} chars of content...")
        start = time.time()

        analysis = processor.analyze_full_document(
            content=test_content,
            title="Climate Action Incentive - Tax Credits Guide",
            max_chunk_size=300_000
        )

        elapsed = time.time() - start

        print(f"\n✅ Analysis completed in {elapsed:.1f}s")
        print(f"\nClassification:")
        print(f"  Primary: {analysis.classification.primary_category}")
        print(f"  Confidence: {analysis.classification.confidence:.2f}")
        print(f"  Reasoning: {analysis.classification.reasoning}")

        print(f"\nChunks ({len(analysis.chunks)}):")
        for chunk in analysis.chunks:
            print(f"  {chunk.chunk_id}. {chunk.title}")
            print(f"     Range: {chunk.start_pos:,}-{chunk.end_pos:,} ({chunk.length:,} chars)")
            print(f"     Topic: {chunk.primary_topic}")
            print(f"     Coherence: {chunk.semantic_coherence:.2f}")

        return analysis

    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return None


if __name__ == "__main__":
    # Run test if executed directly
    test_gemini_smart_processor()
