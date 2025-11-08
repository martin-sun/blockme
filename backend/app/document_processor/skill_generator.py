"""
Skill Generator - Convert processed documents to Skill files

Generates Markdown files with YAML front matter compatible with MVP skill_loader.py
"""

import hashlib
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
        self.max_skill_lines = 500  # Claude Skills best practice

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
        Save Skill to file (legacy single-file mode).

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

    def save_skill_directory(
        self,
        skill_id: str,
        raw_text: str,
        reference_chunks: List[dict],
        metadata: SkillMetadata,
        subdirectory: Optional[str] = None
    ) -> Path:
        """
        Save skill as directory structure (Skill_Seekers pattern).

        Creates:
        - skill_id/
          - SKILL.md (lightweight index)
          - references/
            - index.md (navigation)
            - {chunk-slug}.md (enhanced content)
          - raw/
            - full-extract.txt (original text)

        Args:
            skill_id: Skill identifier
            raw_text: Original extracted text
            reference_chunks: List of enhanced chunks with metadata
            metadata: Skill metadata
            subdirectory: Optional parent subdirectory

        Returns:
            Path to skill directory
        """
        # Create skill directory
        if subdirectory:
            skill_dir = self.output_dir / subdirectory / skill_id
        else:
            skill_dir = self.output_dir / skill_id

        skill_dir.mkdir(parents=True, exist_ok=True)

        # Create subdirectories
        (skill_dir / "references").mkdir(exist_ok=True)
        (skill_dir / "raw").mkdir(exist_ok=True)

        # 1. Save raw text
        self._save_raw_text(skill_dir / "raw" / "full-extract.txt", raw_text)

        # 2. Save reference chunks
        reference_files = []
        for chunk in reference_chunks:
            ref_path = self._save_reference_file(
                skill_dir / "references",
                chunk['slug'],
                chunk['title'],
                chunk['content'],
                chunk['chapter_num']
            )
            reference_files.append({
                'path': ref_path.name,
                'title': chunk['title'],
                'chapter_num': chunk['chapter_num']
            })

        # 3. Generate references/index.md
        self._create_reference_index(
            skill_dir / "references" / "index.md",
            reference_files,
            metadata
        )

        # 4. Generate SKILL.md
        self._create_skill_index(
            skill_dir / "SKILL.md",
            metadata,
            reference_files,
            len(raw_text)
        )

        logger.info(f"Skill directory created: {skill_dir}")
        return skill_dir

    def _save_raw_text(self, file_path: Path, content: str) -> None:
        """Save raw extracted text."""
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        logger.info(f"Raw text saved: {file_path}")

    def _save_reference_file(
        self,
        references_dir: Path,
        slug: str,
        title: str,
        content: str,
        chapter_num: int
    ) -> Path:
        """Save a single reference file."""
        file_path = references_dir / f"{slug}.md"

        # Format reference file content
        formatted_content = f"""# {title}

**Chapter {chapter_num}**

---

{content}
"""

        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(formatted_content)

        logger.info(f"Reference file saved: {file_path}")
        return file_path

    def _create_reference_index(
        self,
        index_path: Path,
        reference_files: List[dict],
        metadata: SkillMetadata
    ) -> None:
        """Create references/index.md navigation file."""
        content = f"""# {metadata.title} - Reference Index

**Source:** {metadata.source}
**Category:** {metadata.category}
**Quality:** {metadata.quality_grade}

---

## Available References

This documentation is organized into the following sections:

"""

        # Add table of contents
        for ref in sorted(reference_files, key=lambda x: x['chapter_num']):
            content += f"{ref['chapter_num']}. **[{ref['title']}]({ref['path']})** \n"

        content += f"""
---

**Total Chapters:** {len(reference_files)}

**Navigation:**
- Return to [SKILL.md](../SKILL.md)
- View [raw extracted text](../raw/full-extract.txt)
"""

        with open(index_path, 'w', encoding='utf-8') as f:
            f.write(content)

        logger.info(f"Reference index created: {index_path}")

    def _create_skill_index(
        self,
        skill_path: Path,
        metadata: SkillMetadata,
        reference_files: List[dict],
        raw_text_size: int
    ) -> None:
        """Create SKILL.md lightweight index file."""
        # Generate YAML front matter
        yaml_content = yaml.dump(
            metadata.model_dump(exclude_none=True),
            allow_unicode=True,
            sort_keys=False,
            default_flow_style=False
        )

        content = f"""---
{yaml_content}---

# {metadata.title}

{metadata.description}

---

## 📖 When to Use This Skill

Use this skill when you need information about:
{self._generate_use_cases(metadata)}

---

## 📚 Reference Documentation

This skill contains {len(reference_files)} reference chapters:

"""

        # Add compact table of contents
        for ref in sorted(reference_files, key=lambda x: x['chapter_num']):
            content += f"{ref['chapter_num']}. [{ref['title']}](references/{ref['path']})\n"

        content += f"""
**[View Full Index](references/index.md)** | **[Raw Text](raw/full-extract.txt)** ({raw_text_size:,} chars)

---

## 🏷️ Tags

{', '.join(f'`{tag}`' for tag in metadata.tags)}

---

## 📊 Quality Information

- **Grade:** {metadata.quality_grade}
- **Priority:** {metadata.priority}
- **Domain:** {metadata.domain}
- **Source:** {metadata.source}

---

*Generated by BeanFlow CRA Document Processor*
"""

        with open(skill_path, 'w', encoding='utf-8') as f:
            f.write(content)

        logger.info(f"SKILL.md index created: {skill_path}")

    def _deduplicate_content_chunks(self, reference_chunks):
        """Remove duplicate or similar content chunks."""
        seen_hashes = set()
        unique_chunks = []

        for chunk in reference_chunks:
            content_hash = hashlib.md5(chunk['content'].encode()).hexdigest()

            if content_hash not in seen_hashes:
                seen_hashes.add(content_hash)
                unique_chunks.append(chunk)
            else:
                logger.warning(f"Duplicate content detected: {chunk['title']}")

        return unique_chunks

    def _generate_continuous_chapters(self, reference_chunks):
        """Generate continuous chapter numbering."""
        # Sort by original chunk_id to maintain document order
        sorted_chunks = sorted(reference_chunks, key=lambda x: x['chapter_num'])
        continuous_chunks = []

        for i, chunk in enumerate(sorted_chunks, 1):
            # Reset chapter number to ensure continuity
            chunk['chapter_num'] = i
            continuous_chunks.append(chunk)

        return continuous_chunks

    def _improve_chapter_titles_with_toc(self, reference_chunks, toc_entries):
        """Improve chapter titles using TOC information."""

        # Sort TOC entries by character position
        sorted_toc = sorted([entry for entry in toc_entries if entry.char_start is not None],
                          key=lambda x: x.char_start)

        improved_chunks = []

        for chunk in reference_chunks:
            improved_title = chunk['title']

            # Find the best TOC entry for this chunk
            if sorted_toc:
                # Use simple heuristic: find TOC entry that might correspond to this chapter
                chapter_num = chunk['chapter_num']

                # Try to match by chapter number or position
                if chapter_num <= len(sorted_toc):
                    # Use chapter number as index (adjusted for 0-based)
                    toc_entry = sorted_toc[min(chapter_num - 1, len(sorted_toc) - 1)]
                    improved_title = f"{toc_entry.title}"

                # Fallback: look for matching "Section X" pattern
                if improved_title.startswith("Section"):
                    for toc_entry in sorted_toc:
                        if f"Section {chapter_num}" in improved_title or chapter_num == 1:
                            improved_title = toc_entry.title
                            break

            # If no improvement found, keep original
            chunk['title'] = improved_title
            improved_chunks.append(chunk)

        return improved_chunks

    def _generate_use_cases(self, metadata: SkillMetadata) -> str:
        """Generate use cases based on category and tags."""
        use_cases = []

        # Category-specific use cases
        category_uses = {
            "personal_income": "- Personal income tax filing and calculations",
            "credits": "- Tax credits and rebates\n- Credit eligibility and applications",
            "deductions": "- Tax deductions and relief programs\n- Deductible expenses",
            "business_income": "- Business income reporting\n- Corporate tax matters",
            "gst_hst": "- GST/HST calculations and filing",
        }

        if metadata.category in category_uses:
            use_cases.append(category_uses[metadata.category])

        # Tag-based use cases
        if not use_cases:
            for tag in metadata.tags[:3]:
                use_cases.append(f"- {tag}-related tax matters")

        return "\n".join(use_cases) if use_cases else "- Canadian tax information and guidance"

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
        """Generate short description from first paragraph, skipping page markers."""
        # Remove page markers first
        clean_content = re.sub(r'=== Page \d+ ===\n', '', content)

        # Remove markdown headings
        clean_content = re.sub(r'^#+\s+.+$', '', clean_content, flags=re.MULTILINE)
        clean_content = clean_content.strip()

        # Extract first meaningful paragraph
        paragraphs = clean_content.split('\n\n')
        first_paragraph = ""

        for para in paragraphs:
            if para.strip() and not para.strip().startswith('==='):
                first_paragraph = para.strip()
                break

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
