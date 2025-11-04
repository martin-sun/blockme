#!/usr/bin/env python3
"""
Enhance SKILL.md using AI (Skill_Seekers pattern).

Usage:
    # Basic usage
    uv run python enhance_skill.py --skill-dir skills_output/business-income-t4012-24e

    # With specific provider
    uv run python enhance_skill.py --skill-dir PATH --provider claude

    # Force re-enhancement
    uv run python enhance_skill.py --skill-dir PATH --force

    # Verbose logging
    uv run python enhance_skill.py --skill-dir PATH --verbose
"""

import argparse
import logging
import sys
from pathlib import Path

from app.document_processor.skill_enhancer import SkillEnhancer
from app.document_processor.llm_cli_providers import get_provider, detect_available_providers


def setup_logging(verbose: bool = False):
    """Configure logging."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Enhance SKILL.md with AI',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Enhance with default provider (claude)
    %(prog)s --skill-dir skills_output/business-income-t4012-24e

    # Use Gemini (faster, cheaper)
    %(prog)s --skill-dir PATH --provider gemini

    # Force re-enhancement even if already enhanced
    %(prog)s --skill-dir PATH --force
        """
    )

    parser.add_argument(
        '--skill-dir',
        required=True,
        type=Path,
        help='Path to skill directory (must contain SKILL.md and references/)'
    )

    parser.add_argument(
        '--provider',
        default='claude',
        choices=['claude', 'gemini', 'codex'],
        help='LLM provider to use (default: claude)'
    )

    parser.add_argument(
        '--force',
        action='store_true',
        help='Force re-enhancement even if .backup exists'
    )

    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )

    args = parser.parse_args()

    # Setup logging
    setup_logging(args.verbose)
    logger = logging.getLogger(__name__)

    print("=" * 60)
    print("SKILL.md AI Enhancement")
    print("=" * 60)

    # Validate skill directory
    skill_dir = args.skill_dir.resolve()
    if not skill_dir.exists():
        print(f"❌ Error: Skill directory not found: {skill_dir}")
        return 1

    skill_md = skill_dir / "SKILL.md"
    if not skill_md.exists():
        print(f"❌ Error: SKILL.md not found in {skill_dir}")
        return 1

    references_dir = skill_dir / "references"
    if not references_dir.exists():
        print(f"❌ Error: references/ directory not found in {skill_dir}")
        return 1

    # Check if already enhanced (unless --force)
    backup_file = skill_dir / "SKILL.md.backup"
    if backup_file.exists() and not args.force:
        print(f"⚠️  Warning: Backup file already exists: {backup_file}")
        print("   This skill may have already been enhanced.")
        print("   Use --force to re-enhance anyway.")
        response = input("Continue anyway? (y/N): ")
        if response.lower() != 'y':
            print("Aborted.")
            return 0

    # Detect available providers
    available_providers = detect_available_providers()
    print(f"\n📋 Available LLM providers: {', '.join(available_providers) if available_providers else 'None'}")

    # Get provider
    provider = get_provider(args.provider)
    if not provider:
        print(f"❌ Error: Unknown provider: {args.provider}")
        print(f"   Available providers: {', '.join(['claude', 'gemini', 'codex'])}")
        return 1

    if not provider.is_available():
        print(f"❌ Error: {provider.name} CLI is not installed or not in PATH")
        print(f"\nInstallation instructions:")
        if args.provider == 'claude':
            print("   Visit: https://claude.com/download")
        elif args.provider == 'gemini':
            print("   Run: npm install -g @google/gemini-cli")
        elif args.provider == 'codex':
            print("   Visit: https://github.com/openai/codex")
        return 1

    print(f"\n🤖 Using provider: {provider.name}")
    print(f"📁 Skill directory: {skill_dir}")
    print(f"📄 SKILL.md: {skill_md}")
    print(f"📚 References: {references_dir}")

    # Count reference files
    reference_files = list(references_dir.glob("*.md"))
    reference_files = [f for f in reference_files if f.name != "index.md"]
    print(f"📖 Found {len(reference_files)} reference files")

    # Estimate processing time
    print(f"\n⏱️  Estimated time: 30-60 seconds")
    print(f"💾 Backup will be saved to: {backup_file}")

    # Confirm
    print("\n" + "=" * 60)
    response = input("Proceed with enhancement? (Y/n): ")
    if response.lower() == 'n':
        print("Aborted.")
        return 0

    # Run enhancement
    print("\n🚀 Starting enhancement...")
    print("=" * 60)

    enhancer = SkillEnhancer()

    try:
        success = enhancer.enhance_skill(skill_dir, provider)
    except KeyboardInterrupt:
        print("\n\n❌ Enhancement interrupted by user")
        return 1

    print("=" * 60)

    if success:
        print("\n✅ SUCCESS: SKILL.md enhanced successfully!")
        print(f"📄 Enhanced file: {skill_md}")
        print(f"💾 Backup saved: {backup_file}")

        # Show file size comparison
        backup_size = backup_file.stat().st_size
        enhanced_size = skill_md.stat().st_size
        print(f"\n📊 File size:")
        print(f"   Before: {backup_size:,} bytes")
        print(f"   After:  {enhanced_size:,} bytes")
        print(f"   Growth: {enhanced_size - backup_size:+,} bytes ({enhanced_size / backup_size:.1f}x)")

        return 0
    else:
        print("\n❌ FAILED: Enhancement failed")
        print("   Check logs above for details")
        print("   Original SKILL.md has been restored")
        return 1


if __name__ == '__main__':
    sys.exit(main())
