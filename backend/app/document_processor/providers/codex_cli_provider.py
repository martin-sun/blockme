"""
Codex CLI Provider

Provider for OpenAI Codex CLI using command-line interface.
"""

import shutil
from typing import Optional


class CodexCLIProvider:
    """
    Provider for OpenAI Codex CLI.

    Uses OpenAI's Codex CLI for non-interactive code generation.
    Command: codex exec "prompt"

    Features:
    - OpenAI backing (high quality)
    - Open source on GitHub
    - Supports ChatGPT plan authentication
    - Default read-only mode (safe for content processing)

    Installation:
        Download from: https://github.com/openai/codex

    Authentication:
        Requires ChatGPT subscription or API key:
        - Interactive: `codex login`
        - Environment: `CODEX_API_KEY=your-key codex exec ...`

    Command Pattern:
        codex exec "your prompt here"
        Output: Streams to stderr, final message to stdout
    """

    def is_available(self) -> bool:
        """Check if codex CLI is available in PATH."""
        return shutil.which('codex') is not None

    def build_command(self, prompt: str) -> list[str]:
        """
        Build command for Codex CLI.

        Codex accepts prompts as command-line arguments, not stdin.
        Uses default read-only mode for safe content processing.
        """
        return ['codex', 'exec', prompt]

    def parse_output(self, stdout: str, stderr: str) -> str:
        """
        Parse Codex CLI output.

        Codex streams activity to stderr and final message to stdout.
        We only use stdout for the enhanced content.
        """
        enhanced = stdout.strip()

        if len(enhanced) < 50:
            raise ValueError(f"Output too short: {len(enhanced)} chars")

        # Stderr contains activity logs, not necessarily errors
        # Only check stdout for error messages
        if enhanced.lower().startswith("error"):
            raise ValueError(f"CLI error: {enhanced[:200]}")

        return enhanced

    def get_timeout(self, content_length: int) -> int:
        """
        Calculate timeout for Codex CLI.

        Using conservative estimate similar to Claude.
        Formula: max(240 seconds, 5 seconds per 1K characters)
        For skill enhancement: ~4-5 minutes for 40K prompt
        """
        MIN_TIMEOUT = 240  # 4 minutes minimum for skill enhancement
        TIMEOUT_PER_1K_CHARS = 5  # More time for content generation
        return max(MIN_TIMEOUT, content_length // 1000 * TIMEOUT_PER_1K_CHARS)

    def uses_stdin(self) -> bool:
        """
        Codex CLI uses command arguments, not stdin.

        The prompt is passed as an argument to `codex exec "prompt"`.
        """
        return False

    def is_api_based(self) -> bool:
        """Codex CLI is command-line based."""
        return False

    def get_max_chunk_size(self) -> int:
        """
        Get maximum chunk size for Codex.

        Based on estimated Codex specifications:
        - ~128K token context window (estimated)
        - ~4 chars per token ratio
        - Theoretical max: ~512K chars

        Using 250K chars (~62K tokens) provides:
        - Conservative limit to ensure stability
        - Leaves ample room for output
        - Slightly smaller than Claude to be safe
        - Prevents potential context overflow

        Returns:
            int: 250,000 characters
        """
        return 250_000

    @property
    def name(self) -> str:
        return "OpenAI Codex"

    def get_env(self) -> Optional[dict]:
        """
        Get custom environment variables for this provider.

        Returns:
            Optional[dict]: Environment variables to use for subprocess calls,
                          or None to use system default environment.
        """
        return None