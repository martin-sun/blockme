# Skills Directory Organization

**BeanFlow-CRA Skills organization and routing architecture**

This document describes how Skills are organized, loaded, and routed to handle user queries.

---

## Overview

Skills are structured knowledge units derived from CRA tax documents (PDFs). Each Skill contains:

- **SKILL.md**: Main skill file with metadata and content
- **references/**: Supporting reference documents organized by region
- **raw/**: Original extracted content (optional)

---

## Directory Structure

### Recommended: Flat Structure with Category Metadata

```
mvp/skills/
├── t2-corporate-tax-guide/           # category: corporate
│   ├── SKILL.md
│   ├── references/
│   │   ├── federal/                  # Federal tax content
│   │   │   ├── index.md
│   │   │   ├── section-001-*.md
│   │   │   └── ...
│   │   ├── ontario/                  # Provincial (Ontario) content
│   │   │   ├── index.md
│   │   │   └── ...
│   │   └── general/                  # General/overview content
│   │       ├── index.md
│   │       └── ...
│   └── raw/
├── t1-personal-tax-guide/            # category: personal
│   ├── SKILL.md
│   ├── references/
│   └── raw/
├── payroll-deductions-guide/         # category: payroll
│   └── ...
└── employer-guide-t4/                # category: payroll
    └── ...
```

### Why Flat Structure?

| Advantage | Description |
|-----------|-------------|
| **Simple** | All skills at same level, easy to find |
| **No code changes** | Current `skill_loader.py` already supports this |
| **Scale-appropriate** | 5-10 skills don't need nested folders |
| **Easy routing** | LLM can select directly from all skills |

### Category via Metadata

Instead of organizing by folders, use the `category` field in SKILL.md:

```yaml
---
id: t2-corporate-tax-guide
title: T2 Corporation Income Tax Guide
category: corporate    # Values: corporate | personal | payroll
domain: tax
tags: [T2, corporate, CRA, 2024]
triggers: [corporate tax, T2 return, business income]
keywords: [corporation, income tax, T2, CRA]
---
```

---

## SKILL.md Metadata Format

### Required Fields

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Unique identifier (matches directory name) |
| `title` | string | Human-readable skill title |
| `description` | string | Brief description of what this skill covers |
| `domain` | string | Always `tax` for CRA documents |

### Routing Fields

| Field | Type | Description |
|-------|------|-------------|
| `category` | string | Skill category: `corporate`, `personal`, `payroll` |
| `tags` | list | Searchable tags |
| `triggers` | list | Phrases that should trigger this skill |
| `keywords` | list | Keywords for prefilter matching |

### Example SKILL.md

```yaml
---
id: t2-corporate-tax-guide
title: T2 Corporation Income Tax Guide
description: >
  Comprehensive guide to filing T2 Corporation Income Tax Returns in Canada,
  including federal requirements, provincial taxes (Ontario), small business
  deductions, and investment tax credits.
domain: tax
category: corporate
tags:
  - T2
  - corporate
  - CRA
  - 2024
triggers:
  - corporate tax
  - T2 return
  - corporation income tax
  - business tax
keywords:
  - corporation
  - T2
  - income tax
  - small business deduction
  - CCUS
  - Schedule 500
---

# T2 Corporation Income Tax Guide

[Skill content...]
```

---

## Naming Conventions

| Item | Convention | Example |
|------|------------|---------|
| **Directory name** | `{form-code}-{brief-description}` | `t2-corporate-tax-guide` |
| **Skill ID** | Same as directory name | `t2-corporate-tax-guide` |
| **Category** | `corporate` / `personal` / `payroll` | `corporate` |
| **Domain** | Always `tax` | `tax` |
| **Tags** | Form codes, year, keywords | `[T2, 2024, CRA, corporate]` |

---

## Skill Routing Architecture

### Two-Layer Routing System

```
User Query
    │
    ▼
┌─────────────────────────────┐
│  Layer 1: Prefilter         │  (Optional, for 50+ skills)
│  - Keyword matching         │
│  - Tag matching             │
│  - Trigger matching         │
│  Reduces candidates to ~30% │
└─────────────────────────────┘
    │
    ▼
┌─────────────────────────────┐
│  Layer 2: LLM Router        │
│  - Claude Haiku 4.5 or      │
│  - GLM-4-Flash              │
│  Returns top 1-3 Skills     │
└─────────────────────────────┘
    │
    ▼
┌─────────────────────────────┐
│  Skill Loader               │
│  - Load matched Skills      │
│  - Inject into context      │
└─────────────────────────────┘
    │
    ▼
┌─────────────────────────────┐
│  Answer Generator           │
│  - Use loaded skills        │
│  - Generate response        │
└─────────────────────────────┘
```

### Prefilter Logic (Layer 1)

The prefilter runs only when there are 50+ skills. It scores skills based on:

| Field | Weight | Description |
|-------|--------|-------------|
| `triggers` | 10 | Exact phrase match in query |
| `keywords` | 5 | Keyword found in query |
| `domain` | 3 | Domain match |
| `tags` | 2 | Tag found in query |

Skills with any score > 0 are kept, plus at least 30% of total skills.

### LLM Router (Layer 2)

The LLM router receives:
- User query
- Filtered skill metadata (id, title, description, tags)

Returns:
```json
{
  "matched_skills": ["t2-corporate-tax-guide"],
  "confidence": "high",
  "reasoning": "User asked about T2 corporate tax filing deadlines..."
}
```

### Supported Routers

| Router | Model | API | Notes |
|--------|-------|-----|-------|
| `SkillRouter` | Claude Haiku 4.5 | Anthropic | Default, high accuracy |
| `SkillRouterGLM` | GLM-4-Flash | ZhipuAI | Free tier alternative |

---

## Skill Loader

### Loading Process

1. **Discover skills**: Find all directories with `SKILL.md`
2. **Parse metadata**: Extract YAML front matter
3. **Build index**: Create in-memory skill index
4. **Support routing**: Provide metadata for router

### Code Reference

```python
# mvp/skill_loader.py

class SkillLoader:
    def load_all_skills(self):
        """Load all Skill files (supports directory structure)"""
        # Load directory structure Skills (skill_id/SKILL.md)
        for skill_dir in self.skills_dir.iterdir():
            if skill_dir.is_dir():
                skill_file = skill_dir / "SKILL.md"
                if skill_file.exists():
                    skill = self._load_skill_file(skill_file)
                    self.skills[skill.skill_id] = skill
```

---

## Region-Based References

Within each skill, references are organized by content region:

```
references/
├── federal/          # Federal CRA requirements
│   ├── index.md      # Region overview
│   ├── section-001-general-information.md
│   └── section-005-small-business-deduction.md
├── ontario/          # Ontario-specific content
│   ├── index.md
│   └── section-003-ontario-corporation-tax.md
└── general/          # Overview/introduction content
    ├── index.md
    └── section-000-introduction.md
```

### Region Values

| Region | Description |
|--------|-------------|
| `federal` | Federal CRA tax rules and requirements |
| `ontario` | Ontario provincial tax specifics |
| `general` | Introduction, overview, or non-region-specific content |

---

## Scaling Strategy

### Current (5-10 Skills)

- **Structure**: Flat directory with category metadata
- **Routing**: Direct LLM routing (no prefilter)
- **Index**: In-memory skill list

### Future (30+ Skills)

Consider migrating to nested directory structure:

```
skills/
├── corporate/
│   ├── t2-corporate-tax-guide/
│   └── corporate-tax-credits/
├── personal/
│   ├── t1-personal-tax-guide/
│   └── t1-special-situations/
└── payroll/
    ├── payroll-deductions-guide/
    └── employer-guide-t4/
```

This would require:
- Modify `skill_loader.py` for recursive loading
- Enable prefilter by default
- Consider adding category-based routing

---

## Related Documents

- [Pipeline Architecture](PIPELINE_ARCHITECTURE.md) - How skills are generated
- [SKILL.md Enhancement](SKILL_ENHANCEMENT.md) - Improving skill quality
- [LLM Provider System](LLM_PROVIDERS.md) - Router LLM configuration

---

**Version**: 1.0
**Updated**: 2025-12-09
