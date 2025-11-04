"""
PDF Text Extractor - Production Version

PDF text extraction with PyMuPDF, OCR support, and intelligent quality assessment.
Designed for offline processing of CRA tax documents.
"""

import io
import logging
import time
from pathlib import Path
from typing import Dict, List, Optional

import fitz  # PyMuPDF
from PIL import Image
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class PageResult(BaseModel):
    """Single page processing result."""

    page_number: int = Field(..., description="Page number (starting from 1)")
    text: str = Field(..., description="Extracted text content")
    text_quality: float = Field(..., ge=0.0, le=1.0, description="Text quality score 0-1")
    has_images: bool = Field(default=False, description="Whether page contains images")
    needs_ocr: bool = Field(default=False, description="Whether OCR was used")
    processing_time: float = Field(..., description="Processing time in seconds")
    word_count: int = Field(..., description="Number of words")
    char_count: int = Field(..., description="Number of characters")
    line_count: int = Field(..., description="Number of lines")


class PDFMetadata(BaseModel):
    """PDF document metadata."""

    title: str = Field(default="", description="Document title")
    author: str = Field(default="", description="Author name")
    subject: str = Field(default="", description="Document subject")
    creator: str = Field(default="", description="Creator application")
    producer: str = Field(default="", description="Producer application")
    creation_date: str = Field(default="", description="Creation date")
    modification_date: str = Field(default="", description="Last modification date")
    page_count: int = Field(..., description="Total number of pages")
    is_encrypted: bool = Field(default=False, description="Whether PDF is encrypted")


class ExtractionResult(BaseModel):
    """Complete extraction result."""

    file_path: str = Field(..., description="Path to the PDF file")
    total_pages: int = Field(..., description="Total number of pages processed")
    successful_pages: int = Field(..., description="Number of successfully processed pages")
    pages_needing_ocr: int = Field(default=0, description="Number of pages that needed OCR")
    total_text: str = Field(..., description="Combined text from all pages")
    processing_time: float = Field(..., description="Total processing time in seconds")
    pages: List[PageResult] = Field(default_factory=list, description="Individual page results")
    metadata: PDFMetadata = Field(..., description="PDF metadata")
    average_quality: float = Field(default=0.0, description="Average text quality across all pages")


class PDFExtractorConfig(BaseModel):
    """PDF extractor configuration."""

    enable_ocr: bool = Field(default=True, description="Whether to enable OCR fallback")
    ocr_language: str = Field(default="eng", description="OCR language (eng, fra, etc.)")
    text_quality_threshold: float = Field(
        default=0.3, ge=0.0, le=1.0, description="Quality threshold for triggering OCR"
    )
    ocr_resolution_scale: float = Field(default=2.0, description="OCR image resolution multiplier")
    max_pages: Optional[int] = Field(default=None, description="Maximum pages to process (None for all)")


class PDFTextExtractor:
    """
    PDF text extractor for CRA tax documents.

    Features:
    - High-performance text extraction with PyMuPDF
    - Intelligent text quality assessment
    - OCR fallback for scanned documents
    - CRA document optimization
    """

    def __init__(self, config: Optional[PDFExtractorConfig] = None):
        """
        Initialize the PDF extractor.

        Args:
            config: Extractor configuration (defaults to standard config if None)
        """
        self.config = config or PDFExtractorConfig()

        # Check OCR availability
        if self.config.enable_ocr:
            try:
                import pytesseract
                self._pytesseract = pytesseract
                logger.info("OCR enabled successfully")
            except ImportError:
                logger.warning("pytesseract not installed, OCR disabled")
                self.config.enable_ocr = False
                self._pytesseract = None

    def extract(self, pdf_path: str) -> ExtractionResult:
        """
        Extract text from PDF file.

        Args:
            pdf_path: Path to the PDF file

        Returns:
            ExtractionResult with extracted text and metadata

        Raises:
            FileNotFoundError: If PDF file doesn't exist
            ValueError: If PDF cannot be processed (encrypted, corrupted, etc.)
        """
        pdf_file = Path(pdf_path)
        if not pdf_file.exists():
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")

        logger.info("Starting PDF extraction", extra={"file": pdf_file.name})
        start_time = time.time()

        try:
            # Open PDF
            doc = fitz.open(str(pdf_file))

            # Check encryption
            if doc.is_encrypted:
                logger.warning("PDF is encrypted, attempting to decrypt")
                if not doc.authenticate(""):
                    raise ValueError("Cannot decrypt PDF file, password required")

            # Determine pages to process
            total_pages = len(doc)
            if self.config.max_pages:
                total_pages = min(total_pages, self.config.max_pages)
                logger.info(f"Limiting processing to {total_pages} pages")

            # Extract metadata
            metadata = self._extract_metadata(doc)

            # Process pages
            pages: List[PageResult] = []
            successful_pages = 0
            pages_needing_ocr = 0

            for page_num in range(total_pages):
                try:
                    page_result = self._process_page(doc, page_num)
                    pages.append(page_result)

                    if page_result.text_quality > 0.1:
                        successful_pages += 1

                    if page_result.needs_ocr:
                        pages_needing_ocr += 1

                except Exception as e:
                    logger.error(
                        f"Failed to process page {page_num + 1}",
                        extra={"page": page_num + 1, "error": str(e)},
                        exc_info=True
                    )
                    # Create empty page result
                    pages.append(PageResult(
                        page_number=page_num + 1,
                        text="",
                        text_quality=0.0,
                        processing_time=0.0,
                        word_count=0,
                        char_count=0,
                        line_count=0
                    ))

            # Combine text
            total_text = self._combine_pages_text(pages)

            # Calculate average quality
            avg_quality = sum(p.text_quality for p in pages) / len(pages) if pages else 0.0

            # Close document
            doc.close()

            processing_time = time.time() - start_time

            result = ExtractionResult(
                file_path=str(pdf_file),
                total_pages=total_pages,
                successful_pages=successful_pages,
                pages_needing_ocr=pages_needing_ocr,
                total_text=total_text,
                processing_time=processing_time,
                pages=pages,
                metadata=metadata,
                average_quality=avg_quality
            )

            logger.info(
                "PDF extraction completed",
                extra={
                    "pages": total_pages,
                    "successful": successful_pages,
                    "ocr_used": pages_needing_ocr,
                    "time": f"{processing_time:.2f}s"
                }
            )

            return result

        except Exception as e:
            logger.error(f"PDF extraction failed: {e}", exc_info=True)
            raise

    def _process_page(self, doc: fitz.Document, page_num: int) -> PageResult:
        """Process a single page."""
        start_time = time.time()
        page = doc[page_num]

        # Direct text extraction
        text = page.get_text()
        text_quality = self._evaluate_text_quality(text)

        needs_ocr = False

        # OCR fallback if quality is low
        if (
            text_quality < self.config.text_quality_threshold
            and self.config.enable_ocr
            and self._pytesseract
        ):
            logger.debug(
                f"Low text quality ({text_quality:.2f}) on page {page_num + 1}, trying OCR"
            )
            try:
                ocr_text = self._ocr_page(page)
                if ocr_text and len(ocr_text.strip()) > len(text.strip()):
                    text = ocr_text
                    needs_ocr = True
                    text_quality = self._evaluate_text_quality(text)
                    logger.debug(f"OCR successful, new quality: {text_quality:.2f}")
            except Exception as e:
                logger.warning(f"OCR failed: {e}")

        # Check for images
        image_list = page.get_images()
        has_images = len(image_list) > 0

        processing_time = time.time() - start_time
        text = text.strip()

        return PageResult(
            page_number=page_num + 1,
            text=text,
            text_quality=text_quality,
            has_images=has_images,
            needs_ocr=needs_ocr,
            processing_time=processing_time,
            word_count=len(text.split()),
            char_count=len(text),
            line_count=len(text.split('\n'))
        )

    def _evaluate_text_quality(self, text: str) -> float:
        """
        Evaluate text quality based on multiple factors.

        Quality scoring:
        1. Text length (30%)
        2. Word completeness (30%)
        3. Sentence structure (20%)
        4. Character validity (20%)

        Args:
            text: Text content to evaluate

        Returns:
            Quality score from 0.0 to 1.0
        """
        if not text or len(text.strip()) < 10:
            return 0.0

        score = 0.0
        text = text.strip()

        # 1. Text length (0-0.3 points)
        text_length = len(text)
        if text_length > 100:
            score += 0.3
        elif text_length > 50:
            score += 0.2
        else:
            score += 0.1

        # 2. Word completeness (0-0.3 points)
        words = text.split()
        if words:
            complete_words = sum(
                1 for word in words
                if word.isalpha() or any(c in word for c in '.,!?;:-')
            )
            word_completeness = complete_words / len(words)
            score += word_completeness * 0.3

        # 3. Sentence structure (0-0.2 points)
        sentences = text.split('.')
        if len(sentences) > 1:
            score += 0.2

        # 4. Character validity (0-0.2 points)
        common_chars = set(
            "abcdefghijklmnopqrstuvwxyz"
            "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
            "0123456789.,!?;:()- \n\t"
        )
        valid_chars = sum(1 for c in text if c in common_chars)
        char_ratio = valid_chars / len(text) if text else 0
        score += char_ratio * 0.2

        return min(score, 1.0)

    def _ocr_page(self, page: fitz.Page) -> str:
        """
        Perform OCR on a page.

        Args:
            page: PDF page object

        Returns:
            OCR extracted text
        """
        if not self._pytesseract:
            return ""

        try:
            # Convert to high-resolution image
            matrix = fitz.Matrix(
                self.config.ocr_resolution_scale,
                self.config.ocr_resolution_scale
            )
            pix = page.get_pixmap(matrix=matrix)
            img_data = pix.tobytes("png")
            img = Image.open(io.BytesIO(img_data))

            # Perform OCR
            text = self._pytesseract.image_to_string(
                img,
                lang=self.config.ocr_language
            )
            return text

        except Exception as e:
            logger.error(f"OCR processing failed: {e}")
            return ""

    def _extract_metadata(self, doc: fitz.Document) -> PDFMetadata:
        """Extract PDF metadata."""
        metadata = doc.metadata or {}

        return PDFMetadata(
            title=metadata.get("title", ""),
            author=metadata.get("author", ""),
            subject=metadata.get("subject", ""),
            creator=metadata.get("creator", ""),
            producer=metadata.get("producer", ""),
            creation_date=metadata.get("creationDate", ""),
            modification_date=metadata.get("modDate", ""),
            page_count=len(doc),
            is_encrypted=doc.is_encrypted
        )

    def _combine_pages_text(self, pages: List[PageResult]) -> str:
        """Combine text from all pages."""
        combined_parts = []

        for page in pages:
            if page.text:
                combined_parts.append(f"\n=== Page {page.page_number} ===\n")
                combined_parts.append(page.text)
                combined_parts.append("\n")

        return "\n".join(combined_parts)


def extract_pdf(
    pdf_path: str,
    enable_ocr: bool = True,
    max_pages: Optional[int] = None
) -> ExtractionResult:
    """
    Convenience function to extract PDF text.

    Args:
        pdf_path: Path to PDF file
        enable_ocr: Whether to enable OCR fallback
        max_pages: Maximum number of pages to process

    Returns:
        ExtractionResult with extracted text and metadata
    """
    config = PDFExtractorConfig(
        enable_ocr=enable_ocr,
        max_pages=max_pages
    )
    extractor = PDFTextExtractor(config)
    return extractor.extract(pdf_path)
