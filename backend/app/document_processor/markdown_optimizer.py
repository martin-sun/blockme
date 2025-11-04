"""
Markdown Optimizer - AI-Enhanced Content Optimization

Markdown optimization and AI content enhancement for offline document processing.
Uses Claude API or other LLM providers to improve content quality.
"""

import logging
import os
import re
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class AIProvider(str, Enum):
    """AI provider options."""

    ANTHROPIC = "anthropic"  # Claude API
    OPENAI = "openai"  # OpenAI API
    ZHIPUAI = "zhipuai"  # ZhipuAI
    NONE = "none"  # No AI enhancement


class OptimizationConfig(BaseModel):
    """Optimization configuration."""

    # AI enhancement settings
    enable_ai_enhancement: bool = Field(default=True, description="Enable AI enhancement")
    ai_provider: AIProvider = Field(default=AIProvider.ANTHROPIC, description="AI provider")
    ai_model: str = Field(default="claude-3-5-sonnet-20241022", description="AI model")

    # Content enhancement options
    add_examples: bool = Field(default=True, description="Add examples")
    add_calculations: bool = Field(default=True, description="Add calculation examples")
    add_faqs: bool = Field(default=True, description="Add frequently asked questions")
    add_tips: bool = Field(default=True, description="Add practical tips")
    improve_clarity: bool = Field(default=True, description="Improve clarity")

    # Basic cleaning options
    clean_artifacts: bool = Field(default=True, description="Clean PDF extraction artifacts")
    fix_tables: bool = Field(default=True, description="Fix table formatting")
    standardize_headings: bool = Field(default=True, description="Standardize headings")

    # API settings
    max_tokens: int = Field(default=4000, description="Maximum tokens")
    temperature: float = Field(default=0.7, ge=0.0, le=1.0, description="Temperature parameter")


class OptimizationResult(BaseModel):
    """Optimization result."""

    original_content: str = Field(..., description="Original content")
    optimized_content: str = Field(..., description="Optimized content")
    ai_enhanced: bool = Field(default=False, description="Whether AI enhancement was used")
    provider_used: Optional[AIProvider] = Field(None, description="AI provider used")
    improvements: list[str] = Field(default_factory=list, description="List of improvements made")
    word_count_before: int = Field(..., description="Word count before optimization")
    word_count_after: int = Field(..., description="Word count after optimization")


class MarkdownOptimizer:
    """
    Markdown content optimizer.

    Features:
    - Basic cleaning: remove PDF artifacts, fix formatting
    - AI enhancement: use Claude/OpenAI to improve content quality
    - Offline processing: can use API (not real-time service)
    """

    def __init__(self, config: Optional[OptimizationConfig] = None):
        """
        Initialize the optimizer.

        Args:
            config: Optimization configuration
        """
        self.config = config or OptimizationConfig()

        # Initialize AI client
        self._ai_client = None
        if self.config.enable_ai_enhancement:
            self._init_ai_client()

    def _init_ai_client(self):
        """Initialize AI client based on provider."""
        try:
            if self.config.ai_provider == AIProvider.ANTHROPIC:
                import anthropic
                api_key = os.getenv("ANTHROPIC_API_KEY")
                if not api_key:
                    logger.warning("ANTHROPIC_API_KEY not set, AI enhancement disabled")
                    self.config.enable_ai_enhancement = False
                    return
                self._ai_client = anthropic.Anthropic(api_key=api_key)
                logger.info("Claude AI client initialized")

            elif self.config.ai_provider == AIProvider.OPENAI:
                import openai
                api_key = os.getenv("OPENAI_API_KEY")
                if not api_key:
                    logger.warning("OPENAI_API_KEY not set, AI enhancement disabled")
                    self.config.enable_ai_enhancement = False
                    return
                self._ai_client = openai.OpenAI(api_key=api_key)
                logger.info("OpenAI client initialized")

            elif self.config.ai_provider == AIProvider.ZHIPUAI:
                import zhipuai
                api_key = os.getenv("ZHIPUAI_API_KEY")
                if not api_key:
                    logger.warning("ZHIPUAI_API_KEY not set, AI enhancement disabled")
                    self.config.enable_ai_enhancement = False
                    return
                self._ai_client = zhipuai.ZhipuAI(api_key=api_key)
                logger.info("ZhipuAI client initialized")

        except ImportError as e:
            logger.warning(f"AI library not installed: {e}")
            self.config.enable_ai_enhancement = False
        except Exception as e:
            logger.error(f"AI client initialization failed: {e}")
            self.config.enable_ai_enhancement = False

    def optimize(self, content: str, category: str = "general") -> OptimizationResult:
        """
        Optimize Markdown content.

        Args:
            content: Original content
            category: Content category (for AI enhancement)

        Returns:
            OptimizationResult with optimized content and metadata
        """
        original_content = content
        improvements = []

        # 1. Basic cleaning
        if self.config.clean_artifacts:
            content = self._clean_pdf_artifacts(content)
            improvements.append("Cleaned PDF extraction artifacts")

        if self.config.fix_tables:
            content = self._fix_tables(content)
            improvements.append("Fixed table formatting")

        if self.config.standardize_headings:
            content = self._standardize_headings(content)
            improvements.append("Standardized heading format")

        # 2. AI enhancement
        ai_enhanced = False
        provider_used = None

        if self.config.enable_ai_enhancement and self._ai_client:
            try:
                content = self._ai_enhance(content, category)
                ai_enhanced = True
                provider_used = self.config.ai_provider
                improvements.append(f"AI content enhancement ({self.config.ai_provider.value})")
            except Exception as e:
                logger.error(f"AI enhancement failed: {e}")
                improvements.append("AI enhancement failed, using basic optimization")

        # 3. Final cleanup
        content = self._final_cleanup(content)

        return OptimizationResult(
            original_content=original_content,
            optimized_content=content,
            ai_enhanced=ai_enhanced,
            provider_used=provider_used,
            improvements=improvements,
            word_count_before=len(original_content.split()),
            word_count_after=len(content.split())
        )

    def _clean_pdf_artifacts(self, content: str) -> str:
        """
        Clean PDF extraction artifacts.

        - Remove headers and footers
        - Clean excess whitespace
        - Fix line breaks
        """
        # Remove excess blank lines
        content = re.sub(r'\n{3,}', '\n\n', content)

        # Fix broken words (word- word -> word)
        content = re.sub(r'(\w+)-\s*\n\s*(\w+)', r'\1\2', content)

        # Clean page numbers (standalone numbers on a line)
        content = re.sub(r'^\s*\d+\s*$', '', content, flags=re.MULTILINE)

        # Remove duplicate page markers
        content = re.sub(r'^(=== Page \d+ ===\s*)+', '=== Page ===\n', content, flags=re.MULTILINE)

        return content.strip()

    def _fix_tables(self, content: str) -> str:
        """Fix table formatting."""
        # Basic table format fixing
        # Can be enhanced based on specific requirements
        return content

    def _standardize_headings(self, content: str) -> str:
        """Standardize heading formatting."""
        lines = content.split('\n')
        standardized = []

        for line in lines:
            # Ensure headings have blank lines before and after
            if re.match(r'^#+\s', line):
                if standardized and standardized[-1].strip():
                    standardized.append('')
                standardized.append(line)
                standardized.append('')
            else:
                standardized.append(line)

        # Remove excess blank lines
        result = '\n'.join(standardized)
        result = re.sub(r'\n{3,}', '\n\n', result)

        return result.strip()

    def _ai_enhance(self, content: str, category: str) -> str:
        """
        Use AI to enhance content quality.

        Args:
            content: Original content
            category: Content category

        Returns:
            Enhanced content
        """
        # Build enhancement features list
        enhancement_features = []
        if self.config.add_examples:
            enhancement_features.append("specific examples")
        if self.config.add_calculations:
            enhancement_features.append("calculation examples")
        if self.config.add_faqs:
            enhancement_features.append("frequently asked questions")
        if self.config.add_tips:
            enhancement_features.append("practical tips")

        features_text = ", ".join(enhancement_features) if enhancement_features else "practical information"

        prompt = f"""Please optimize the following CRA tax document content to make it more professional, clear, and useful.

Content category: {category}

Optimization requirements:
1. Maintain accuracy of original information - do not add fictitious legal provisions or numbers
2. Improve structure and organization with clear headings and paragraphs
3. Add {features_text} to help readers understand
4. Use professional tax terminology while keeping it understandable
5. Ensure standard Markdown formatting
6. For specific amounts or dates, add "(example)" notation

Return only the optimized Markdown content without any explanation.

---

{content}
"""

        # Call AI API
        if self.config.ai_provider == AIProvider.ANTHROPIC:
            return self._enhance_with_claude(prompt)
        elif self.config.ai_provider == AIProvider.OPENAI:
            return self._enhance_with_openai(prompt)
        elif self.config.ai_provider == AIProvider.ZHIPUAI:
            return self._enhance_with_zhipuai(prompt)
        else:
            return content

    def _enhance_with_claude(self, prompt: str) -> str:
        """Enhance content using Claude."""
        try:
            response = self._ai_client.messages.create(
                model=self.config.ai_model,
                max_tokens=self.config.max_tokens,
                temperature=self.config.temperature,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )

            enhanced_content = response.content[0].text
            logger.info("Claude AI enhancement successful")
            return enhanced_content

        except Exception as e:
            logger.error(f"Claude AI enhancement failed: {e}")
            raise

    def _enhance_with_openai(self, prompt: str) -> str:
        """Enhance content using OpenAI."""
        try:
            response = self._ai_client.chat.completions.create(
                model=self.config.ai_model,
                max_tokens=self.config.max_tokens,
                temperature=self.config.temperature,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )

            enhanced_content = response.choices[0].message.content
            logger.info("OpenAI enhancement successful")
            return enhanced_content

        except Exception as e:
            logger.error(f"OpenAI enhancement failed: {e}")
            raise

    def _enhance_with_zhipuai(self, prompt: str) -> str:
        """Enhance content using ZhipuAI."""
        try:
            response = self._ai_client.chat.completions.create(
                model=self.config.ai_model,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )

            enhanced_content = response.choices[0].message.content
            logger.info("ZhipuAI enhancement successful")
            return enhanced_content

        except Exception as e:
            logger.error(f"ZhipuAI enhancement failed: {e}")
            raise

    def _final_cleanup(self, content: str) -> str:
        """Final content cleanup."""
        # Ensure proper code block formatting
        content = re.sub(r'```\s*\n\s*\n', '```\n', content)

        # Ensure proper list formatting
        content = re.sub(r'([^\n])\n([•\-\*])', r'\1\n\n\2', content)

        # Remove trailing whitespace
        content = re.sub(r' +\n', '\n', content)
        content = re.sub(r'\n{3,}', '\n\n', content)

        return content.strip()


def optimize_markdown(
    content: str,
    category: str = "general",
    enable_ai: bool = True,
    ai_provider: AIProvider = AIProvider.ANTHROPIC
) -> OptimizationResult:
    """
    Convenience function to optimize Markdown content.

    Args:
        content: Original content
        category: Content category
        enable_ai: Whether to enable AI enhancement
        ai_provider: AI provider to use

    Returns:
        OptimizationResult with optimized content
    """
    config = OptimizationConfig(
        enable_ai_enhancement=enable_ai,
        ai_provider=ai_provider
    )
    optimizer = MarkdownOptimizer(config)
    return optimizer.optimize(content, category)
