"""
LLM CLI Provider Abstraction

Provides a unified interface for different local LLM CLI tools and API-based providers.
Supports Claude Code, Gemini CLI, OpenAI Codex, ZhipuAI GLM API, and others.
"""

import os
import shutil
import subprocess
from abc import ABC, abstractmethod
from typing import Optional

# 加载环境变量
from dotenv import load_dotenv
load_dotenv()


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
    def is_api_based(self) -> bool:
        """
        Determine if this provider uses API (not CLI).

        Returns:
            bool: True if provider uses API directly, False if CLI-based
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


class GLMAPIProvider(LLMCLIProvider):
    """
    Provider for ZhipuAI GLM API.

    Uses the ZhipuAI Python SDK to call GLM-4.6 model directly via API.
    This is an API-based provider, not a CLI tool.

    Features:
    - Uses GLM-4.6 model (high quality)
    - 128K token context window
    - Fast response times
    - Direct API integration (no CLI needed)

    Configuration:
    - Requires GLM_API_KEY environment variable
    - Model: glm-4.6 (can be changed via model parameter)
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
            except ImportError:
                raise ImportError("zhipuai package is required. Install with: pip install zhipuai>=2.1.0")

        return self._client

    def is_available(self) -> bool:
        """Check if GLM API is available (API key exists and package installed)."""
        try:
            api_key = os.environ.get("GLM_API_KEY")
            if not api_key:
                return False

            from zhipuai import ZhipuAI
            return True
        except ImportError:
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

            response = client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,  # Lower temperature for consistent output
                max_tokens=8192,  # Reasonable output limit
            )

            enhanced = response.choices[0].message.content.strip()

            if len(enhanced) < 50:
                raise ValueError(f"GLM API response too short: {len(enhanced)} chars")

            return enhanced

        except Exception as e:
            raise ValueError(f"GLM API call failed: {str(e)}")

    def get_timeout(self, content_length: int) -> int:
        """
        Calculate timeout for GLM API.

        GLM API typically has fast response times.
        Formula: max(120 seconds, 2 seconds per 1K characters)
        For skill enhancement: ~2-3 minutes for 40K prompt

        Args:
            content_length: Length of content to be processed

        Returns:
            int: Timeout in seconds
        """
        MIN_TIMEOUT = 120  # 2 minutes minimum for skill enhancement
        TIMEOUT_PER_1K_CHARS = 2  # Fast API response
        return max(MIN_TIMEOUT, content_length // 1000 * TIMEOUT_PER_1K_CHARS)

    def uses_stdin(self) -> bool:
        """GLM API doesn't use stdin (direct Python calls)."""
        return False

    def is_api_based(self) -> bool:
        """GLM provider uses API directly."""
        return True

    def get_max_chunk_size(self) -> int:
        """
        Get maximum chunk size for GLM-4.6.

        Based on GLM-4.6 specifications:
        - 128K token context window
        - Chinese chars: ~1-2 tokens per char
        - English chars: ~4 chars per token

        Using 150K chars (~38K-75K tokens) provides:
        - Safe buffer for input + output (leaves 53K-90K tokens for response)
        - Conservative but safe approach
        - Similar capacity to Claude's 150K chars
        - Ensures reliable processing without context overflow

        Returns:
            int: 150,000 characters
        """
        return 150_000

    @property
    def name(self) -> str:
        return f"GLM API ({self.model})"


def get_provider(provider_name: str) -> Optional[LLMCLIProvider]:
    """
    Factory function to get a provider instance by name.

    Args:
        provider_name: Name of the provider ('claude', 'gemini', 'codex', 'glm-api')

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
        'glm-api': GLMAPIProvider,
    }

    provider_class = providers.get(provider_name.lower())
    if provider_class:
        return provider_class()
    return None


def detect_available_providers() -> list[str]:
    """
    Detect all available LLM CLI providers on the system.

    Returns:
        list[str]: Names of available providers (e.g., ['claude', 'gemini', 'glm-api'])

    Example:
        available = detect_available_providers()
        print(f"Available providers: {', '.join(available)}")
    """
    available = []
    for name in ['claude', 'gemini', 'codex', 'glm-api']:
        provider = get_provider(name)
        if provider and provider.is_available():
            available.append(name)
    return available
