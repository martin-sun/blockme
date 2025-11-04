"""Enhancement validation logic for SKILL.md quality assurance."""

import re
from typing import Tuple, List


class EnhancementValidator:
    """Validate enhanced SKILL.md quality."""

    def __init__(self):
        """Initialize validator with quality criteria."""
        self.required_sections = [
            "When to Use This Skill",
            "Quick Reference",
            "Reference Documentation"
        ]
        self.cra_forms = ['T1', 'T2', 'T4', 'Schedule']
        self.tax_terms = ['tax', 'deduction', 'credit', 'CRA', 'income']

    def validate(self, content: str) -> Tuple[bool, List[str]]:
        """
        Validate enhanced SKILL.md.

        Args:
            content: Enhanced SKILL.md content

        Returns:
            (is_valid, warnings_list)
            - is_valid: True if content meets quality standards
            - warnings_list: List of validation warnings/issues
        """
        warnings = []

        # Check 1: Minimum length
        if len(content) < 500:
            warnings.append(f"Content too short ({len(content)} chars < 500 chars minimum)")

        # Check 2: Required sections
        for section in self.required_sections:
            if section not in content:
                warnings.append(f"Missing required section: '{section}'")

        # Check 3: Code blocks (at least 2 examples)
        code_block_count = content.count('```')
        num_code_blocks = code_block_count // 2
        if code_block_count < 4:  # Opening + closing for 2 blocks
            warnings.append(f"Insufficient code examples (found {num_code_blocks}, need at least 2)")

        # Check 4: Valid markdown structure
        has_frontmatter = content.startswith('---')
        has_heading = '# ' in content
        if not has_frontmatter and not has_heading:
            warnings.append("Missing frontmatter or main heading")

        # Check 5: CRA-specific content - form references
        found_forms = [form for form in self.cra_forms if form in content]
        if not found_forms:
            warnings.append(f"Missing CRA form references (expected: {', '.join(self.cra_forms)})")

        # Check 6: Tax-specific terminology
        found_terms = [term for term in self.tax_terms if term.lower() in content.lower()]
        if len(found_terms) < 3:
            warnings.append(f"Insufficient tax-specific terminology (found only {len(found_terms)} terms)")

        # Check 7: Examples with numbers (tax calculations)
        # Look for dollar amounts or percentages in the content
        has_dollar_amounts = bool(re.search(r'\$[\d,]+', content))
        has_percentages = bool(re.search(r'\d+%', content))
        if not (has_dollar_amounts or has_percentages):
            warnings.append("Missing concrete examples with numbers (tax calculations, dollar amounts, or percentages)")

        # Check 8: Frontmatter structure (if present)
        if has_frontmatter:
            frontmatter_match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
            if frontmatter_match:
                frontmatter = frontmatter_match.group(1)
                if 'id:' not in frontmatter:
                    warnings.append("Frontmatter missing 'id' field")
                if 'title:' not in frontmatter:
                    warnings.append("Frontmatter missing 'title' field")

        # Validation passes if <= 2 warnings
        # Allow some flexibility for edge cases
        is_valid = len(warnings) <= 2

        return is_valid, warnings

    def validate_strict(self, content: str) -> Tuple[bool, List[str]]:
        """
        Strict validation - all checks must pass.

        Args:
            content: Enhanced SKILL.md content

        Returns:
            (is_valid, warnings_list)
        """
        is_valid, warnings = self.validate(content)
        # In strict mode, any warning means failure
        return len(warnings) == 0, warnings

    def get_quality_score(self, content: str) -> float:
        """
        Calculate quality score (0-10).

        Args:
            content: Enhanced SKILL.md content

        Returns:
            Quality score from 0 to 10
        """
        is_valid, warnings = self.validate(content)

        # Start with base score
        score = 10.0

        # Deduct points for each warning
        # Major issues: -2 points
        major_issues = [
            "Content too short",
            "Missing required section",
            "Missing frontmatter or main heading"
        ]
        # Minor issues: -1 point
        minor_issues = [
            "Insufficient code examples",
            "Missing CRA form references",
            "Insufficient tax-specific terminology",
            "Missing concrete examples"
        ]

        for warning in warnings:
            if any(issue in warning for issue in major_issues):
                score -= 2.0
            elif any(issue in warning for issue in minor_issues):
                score -= 1.0
            else:
                score -= 0.5

        # Ensure score is in valid range
        score = max(0.0, min(10.0, score))

        return score
