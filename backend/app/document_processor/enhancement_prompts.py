"""CRA tax-specific enhancement prompts for SKILL.md enhancement."""

CRA_ENHANCEMENT_PROMPT = """I need you to enhance the SKILL.md file for the {skill_name} CRA tax skill.

CURRENT SKILL.MD:
------------------------------------------------------------
{current_skill_md}
------------------------------------------------------------

REFERENCE DOCUMENTATION (extracted from references/*.md):
------------------------------------------------------------
{reference_content}
------------------------------------------------------------

YOUR TASK:
Create an EXCELLENT SKILL.md file optimized for Canadian tax professionals and developers building tax applications.

Requirements:

1. **Clear "When to Use This Skill" section**
   - Be SPECIFIC about tax scenarios:
     * "When filing T2 Corporation Income Tax Returns"
     * "Calculating taxable income for Canadian corporations"
     * "Determining eligible business deductions (Schedule 1)"
   - Include CRA form numbers (T1, T2, T4, Schedule X)
   - Include tax year information where applicable

2. **Excellent Quick Reference section**
   - Extract 5-10 PRACTICAL tax examples from the reference docs:
     * Tax calculations WITH NUMBERS
       Example: "Taxable Income: $500,000 × 15% = $75,000"
     * Form completion examples
     * Eligibility criteria checklists
     * Deadline reminders
   - Keep examples SHORT (5-20 lines max)
   - Use proper language tags (```python, ```json, etc.)
   - Include CRA form references

3. **Tax-Specific Sections** (critical for CRA):
   - **Key Tax Concepts**: Define terminology
     * Marginal tax rate
     * Taxable income vs. net income
     * Non-refundable vs. refundable credits
     * RRSP, TFSA, capital gains, etc.

   - **Important Deadlines**: Filing and payment dates
     * T1 filing deadline: April 30
     * T2 filing deadline: 6 months after fiscal year-end
     * Payment deadlines

   - **Common Pitfalls**: What to watch for
     * Missing deductions
     * Incorrect form selection
     * Calculation errors

   - **CRA Forms Reference**: Map concepts to forms
     * T1 General: Personal income tax return
     * T2 Corporation Income Tax Return
     * Schedule 1: Federal tax calculation
     * Schedule 3: Capital gains

4. **Reference Files Navigation**
   - Explain what's in each reference file
   - Highlight critical sections for:
     * Quick lookups
     * Detailed calculations
     * Form instructions

5. **Working with This Skill** (multi-level guidance)
   - **For Tax Professionals**: Quick lookup guide
     * Where to find specific deductions
     * How to navigate between forms

   - **For Developers**: Integration examples
     * How to structure tax calculation code
     * API design patterns

   - **For Learners**: Step-by-step learning path
     * Start with basic concepts
     * Progress to advanced topics

IMPORTANT CRA-SPECIFIC REQUIREMENTS:
- Use official CRA terminology consistently
- Reference specific CRA forms and schedules
- Include tax year information (e.g., "for 2024 tax year")
- Emphasize accuracy and compliance
- Flag areas requiring professional tax advice:
  "⚠️ This is complex - consult a tax professional"
- Include links to official CRA resources when relevant
- Prioritize practical, actionable guidance over theory

OUTPUT FORMAT:
- Keep the frontmatter (---\\nid: ...\\n---) EXACTLY as is
- Use proper markdown formatting
- Add language tags to ALL code blocks
- Make it comprehensive but scannable
- Use emojis sparingly for visual organization (📖, 🚀, 💡, 📅, ⚠️)

Enhanced SKILL.md:"""


def build_enhancement_prompt(
    skill_name: str,
    current_skill: str,
    references: dict[str, str]
) -> str:
    """
    Build the enhancement prompt for a skill.

    Args:
        skill_name: Name of the skill (e.g., "business-income-t4012-24e")
        current_skill: Current SKILL.md content
        references: Dict mapping filename to content

    Returns:
        Complete prompt string ready for LLM
    """
    # Format reference content
    reference_sections = []
    for filename, content in references.items():
        reference_sections.append(f"=== {filename} ===\n{content}\n")

    reference_content = "\n".join(reference_sections)

    # Build the complete prompt
    prompt = CRA_ENHANCEMENT_PROMPT.format(
        skill_name=skill_name,
        current_skill_md=current_skill,
        reference_content=reference_content
    )

    return prompt
