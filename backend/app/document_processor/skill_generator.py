"""
Skill Generator - Convert processed documents to Skill files

Generates Markdown files with YAML front matter compatible with MVP skill_loader.py
"""

import logging
import re
import time
from pathlib import Path
from typing import Dict, List, Optional

import yaml
from pydantic import BaseModel, Field

from .content_classifier import ClassificationResult, TaxCategory

logger = logging.getLogger(__name__)


class SkillMetadata(BaseModel):
    """Skill metadata for YAML front matter."""

    id: str = Field(..., description="Unique skill identifier (kebab-case)")
    title: str = Field(..., description="Skill title")
    tags: List[str] = Field(default_factory=list, description="Tag list")
    description: str = Field(..., description="Short description (1-2 sentences)")
    domain: str = Field(default="tax", description="Domain")
    priority: str = Field(default="medium", description="Priority: low, medium, high")
    category: str = Field(..., description="Tax category")
    source: str = Field(default="", description="Source document")
    quality_grade: str = Field(default="", description="Quality grade")


class SkillContent(BaseModel):
    """Skill content structure."""

    metadata: SkillMetadata = Field(..., description="Skill metadata")
    markdown_body: str = Field(..., description="Markdown body content")


class SkillGenerator:
    """
    Skill file generator.

    Features:
    - Convert classified content to Skill format
    - Generate YAML front matter
    - Organize Markdown content
    - Generate file names and directory structure
    """

    # Category to tags mapping
    CATEGORY_TAGS: Dict[TaxCategory, List[str]] = {
        TaxCategory.PERSONAL_INCOME: ["Personal Income Tax", "Individual", "Tax Filing"],
        TaxCategory.EMPLOYMENT_INCOME: ["Employment Income", "Salary", "T4"],
        TaxCategory.SELF_EMPLOYMENT: ["Self-Employment", "Business", "T4A"],
        TaxCategory.BUSINESS_INCOME: ["Business Income", "Corporation", "Enterprise"],
        TaxCategory.BUSINESS_EXPENSES: ["Business Expenses", "Deductions"],
        TaxCategory.CAPITAL_GAINS: ["Capital Gains", "Investment", "Property"],
        TaxCategory.DEDUCTIONS: ["Tax Deductions", "Tax Relief"],
        TaxCategory.CREDITS: ["Tax Credits", "Refunds"],
        TaxCategory.RRSP: ["RRSP", "Retirement Savings", "Retirement"],
        TaxCategory.TFSA: ["TFSA", "Tax-Free Savings", "Investment"],
        TaxCategory.GST_HST: ["GST", "HST", "Sales Tax"],
        TaxCategory.MEDICAL_EXPENSES: ["Medical Expenses", "Health"],
        TaxCategory.CHARITABLE_DONATIONS: ["Charitable Donations", "Charity"],
        TaxCategory.NON_RESIDENT_TAX: ["Non-Resident", "Immigration"],
        TaxCategory.FOREIGN_INCOME: ["Foreign Income", "Offshore"],
        TaxCategory.FILING_PROCEDURES: ["Filing Procedures", "Tax Return"],
        TaxCategory.PAYMENTS: ["Tax Payments", "Refunds"],
    }

    # Category to priority mapping
    CATEGORY_PRIORITY: Dict[TaxCategory, str] = {
        TaxCategory.PERSONAL_INCOME: "high",
        TaxCategory.EMPLOYMENT_INCOME: "high",
        TaxCategory.RRSP: "high",
        TaxCategory.TFSA: "high",
        TaxCategory.GST_HST: "high",
        TaxCategory.DEDUCTIONS: "medium",
        TaxCategory.CREDITS: "medium",
        TaxCategory.FILING_PROCEDURES: "medium",
    }

    def __init__(self, output_dir: str = "skills"):
        """
        Initialize the skill generator.

        Args:
            output_dir: Output directory for Skill files
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate_skill(
        self,
        content: str,
        classification: ClassificationResult,
        source_file: str = "",
        title: Optional[str] = None
    ) -> SkillContent:
        """
        Generate a Skill.

        Args:
            content: Document content
            classification: Classification result
            source_file: Source file path
            title: Custom title (optional)

        Returns:
            SkillContent with metadata and markdown body
        """
        # 1. Generate Skill ID
        skill_id = self._generate_skill_id(
            classification.primary_category,
            source_file
        )

        # 2. Generate title
        if not title:
            title = self._generate_title(
                classification.primary_category,
                content
            )

        # 3. Generate description
        description = self._generate_description(content)

        # 4. Generate tags
        tags = self._generate_tags(classification)

        # 5. Determine priority
        priority = self.CATEGORY_PRIORITY.get(
            classification.primary_category,
            "low"
        )

        # 6. Create metadata
        metadata = SkillMetadata(
            id=skill_id,
            title=title,
            tags=tags,
            description=description,
            domain="tax",
            priority=priority,
            category=classification.primary_category.value,
            source=source_file,
            quality_grade=classification.quality_metrics.quality_grade
        )

        # 7. Organize Markdown content
        markdown_body = self._organize_markdown_content(
            content,
            classification
        )

        return SkillContent(
            metadata=metadata,
            markdown_body=markdown_body
        )

    def save_skill(
        self,
        skill: SkillContent,
        subdirectory: Optional[str] = None
    ) -> Path:
        """
        Save Skill to file.

        Args:
            skill: Skill content
            subdirectory: Optional subdirectory for organization

        Returns:
            Path to saved file
        """
        # Determine output directory
        if subdirectory:
            output_path = self.output_dir / subdirectory
        else:
            output_path = self.output_dir

        output_path.mkdir(parents=True, exist_ok=True)

        # Generate file path
        file_path = output_path / f"{skill.metadata.id}.md"

        # Generate full content
        full_content = self._render_skill_file(skill)

        # Write file
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(full_content)

        logger.info(f"Skill saved: {file_path}")
        return file_path

    def _generate_skill_id(
        self,
        category: TaxCategory,
        source_file: str
    ) -> str:
        """
        Generate Skill ID.

        Format: {category}-{source-name} or {category}-{timestamp}

        Args:
            category: Tax category
            source_file: Source file path

        Returns:
            Skill ID in kebab-case
        """
        # Generate prefix from category
        category_prefix = category.value.replace("_", "-")

        # Extract name from source file
        if source_file:
            source_name = Path(source_file).stem
            # Clean filename
            source_name = re.sub(r'[^a-zA-Z0-9-]', '-', source_name.lower())
            source_name = re.sub(r'-+', '-', source_name).strip('-')
            skill_id = f"{category_prefix}-{source_name}"
        else:
            # Use timestamp
            timestamp = int(time.time())
            skill_id = f"{category_prefix}-{timestamp}"

        # Ensure ID doesn't exceed 50 characters
        if len(skill_id) > 50:
            skill_id = skill_id[:50].rstrip('-')

        return skill_id

    def _generate_title(
        self,
        category: TaxCategory,
        content: str
    ) -> str:
        """Generate Skill title."""
        # Try to extract first heading from content
        title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
        if title_match:
            title = title_match.group(1).strip()
            # Limit length
            if len(title) <= 100:
                return title

        # Generate default title based on category
        category_titles = {
            TaxCategory.PERSONAL_INCOME: "Personal Income Tax Guide",
            TaxCategory.EMPLOYMENT_INCOME: "Employment Income Tax Filing",
            TaxCategory.SELF_EMPLOYMENT: "Self-Employment Tax Guide",
            TaxCategory.BUSINESS_INCOME: "Business Income Tax",
            TaxCategory.CAPITAL_GAINS: "Capital Gains Tax",
            TaxCategory.RRSP: "RRSP Registered Retirement Savings Plan",
            TaxCategory.TFSA: "TFSA Tax-Free Savings Account",
            TaxCategory.GST_HST: "GST/HST Sales Tax",
            TaxCategory.DEDUCTIONS: "Tax Deductions",
            TaxCategory.CREDITS: "Tax Credits",
        }

        return category_titles.get(category, "CRA Tax Information")

    def _generate_description(self, content: str) -> str:
        """Generate short description from first paragraph."""
        # Remove markdown headings
        clean_content = re.sub(r'^#+\s+.+$', '', content, flags=re.MULTILINE)
        clean_content = clean_content.strip()

        # Extract first paragraph
        paragraphs = clean_content.split('\n\n')
        first_paragraph = paragraphs[0] if paragraphs else ""

        # Clean formatting
        first_paragraph = re.sub(r'\*\*(.+?)\*\*', r'\1', first_paragraph)
        first_paragraph = re.sub(r'\*(.+?)\*', r'\1', first_paragraph)
        first_paragraph = re.sub(r'\[(.+?)\]\(.+?\)', r'\1', first_paragraph)
        first_paragraph = first_paragraph.replace('\n', ' ')

        # Limit length
        if len(first_paragraph) > 200:
            first_paragraph = first_paragraph[:197] + "..."

        return first_paragraph or "CRA tax information"

    def _generate_tags(self, classification: ClassificationResult) -> List[str]:
        """Generate tag list."""
        tags = set()

        # Add primary category tags
        primary_tags = self.CATEGORY_TAGS.get(
            classification.primary_category,
            []
        )
        tags.update(primary_tags)

        # Add secondary category tags
        for secondary_cat in classification.secondary_categories[:2]:
            secondary_tags = self.CATEGORY_TAGS.get(secondary_cat, [])
            tags.update(secondary_tags[:2])  # Max 2 tags per secondary category

        # Add general tags
        tags.add("CRA")
        tags.add("Canadian Tax")

        # Convert to list and limit
        return sorted(list(tags))[:8]

    def _organize_markdown_content(
        self,
        content: str,
        classification: ClassificationResult
    ) -> str:
        """Organize Markdown content."""
        sections = []

        # Ensure main heading exists
        if not content.strip().startswith('#'):
            sections.append(f"# {self._generate_title(classification.primary_category, content)}\n")

        # Add main content
        sections.append(content.strip())

        # Add notice if quality is low
        if classification.quality_metrics.overall_score < 0.7:
            sections.append("\n## Notice\n")
            sections.append("This content was auto-generated. Please refer to official CRA documentation for the most accurate information.\n")

        # Add related topics if secondary categories exist
        if classification.secondary_categories:
            sections.append("\n## Related Topics\n")
            for cat in classification.secondary_categories[:3]:
                category_name = cat.value.replace("_", " ").title()
                sections.append(f"- {category_name}\n")

        return "\n".join(sections)

    def _render_skill_file(self, skill: SkillContent) -> str:
        """Render complete Skill file (YAML front matter + Markdown)."""
        # Convert metadata to dict
        metadata_dict = skill.metadata.model_dump(exclude_none=True)

        # Generate YAML front matter
        yaml_content = yaml.dump(
            metadata_dict,
            allow_unicode=True,
            sort_keys=False,
            default_flow_style=False
        )

        # Combine full content
        full_content = f"---\n{yaml_content}---\n\n{skill.markdown_body}\n"

        return full_content


def generate_and_save_skill(
    content: str,
    classification: ClassificationResult,
    output_dir: str = "skills",
    source_file: str = "",
    title: Optional[str] = None
) -> Path:
    """
    Convenience function to generate and save Skill.

    Args:
        content: Document content
        classification: Classification result
        output_dir: Output directory
        source_file: Source file path
        title: Custom title

    Returns:
        Path to saved Skill file
    """
    generator = SkillGenerator(output_dir)
    skill = generator.generate_skill(content, classification, source_file, title)

    # Save to subdirectory based on category
    subdirectory = classification.primary_category.value
    return generator.save_skill(skill, subdirectory)
