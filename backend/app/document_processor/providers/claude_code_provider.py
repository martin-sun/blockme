"""
Claude Code CLI Provider

Provider for Claude Code CLI using subscription-based access.
"""

import shutil
from typing import Optional


class ClaudeCodeProvider:
    """
    Provider for Claude Code CLI.

    Uses the local Claude Code CLI with subscription-based access.
    Command: claude --print --tools ''
    """

    def is_available(self) -> bool:
        """Check if claude CLI is available in PATH."""
        return shutil.which('claude') is not None

    def build_command(self, prompt: str) -> list[str]:
        """
        Build command for Claude CLI.

        Flags:
        - --print: Output to stdout (non-interactive mode)
        - --tools '': Disable tool usage (empty string)
        - --model sonnet: Use Sonnet 4.5 (balanced quality and speed)
        """
        return ['claude', '--print', '--tools', '', '--model', 'sonnet']

    def parse_output(self, stdout: str, stderr: str) -> str:
        """
        Parse Claude CLI output.

        Validates that:
        - Output is not empty
        - Output length > 50 characters
        - Output doesn't start with "Error"
        """
        enhanced = stdout.strip()

        if len(enhanced) < 50:
            raise ValueError(f"Output too short: {len(enhanced)} chars")

        if enhanced.startswith("Error"):
            raise ValueError(f"CLI returned error: {enhanced[:100]}")

        return enhanced

    def get_timeout(self, content_length: int) -> int:
        """
        Calculate timeout for Claude CLI.

        Formula: max(240 seconds, 5 seconds per 1K characters)
        Typical: 5-8 minutes for 300K chunk
        For skill enhancement: ~4-5 minutes for 40K prompt
        """
        MIN_TIMEOUT = 240  # 4 minutes minimum for skill enhancement
        TIMEOUT_PER_1K_CHARS = 5  # More time for content generation
        return max(MIN_TIMEOUT, content_length // 1000 * TIMEOUT_PER_1K_CHARS)

    def uses_stdin(self) -> bool:
        """Claude CLI accepts prompts via stdin."""
        return True

    def is_api_based(self) -> bool:
        """Claude CLI is command-line based."""
        return False

    def get_max_chunk_size(self) -> int:
        """
        Get maximum chunk size for Claude.

        Based on Claude Sonnet 4.5 specifications:
        - 200K token input limit
        - 64K token output limit
        - ~4 chars per token ratio

        Using 300K chars (~75K tokens) leaves safe margin for:
        - 75K input + 16K output = 91K tokens total
        - Well within 200K input limit
        - Ensures 64K output capacity remains available

        Returns:
            int: 300,000 characters
        """
        return 300_000

    @property
    def name(self) -> str:
        return "Claude Code"

    def get_env(self) -> Optional[dict]:
        """
        Get custom environment variables for this provider.

        Returns:
            Optional[dict]: Environment variables to use for subprocess calls,
                          or None to use system default environment.
        """
        return None