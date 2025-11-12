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

# Import all providers from separate modules
from .providers.glm_api_provider import GLMAPIProvider
from .providers.claude_code_provider import ClaudeCodeProvider
from .providers.gemini_cli_provider import GeminiCLIProvider
from .providers.gemini_api_provider import GeminiAPIProvider
from .providers.codex_cli_provider import CodexCLIProvider

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
        'claude': ClaudeCodeProvider,
        'glm-api': GLMAPIProvider,
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
    for name in ['claude', 'glm-api', 'gemini', 'gemini-api', 'codex']:
        provider = get_provider(name)
        if provider and provider.is_available():
            available.append(name)
    return available
