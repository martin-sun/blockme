"""SKILL.md AI enhancement engine."""

import logging
import shutil
import subprocess
from pathlib import Path
from typing import Dict, Tuple, List

from .llm_cli_providers import LLMCLIProvider
from .enhancement_prompts import build_enhancement_prompt
from .enhancement_validator import EnhancementValidator


logger = logging.getLogger(__name__)


class SkillEnhancer:
    """SKILL.md AI enhancement engine using Skill_Seekers pattern."""

    def __init__(self):
        """Initialize the skill enhancer."""
        self.validator = EnhancementValidator()

    def enhance_skill(
        self,
        skill_dir: Path,
        provider: LLMCLIProvider
    ) -> bool:
        """
        Main enhancement workflow.

        Steps:
        1. Create backup
        2. Read references
        3. Build prompt
        4. Call LLM
        5. Validate output
        6. Save or restore

        Args:
            skill_dir: Path to skill directory
            provider: LLM CLI provider instance

        Returns:
            True if successful, False if failed
        """
        skill_path = skill_dir / "SKILL.md"
        backup_path = None

        try:
            # 1. Create backup
            backup_path = self.create_backup(skill_path)
            logger.info(f"✅ Backup created: {backup_path}")

            # 2. Read references
            references = self.read_references(skill_dir)
            if not references:
                logger.error("❌ No reference files found")
                return False

            logger.info(f"📖 Read {len(references)} reference files")

            # 3. Read current SKILL.md
            current_skill = skill_path.read_text(encoding='utf-8') if skill_path.exists() else ""

            # 4. Build prompt
            skill_name = skill_dir.name
            prompt = build_enhancement_prompt(skill_name, current_skill, references)

            logger.info(f"📝 Prompt size: {len(prompt):,} chars")

            # 5. Call LLM
            timeout = provider.get_timeout(len(prompt))
            logger.info(f"🤖 Calling {provider.name} (timeout: {timeout}s)")

            enhanced = self.call_llm(provider, prompt, timeout)

            # 6. Validate
            is_valid, warnings = self.validate_enhancement(enhanced)

            if warnings:
                logger.warning(f"⚠️  Validation warnings: {warnings}")

            if not is_valid:
                logger.error("❌ Validation failed, restoring backup")
                self.restore_backup(backup_path, skill_path)
                return False

            # 7. Save enhanced
            skill_path.write_text(enhanced, encoding='utf-8')
            logger.info("✅ Enhanced SKILL.md saved")

            # Calculate quality score
            quality_score = self.validator.get_quality_score(enhanced)
            logger.info(f"📊 Quality score: {quality_score:.1f}/10")

            return True

        except subprocess.TimeoutExpired:
            logger.error(f"❌ LLM timeout after {timeout}s, restoring backup")
            if backup_path:
                self.restore_backup(backup_path, skill_path)
            return False

        except Exception as e:
            logger.error(f"❌ Enhancement failed: {e}")
            if backup_path:
                self.restore_backup(backup_path, skill_path)
            return False

    def read_references(
        self,
        skill_dir: Path,
        max_total_chars: int = 50_000,
        max_per_file: int = 15_000
    ) -> Dict[str, str]:
        """
        Read reference files with size limits.

        Args:
            skill_dir: Path to skill directory
            max_total_chars: Maximum total characters across all references
            max_per_file: Maximum characters per individual file

        Returns:
            Dict mapping filename to content
        """
        references_dir = skill_dir / "references"
        if not references_dir.exists():
            logger.warning(f"References directory not found: {references_dir}")
            return {}

        references = {}
        total_chars = 0

        # Get all .md files except index.md, sorted by name
        md_files = sorted([
            f for f in references_dir.glob("*.md")
            if f.name != "index.md"
        ])

        if not md_files:
            logger.warning(f"No markdown files found in {references_dir}")
            return {}

        for md_file in md_files:
            if total_chars >= max_total_chars:
                logger.warning(f"Reached total char limit ({max_total_chars:,}), stopping at {len(references)} files")
                break

            try:
                content = md_file.read_text(encoding='utf-8')

                # Truncate if needed
                if len(content) > max_per_file:
                    content = content[:max_per_file] + "\n\n[Content truncated...]"
                    logger.debug(f"Truncated {md_file.name} to {max_per_file:,} chars")

                references[md_file.name] = content
                total_chars += len(content)

                logger.debug(f"Read {md_file.name}: {len(content):,} chars")

            except Exception as e:
                logger.warning(f"Failed to read {md_file.name}: {e}")
                continue

        logger.info(f"Total reference content: {total_chars:,} chars from {len(references)} files")

        return references

    def call_llm(
        self,
        provider: LLMCLIProvider,
        prompt: str,
        timeout: int = 300
    ) -> str:
        """
        Call LLM via existing provider infrastructure.

        Args:
            provider: LLM CLI provider instance
            prompt: Enhancement prompt
            timeout: Timeout in seconds

        Returns:
            Enhanced SKILL.md content

        Raises:
            subprocess.TimeoutExpired: If LLM call times out
            ValueError: If LLM output is invalid
        """
        # Build command
        command = provider.build_command(prompt)

        logger.debug(f"Executing command: {' '.join(command[:3])}...")

        # Execute command
        if provider.uses_stdin():
            # Pass prompt via stdin
            result = subprocess.run(
                command,
                input=prompt,
                capture_output=True,
                text=True,
                timeout=timeout
            )
        else:
            # Prompt is already in command
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=timeout
            )

        # Check for errors
        if result.returncode != 0:
            logger.error(f"LLM CLI failed with return code {result.returncode}")
            logger.error(f"stderr: {result.stderr[:500]}")
            raise ValueError(f"LLM CLI failed: {result.stderr[:200]}")

        # Parse output
        enhanced = provider.parse_output(result.stdout, result.stderr)

        logger.info(f"✅ LLM returned {len(enhanced):,} chars")

        return enhanced

    def validate_enhancement(
        self,
        content: str
    ) -> Tuple[bool, List[str]]:
        """
        Validate enhanced SKILL.md.

        Checks:
        - Minimum length (500 chars)
        - Required sections present
        - Has code blocks
        - Valid markdown structure
        - CRA-specific content

        Args:
            content: Enhanced SKILL.md content

        Returns:
            (is_valid, warnings)
        """
        return self.validator.validate(content)

    def create_backup(self, skill_path: Path) -> Path:
        """
        Create .backup file.

        Args:
            skill_path: Path to SKILL.md

        Returns:
            Path to backup file

        Raises:
            FileNotFoundError: If skill_path doesn't exist
        """
        if not skill_path.exists():
            raise FileNotFoundError(f"SKILL.md not found: {skill_path}")

        backup_path = skill_path.with_suffix('.md.backup')

        # Copy the file
        shutil.copy2(skill_path, backup_path)

        logger.debug(f"Created backup: {backup_path}")

        return backup_path

    def restore_backup(self, backup_path: Path, skill_path: Path) -> None:
        """
        Restore from backup on failure.

        Args:
            backup_path: Path to backup file
            skill_path: Path to SKILL.md
        """
        if not backup_path.exists():
            logger.error(f"Backup file not found: {backup_path}")
            return

        try:
            shutil.copy2(backup_path, skill_path)
            logger.info(f"✅ Restored from backup: {backup_path}")
        except Exception as e:
            logger.error(f"❌ Failed to restore backup: {e}")
