"""
Gemini CLI Provider

Provider for Google Gemini CLI using open-source CLI tool.
"""

import shutil
from typing import Optional


class GeminiCLIProvider:
    """
    Provider for Google Gemini CLI.

    Uses the open-source Gemini CLI (Apache 2.0).
    Command: gemini -p "prompt"

    Features:
    - Free tier: 1000 requests/day, 60 req/min
    - 1M token context window
    - Faster than Claude for large contexts

    Installation:
        npm install -g @google/gemini-cli
    """

    def is_available(self) -> bool:
        """Check if gemini CLI is available in PATH."""
        return shutil.which('gemini') is not None

    def build_command(self, prompt: str) -> list[str]:
        """
        Build command for Gemini CLI.

        Flags:
        - -m gemini-2.5-pro: Use Gemini 2.5 Pro (highest quality)
        - -p: Provide prompt as argument
        - --output-format text: Plain text output (no JSON)
        """
        return ['gemini', '-m', 'gemini-2.5-pro', '-p', prompt, '--output-format', 'text']

    def parse_output(self, stdout: str, stderr: str) -> str:
        """
        Parse Gemini CLI output.

        Gemini returns plain text with --output-format text.
        Basic validation ensures non-empty output.
        """
        # Check stderr for errors FIRST before validating stdout
        if stderr and ("error" in stderr.lower() or "failed" in stderr.lower() or "no input provided" in stderr.lower()):
            raise ValueError(f"CLI error in stderr: {stderr[:200]}")

        enhanced = stdout.strip()

        if len(enhanced) < 50:
            raise ValueError(f"Output too short: {len(enhanced)} chars. Stderr: {stderr[:100] if stderr else 'empty'}")

        return enhanced

    def get_timeout(self, content_length: int) -> int:
        """
        Calculate timeout for Gemini CLI with optimized handling for large documents.

        Timeout strategy:
        - Small docs (<100K): 3 minutes minimum
        - Medium docs (100K-500K): 2s per 1K chars
        - Large docs (500K-1.5M): 3s per 1K chars (full document analysis)

        Examples:
        - 40K chars (skill enhancement): 180s (3 min)
        - 300K chars (regular chunk): 600s (10 min)
        - 721K chars (full doc analysis): 2163s (36 min)
        - 1.5M chars (max input): 4500s (75 min)

        The generous timeout for large documents accounts for:
        - Complete document parsing
        - Deep semantic analysis
        - Chunk boundary identification
        - Quality assessment
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
            # 721K → 36 min, 1.5M → 75 min
            TIMEOUT_PER_1K = 3
            timeout = content_length // 1000 * TIMEOUT_PER_1K

            # Add extra buffer for very large docs (>1M)
            if content_length > 1_000_000:
                timeout = int(timeout * 1.1)  # +10% safety margin

            return timeout

    def uses_stdin(self) -> bool:
        """Gemini CLI uses command argument for prompt (not stdin)."""
        return False

    def is_api_based(self) -> bool:
        """Gemini CLI is command-line based."""
        return False

    def get_max_chunk_size(self) -> int:
        """
        Get maximum chunk size for Gemini.

        Based on Gemini specifications:
        - 1M token context window
        - ~4 chars per token ratio
        - Theoretical max: ~4M chars

        Using 1.5M chars (~375K tokens) provides:
        - Massive throughput compared to other providers
        - Reduces chunks by ~3x vs Claude
        - Still leaves 625K tokens for output and safety margin
        - Enables processing 721K char docs in 1 chunk instead of 3

        Performance impact:
        - 721K doc: 3 chunks → 1 chunk
        - Processing time: 15-25 min → 5-10 min

        Returns:
            int: 1,500,000 characters
        """
        return 1_500_000

    @property
    def name(self) -> str:
        return "Gemini CLI"

    def get_env(self) -> Optional[dict]:
        """
        Get custom environment variables for this provider.

        Returns:
            Optional[dict]: Environment variables to use for subprocess calls,
                          or None to use system default environment.
        """
        return None