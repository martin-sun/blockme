"""
Quality Validator - Skill File Quality Validation

Validates format, content, and quality of generated Skill files.
"""

import logging
import re
from pathlib import Path
from typing import Dict, List, Optional, Set

import yaml
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class ValidationIssue(BaseModel):
    """Validation issue."""

    severity: str = Field(..., description="Severity: error, warning, info")
    category: str = Field(..., description="Category: format, content, quality")
    message: str = Field(..., description="Issue description")
    line_number: Optional[int] = Field(None, description="Line number if applicable")


class ValidationResult(BaseModel):
    """Validation result."""

    is_valid: bool = Field(..., description="Whether validation passed")
    score: float = Field(..., ge=0.0, le=100.0, description="Quality score 0-100")
    errors: List[ValidationIssue] = Field(default_factory=list, description="Error list")
    warnings: List[ValidationIssue] = Field(default_factory=list, description="Warning list")
    info: List[ValidationIssue] = Field(default_factory=list, description="Info list")

    @property
    def total_issues(self) -> int:
        """Total number of issues."""
        return len(self.errors) + len(self.warnings)

    @property
    def quality_grade(self) -> str:
        """Quality grade based on score."""
        if self.score >= 90:
            return "A+"
        elif self.score >= 80:
            return "A"
        elif self.score >= 70:
            return "B"
        elif self.score >= 60:
            return "C"
        elif self.score >= 50:
            return "D"
        else:
            return "F"


class QualityValidator:
    """
    Skill file quality validator.

    Validates:
    - YAML front matter format and required fields
    - Markdown format and structure
    - Content completeness and quality
    - Link validity
    - Tax content accuracy
    """

    # Required YAML fields
    REQUIRED_YAML_FIELDS = ["id", "title", "description", "domain"]

    # Recommended YAML fields
    RECOMMENDED_YAML_FIELDS = ["tags", "category", "priority"]

    # Forbidden content patterns
    FORBIDDEN_PATTERNS = [
        (r"TODO", "Contains unfinished TODO marker"),
        (r"FIXME", "Contains FIXME marker"),
        (r"XXX", "Contains XXX marker"),
    ]

    # Tax terminology validation
    TAX_TERMS_CHECK = {
        "good": [
            "CRA", "Canada Revenue Agency", "tax credit", "deduction",
            "RRSP", "TFSA", "GST", "HST", "income tax"
        ],
        "questionable": [
            "IRS",  # US tax agency (should be CRA)
            "401k",  # US retirement plan (should be RRSP)
        ]
    }

    def __init__(self):
        """Initialize the validator."""
        pass

    def validate_file(self, file_path: str) -> ValidationResult:
        """
        Validate Skill file.

        Args:
            file_path: Path to Skill file

        Returns:
            ValidationResult with validation status and issues
        """
        file_path_obj = Path(file_path)

        if not file_path_obj.exists():
            return ValidationResult(
                is_valid=False,
                score=0.0,
                errors=[
                    ValidationIssue(
                        severity="error",
                        category="format",
                        message=f"File does not exist: {file_path}"
                    )
                ]
            )

        # Read file
        try:
            with open(file_path_obj, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            return ValidationResult(
                is_valid=False,
                score=0.0,
                errors=[
                    ValidationIssue(
                        severity="error",
                        category="format",
                        message=f"Cannot read file: {e}"
                    )
                ]
            )

        return self.validate_content(content)

    def validate_content(self, content: str) -> ValidationResult:
        """
        Validate Skill content.

        Args:
            content: Skill file content

        Returns:
            ValidationResult with validation status and issues
        """
        issues: List[ValidationIssue] = []

        # 1. YAML front matter validation
        yaml_issues, yaml_data = self._validate_yaml_frontmatter(content)
        issues.extend(yaml_issues)

        # 2. Markdown format validation
        markdown_issues = self._validate_markdown_format(content)
        issues.extend(markdown_issues)

        # 3. Content quality validation
        quality_issues = self._validate_content_quality(content)
        issues.extend(quality_issues)

        # 4. Tax content validation
        tax_issues = self._validate_tax_content(content)
        issues.extend(tax_issues)

        # 5. Link validation
        link_issues = self._validate_links(content)
        issues.extend(link_issues)

        # Categorize issues
        errors = [i for i in issues if i.severity == "error"]
        warnings = [i for i in issues if i.severity == "warning"]
        info_items = [i for i in issues if i.severity == "info"]

        # Calculate quality score
        score = self._calculate_score(errors, warnings, content)

        # Validation passes if no errors
        is_valid = len(errors) == 0

        return ValidationResult(
            is_valid=is_valid,
            score=score,
            errors=errors,
            warnings=warnings,
            info=info_items
        )

    def _validate_yaml_frontmatter(
        self,
        content: str
    ) -> tuple[List[ValidationIssue], Optional[Dict]]:
        """Validate YAML front matter."""
        issues = []
        yaml_data = None

        # Check for YAML front matter
        if not content.startswith('---'):
            issues.append(ValidationIssue(
                severity="error",
                category="format",
                message="Missing YAML front matter (should start with ---)",
                line_number=1
            ))
            return issues, None

        # Extract YAML content
        parts = content.split('---', 2)
        if len(parts) < 3:
            issues.append(ValidationIssue(
                severity="error",
                category="format",
                message="YAML front matter format error (missing closing ---)"
            ))
            return issues, None

        yaml_content = parts[1]

        # Parse YAML
        try:
            yaml_data = yaml.safe_load(yaml_content)
        except yaml.YAMLError as e:
            issues.append(ValidationIssue(
                severity="error",
                category="format",
                message=f"YAML parsing failed: {e}"
            ))
            return issues, None

        if not isinstance(yaml_data, dict):
            issues.append(ValidationIssue(
                severity="error",
                category="format",
                message="YAML front matter must be a dictionary"
            ))
            return issues, None

        # Check required fields
        for field in self.REQUIRED_YAML_FIELDS:
            if field not in yaml_data or not yaml_data[field]:
                issues.append(ValidationIssue(
                    severity="error",
                    category="content",
                    message=f"Missing required field: {field}"
                ))

        # Check recommended fields
        for field in self.RECOMMENDED_YAML_FIELDS:
            if field not in yaml_data or not yaml_data[field]:
                issues.append(ValidationIssue(
                    severity="warning",
                    category="content",
                    message=f"Recommended to add field: {field}"
                ))

        # Validate specific fields
        if "id" in yaml_data:
            if not re.match(r'^[a-z0-9-]+$', yaml_data["id"]):
                issues.append(ValidationIssue(
                    severity="error",
                    category="format",
                    message="ID format error (should be lowercase letters, numbers, and hyphens)"
                ))

        if "tags" in yaml_data:
            if not isinstance(yaml_data["tags"], list):
                issues.append(ValidationIssue(
                    severity="error",
                    category="format",
                    message="tags should be a list"
                ))

        return issues, yaml_data

    def _validate_markdown_format(self, content: str) -> List[ValidationIssue]:
        """Validate Markdown formatting."""
        issues = []

        # Extract Markdown content (skip YAML front matter)
        parts = content.split('---', 2)
        if len(parts) >= 3:
            markdown_content = parts[2]
        else:
            markdown_content = content

        # Check for main heading
        if not re.search(r'^#\s+.+$', markdown_content, re.MULTILINE):
            issues.append(ValidationIssue(
                severity="warning",
                category="format",
                message="Recommend adding main heading (# Heading)"
            ))

        # Check heading hierarchy
        headings = re.findall(r'^(#+)\s+(.+)$', markdown_content, re.MULTILINE)
        if headings:
            levels = [len(h[0]) for h in headings]
            # Check for level skipping (e.g., # to ###)
            for i in range(len(levels) - 1):
                if levels[i + 1] - levels[i] > 1:
                    issues.append(ValidationIssue(
                        severity="info",
                        category="format",
                        message=f"Heading level skip: from {'#' * levels[i]} to {'#' * levels[i + 1]}"
                    ))

        # Check list formatting
        list_lines = re.findall(r'^(\s*)([•\-\*]|\d+\.)\s', markdown_content, re.MULTILINE)
        if list_lines:
            # Check indent consistency
            indents = [len(line[0]) for line in list_lines]
            if len(set(indents)) > 3:  # More than 3 different indent levels
                issues.append(ValidationIssue(
                    severity="info",
                    category="format",
                    message="Many list indent levels, consider simplifying"
                ))

        # Check code blocks
        code_blocks = re.findall(r'```(\w*)\n(.*?)\n```', markdown_content, re.DOTALL)
        for lang, code in code_blocks:
            if not lang:
                issues.append(ValidationIssue(
                    severity="info",
                    category="format",
                    message="Code block should specify language"
                ))

        return issues

    def _validate_content_quality(self, content: str) -> List[ValidationIssue]:
        """Validate content quality."""
        issues = []

        # Extract Markdown content
        parts = content.split('---', 2)
        if len(parts) >= 3:
            markdown_content = parts[2].strip()
        else:
            markdown_content = content

        # Check content length
        word_count = len(markdown_content.split())
        if word_count < 100:
            issues.append(ValidationIssue(
                severity="warning",
                category="quality",
                message=f"Content is short ({word_count} words), recommend expansion"
            ))
        elif word_count < 50:
            issues.append(ValidationIssue(
                severity="error",
                category="quality",
                message=f"Content too short ({word_count} words), insufficient information"
            ))

        # Check for forbidden patterns
        for pattern, message in self.FORBIDDEN_PATTERNS:
            if re.search(pattern, content, re.IGNORECASE):
                issues.append(ValidationIssue(
                    severity="warning",
                    category="content",
                    message=message
                ))

        # Check for examples
        has_example = bool(re.search(
            r'(example|for instance|e\.g\.)',
            markdown_content,
            re.IGNORECASE
        ))
        if not has_example:
            issues.append(ValidationIssue(
                severity="info",
                category="quality",
                message="Recommend adding specific examples for improved usefulness"
            ))

        # Check for numbers/amounts
        has_numbers = bool(re.search(r'\$[\d,]+|\d+%', markdown_content))
        if not has_numbers:
            issues.append(ValidationIssue(
                severity="info",
                category="quality",
                message="Recommend adding specific numbers or dollar amount examples"
            ))

        return issues

    def _validate_tax_content(self, content: str) -> List[ValidationIssue]:
        """Validate tax content."""
        issues = []

        content_lower = content.lower()

        # Check for correct tax terminology
        good_terms_found = sum(
            1 for term in self.TAX_TERMS_CHECK["good"]
            if term.lower() in content_lower
        )

        if good_terms_found == 0:
            issues.append(ValidationIssue(
                severity="warning",
                category="content",
                message="No CRA-related professional terminology detected"
            ))

        # Check for incorrect terminology
        for term in self.TAX_TERMS_CHECK["questionable"]:
            if term.lower() in content_lower:
                issues.append(ValidationIssue(
                    severity="warning",
                    category="content",
                    message=f"Detected questionable term '{term}' (Is this Canadian tax documentation?)"
                ))

        # Check for specific tax forms
        tax_forms = re.findall(r'\b(T\d+[A-Z]?|RC\d+)\b', content)
        if not tax_forms:
            issues.append(ValidationIssue(
                severity="info",
                category="quality",
                message="Recommend referencing specific tax form numbers (e.g., T4, T1, RC)"
            ))

        return issues

    def _validate_links(self, content: str) -> List[ValidationIssue]:
        """Validate links."""
        issues = []

        # Extract all Markdown links
        links = re.findall(r'\[([^\]]+)\]\(([^)]+)\)', content)

        for link_text, link_url in links:
            # Check link text
            if not link_text or link_text.strip() == "":
                issues.append(ValidationIssue(
                    severity="warning",
                    category="format",
                    message="Link missing description text"
                ))

            # Check link URL
            if not link_url or link_url.strip() == "":
                issues.append(ValidationIssue(
                    severity="error",
                    category="format",
                    message=f"Link '{link_text}' missing URL"
                ))

            # Check for placeholders
            if link_url in ["#", "TODO", "FIXME"]:
                issues.append(ValidationIssue(
                    severity="warning",
                    category="content",
                    message=f"Link '{link_text}' uses placeholder URL: {link_url}"
                ))

        return issues

    def _calculate_score(
        self,
        errors: List[ValidationIssue],
        warnings: List[ValidationIssue],
        content: str
    ) -> float:
        """
        Calculate quality score.

        Args:
            errors: Error list
            warnings: Warning list
            content: Content

        Returns:
            Score from 0-100
        """
        # Base score 100
        score = 100.0

        # Deduct 15 points per error
        score -= len(errors) * 15

        # Deduct 5 points per warning
        score -= len(warnings) * 5

        # Add points for content length
        word_count = len(content.split())
        if word_count > 500:
            score += 5
        elif word_count > 1000:
            score += 10

        # Ensure in 0-100 range
        return max(0.0, min(100.0, score))


def validate_skill_file(file_path: str) -> ValidationResult:
    """
    Convenience function to validate Skill file.

    Args:
        file_path: Path to Skill file

    Returns:
        ValidationResult with validation status
    """
    validator = QualityValidator()
    return validator.validate_file(file_path)


def validate_skill_content(content: str) -> ValidationResult:
    """
    Convenience function to validate Skill content.

    Args:
        content: Skill content

    Returns:
        ValidationResult with validation status
    """
    validator = QualityValidator()
    return validator.validate_content(content)
