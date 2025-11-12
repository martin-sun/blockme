"""
Document Processor - Phase-02 CRA Tax Document Processing

Offline processing of CRA PDF documents to generate high-quality Skill files.

Main Modules:
- pdf_extractor: PDF text extraction (PyMuPDF + OCR)
- content_classifier: Content classification and quality assessment
- skill_generator: Generate Skill files (Markdown + YAML)
- markdown_optimizer: AI content enhancement
- quality_validator: Quality validation
- llm_cli_providers: LLM CLI provider abstraction (Claude, Gemini, Codex)
"""

# PDF Extraction
from .pdf_extractor import (
    PDFExtractorConfig,
    PDFTextExtractor,
    ExtractionResult,
    PageResult,
    PDFMetadata,
    extract_pdf
)

# Content Classification
from .content_classifier import (
    ContentClassifier,
    TaxCategory,
    QualityMetrics,
    ClassificationResult,
    classify_content
)

# Skill Generation
from .skill_generator import (
    SkillGenerator,
    SkillMetadata,
    SkillContent,
    generate_and_save_skill
)

# Markdown Optimization
from .markdown_optimizer import (
    MarkdownOptimizer,
    OptimizationConfig,
    OptimizationResult,
    AIProvider,
    optimize_markdown
)

# Quality Validation
from .quality_validator import (
    QualityValidator,
    ValidationResult,
    ValidationIssue,
    validate_skill_file,
    validate_skill_content
)

# LLM CLI Providers
from .llm_cli_providers import (
    LLMCLIProvider,
    get_provider,
    detect_available_providers
)
from .providers import (
    ClaudeCodeProvider,
    GeminiCLIProvider,
    CodexCLIProvider
)

__version__ = "0.1.0"

__all__ = [
    # PDF Extraction
    "PDFExtractorConfig",
    "PDFTextExtractor",
    "ExtractionResult",
    "PageResult",
    "PDFMetadata",
    "extract_pdf",
    # Content Classification
    "ContentClassifier",
    "TaxCategory",
    "QualityMetrics",
    "ClassificationResult",
    "classify_content",
    # Skill Generation
    "SkillGenerator",
    "SkillMetadata",
    "SkillContent",
    "generate_and_save_skill",
    # Markdown Optimization
    "MarkdownOptimizer",
    "OptimizationConfig",
    "OptimizationResult",
    "AIProvider",
    "optimize_markdown",
    # Quality Validation
    "QualityValidator",
    "ValidationResult",
    "ValidationIssue",
    "validate_skill_file",
    "validate_skill_content",
    # LLM CLI Providers
    "LLMCLIProvider",
    "ClaudeCodeProvider",
    "GeminiCLIProvider",
    "CodexCLIProvider",
    "get_provider",
    "detect_available_providers",
]
