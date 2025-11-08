"""
GLM Claude Processor

Uses GLM-4.6 through Claude Code CLI to perform intelligent document analysis:
- Semantic classification (vs keyword matching)
- TOC identification and generation with Chinese language optimization
- Local processing with no API dependencies

This provides an alternative to Gemini API with better Chinese language support
and local processing capabilities.
"""

import logging
import re
import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
from pydantic import BaseModel, Field

from .content_classifier import TaxCategory, QualityMetrics
from .llm_cli_providers import get_provider

logger = logging.getLogger(__name__)

# Map GLM categories to our TaxCategory
GLM_CATEGORY_MAP = {
    "TAX_RETURN": TaxCategory.FILING_PROCEDURES,
    "TAX_GUIDE": TaxCategory.GENERAL,
    "INCOME_STATEMENT": TaxCategory.BUSINESS_INCOME,
    "BALANCE_SHEET": TaxCategory.BUSINESS_INCOME,
    "CASH_FLOW": TaxCategory.BUSINESS_INCOME,
    "TAX_NOTICE": TaxCategory.ASSESSMENTS,
    "TAX_RECEIPT": TaxCategory.PAYMENTS,
    "INVOICE": TaxCategory.BUSINESS_EXPENSES,
    "CONTRACT": TaxCategory.GENERAL,
    "BANK_STATEMENT": TaxCategory.BUSINESS_INCOME,
    "APPRAISAL_REPORT": TaxCategory.CAPITAL_GAINS,
    "UNKNOWN": TaxCategory.UNKNOWN
}

def map_glm_category_to_tax_category(glm_category: str) -> TaxCategory:
    """Map GLM category to TaxCategory enum."""
    return GLM_CATEGORY_MAP.get(glm_category, TaxCategory.UNKNOWN)


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
    """Classification result from GLM semantic analysis."""

    primary_category: TaxCategory = Field(..., description="Primary tax category")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Classification confidence")
    secondary_categories: List[TaxCategory] = Field(default_factory=list,
                                                      description="Secondary categories")
    reasoning: str = Field(..., description="Explanation for the classification")
    method: str = Field(default="glm_semantic", description="Classification method used")

    # Quality metrics (can be optionally filled by LLM or computed)
    quality_metrics: Optional[QualityMetrics] = None


class DocumentAnalysis(BaseModel):
    """Complete document analysis result from GLM."""

    classification: SmartClassification
    toc: DocumentTOC
    total_chars: int
    processing_time: float
    model: str = "glm-4.6"


@dataclass
class DocumentChunk:
    """Represents a document chunk for processing."""
    chunk_id: int
    content: str
    char_start: int
    char_end: int
    title: str
    context_before: str = ""
    context_after: str = ""
    toc_entries: List[TOCEntry] = field(default_factory=list)
    estimated_pages: int = 0

    @property
    def size(self) -> int:
        """Get chunk size in characters."""
        return len(self.content)


@dataclass
class ChunkAnalysis:
    """Analysis result for a single document chunk."""
    chunk_id: int
    classification: SmartClassification
    toc_entries: List[TOCEntry]
    confidence: float
    processing_time: float
    chunk_summary: str

    @property
    def is_high_quality(self) -> bool:
        """Check if this chunk analysis meets quality threshold."""
        return self.confidence >= 0.7 and len(self.toc_entries) > 0


class DocumentSplitter:
    """
    Splits large documents into GLM-4.6 compatible chunks (400K chars max)
    while preserving document structure and context.
    """

    def __init__(self, max_chunk_size: int = 400_000, overlap_size: int = 2000):
        self.max_chunk_size = max_chunk_size
        self.overlap_size = overlap_size

    def split_document(self, content: str, toc_entries: List[TOCEntry] = None) -> List[DocumentChunk]:
        """
        Split document using TOC-based approach when available,
        fall back to intelligent content-based splitting.

        Args:
            content: Full document content
            toc_entries: Optional list of TOC entries for structure-aware splitting

        Returns:
            List of DocumentChunk objects
        """
        if not content or not content.strip():
            return []

        content_length = len(content)

        # If content fits in one chunk, return single chunk
        if content_length <= self.max_chunk_size:
            return [DocumentChunk(
                chunk_id=1,
                content=content,
                char_start=0,
                char_end=content_length,
                title="Full Document",
                toc_entries=toc_entries or [],
                estimated_pages=self._estimate_pages(content)
            )]

        # Try TOC-aware splitting first
        if toc_entries:
            try:
                chunks = self._split_by_toc_boundaries(content, toc_entries)
                if chunks:
                    logger.info(f"Split document into {len(chunks)} chunks using TOC boundaries")
                    return chunks
            except Exception as e:
                logger.warning(f"TOC-based splitting failed, falling back to content structure: {e}")

        # Fall back to content structure splitting
        chunks = self._split_by_content_structure(content)
        logger.info(f"Split document into {len(chunks)} chunks using content structure")
        return chunks

    def _split_by_toc_boundaries(self, content: str, toc_entries: List[TOCEntry]) -> List[DocumentChunk]:
        """
        Use TOC entries to find natural split points at 400K boundaries.
        Preserves chapter/section integrity.

        Args:
            content: Full document content
            toc_entries: Sorted list of TOC entries

        Returns:
            List of DocumentChunk objects
        """
        # Sort TOC entries by character position
        sorted_toc = sorted([entry for entry in toc_entries if entry.char_start is not None],
                          key=lambda x: x.char_start)

        if not sorted_toc:
            return []

        chunks = []
        current_pos = 0
        chunk_id = 1

        while current_pos < len(content):
            # Find ideal split point (400K chars from current_pos)
            target_end = min(current_pos + self.max_chunk_size, len(content))

            # Look for TOC entry near target_end (within 50K chars)
            best_split_pos = self._find_optimal_split_position(
                sorted_toc, current_pos, target_end
            )

            # Create chunk with overlap, but ensure content doesn't exceed max_chunk_size
            actual_start = max(0, current_pos - self.overlap_size)
            actual_end = min(len(content), best_split_pos + self.overlap_size)

            # Adjust if chunk is too large
            chunk_content_size = actual_end - actual_start
            if chunk_content_size > self.max_chunk_size:
                # Reduce overlap to fit within limit
                excess = chunk_content_size - self.max_chunk_size
                actual_start = max(0, actual_start + excess // 2)
                actual_end = min(len(content), actual_end - excess // 2)

            chunk_content = content[actual_start:actual_end]

            # Extract relevant TOC entries for this chunk
            chunk_toc_entries = self._extract_relevant_toc_entries(
                sorted_toc, current_pos, best_split_pos
            )

            # Generate chunk title
            chunk_title = self._generate_chunk_title(
                chunk_id, sorted_toc, current_pos, best_split_pos
            )

            chunk = DocumentChunk(
                chunk_id=chunk_id,
                content=chunk_content,
                char_start=current_pos,
                char_end=best_split_pos,
                title=chunk_title,
                context_before=content[actual_start:current_pos],
                context_after=content[best_split_pos:actual_end],
                toc_entries=chunk_toc_entries,
                estimated_pages=self._estimate_pages(chunk_content)
            )

            chunks.append(chunk)
            current_pos = best_split_pos
            chunk_id += 1

        return chunks

    def _split_by_content_structure(self, content: str) -> List[DocumentChunk]:
        """
        Fallback strategy when no TOC is available:
        1. Look for page breaks "=== Page N ==="
        2. Identify chapter patterns
        3. Use paragraph boundaries as last resort
        4. Ensure no chunk exceeds 400K limit

        Args:
            content: Full document content

        Returns:
            List of DocumentChunk objects
        """
        chunks = []
        current_pos = 0
        chunk_id = 1

        while current_pos < len(content):
            target_end = min(current_pos + self.max_chunk_size, len(content))

            if target_end >= len(content):
                # Final chunk
                actual_start = max(0, current_pos - self.overlap_size)
                chunk_content = content[actual_start:]

                chunk = DocumentChunk(
                    chunk_id=chunk_id,
                    content=chunk_content,
                    char_start=current_pos,
                    char_end=len(content),
                    title=f"Section {chunk_id} (End)",
                    context_before=content[actual_start:current_pos],
                    estimated_pages=self._estimate_pages(chunk_content)
                )
                chunks.append(chunk)
                break

            # Try to find natural split points
            split_pos = self._find_natural_split_position(content, current_pos, target_end)

            # Create chunk with overlap, but ensure content doesn't exceed max_chunk_size
            actual_start = max(0, current_pos - self.overlap_size)
            actual_end = min(len(content), split_pos + self.overlap_size)

            # Adjust if chunk is too large
            chunk_content_size = actual_end - actual_start
            if chunk_content_size > self.max_chunk_size:
                # Reduce overlap to fit within limit
                excess = chunk_content_size - self.max_chunk_size
                actual_start = max(0, actual_start + excess // 2)
                actual_end = min(len(content), actual_end - excess // 2)

            chunk_content = content[actual_start:actual_end]

            chunk = DocumentChunk(
                chunk_id=chunk_id,
                content=chunk_content,
                char_start=current_pos,
                char_end=split_pos,
                title=f"Section {chunk_id}",
                context_before=content[actual_start:current_pos],
                context_after=content[split_pos:actual_end],
                estimated_pages=self._estimate_pages(chunk_content)
            )

            chunks.append(chunk)
            current_pos = split_pos
            chunk_id += 1

        return chunks

    def _find_optimal_split_position(self, toc_entries: List[TOCEntry],
                                   current_pos: int, target_end: int) -> int:
        """
        Find the best split position near target_end based on TOC entries.

        Args:
            toc_entries: Sorted TOC entries
            current_pos: Current starting position
            target_end: Target ending position

        Returns:
            Optimal split position
        """
        # Look for TOC entries within reasonable range of target_end
        search_range = 50000  # 50K characters

        best_split = target_end
        best_distance = float('inf')

        for entry in toc_entries:
            if entry.char_start < current_pos:
                continue

            distance = abs(entry.char_start - target_end)
            if distance < best_distance and distance <= search_range:
                best_split = entry.char_start
                best_distance = distance

        # If no good TOC entry found, use target_end
        return best_split

    def _find_natural_split_position(self, content: str, current_pos: int, target_end: int) -> int:
        """
        Find natural split position in content when no TOC is available.

        Args:
            content: Full document content
            current_pos: Current starting position
            target_end: Target ending position

        Returns:
            Natural split position
        """
        # Search backward from target_end for natural break points
        search_start = max(current_pos, target_end - 20000)  # Search 20K back

        # Priority order for split points
        split_patterns = [
            r'\n=== Page \d+ ===\n',  # Page breaks
            r'\n#{1,6}\s+',           # Markdown headers
            r'\n\d+\.\s+',            # Numbered sections
            r'\n[A-Z][A-Z\s]{10,}\n', # All-caps headers
            r'\n\n\s*\n',             # Double newlines (paragraph breaks)
            r'\.\s+',                 # Sentence endings
        ]

        for pattern in split_patterns:
            matches = list(re.finditer(pattern, content[search_start:target_end]))
            if matches:
                # Use the last match (closest to target_end)
                last_match = matches[-1]
                return search_start + last_match.start()

        # Fallback: split at target_end
        return target_end

    def _extract_relevant_toc_entries(self, toc_entries: List[TOCEntry],
                                    start_pos: int, end_pos: int) -> List[TOCEntry]:
        """
        Extract TOC entries that are relevant to this chunk.

        Args:
            toc_entries: Sorted TOC entries
            start_pos: Chunk start position
            end_pos: Chunk end position

        Returns:
            List of relevant TOC entries
        """
        relevant_entries = []

        for entry in toc_entries:
            if entry.char_start is None:
                continue

            # Include entries that start within this chunk
            if start_pos <= entry.char_start < end_pos:
                relevant_entries.append(entry)
            # Also include entries that start just before (for context)
            elif start_pos - 1000 <= entry.char_start < start_pos:
                relevant_entries.append(entry)

        return relevant_entries

    def _generate_chunk_title(self, chunk_id: int, toc_entries: List[TOCEntry],
                            start_pos: int, end_pos: int) -> str:
        """
        Generate a descriptive title for the chunk based on TOC entries.

        Args:
            chunk_id: Chunk identifier
            toc_entries: Available TOC entries
            start_pos: Chunk start position
            end_pos: Chunk end position

        Returns:
            Chunk title
        """
        # Find the first TOC entry within this chunk
        for entry in toc_entries:
            if entry.char_start and start_pos <= entry.char_start < end_pos:
                return f"Chunk {chunk_id}: {entry.title}"

        # Fallback titles
        if chunk_id == 1:
            return f"Chunk {chunk_id}: Beginning"
        else:
            return f"Chunk {chunk_id}: Section"

    def _estimate_pages(self, content: str) -> int:
        """
        Estimate number of pages in content based on page markers.

        Args:
            content: Content to analyze

        Returns:
            Estimated page count
        """
        # Look for page markers
        page_matches = re.findall(r'=== Page (\d+) ===', content)
        if page_matches:
            return max(int(page) for page in page_matches)

        # Rough estimate: 2500 characters per page
        return max(1, len(content) // 2500)


class GLMClaudeProcessor:
    """
    Intelligent document processor using GLM-4.6 through Claude Code.

    Capabilities:
    - 400K character context window (optimized for Chinese documents)
    - Semantic understanding with Chinese language optimization
    - Local processing (no API calls or costs)
    - Unified analysis (classification + TOC in one pass)
    """

    # Maximum input size supported by GLM-4.6
    MAX_INPUT_SIZE = 400_000  # 400K chars (~100K tokens)

    # Chunk size limits
    # For GLM-4.6: optimized for Chinese content processing
    DEFAULT_MAX_CHUNK_SIZE = 400_000  # 400K chars (full GLM context)

    def __init__(self, provider_name: str = 'glm-claude'):
        """
        Initialize the GLM Claude processor.

        Args:
            provider_name: Name of the LLM provider (default: 'glm-claude')
        """
        self.provider = get_provider(provider_name)

        if not self.provider.is_available():
            raise RuntimeError(
                f"GLM Claude Code is not available. Please ensure:\n"
                f"  1. ccc command is available in PATH\n"
                f"  2. GLM-4.6 model is properly configured\n"
                f"  3. Claude Code CLI is installed: npm install -g @anthropic-ai/claude-code"
            )

        logger.info(f"Initialized GLMClaudeProcessor with provider: {provider_name}")

    def analyze_full_document(
        self,
        content: str,
        title: str = "",
        max_chunk_size: Optional[int] = None
    ) -> DocumentAnalysis:
        """
        Analyze the full document in one pass using GLM's Chinese-optimized capabilities.

        This is the main entry point that performs:
        1. Document classification (tax category)
        2. TOC identification or generation (document structure)

        Args:
            content: Full document text
            title: Document title (optional, helps with classification)
            max_chunk_size: Maximum chunk size in characters (default: 400K)

        Returns:
            DocumentAnalysis: Complete analysis including classification and TOC

        Raises:
            ValueError: If content is too large or empty
            RuntimeError: If GLM processing fails
        """
        # Validate input
        if not content or not content.strip():
            raise ValueError("Content cannot be empty or whitespace-only")

        content_length = len(content)
        max_chunk_size = max_chunk_size or self.DEFAULT_MAX_CHUNK_SIZE

        logger.info(f"Analyzing document with GLM: {content_length} chars, max_chunk={max_chunk_size}")

        # Check if chunking is needed
        if content_length > max_chunk_size:
            logger.info(f"Document too large for single chunk, using chunked processing")
            return self.analyze_large_document(content, title, max_chunk_size)

        # Single chunk processing (existing logic)
        start_time = time.time()

        try:
            # Build the analysis prompt optimized for GLM-4.6
            prompt = self._build_analysis_prompt(content, title)

            # Call GLM through Claude Code
            result_text = self._call_glm(prompt)

            # Parse the result
            analysis = self._parse_result(result_text, content_length, time.time() - start_time)

            logger.info(
                f"GLM analysis completed: {analysis.classification.primary_category.value}, "
                f"confidence {analysis.classification.confidence:.2f}, "
                f"TOC entries: {analysis.toc.total_entries}, "
                f"processing time: {analysis.processing_time:.2f}s"
            )

            return analysis

        except Exception as e:
            logger.error(f"GLM processing failed: {str(e)}")
            raise RuntimeError(f"GLM processing failed: {str(e)}") from e

    def analyze_large_document(
        self,
        content: str,
        title: str = "",
        max_chunk_size: Optional[int] = None
    ) -> DocumentAnalysis:
        """
        Analyze documents larger than 400K chars through intelligent chunking.

        Strategy:
        1. Split document into 400K chunks with overlap
        2. Process each chunk with GLM-4.6
        3. Merge results with conflict resolution
        4. Generate unified TOC and classification

        Args:
            content: Full document text
            title: Document title
            max_chunk_size: Maximum chunk size for processing

        Returns:
            DocumentAnalysis: Unified analysis from all chunks
        """
        import time

        start_time = time.time()
        max_chunk_size = max_chunk_size or self.DEFAULT_MAX_CHUNK_SIZE

        logger.info(f"Starting chunked analysis for {len(content)} chars document")

        # Initialize document splitter
        splitter = DocumentSplitter(max_chunk_size=max_chunk_size)

        # For initial implementation, we don't have TOC yet, so use content structure
        # In future versions, we could do a quick first pass to identify structure
        chunks = splitter.split_document(content)

        if not chunks:
            raise ValueError("Failed to split document into chunks")

        logger.info(f"Split document into {len(chunks)} chunks")

        # Process each chunk
        chunk_analyses = []
        self.total_chunks = len(chunks)

        for i, chunk in enumerate(chunks, 1):
            logger.info(f"Processing chunk {i}/{len(chunks)}: {chunk.title} ({chunk.size} chars)")

            try:
                chunk_analysis = self._process_chunk(chunk, title, i)
                chunk_analyses.append(chunk_analysis)

                logger.info(
                    f"Chunk {i} completed: {chunk_analysis.classification.primary_category.value}, "
                    f"confidence {chunk_analysis.confidence:.2f}, "
                    f"TOC entries: {len(chunk_analysis.toc_entries)}"
                )

            except Exception as e:
                logger.error(f"Failed to process chunk {i}: {str(e)}")
                # Create fallback analysis for this chunk
                fallback_analysis = ChunkAnalysis(
                    chunk_id=i,
                    classification=SmartClassification(
                        primary_category=TaxCategory.UNKNOWN,
                        confidence=0.1,
                        secondary_categories=[],
                        reasoning=f"Chunk processing failed: {str(e)}",
                        method="glm_fallback"
                    ),
                    toc_entries=[],
                    confidence=0.1,
                    processing_time=0,
                    chunk_summary=f"Failed to process chunk {i}"
                )
                chunk_analyses.append(fallback_analysis)

        # Merge all chunk analyses
        logger.info("Merging chunk analyses into unified result")
        merged_analysis = self._merge_chunk_analyses(chunk_analyses, content_length=len(content))

        total_processing_time = time.time() - start_time
        merged_analysis.processing_time = total_processing_time

        logger.info(
            f"Chunked analysis completed: {merged_analysis.classification.primary_category.value}, "
            f"confidence {merged_analysis.classification.confidence:.2f}, "
            f"TOC entries: {merged_analysis.toc.total_entries}, "
            f"total time: {total_processing_time:.2f}s"
        )

        return merged_analysis

    def _process_chunk(self, chunk: DocumentChunk, overall_title: str, chunk_id: int) -> ChunkAnalysis:
        """
        Process individual chunk with context.

        Args:
            chunk: Document chunk to process
            overall_title: Overall document title
            chunk_id: Chunk identifier

        Returns:
            ChunkAnalysis: Analysis result for this chunk
        """
        import time

        start_time = time.time()

        # Build chunk-specific prompt with context
        prompt = self._build_chunk_prompt(chunk, overall_title, chunk_id)

        # Call GLM through Claude Code
        result_text = self._call_glm(prompt)

        # Parse chunk result
        chunk_analysis = self._parse_chunk_result(result_text, chunk, time.time() - start_time)

        return chunk_analysis

    def _build_chunk_prompt(
        self,
        chunk: DocumentChunk,
        overall_title: str,
        chunk_id: int
    ) -> str:
        """
        Build prompt for chunk analysis including context.

        Args:
            chunk: Document chunk to analyze
            overall_title: Overall document title
            chunk_id: Chunk identifier

        Returns:
            Complete prompt for chunk analysis
        """
        # Truncate content if necessary
        max_content = self.provider.get_max_chunk_size() - 6000  # Leave room for context
        truncated_content = chunk.content[:max_content]

        if len(chunk.content) > max_content:
            truncated_content += "\n\n[Content truncated due to length limit]"

        context_info = ""
        if chunk.context_before:
            context_info += f"PREVIOUS CHUNK END: {chunk.context_before[-500:]}...\n\n"
        if chunk.context_after:
            context_info += f"NEXT CHUNK START: ...{chunk.context_after[:500:]}\n\n"

        prompt = f"""You are a professional document analysis assistant, processing section {chunk_id} of a large document (total {self.total_chunks} sections).

Overall document title: {overall_title if overall_title else "Unknown"}
Current section title: {chunk.title}
Current section range: characters {chunk.char_start:,} - {chunk.char_end:,}

{context_info}
Current section content:
{truncated_content}

Please return analysis results for this section in the following JSON format:

{{
  "classification": {{
    "primary_category": "DOCUMENT_TYPE",
    "confidence": 0.95,
    "secondary_categories": ["SECONDARY_TYPE"],
    "reasoning": "Explanation for this document section classification",
    "method": "glm_chunked"
  }},
  "toc_entries": [
    {{
      "level": 1,
      "title": "Chapter/section title",
      "page_number": 1,
      "char_start": Character position relative to entire document,
      "char_end": Character position relative to entire document
    }}
  ],
  "chunk_summary": "Brief summary of this section content",
  "confidence": 0.95
}}

Classification options (primary_category, secondary_categories):
- personal_income: Personal Income Tax documents
- employment_income: Employment income and T4 slips
- self_employment: Self-employment and business income
- business_income: Business/corporate income tax
- business_expenses: Business expense deductions
- corporate_tax: Corporate tax filings and T2 returns
- capital_gains: Capital gains and investment income
- dividends: Dividend income and tax credits
- deductions: Tax deductions and write-offs
- credits: Tax credits and refunds
- gst_hst: GST/HST and sales tax
- filing_procedures: Tax filing procedures and forms
- payments: Tax payments and installments
- assessments: Tax assessments and reassessments
- unknown: Other / unknown document type

TOC Analysis Requirements:
1. Identify document structure of current section
2. Extract chapter titles and hierarchy levels
3. Estimate character positions (relative to entire document, using current section's starting position as baseline)
4. Maintain consistency with overall document structure

Important Notes:
- This is section {chunk_id} of a large document, ensure analysis results are consistent with overall document structure
- TOC character positions should be absolute positions relative to the entire document
- If current section content is incomplete, mention this in the reasoning

Please carefully analyze the current section and return valid JSON format."""

        return prompt

    def _parse_chunk_result(self, result_text: str, chunk: DocumentChunk, processing_time: float) -> ChunkAnalysis:
        """
        Parse GLM response for chunk analysis.

        Args:
            result_text: GLM response text
            chunk: Original chunk for context
            processing_time: Processing time for this chunk

        Returns:
            ChunkAnalysis: Parsed analysis result
        """
        import json

        try:
            # Extract JSON from response
            json_match = re.search(r'\{[\s\S]*\}', result_text)
            if not json_match:
                raise ValueError("No JSON found in GLM chunk response")

            json_str = json_match.group()
            data = json.loads(json_str)

            # Parse classification
            classification_data = data['classification']

            # Map GLM categories to our TaxCategory
            primary_cat = map_glm_category_to_tax_category(classification_data['primary_category'])
            secondary_cats = [map_glm_category_to_tax_category(cat) for cat in classification_data.get('secondary_categories', [])]

            classification = SmartClassification(
                primary_category=primary_cat,
                confidence=float(classification_data['confidence']),
                secondary_categories=secondary_cats,
                reasoning=classification_data['reasoning'],
                method=classification_data.get('method', 'glm_chunked')
            )

            # Parse TOC entries
            toc_entries = []
            for entry_data in data.get('toc_entries', []):
                # Adjust character positions to be relative to original document
                char_start = entry_data.get('char_start', chunk.char_start)
                char_end = entry_data.get('char_end', chunk.char_end)

                # If positions are relative to chunk, adjust them
                if char_start < chunk.char_start:
                    char_start += chunk.char_start
                if char_end < chunk.char_end:
                    char_end += chunk.char_start

                entry = TOCEntry(
                    level=entry_data['level'],
                    title=entry_data['title'],
                    page_number=entry_data['page_number'],
                    char_start=char_start,
                    char_end=char_end
                )
                toc_entries.append(entry)

            return ChunkAnalysis(
                chunk_id=chunk.chunk_id,
                classification=classification,
                toc_entries=toc_entries,
                confidence=float(data.get('confidence', classification.confidence)),
                processing_time=processing_time,
                chunk_summary=data.get('chunk_summary', f'Processed {chunk.title}')
            )

        except (json.JSONDecodeError, KeyError, ValueError) as e:
            logger.error(f"Failed to parse GLM chunk response: {str(e)}")
            logger.error(f"Response text: {result_text[:500]}...")

            # Create fallback analysis
            fallback_classification = SmartClassification(
                primary_category=TaxCategory.UNKNOWN,
                confidence=0.1,
                secondary_categories=[],
                reasoning=f"GLM chunk response parsing failed: {str(e)}",
                method="glm_fallback"
            )

            return ChunkAnalysis(
                chunk_id=chunk.chunk_id,
                classification=fallback_classification,
                toc_entries=[],
                confidence=0.1,
                processing_time=processing_time,
                chunk_summary=f"Failed to parse GLM response for {chunk.title}"
            )

    def _merge_chunk_analyses(self, chunk_analyses: List[ChunkAnalysis], content_length: int) -> DocumentAnalysis:
        """
        Merge multiple chunk analyses into unified result.

        Args:
            chunk_analyses: List of chunk analysis results
            content_length: Total document content length

        Returns:
            DocumentAnalysis: Unified analysis result
        """
        if not chunk_analyses:
            raise ValueError("No chunk analyses to merge")

        # Merge classifications using weighted confidence
        merged_classification = self._merge_classifications(chunk_analyses)

        # Merge TOC entries
        merged_toc = self._merge_toc_entries(chunk_analyses, content_length)

        return DocumentAnalysis(
            classification=merged_classification,
            toc=merged_toc,
            total_chars=content_length,
            processing_time=sum(ca.processing_time for ca in chunk_analyses),
            model="glm-4.6-chunked"
        )

    def _merge_classifications(self, chunk_analyses: List[ChunkAnalysis]) -> SmartClassification:
        """
        Merge classifications from multiple chunks.

        Args:
            chunk_analyses: List of chunk analyses

        Returns:
            SmartClassification: Merged classification
        """
        if not chunk_analyses:
            return SmartClassification(
                primary_category=TaxCategory.UNKNOWN,
                confidence=0.0,
                secondary_categories=[],
                reasoning="No chunk analyses available",
                method="glm_merged"
            )

        # Weight by confidence and processing quality
        weighted_votes = {}
        total_weight = 0

        for analysis in chunk_analyses:
            weight = analysis.confidence * (1.5 if analysis.is_high_quality else 1.0)
            category = analysis.classification.primary_category

            weighted_votes[category] = weighted_votes.get(category, 0) + weight
            total_weight += weight

        if total_weight == 0:
            # Fallback to majority vote
            category_counts = {}
            for analysis in chunk_analyses:
                category = analysis.classification.primary_category
                category_counts[category] = category_counts.get(category, 0) + 1

            primary_category = max(category_counts, key=category_counts.get)
            confidence = category_counts[primary_category] / len(chunk_analyses)
        else:
            primary_category = max(weighted_votes, key=weighted_votes.get)
            confidence = weighted_votes[primary_category] / total_weight

        # Collect secondary categories
        secondary_categories = set()
        for analysis in chunk_analyses:
            for cat in analysis.classification.secondary_categories:
                if cat != primary_category:
                    secondary_categories.add(cat)

        # Build reasoning
        high_quality_analyses = [ca for ca in chunk_analyses if ca.is_high_quality]
        if high_quality_analyses:
            reasoning = f"Merged from {len(chunk_analyses)} chunks ({len(high_quality_analyses)} high quality). Primary category: {primary_category.value} (confidence: {confidence:.2f})"
        else:
            reasoning = f"Merged from {len(chunk_analyses)} chunks (low quality). Primary category: {primary_category.value} (confidence: {confidence:.2f})"

        return SmartClassification(
            primary_category=primary_category,
            confidence=min(confidence, 1.0),
            secondary_categories=list(secondary_categories),
            reasoning=reasoning,
            method="glm_merged"
        )

    def _merge_toc_entries(self, chunk_analyses: List[ChunkAnalysis], content_length: int) -> DocumentTOC:
        """
        Merge TOC entries from multiple chunks.

        Args:
            chunk_analyses: List of chunk analyses
            content_length: Total document content length

        Returns:
            DocumentTOC: Merged TOC structure
        """
        all_entries = []
        has_any_toc = False

        # Collect all TOC entries
        for analysis in chunk_analyses:
            if analysis.toc_entries:
                has_any_toc = True
                all_entries.extend(analysis.toc_entries)

        if not all_entries:
            return DocumentTOC(
                has_toc=False,
                source="generated",
                entries=[],
                max_level=1
            )

        # Sort by character position
        all_entries.sort(key=lambda x: (x.char_start or 0, x.level))

        # Remove duplicates and overlaps
        filtered_entries = self._filter_toc_entries(all_entries)

        # Determine max level
        max_level = max(entry.level for entry in filtered_entries) if filtered_entries else 1

        return DocumentTOC(
            has_toc=has_any_toc,
            source="merged_chunks",
            entries=filtered_entries,
            max_level=max_level
        )

    def _filter_toc_entries(self, entries: List[TOCEntry]) -> List[TOCEntry]:
        """
        Filter and deduplicate TOC entries.

        Args:
            entries: List of TOC entries from all chunks

        Returns:
            List[TOCEntry]: Filtered and deduplicated entries
        """
        if not entries:
            return []

        filtered = []
        seen_titles = set()

        for entry in entries:
            # Normalize title for comparison
            normalized_title = entry.title.strip().lower()

            # Skip duplicates
            if normalized_title in seen_titles:
                continue

            # Skip entries without proper positions
            if entry.char_start is None or entry.char_start < 0:
                continue

            seen_titles.add(normalized_title)
            filtered.append(entry)

        return filtered

    def _build_analysis_prompt(self, content: str, title: str) -> str:
        """
        Build analysis prompt optimized for GLM-4.6 Chinese processing.

        Args:
            content: Document content to analyze
            title: Document title

        Returns:
            Complete prompt for GLM analysis
        """
        # Truncate content if necessary
        max_content = self.provider.get_max_chunk_size() - 4000  # Leave room for prompt template
        truncated_content = content[:max_content]

        if len(content) > max_content:
            truncated_content += "\n\n[Content truncated due to length limit]"

        prompt = f"""You are a professional document analysis assistant, specializing in Canadian tax document analysis. Please perform comprehensive analysis of the following document:

Document title: {title if title else "Unknown"}

Document content:
{truncated_content}

Please return analysis results in the following JSON format:

{{
  "classification": {{
    "primary_category": "DOCUMENT_TYPE",
    "confidence": 0.95,
    "secondary_categories": ["SECONDARY_TYPE"],
    "reasoning": "Detailed explanation for classification reasoning",
    "method": "glm_semantic"
  }},
  "toc": {{
    "has_toc": true/false,
    "source": "document_page/generated/embedded",
    "entries": [
      {{
        "level": 1,
        "title": "Chapter/section title",
        "page_number": 1,
        "char_start": 0,
        "char_end": 1000
      }}
    ],
    "max_level": 3
  }}
}}

Classification options (primary_category, secondary_categories):
- personal_income: Personal Income Tax documents
- employment_income: Employment income and T4 slips
- self_employment: Self-employment and business income
- business_income: Business/corporate income tax
- business_expenses: Business expense deductions
- corporate_tax: Corporate tax filings and T2 returns
- capital_gains: Capital gains and investment income
- dividends: Dividend income and tax credits
- deductions: Tax deductions and write-offs
- credits: Tax credits and refunds
- gst_hst: GST/HST and sales tax
- filing_procedures: Tax filing procedures and forms
- payments: Tax payments and installments
- assessments: Tax assessments and reassessments
- unknown: Other / unknown document type

TOC Analysis Requirements:
1. First, search for existing document structure
2. If no clear structure, generate hierarchical outline based on logical document structure
3. Estimate starting character positions for each section
4. Support multi-level headings (maximum 3 levels)

Please carefully analyze the document content, ensure accurate classification and reasonable TOC structure. Return valid JSON format."""

        return prompt

    def _call_glm(self, prompt: str) -> str:
        """
        Call GLM through Claude Code CLI.

        Args:
            prompt: Analysis prompt

        Returns:
            GLM response text
        """
        import subprocess
        import tempfile

        try:
            # Create temporary file for prompt
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
                f.write(prompt)
                prompt_file = f.name

            # Build command
            cmd = self.provider.build_command(prompt)

            logger.info(f"Calling GLM through Claude Code: {' '.join(cmd)}")

            # Execute with timeout
            timeout = self.provider.get_timeout(len(prompt))
            result = subprocess.run(
                cmd,
                input=prompt,
                text=True,
                capture_output=True,
                timeout=timeout,
                encoding='utf-8'
            )

            # Parse output
            response = self.provider.parse_output(result.stdout, result.stderr)

            logger.info(f"GLM response received: {len(response)} chars")
            return response

        except subprocess.TimeoutExpired:
            raise RuntimeError(f"GLM processing timed out after {timeout} seconds")
        except Exception as e:
            raise RuntimeError(f"GLM CLI execution failed: {str(e)}")
        finally:
            # Cleanup temporary file
            try:
                import os
                os.unlink(prompt_file)
            except:
                pass

    def _parse_result(self, result_text: str, content_length: int, processing_time: float) -> DocumentAnalysis:
        """
        Parse GLM response into DocumentAnalysis.

        Args:
            result_text: GLM response text
            content_length: Original content length
            processing_time: Processing time in seconds

        Returns:
            Parsed DocumentAnalysis object
        """
        import json

        try:
            # Extract JSON from response
            json_match = re.search(r'\{[\s\S]*\}', result_text)
            if not json_match:
                raise ValueError("No JSON found in GLM response")

            json_str = json_match.group()
            data = json.loads(json_str)

            # Parse classification
            classification_data = data['classification']

            # Map GLM categories to our TaxCategory
            primary_cat = map_glm_category_to_tax_category(classification_data['primary_category'])
            secondary_cats = [map_glm_category_to_tax_category(cat) for cat in classification_data.get('secondary_categories', [])]

            classification = SmartClassification(
                primary_category=primary_cat,
                confidence=float(classification_data['confidence']),
                secondary_categories=secondary_cats,
                reasoning=classification_data['reasoning'],
                method=classification_data.get('method', 'glm_semantic')
            )

            # Parse TOC
            toc_data = data['toc']
            toc_entries = []
            for entry_data in toc_data.get('entries', []):
                entry = TOCEntry(
                    level=entry_data['level'],
                    title=entry_data['title'],
                    page_number=entry_data['page_number'],
                    char_start=entry_data.get('char_start'),
                    char_end=entry_data.get('char_end')
                )
                toc_entries.append(entry)

            toc = DocumentTOC(
                has_toc=toc_data['has_toc'],
                source=toc_data['source'],
                entries=toc_entries,
                max_level=toc_data.get('max_level', 1)
            )

            return DocumentAnalysis(
                classification=classification,
                toc=toc,
                total_chars=content_length,
                processing_time=processing_time,
                model="glm-4.6"
            )

        except (json.JSONDecodeError, KeyError, ValueError) as e:
            logger.error(f"Failed to parse GLM response: {str(e)}")
            logger.error(f"Response text: {result_text[:500]}...")

            # Create fallback analysis
            fallback_classification = SmartClassification(
                primary_category=TaxCategory.UNKNOWN,
                confidence=0.1,
                secondary_categories=[],
                reasoning=f"GLM response parsing failed: {str(e)}",
                method="glm_fallback"
            )

            fallback_toc = DocumentTOC(
                has_toc=False,
                source="generated",
                entries=[],
                max_level=1
            )

            return DocumentAnalysis(
                classification=fallback_classification,
                toc=fallback_toc,
                total_chars=content_length,
                processing_time=processing_time,
                model="glm-4.6"
            )