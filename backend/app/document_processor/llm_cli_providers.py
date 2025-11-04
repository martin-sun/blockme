"""
LLM CLI Provider Abstraction

Provides a unified interface for different local LLM CLI tools.
Supports Claude Code, Gemini CLI, OpenAI Codex, and others.
"""

import shutil
import subprocess
from abc import ABC, abstractmethod
from typing import Optional


class LLMCLIProvider(ABC):
    """
    Abstract base class for LLM CLI providers.

    Defines the interface that all LLM CLI providers must implement
    to work with the document processor's enhancement pipeline.
    """

    @abstractmethod
    def is_available(self) -> bool:
        """
        Check if the CLI tool is installed and available in PATH.

        Returns:
            bool: True if the CLI is available, False otherwise
        """
        pass

    @abstractmethod
    def build_command(self, prompt: str) -> list[str]:
        """
        Build the command array for subprocess execution.

        Args:
            prompt: The enhancement prompt to send to the LLM

        Returns:
            list[str]: Command array suitable for subprocess.run()
        """
        pass

    @abstractmethod
    def parse_output(self, stdout: str, stderr: str) -> str:
        """
        Parse and validate the CLI output.

        Args:
            stdout: Standard output from the CLI
            stderr: Standard error from the CLI

        Returns:
            str: Parsed and validated enhanced content

        Raises:
            ValueError: If output is invalid or indicates an error
        """
        pass

    @abstractmethod
    def get_timeout(self, content_length: int) -> int:
        """
        Calculate appropriate timeout based on content length.

        Args:
            content_length: Length of content to be processed (in characters)

        Returns:
            int: Timeout in seconds
        """
        pass

    @abstractmethod
    def uses_stdin(self) -> bool:
        """
        Determine if this provider accepts prompts via stdin.

        Returns:
            bool: True if prompt should be passed via stdin, False if via command argument
        """
        pass

    @abstractmethod
    def get_max_chunk_size(self) -> int:
        """
        Get the maximum recommended chunk size for this provider.

        Based on the provider's context window and optimal token limits.
        Allows each provider to process content at its optimal capacity.

        Returns:
            int: Maximum chunk size in characters
        """
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        """
        Get the display name of this provider.

        Returns:
            str: Provider name (e.g., "Claude Code", "Gemini CLI")
        """
        pass


class ClaudeCLIProvider(LLMCLIProvider):
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


class GeminiCLIProvider(LLMCLIProvider):
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
        enhanced = stdout.strip()

        if len(enhanced) < 50:
            raise ValueError(f"Output too short: {len(enhanced)} chars")

        # Check for common error patterns
        if stderr and ("error" in stderr.lower() or "failed" in stderr.lower()):
            raise ValueError(f"CLI error in stderr: {stderr[:200]}")

        return enhanced

    def get_timeout(self, content_length: int) -> int:
        """
        Calculate timeout for Gemini CLI.

        Gemini is typically faster than Claude but still needs time for generation.
        Formula: max(180 seconds, 3 seconds per 1K characters)
        For skill enhancement: ~3-4 minutes for 40K prompt
        """
        MIN_TIMEOUT = 180  # 3 minutes minimum for skill enhancement
        TIMEOUT_PER_1K_CHARS = 3  # Faster than Claude but still generous
        return max(MIN_TIMEOUT, content_length // 1000 * TIMEOUT_PER_1K_CHARS)

    def uses_stdin(self) -> bool:
        """Gemini CLI uses command argument for prompt (not stdin)."""
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


class CodexCLIProvider(LLMCLIProvider):
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


def get_provider(provider_name: str) -> Optional[LLMCLIProvider]:
    """
    Factory function to get a provider instance by name.

    Args:
        provider_name: Name of the provider ('claude', 'gemini', 'codex')

    Returns:
        LLMCLIProvider instance or None if provider not found

    Example:
        provider = get_provider('gemini')
        if provider and provider.is_available():
            # Use provider...
    """
    providers = {
        'claude': ClaudeCLIProvider,
        'gemini': GeminiCLIProvider,
        'codex': CodexCLIProvider,
    }

    provider_class = providers.get(provider_name.lower())
    if provider_class:
        return provider_class()
    return None


def detect_available_providers() -> list[str]:
    """
    Detect all available LLM CLI providers on the system.

    Returns:
        list[str]: Names of available providers (e.g., ['claude', 'gemini'])

    Example:
        available = detect_available_providers()
        print(f"Available providers: {', '.join(available)}")
    """
    available = []
    for name in ['claude', 'gemini', 'codex']:
        provider = get_provider(name)
        if provider and provider.is_available():
            available.append(name)
    return available
