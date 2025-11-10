"""
LLM CLI Provider Abstraction

Provides a unified interface for different local LLM CLI tools and API-based providers.
Supports Claude Code, Gemini CLI, OpenAI Codex, ZhipuAI GLM API, and others.
"""

import os
import shutil
import subprocess
import time
import logging
from abc import ABC, abstractmethod
from typing import Optional, List, Tuple

# 加载环境变量
from dotenv import load_dotenv
load_dotenv()

logger = logging.getLogger(__name__)


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

    def get_env(self) -> Optional[dict]:
        """
        Get custom environment variables for this provider.

        Returns:
            Optional[dict]: Environment variables to use for subprocess calls,
                          or None to use system default environment.
        """
        return None

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



class GLMClaudeCodeProvider(LLMCLIProvider):
    """
    Provider for GLM model through Claude Code CLI.

    Uses the ccc glm command to launch Claude Code with GLM-4.6 model.
    This provides local processing with Chinese language advantages.
    Command: ccc glm --print --tools ''

    Features:
    - Local GLM-4.6 model processing
    - Chinese language optimization
    - Large context window support
    - No API dependencies or costs
    - Optimized timeout configuration for better performance
    - Environment variable caching (ccm glm runs only once)
    """

    def __init__(self):
        """Initialize GLM provider with environment caching."""
        self._cached_env = None

    def is_available(self) -> bool:
        """Check if ccc command is available (shell function or executable)."""
        import subprocess
        import os

        # Check if claude CLI is available (required)
        claude_available = shutil.which('claude') is not None
        if not claude_available:
            return False

        # Check if ccm script is available
        ccm_script = os.path.expanduser("~/.local/share/ccm/ccm.sh")
        if not os.path.isfile(ccm_script):
            return False

        # Try to run ccm to see if it works
        try:
            result = subprocess.run(
                ['bash', ccm_script, 'status'],
                capture_output=True,
                timeout=10
            )
            # If we can run ccm, we assume ccc functionality is available
            return True
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False

    def _init_env(self) -> dict:
        """
        Initialize GLM environment by running ccm glm and parsing environment variables.

        This method executes 'ccm glm' once and caches the environment variables
        for all subsequent claude CLI calls.

        Uses shell eval to properly expand variable references like ${GLM_API_KEY}.

        Returns:
            dict: Environment variables with GLM configuration

        Raises:
            Exception: If ccm glm fails to execute
        """
        if self._cached_env is not None:
            return self._cached_env

        logger.info("Initializing GLM environment (running ccm glm once)...")

        try:
            # Get ccm script path
            ccm_script = os.path.expanduser("~/.local/share/ccm/ccm.sh")
            if not os.path.isfile(ccm_script):
                raise Exception(f"ccm script not found at {ccm_script}")

            # Use eval to execute ccm glm output and expand variables
            # sed comments out problematic unset lines
            # This allows shell to expand variable references like ${GLM_API_KEY}
            bash_command = (
                f'eval "$(bash {ccm_script} glm 2>/dev/null | sed \'s/^unset/# unset/\')" && '
                'printenv'
            )

            result = subprocess.run(
                ['bash', '-c', bash_command],
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode != 0:
                raise Exception(f"Failed to get GLM environment: {result.stderr}")

            # Parse printenv output (format: KEY=value)
            env = {}
            for line in result.stdout.splitlines():
                line = line.strip()
                if '=' in line:
                    # Split on first '=' to handle values containing '='
                    key, value = line.split('=', 1)
                    env[key] = value

            # Verify essential GLM variables are present
            required_vars = ['ANTHROPIC_BASE_URL', 'ANTHROPIC_AUTH_TOKEN', 'ANTHROPIC_MODEL']
            missing_vars = [var for var in required_vars if var not in env or not env[var]]

            if missing_vars:
                logger.warning(f"Missing or empty GLM environment variables: {missing_vars}")
                logger.debug(f"Available ANTHROPIC_* vars: {[k for k in env.keys() if 'ANTHROPIC' in k]}")

            self._cached_env = env
            logger.info("GLM environment initialized and cached successfully")
            logger.debug(f"  ANTHROPIC_BASE_URL: {env.get('ANTHROPIC_BASE_URL', 'NOT SET')}")
            logger.debug(f"  ANTHROPIC_MODEL: {env.get('ANTHROPIC_MODEL', 'NOT SET')}")
            logger.debug(f"  ANTHROPIC_AUTH_TOKEN: {'SET' if env.get('ANTHROPIC_AUTH_TOKEN') else 'NOT SET'}")

            return env

        except subprocess.TimeoutExpired:
            raise Exception("ccm glm timed out")
        except Exception as e:
            raise Exception(f"Failed to initialize GLM environment: {str(e)}")

    def build_command(self, prompt: str) -> list[str]:
        """
        Build command for GLM through Claude Code.

        Environment variables are managed separately via get_env() method,
        which caches the ccm glm output. This command just launches claude CLI.

        Returns:
            list[str]: Command to run claude CLI with GLM backend
        """
        return ['claude', '--print', '--tools', '']

    def parse_output(self, stdout: str, stderr: str) -> str:
        """
        Parse GLM Claude Code output.

        Similar to Claude CLI but handles GLM-specific output patterns.
        Validates that output is substantial and error-free.
        """
        enhanced = stdout.strip()

        if len(enhanced) < 50:
            raise ValueError(f"GLM output too short: {len(enhanced)} chars")

        if enhanced.startswith("Error") or enhanced.startswith("❌"):
            raise ValueError(f"GLM CLI returned error: {enhanced[:100]}")

        return enhanced

    def get_timeout(self, content_length: int) -> int:
        """
        Calculate optimized timeout for GLM Claude Code.

        GLM-4.6 processes much faster than the previous conservative estimate.
        Based on observed performance with session optimization:
        - Further reduced base timeout and processing rate
        - Added maximum timeout limit to prevent excessive waiting
        - Optimized for typical GLM performance with session reuse

        Expected performance with session optimization:
        - Small chunks (10K chars): ~60s
        - Medium chunks (100K chars): ~120s
        - Large chunks (300K chars): ~240s
        """
        MIN_TIMEOUT = 60   # 1 minute minimum for small chunks
        MAX_TIMEOUT = 300  # 5 minutes maximum for any chunk
        TIMEOUT_PER_1K_CHARS = 0.8  # Much faster processing with session optimization

        calculated_timeout = max(MIN_TIMEOUT, int(content_length // 1000 * TIMEOUT_PER_1K_CHARS))
        return min(MAX_TIMEOUT, calculated_timeout)

    def uses_stdin(self) -> bool:
        """GLM through Claude Code accepts prompts via stdin."""
        return True

    def is_api_based(self) -> bool:
        """GLM Claude Code is command-line based."""
        return False

    def get_max_chunk_size(self) -> int:
        """
        Get maximum chunk size for GLM-4.6.

        Based on GLM-4.6 specifications:
        - 128K token context window
        - ~4 chars per token ratio
        - Optimized for Chinese content processing

        Using 400K chars (~100K tokens) provides good balance:
        - Leverages GLM's large context advantage
        - Leaves room for response generation
        - Optimized for Chinese document processing

        Returns:
            int: 400,000 characters
        """
        return 400_000

    def get_env(self) -> Optional[dict]:
        """
        Get cached GLM environment variables.

        Initializes environment on first call by running 'ccm glm' and parsing
        the export statements. Subsequent calls return the cached environment.

        Returns:
            dict: Environment variables with GLM configuration
        """
        return self._init_env()

    @property
    def name(self) -> str:
        return "GLM via Claude Code"


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


class GeminiAPIProvider(LLMCLIProvider):
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



def get_provider(provider_name: str) -> Optional[LLMCLIProvider]:
    """
    Factory function to get a provider instance by name.

    Args:
        provider_name: Name of the provider ('claude', 'glm-claude', 'gemini', 'gemini-api', 'codex')

    Returns:
        LLMCLIProvider instance or None if provider not found

    Example:
        provider = get_provider('glm-claude')
        if provider and provider.is_available():
            # Use GLM through Claude Code...
    """
    providers = {
        'claude': ClaudeCLIProvider,
        'glm-claude': GLMClaudeCodeProvider,
        'gemini': GeminiCLIProvider,
        'gemini-api': GeminiAPIProvider,
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
        list[str]: Names of available providers (e.g., ['claude', 'glm-claude', 'gemini', 'gemini-api', 'codex'])

    Example:
        available = detect_available_providers()
        print(f"Available providers: {', '.join(available)}")
    """
    available = []
    for name in ['claude', 'glm-claude', 'gemini', 'gemini-api', 'codex']:
        provider = get_provider(name)
        if provider and provider.is_available():
            available.append(name)
    return available
