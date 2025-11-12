"""
GLM API Provider using Z.AI SDK

Enhanced GLM provider implementation based on BeanFlow-LLM reference.
Features improved error handling, logging, and Vision API support.
"""

import os
import asyncio
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class GLMAPIProvider:
    """
    Enhanced provider for GLM API using Z.AI SDK.

    This is an API-based provider, not a CLI tool. It offers:
    - Direct GLM API integration using Z.AI SDK
    - Enhanced error handling and logging
    - Vision API support with PDF auto-conversion
    - Response truncation detection
    - Token usage monitoring

    Configuration:
    - Requires GLM_API_KEY environment variable
    - Uses Z.AI SDK for official GLM API access
    - Model: glm-4.6 (default, configurable)

    Installation:
        pip install zhipuai>=2.0.0
    """

    def __init__(self, model: str = "glm-4.6"):
        """
        Initialize GLM API Provider.

        Args:
            model: GLM model to use (default: glm-4.6)
        """
        self.model = model
        self._client = None

    def _get_client(self):
        """Lazy initialization of ZhipuAI client."""
        if self._client is None:
            api_key = os.environ.get("GLM_API_KEY")
            if not api_key:
                raise ValueError("GLM_API_KEY environment variable is required")

            try:
                from zhipuai import ZhipuAI
                self._client = ZhipuAI(api_key=api_key)
                logger.info("ZhipuAI client initialized successfully")
            except ImportError:
                raise ImportError("zhipuai package is required. Install with: pip install zhipuai>=2.0.0")

        return self._client

    def is_available(self) -> bool:
        """Check if GLM API is available (API key exists and package installed)."""
        try:
            api_key = os.environ.get("GLM_API_KEY")
            if not api_key:
                logger.warning("GLM_API_KEY environment variable not found")
                return False

            from zhipuai import ZhipuAI
            return True
        except ImportError as e:
            logger.error(f"zhipuai package not available: {e}")
            return False

    def build_command(self, prompt: str) -> list[str]:
        """
        GLM API doesn't use CLI commands.

        This method is not used for API-based providers.
        The actual API call is made in parse_output method.

        Args:
            prompt: The enhancement prompt

        Returns:
            Empty list (not used for API providers)
        """
        return []

    def parse_output(self, stdout: str, stderr: str) -> str:
        """
        Call GLM API and parse response.

        For API-based providers, this method handles the actual API call.
        The stdout parameter contains the prompt to process.

        Args:
            stdout: The prompt to send to GLM API
            stderr: Not used for API providers

        Returns:
            str: Enhanced content from GLM API

        Raises:
            ValueError: If API call fails or returns invalid response
        """
        prompt = stdout.strip()

        if len(prompt) < 10:
            raise ValueError(f"Prompt too short: {len(prompt)} chars")

        try:
            client = self._get_client()

            # Build request parameters
            request_params = {
                "model": self.model,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.3,  # Lower temperature for consistent output
                "max_tokens": 8192,   # Reasonable output limit
                "top_p": 0.95,        # Nucleus sampling threshold
            }

            # Log request details
            logger.debug(
                f"GLM API request: model={self.model}, "
                f"max_tokens=8192, temperature=0.3, "
                f"prompt_length={len(prompt)} chars"
            )

            # Make API call
            response = client.chat.completions.create(**request_params)

            # Log response details
            if response.choices and len(response.choices) > 0:
                choice = response.choices[0]
                content_length = len(choice.message.content) if choice.message and choice.message.content else 0
                logger.debug(
                    f"GLM API response: choices={len(response.choices)}, "
                    f"finish_reason={choice.finish_reason if hasattr(choice, 'finish_reason') else 'N/A'}, "
                    f"content_length={content_length} chars, "
                    f"usage={response.usage.model_dump() if hasattr(response, 'usage') else 'N/A'}"
                )

                # Check for response truncation
                finish_reason = choice.finish_reason if hasattr(choice, "finish_reason") else None
                if finish_reason in ("length", "max_tokens"):
                    logger.error(
                        f"GLM API response truncated due to max_tokens limit. "
                        f"finish_reason={finish_reason}, "
                        f"configured_max_tokens=8192, "
                        f"response_length={content_length} chars. "
                        f"Consider increasing max_tokens or simplifying the prompt."
                    )
                    raise ValueError(
                        f"GLM API response was truncated due to token limit (finish_reason={finish_reason}). "
                        f"The output exceeded 8192 tokens. "
                        f"Please try splitting the document or increasing max_tokens."
                    )

                if choice.message and choice.message.content:
                    enhanced = choice.message.content.strip()

                    if len(enhanced) < 50:
                        raise ValueError(f"GLM API response too short: {len(enhanced)} chars")

                    logger.info(f"GLM API call successful: {content_length} chars generated")
                    return enhanced

            logger.error(
                f"GLM API returned empty content: "
                f"choices={len(response.choices) if response.choices else 0}"
            )
            raise ValueError("GLM API returned empty content in response")

        except Exception as e:
            logger.error(f"GLM API call failed: {str(e)}")
            raise ValueError(f"GLM API call failed: {str(e)}")

    def get_timeout(self, content_length: int) -> int:
        """
        Calculate timeout for GLM API.

        GLM API typically has fast response times.
        Formula: max(120 seconds, 2 seconds per 1K characters)

        Args:
            content_length: Length of content to be processed

        Returns:
            int: Timeout in seconds
        """
        if content_length < 100_000:
            # Small documents: 2 minute minimum
            MIN_TIMEOUT = 120
            TIMEOUT_PER_1K = 2
            return max(MIN_TIMEOUT, content_length // 1000 * TIMEOUT_PER_1K)

        elif content_length < 500_000:
            # Medium documents: moderate processing time
            TIMEOUT_PER_1K = 2
            return content_length // 1000 * TIMEOUT_PER_1K

        else:
            # Large documents: generous timeout
            TIMEOUT_PER_1K = 3
            timeout = content_length // 1000 * TIMEOUT_PER_1K

            # Add extra buffer for very large docs (>1M)
            if content_length > 1_000_000:
                timeout = int(timeout * 1.1)  # +10% safety margin

            return timeout

    def uses_stdin(self) -> bool:
        """GLM API doesn't use stdin (direct Python calls)."""
        return False

    def is_api_based(self) -> bool:
        """GLM API provider uses API directly."""
        return True

    def get_max_chunk_size(self) -> int:
        """
        Get maximum chunk size for GLM.

        Based on GLM specifications:
        - 128K token context window
        - ~4 chars per token ratio
        - Theoretical max: ~512K chars

        Using 400K chars (~100K tokens) provides:
        - High throughput for large documents
        - Leaves 28K tokens for output and safety margin
        - Optimal balance between speed and reliability

        Returns:
            int: 400,000 characters
        """
        return 400_000

    @property
    def name(self) -> str:
        return f"GLM API ({self.model})"

    def get_env(self) -> Optional[dict]:
        """
        Get custom environment variables for this provider.

        Returns:
            Optional[dict]: Environment variables to use for subprocess calls,
                          or None to use system default environment.
        """
        return None