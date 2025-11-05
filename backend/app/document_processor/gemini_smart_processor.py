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


class ChunkBoundary(BaseModel):
    """Represents a semantic chunk boundary identified by Gemini."""

    chunk_id: int = Field(..., description="Sequential chunk identifier (1-indexed)")
    title: str = Field(..., description="Descriptive title for this chunk")
    start_pos: int = Field(..., ge=0, description="Start character position (inclusive)")
    end_pos: int = Field(..., gt=0, description="End character position (exclusive)")
    primary_topic: str = Field(..., description="Main topic/theme of this chunk")
    semantic_coherence: float = Field(default=0.85, ge=0.0, le=1.0,
                                       description="Estimated semantic coherence score")

    @property
    def length(self) -> int:
        """Calculate chunk length in characters."""
        return self.end_pos - self.start_pos


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
    chunks: List[ChunkBoundary]
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
    DEFAULT_MAX_CHUNK_SIZE = 300_000  # 300K chars for Claude compatibility

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
        1. Semantic classification
        2. Topic identification
        3. Intelligent chunking

        Args:
            content: Full document text
            title: Document title (optional, helps with classification)
            max_chunk_size: Maximum chunk size in characters (default: 300K)

        Returns:
            DocumentAnalysis: Complete analysis including classification and chunks

        Raises:
            ValueError: If content is too large or empty
            RuntimeError: If Gemini API call fails
        """
        import time

        # Validate input
        content_length = len(content)
        if content_length == 0:
            raise ValueError("Content cannot be empty")

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
                       f"{len(analysis.chunks)} chunks")
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

        # Build the prompt
        prompt = f"""You are analyzing a CRA (Canada Revenue Agency) tax document.

**Document Information:**
- Title: {title or "(untitled)"}
- Length: {len(content):,} characters
- Max chunk size: {max_chunk_size:,} characters

**Your Task:**

Perform a comprehensive analysis of this document and provide:

1. **Classification**: Identify the primary tax category this document belongs to
2. **Topic Analysis**: Identify major topics/sections and their boundaries
3. **Chunking Strategy**: Suggest how to split this document into semantically coherent chunks

**Available Tax Categories:**
{categories_str}

**Output Format:**

Please structure your output EXACTLY as follows:

## CLASSIFICATION

**Primary Category:** [category_name]
**Confidence:** [0.0-1.0]
**Secondary Categories:** [cat1, cat2, ...] (if any)
**Reasoning:** [Brief explanation of why this category was chosen]

## CHUNKS

For each major topic/section, provide:

### Chunk [N]: [Descriptive Title]
- **Character Range:** [start]-[end]
- **Primary Topic:** [Main theme/concept]
- **Coherence:** [0.0-1.0]
- **Summary:** [1-2 sentence summary]

**Important Guidelines:**

1. Each chunk should be semantically coherent (cover one main topic)
2. Chunks should not exceed {max_chunk_size:,} characters
3. Try to break at natural boundaries (end of sections, topics)
4. Avoid breaking in the middle of examples or important explanations
5. Provide 3-10 chunks depending on document structure
6. Character ranges must not overlap and should cover the entire document

**Document Content:**

{content}

---

Please provide your analysis following the format above."""

        return prompt

    def _call_gemini(self, prompt: str, content_length: int) -> str:
        """
        Call Gemini CLI with the analysis prompt.

        Args:
            prompt: The complete analysis prompt
            content_length: Length of content (for timeout calculation)

        Returns:
            str: Raw response from Gemini
        """
        import subprocess

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

        ## CHUNKS
        ### Chunk 1: Title
        - **Character Range:** 0-150000
        ...
        """
        # Extract classification section
        classification = self._parse_classification_section(response)

        # Extract chunks section
        chunks = self._parse_chunks_section(response, content_length)

        # Build DocumentAnalysis
        analysis = DocumentAnalysis(
            classification=classification,
            chunks=chunks,
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
            r'## CLASSIFICATION\s*\n(.*?)(?=## CHUNKS|$)',
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

    def _parse_chunks_section(self, response: str, total_chars: int) -> List[ChunkBoundary]:
        """
        Parse the CHUNKS section from Gemini's response.
        """
        # Extract the chunks section
        chunks_match = re.search(
            r'## CHUNKS\s*\n(.*?)$',
            response,
            re.DOTALL | re.IGNORECASE
        )

        if not chunks_match:
            raise ValueError("Could not find CHUNKS section in response")

        chunks_section = chunks_match.group(1)

        # Find all chunk definitions
        # Pattern: ### Chunk N: Title
        chunk_patterns = re.finditer(
            r'### Chunk (\d+):\s*([^\n]+)\s*\n(.*?)(?=### Chunk \d+:|$)',
            chunks_section,
            re.DOTALL | re.IGNORECASE
        )

        chunks = []
        for match in chunk_patterns:
            chunk_id = int(match.group(1))
            title = match.group(2).strip()
            chunk_body = match.group(3)

            # Parse character range
            range_match = re.search(
                r'\*\*Character Range:\*\*\s*(\d+)\s*-\s*(\d+)',
                chunk_body,
                re.IGNORECASE
            )
            if not range_match:
                logger.warning(f"Chunk {chunk_id}: Could not find character range, skipping")
                continue

            start_pos = int(range_match.group(1))
            end_pos = int(range_match.group(2))

            # Validate range
            if start_pos < 0 or end_pos > total_chars or start_pos >= end_pos:
                logger.warning(f"Chunk {chunk_id}: Invalid range {start_pos}-{end_pos}, adjusting")
                start_pos = max(0, start_pos)
                end_pos = min(total_chars, end_pos)
                if start_pos >= end_pos:
                    continue

            # Parse primary topic
            topic_match = re.search(
                r'\*\*Primary Topic:\*\*\s*([^\n]+)',
                chunk_body,
                re.IGNORECASE
            )
            primary_topic = topic_match.group(1).strip() if topic_match else "General"

            # Parse coherence
            coherence_match = re.search(
                r'\*\*Coherence:\*\*\s*(0?\.\d+|1\.0)',
                chunk_body,
                re.IGNORECASE
            )
            semantic_coherence = float(coherence_match.group(1)) if coherence_match else 0.85

            # Create ChunkBoundary
            chunk = ChunkBoundary(
                chunk_id=chunk_id,
                title=title,
                start_pos=start_pos,
                end_pos=end_pos,
                primary_topic=primary_topic,
                semantic_coherence=semantic_coherence
            )
            chunks.append(chunk)

        if not chunks:
            raise ValueError("No valid chunks found in response")

        # Sort by chunk_id
        chunks.sort(key=lambda c: c.chunk_id)

        # Validate coverage (chunks should cover most of the document)
        total_covered = sum(c.length for c in chunks)
        coverage = total_covered / total_chars if total_chars > 0 else 0

        if coverage < 0.8:
            logger.warning(f"Low document coverage: {coverage:.1%} ({total_covered}/{total_chars} chars)")

        logger.info(f"Parsed {len(chunks)} chunks covering {coverage:.1%} of document")

        return chunks


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
