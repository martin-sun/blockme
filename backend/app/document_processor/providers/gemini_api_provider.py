"""
Gemini API Provider

Provider for Google Gemini API using Generative AI SDK.
"""

import os
from typing import Optional


class GeminiAPIProvider:
    """
    Provider for Google Gemini API.

    Uses the Google Generative AI Python SDK to call Gemini models directly via API.
    This is an API-based provider, not a CLI tool.

    Features:
    - Uses Gemini 2.5 Pro model (highest quality, excellent reasoning)
    - 1M token context window
    - Superior accuracy for complex classification tasks
    - Direct API integration (no CLI needed)

    Configuration:
    - Requires GEMINI_API_KEY environment variable
    - Model: gemini-2.5-pro (can be changed via model parameter)

    Installation:
        pip install google-generativeai>=0.3.0
    """

    def __init__(self, model: str = "gemini-2.5-pro"):
        """
        Initialize Gemini API Provider.

        Args:
            model: Gemini model to use (default: gemini-2.5-pro)
        """
        self.model = model
        self._client = None

    def _get_client(self):
        """Lazy initialization of Google Generative AI client."""
        if self._client is None:
            api_key = os.environ.get("GEMINI_API_KEY")
            if not api_key:
                raise ValueError("GEMINI_API_KEY environment variable is required")

            try:
                import google.generativeai as genai
                genai.configure(api_key=api_key)
                self._client = genai.GenerativeModel(self.model)
            except ImportError:
                raise ImportError("google-generativeai package is required. Install with: pip install google-generativeai>=0.3.0")

        return self._client

    def is_available(self) -> bool:
        """Check if Gemini API is available (API key exists and package installed)."""
        try:
            api_key = os.environ.get("GEMINI_API_KEY")
            if not api_key:
                return False

            import google.generativeai as genai
            return True
        except ImportError:
            return False

    def build_command(self, prompt: str) -> list[str]:
        """
        Gemini API doesn't use CLI commands.

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
        Call Gemini API and parse response.

        For API-based providers, this method handles the actual API call.
        The stdout parameter contains the prompt to process.

        Args:
            stdout: The prompt to send to Gemini API
            stderr: Not used for API providers

        Returns:
            str: Enhanced content from Gemini API

        Raises:
            ValueError: If API call fails or returns invalid response
        """
        prompt = stdout.strip()

        if len(prompt) < 10:
            raise ValueError(f"Prompt too short: {len(prompt)} chars")

        try:
            client = self._get_client()

            # Import generation config
            import google.generativeai as genai

            # Configure generation parameters for consistent, high-quality output
            generation_config = genai.GenerationConfig(
                temperature=0.3,      # Lower temperature for consistent output
                top_p=0.95,           # Nucleus sampling threshold
                top_k=40,             # Top-k sampling parameter
                max_output_tokens=8192,  # Reasonable output limit
            )

            response = client.generate_content(
                prompt,
                generation_config=generation_config
            )

            enhanced = response.text.strip()

            if len(enhanced) < 50:
                raise ValueError(f"Gemini API response too short: {len(enhanced)} chars")

            return enhanced

        except Exception as e:
            raise ValueError(f"Gemini API call failed: {str(e)}")

    def get_timeout(self, content_length: int) -> int:
        """
        Calculate timeout for Gemini API.

        Similar to Gemini CLI but API typically has faster response times.
        Formula: max(180 seconds, 2 seconds per 1K characters)

        Args:
            content_length: Length of content to be processed

        Returns:
            int: Timeout in seconds
        """
        if content_length < 100_000:
            # Small documents: 3 minute minimum
            MIN_TIMEOUT = 180
            TIMEOUT_PER_1K = 2
            return max(MIN_TIMEOUT, content_length // 1000 * TIMEOUT_PER_1K)

        elif content_length < 500_000:
            # Medium documents: faster processing
            TIMEOUT_PER_1K = 2
            return content_length // 1000 * TIMEOUT_PER_1K

        else:
            # Large documents (full doc analysis): generous timeout
            TIMEOUT_PER_1K = 3
            timeout = content_length // 1000 * TIMEOUT_PER_1K

            # Add extra buffer for very large docs (>1M)
            if content_length > 1_000_000:
                timeout = int(timeout * 1.1)  # +10% safety margin

            return timeout

    def uses_stdin(self) -> bool:
        """Gemini API doesn't use stdin (direct Python calls)."""
        return False

    def is_api_based(self) -> bool:
        """Gemini API provider uses API directly."""
        return True

    def get_max_chunk_size(self) -> int:
        """
        Get maximum chunk size for Gemini.

        Based on Gemini specifications:
        - 1M token context window
        - ~4 chars per token ratio
        - Theoretical max: ~4M chars

        Using 1.5M chars (~375K tokens) provides:
        - Massive throughput compared to other providers
        - Still leaves 625K tokens for output and safety margin
        - Enables processing large documents efficiently

        Returns:
            int: 1,500,000 characters
        """
        return 1_500_000

    @property
    def name(self) -> str:
        return f"Gemini API ({self.model})"

    def get_env(self) -> Optional[dict]:
        """
        Get custom environment variables for this provider.

        Returns:
            Optional[dict]: Environment variables to use for subprocess calls,
                          or None to use system default environment.
        """
        return None