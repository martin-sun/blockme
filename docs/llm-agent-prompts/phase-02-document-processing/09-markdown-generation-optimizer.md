# 任务09：Markdown 生成优化（CRA 文档专用）

## 任务目标

优化从 Skill Seeker PyMuPDF 提取的 CRA 文档内容，进行清洗、格式化、增强和质量检查，确保生成的税务知识库 Skill 文件结构清晰、格式统一、符合 MVP 系统规范。

**技术升级**: 集成 Skill_Seekers 的先进模板优化技术和 AI 内容增强功能，将基础的 Markdown 内容转换为专业、实用的税务知识指南，实现从文档到知识的智能化转换。

## 技术要求

**处理内容：**
- 优化 PyMuPDF 提取的文本内容
- 统一税务文档格式规范
- 修复表格结构对齐问题
- 增强法规条款可读性
- 生成符合 MVP 系统的元数据

**Skill_Seekers 集成特性：**
- **AI 模板优化**：基于 Claude Code Max 的智能模板转换
- **内容质量提升**：从基础文档到实用指南的 AI 增强
- **智能结构优化**：自动化的内容组织和导航生成
- **税务专业化**：针对 CRA 文档的专业格式处理

**输出规范：**
- 符合 CommonMark 标准
- 兼容 MVP Skill 系统 YAML Front Matter
- 优化 CRA 文档导航结构
- 提取税务专业术语和关键词
- AI 增强的实用内容结构

## 实现步骤

### 1. 创建 CRA 文档优化器模块

```bash
touch backend/src/document_processor/markdown_optimizer.py
touch backend/src/document_processor/ai_template_optimizer.py
touch backend/src/document_processor/template_engine.py
```

### 2. 实现 CRA 文档专用清理功能

优化 PDF 提取内容：
- 清理 PyMuPDF 提取的页眉页脚
- 去除重复的 CRA 水印信息
- 统一换行符和段落结构
- 处理双语内容（英/法）

### 3. 实现税务文档格式化功能

标准化税务文档格式：
- 统一法规条款格式
- 规范税务术语表述
- 修复 CRA 表格结构
- 优化税收计算说明

### 4. 实现 MVP Skill 元数据生成

生成符合 MVP 系统的元数据：
- 兼容 skill_loader.py 的 YAML 格式
- 生成税务专用标签和分类
- 提取关键税务概念
- 记录 CRA 文档来源和版本

### 5. 实现 CRA 文档质量检查

验证税务文档质量：
- 检查法规条款完整性
- 验证税务计算公式
- 检测术语一致性
- 评估用户可读性

## 关键代码提示

**CRA 文档 Markdown 优化器实现：**

```python
import re
from typing import Dict, List, Optional
from pathlib import Path
import yaml
from datetime import datetime

class CRADocumentOptimizer:
    """CRA 文档 Markdown 优化器（集成 Skill_Seekers AI 增强技术）"""

    def __init__(self):
        self.stats = {
            "cleaned": 0,
            "formatted": 0,
            "metadata_added": 0,
            "cra_processed": 0,
            "ai_enhanced": 0,
            "template_optimized": 0
        }

        # Skill_Seekers AI 增强配置
        self.ai_config = {
            "enable_ai_enhancement": True,
            "enable_template_optimization": True,
            "use_claude_max": True,
            "max_enhancement_attempts": 3
        }

        # 初始化 AI 增强组件
        if self.ai_config["enable_ai_enhancement"]:
            self.ai_enhancer = AITemplateEnhancer()
            self.template_engine = IntelligentTemplateEngine()

        # CRA 文档专用模式（增强版）
        self.cra_patterns = {
            "header_footer": [
                r"^Canada Revenue Agency\s+Agence du revenu du Canada\s*$",
                r"^Page\s+\d+\s*$",
                r"^T4012\s*.*?$",
                r"^www\.canada\.ca/revenue-agency\s*$",
                r"^T4012.*E.*\d{4}$",  # T4012 标题模式
                r"^.*income\s+tax.*guide.*$"  # 所得税指南模式
            ],
            "tax_terms": [
                r"capital\s+gains?",
                r"business\s+income",
                r"tax\s+credits?",
                r"deductions?",
                r"RRSP",
                r"GST/HST",
                r"taxable\s+income",
                r"non.*taxable\s+income",
                r"employment\s+income",
                r"investment\s+income"
            ],
            "legal_phrases": [
                r"must\s+.*",
                r"shall\s+.*",
                r"required\s+to\s+.*",
                r"according\s+to\s+.*",
                r"as\s+per\s+.*",
                r"subject\s+to\s+.*",
                r"liable\s+for\s+.*"
            ],
            "calculation_indicators": [
                r"calculate\s+.*",
                r"formula\s+.*",
                r"=\s*\d+.*%",
                r"\$\s*\d+",
                r"rate\s+of\s+.*%",
                r"\d+%\s+of"
            ]
        }

        # Skill_Seekers 模板优化规则
        self.template_rules = {
            "section_hierarchy": [
                (r"^# (.+)$", 1, "main_title"),
                (r"^## (.+)$", 2, "major_section"),
                (r"^### (.+)$", 3, "subsection"),
                (r"^#### (.+)$", 4, "detail_section")
            ],
            "list_patterns": [
                r"^[-*+]\s+",  # 无序列表
                r"^\d+\.\s+",  # 有序列表
                r"^[a-z]\.\s+"   # 字母列表
            ],
            "emphasis_patterns": [
                r"\*\*(.+?)\*\*",  # 粗体
                r"_(.+?)_",        # 斜体
                r"`(.+?)`"        # 代码
            ]
        }

    def optimize_cra_content(
        self,
        raw_markdown: str,
        source_file: Optional[str] = None,
        document_type: str = "cra_tax_guide",
        enable_ai_enhancement: Optional[bool] = None
    ) -> str:
        """
        全流程优化 CRA 文档内容（集成 Skill_Seekers AI 增强）

        Args:
            raw_markdown: 从 PyMuPDF 提取的原始内容
            source_file: 源 PDF 文件名
            document_type: CRA 文档类型
            enable_ai_enhancement: 是否启用 AI 增强（覆盖配置）

        Returns:
            优化后的 Markdown
        """
        # 确定是否启用 AI 增强
        ai_enabled = enable_ai_enhancement if enable_ai_enhancement is not None else self.ai_config["enable_ai_enhancement"]

        # 1. CRA 专用清理
        cleaned = self._clean_cra_content(raw_markdown)

        # 2. 税务文档格式化
        formatted = self._format_tax_markdown(cleaned)

        # 3. Skill_Seekers AI 增强和模板优化
        if ai_enabled:
            enhanced = self._apply_ai_enhancement(formatted, source_file, document_type)
            formatted = enhanced

        # 4. 生成 MVP 兼容元数据
        metadata = self._generate_mvp_metadata(formatted, source_file, document_type)

        # 5. 组合最终输出
        final_markdown = self._combine_with_metadata(metadata, formatted)

        self.stats["cra_processed"] += 1
        return final_markdown

    def _apply_ai_enhancement(self, content: str, source_file: Optional[str], document_type: str) -> str:
        """应用 Skill_Seekers AI 增强技术"""

        try:
            # 1. 智能模板优化
            if self.ai_config["enable_template_optimization"]:
                optimized = self.template_engine.optimize_template(content, document_type)
                self.stats["template_optimized"] += 1
                content = optimized

            # 2. AI 内容增强
            enhanced_content = self.ai_enhancer.enhance_content(
                content=content,
                source_file=source_file,
                document_type=document_type,
                enhancement_level="comprehensive"
            )

            self.stats["ai_enhanced"] += 1
            return enhanced_content

        except Exception as e:
            print(f"⚠️ AI 增强失败，使用基础格式化: {e}")
            return content

    def _clean_cra_content(self, markdown: str) -> str:
        """清理 CRA 文档内容"""
        # 删除页眉页脚
        for pattern in self.cra_patterns["header_footer"]:
            markdown = re.sub(pattern, "", markdown, flags=re.MULTILINE | re.IGNORECASE)

        # 删除页码
        markdown = re.sub(r"^\s*\d+\s*$", "", markdown, flags=re.MULTILINE)

        # 清理多余空行和空白字符
        markdown = re.sub(r"\n{3,}", "\n\n", markdown)
        lines = [line.rstrip() for line in markdown.split("\n") if line.strip()]
        markdown = "\n".join(lines)

        self.stats["cleaned"] += 1
        return markdown

  
    def _format_tax_markdown(self, markdown: str) -> str:
        """格式化税务文档 Markdown"""
        # 规范化标题（确保 # 后有空格）
        markdown = re.sub(r"^(#{1,6})([^ #])", r"\1 \2", markdown, flags=re.MULTILINE)

        # 规范化列表（确保 - 或 * 后有空格）
        markdown = re.sub(r"^([*\-])([^ ])", r"\1 \2", markdown, flags=re.MULTILINE)

        # 修复 CRA 表格结构
        markdown = self._fix_cra_tables(markdown)

        # 格式化法规条款
        markdown = self._format_legal_sections(markdown)

        # 优化税务计算说明
        markdown = self._enhance_tax_calculations(markdown)

        self.stats["formatted"] += 1
        return markdown

    def _fix_cra_tables(self, markdown: str) -> str:
        """修复 CRA 文档表格"""
        lines = markdown.split("\n")
        fixed_lines = []

        for i, line in enumerate(lines):
            # 检测表格行
            if "|" in line and not line.strip().startswith("|"):
                # 确保表格行以 | 开始和结束
                if not line.startswith("|"):
                    line = "| " + line
                if not line.endswith("|"):
                    line = line + " |"
                fixed_lines.append(line)
            elif re.match(r"^\s*\|[\s\-:|]+\|", line):
                # 表格分隔行
                parts = [p.strip() for p in line.split("|")]
                parts = [p if p else "---" for p in parts]
                fixed_line = "| " + " | ".join(parts[1:-1]) + " |"
                fixed_lines.append(fixed_line)
            else:
                fixed_lines.append(line)

        return "\n".join(fixed_lines)

    def _format_legal_sections(self, markdown: str) -> str:
        """格式化法规条款"""
        lines = markdown.split("\n")
        formatted_lines = []

        for line in lines:
            # 识别法规条款并强化格式
            for pattern in self.cra_patterns["legal_phrases"]:
                if re.search(pattern, line, re.IGNORECASE):
                    # 添加法规标记
                    line = f"⚖️ **{line.strip()}**"
                    break

            # 识别税务术语并高亮
            for term in self.cra_patterns["tax_terms"]:
                if re.search(rf"\b{term}\b", line, re.IGNORECASE):
                    line = re.sub(
                        rf"\b({term})\b",
                        r"**\1**",
                        line,
                        flags=re.IGNORECASE
                    )
                    break

            formatted_lines.append(line)

        return "\n".join(formatted_lines)

    def _enhance_tax_calculations(self, markdown: str) -> str:
        """增强税务计算说明"""
        # 识别百分比计算
        markdown = re.sub(
            r"(\d+)%",
            r"**\1%**",
            markdown
        )

        # 识别金额
        markdown = re.sub(
            r"\$(\d{1,3}(,\d{3})*(\.\d{2})?)",
            r"**$\1**",
            markdown
        )

        # 识别计算公式
        markdown = re.sub(
            r"([A-Z]\s*=\s*[\d\+\-\*\/\(\)\s\$%,\.]+)",
            r"`\1`",
            markdown
        )

        return markdown

    def _generate_mvp_metadata(
        self,
        markdown: str,
        source_file: Optional[str],
        document_type: str
    ) -> Dict:
        """生成 MVP Skill 兼容的元数据"""
        # 提取第一个一级标题作为标题
        title_match = re.search(r"^#\s+(.+)$", markdown, re.MULTILINE)
        title = title_match.group(1) if title_match else "CRA 税务文档"

        # 提取税务关键词
        tax_keywords = self._extract_tax_keywords(markdown)

        # 生成税务专用标签
        tags = ["税务", "加拿大", "CRA", "T4012"] + tax_keywords

        # 生成税务摘要
        summary = self._generate_tax_summary(markdown)

        # 检测目标受众
        target_audience = self._identify_tax_audience(markdown)

        metadata = {
            "id": self._generate_skill_id(title, source_file),
            "title": title,
            "tags": tags,
            "description": summary,
            "domain": "tax",
            "priority": self._determine_priority(markdown),
            "version": "1.0.0",
            "author": "CRA Document Processor",
            "created_at": datetime.now().isoformat(),
            "source": f"CRA {source_file or 'T4012'}",
            "target_audience": target_audience,
            "tax_categories": tax_keywords
        }

        self.stats["metadata_added"] += 1
        return metadata

    def _extract_tax_keywords(self, markdown: str) -> List[str]:
        """提取税务关键词"""
        keywords = []

        # 使用预定义的税务术语
        for term in self.cra_patterns["tax_terms"]:
            if re.search(rf"\b{term}\b", markdown, re.IGNORECASE):
                keywords.append(term.replace(" ", "-").lower())

        # 提取标题中的关键词
        headings = re.findall(r"^#{2,6}\s+(.+)$", markdown, re.MULTILINE)
        for heading in headings:
            # 清理标题
            clean_heading = re.sub(r"[^\w\s]", "", heading)
            words = clean_heading.split()
            keywords.extend([w.lower() for w in words if len(w) > 3])

        return list(set(keywords))[:10]  # 最多10个关键词

    def _generate_tax_summary(self, markdown: str, max_length: int = 150) -> str:
        """生成税务文档摘要"""
        # 移除标题和特殊格式
        text = re.sub(r"^#+\s+.+$", "", markdown, flags=re.MULTILINE)
        text = re.sub(r"⚖️\s*\*\*([^*]+)\*\*", r"\1", text)
        text = re.sub(r"\*\*([^*]+)\*\*", r"\1", text)

        # 获取前N个字符
        text = text.strip()
        if len(text) > max_length:
            return text[:max_length] + "..."
        return text

    def _identify_tax_audience(self, markdown: str) -> List[str]:
        """识别目标受众"""
        audience = []
        text_lower = markdown.lower()

        audience_mapping = {
            "individual": ["you", "your", "personal", "individual", "taxpayer"],
            "business": ["business", "corporation", "company", "self-employed", "professional"],
            "investor": ["investor", "investment", "portfolio", "capital", "gains"],
            "accountant": ["accountant", "advisor", "professional", "preparer"]
        }

        for audience_type, keywords in audience_mapping.items():
            if any(keyword in text_lower for keyword in keywords):
                audience.append(audience_type)

        return audience if audience else ["general"]

    def _determine_priority(self, markdown: str) -> str:
        """确定文档优先级"""
        text_lower = markdown.lower()

        # 检查高优先级指标
        high_priority_indicators = [
            "must", "required", "mandatory", "deadline", "penalty",
            "filing requirement", "due date"
        ]

        for indicator in high_priority_indicators:
            if indicator in text_lower:
                return "high"

        # 检查是否有计算或表格
        if re.search(r"\$?\d+\.?\d*%?", markdown) or "|" in markdown:
            return "medium"

        return "low"

    def _generate_skill_id(self, title: str, source_file: Optional[str]) -> str:
        """生成 Skill ID"""
        # 清理标题
        clean_title = re.sub(r"[^\w\s-]", "", title)
        clean_title = re.sub(r"\s+", "-", clean_title.lower())

        # 添加前缀
        if source_file and "t4012" in source_file.lower():
            return f"t4012-{clean_title}"
        else:
            return f"cra-{clean_title}"

    def _fix_tables(self, markdown: str) -> str:
        """修复 Markdown 表格"""
        lines = markdown.split("\n")
        fixed_lines = []

        for i, line in enumerate(lines):
            # 检测表格分隔行（|---|---|）
            if re.match(r"^\s*\|[\s\-:|]+\|", line):
                # 确保分隔符格式正确
                parts = [p.strip() for p in line.split("|")]
                parts = [p if p else "---" for p in parts]
                fixed_line = "| " + " | ".join(parts[1:-1]) + " |"
                fixed_lines.append(fixed_line)
            else:
                fixed_lines.append(line)

        return "\n".join(fixed_lines)

    def _format_code_blocks(self, markdown: str) -> str:
        """格式化代码块"""
        # 为没有语言标注的代码块添加 "text"
        markdown = re.sub(r"```\n", "```text\n", markdown)

        # 确保代码块前后有空行
        markdown = re.sub(r"([^\n])\n```", r"\1\n\n```", markdown)
        markdown = re.sub(r"```\n([^\n])", r"```\n\n\1", markdown)

        return markdown

    def _generate_metadata(
        self,
        markdown: str,
        source_file: Optional[str],
        document_type: Optional[str]
    ) -> Dict:
        """生成文档元数据"""
        # 提取第一个一级标题作为标题
        title_match = re.search(r"^#\s+(.+)$", markdown, re.MULTILINE)
        title = title_match.group(1) if title_match else "未命名文档"

        # 提取所有标题生成 TOC
        headings = re.findall(r"^(#{1,6})\s+(.+)$", markdown, re.MULTILINE)

        # 生成简单摘要（前200字）
        summary = self._generate_summary(markdown)

        # 提取关键词（简单实现）
        keywords = self._extract_keywords(markdown)

        metadata = {
            "title": title,
            "source": source_file or "unknown",
            "document_type": document_type or "generic",
            "created_at": datetime.now().isoformat(),
            "summary": summary,
            "keywords": keywords,
            "headings_count": len(headings),
            "word_count": len(markdown.split())
        }

        self.stats["metadata_added"] += 1
        return metadata

    def _generate_summary(self, markdown: str, max_length: int = 200) -> str:
        """生成文档摘要"""
        # 移除标题和代码块
        text = re.sub(r"^#+\s+.+$", "", markdown, flags=re.MULTILINE)
        text = re.sub(r"```.*?```", "", text, flags=re.DOTALL)

        # 获取前N个字符
        text = text.strip()
        if len(text) > max_length:
            return text[:max_length] + "..."
        return text

    def _extract_keywords(self, markdown: str, max_keywords: int = 10) -> List[str]:
        """提取关键词（简单实现）"""
        # 提取所有标题作为关键词
        headings = re.findall(r"^#{1,6}\s+(.+)$", markdown, re.MULTILINE)

        # 简单去重和清理
        keywords = []
        for heading in headings:
            # 移除标点符号
            clean = re.sub(r"[^\w\s\u4e00-\u9fff]", "", heading)
            words = clean.split()
            keywords.extend(words[:3])  # 每个标题取前3个词

        # 去重并限制数量
        keywords = list(dict.fromkeys(keywords))[:max_keywords]
        return keywords

    def _combine_with_metadata(self, metadata: Dict, markdown: str) -> str:
        """将元数据和内容组合"""
        # 生成 YAML Front Matter
        front_matter = "---\n" + yaml.dump(metadata, allow_unicode=True, sort_keys=False) + "---\n\n"

        # 可选：生成目录
        toc = self._generate_toc(markdown)

        if toc:
            return front_matter + toc + "\n\n" + markdown
        else:
            return front_matter + markdown

    def _generate_toc(self, markdown: str) -> str:
        """生成目录（TOC）"""
        headings = re.findall(r"^(#{1,6})\s+(.+)$", markdown, re.MULTILINE)

        if len(headings) <= 2:
            # 标题太少，不生成目录
            return ""

        toc_lines = ["## 目录\n"]

        for level, title in headings:
            # 跳过一级标题（通常是文档标题）
            if level == "#":
                continue

            # 计算缩进
            indent = "  " * (len(level) - 2)

            # 生成链接锚点
            anchor = re.sub(r"[^\w\s\u4e00-\u9fff-]", "", title).replace(" ", "-").lower()

            toc_lines.append(f"{indent}- [{title}](#{anchor})")

        return "\n".join(toc_lines)

    def validate_quality(self, markdown: str) -> Dict:
        """验证 Markdown 质量"""
        issues = []

        # 检查空内容
        if len(markdown.strip()) < 50:
            issues.append("内容过短（<50字符）")

        # 检查是否有标题
        if not re.search(r"^#+\s+", markdown, re.MULTILINE):
            issues.append("缺少标题")

        # 检查表格完整性
        table_rows = re.findall(r"^\|.+\|$", markdown, re.MULTILINE)
        if table_rows:
            # 检查是否有分隔行
            if not any("---" in row for row in table_rows):
                issues.append("表格缺少分隔行")

        # 检查代码块闭合
        code_blocks = re.findall(r"```", markdown)
        if len(code_blocks) % 2 != 0:
            issues.append("代码块未闭合")

        return {
            "is_valid": len(issues) == 0,
            "issues": issues,
            "score": max(0, 100 - len(issues) * 20)  # 简单评分
        }
```

**CRA 文档处理完整示例：**

```python
# CRA 文档优化完整流程
from backend.src.document_processor.pdf_extractor import PDFTextExtractor
from backend.src.document_processor.content_classifier import TaxContentClassifier
from backend.src.document_processor.skill_generator import SkillGenerator
from backend.src.document_processor.markdown_optimizer import CRADocumentOptimizer

# 1. PDF 提取
extractor = PDFTextExtractor("t4012-24e.pdf")
extracted_data = extractor.extract_all()

# 2. 内容分类
classifier = TaxContentClassifier()
classified_contents = classifier.classify_content(extracted_data)

# 3. 生成 Skills
skill_generator = SkillGenerator("backend/src/skills")
skill_files = skill_generator.generate_skills(classified_contents)

# 4. 优化 Markdown 格式
optimizer = CRADocumentOptimizer()
for skill_file in skill_files:
    with open(skill_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # 提取 YAML Front Matter 和 Markdown 内容
    parts = content.split('---', 2)
    if len(parts) >= 3:
        yaml_part = parts[1]
        markdown_part = parts[2].strip()

        # 优化 Markdown 内容
        optimized_markdown = optimizer.optimize_cra_content(
            markdown_part,
            source_file="t4012-24e.pdf",
            document_type="cra_tax_guide"
        )

        # 重新组合
        optimized_content = f"---\n{yaml_part}\n---\n\n{optimized_markdown}"

        # 保存优化后的文件
        with open(skill_file, 'w', encoding='utf-8') as f:
            f.write(optimized_content)

print(f"✅ 已优化 {len(skill_files)} 个 CRA Skill 文件")
```

**集成到 MVP 系统：**

```python
# 与现有 MVP 系统集成
from mvp.skill_loader import SkillLoader

# 验证生成的 Skills
loader = SkillLoader("backend/src/skills")
skills = loader.get_all_skills_metadata()

print(f"📚 加载了 {len(skills)} 个 Skills")

# 测试技能路由
from mvp.skill_router import SkillRouter

router = SkillRouter()
test_queries = [
    "资本收益如何计算？",
    "小企业税务抵扣有哪些？",
    "RRSP 的贡献限额是多少？"
]

for query in test_queries:
    result = router.route(query, skills)
    print(f"问题: {query}")
    print(f"匹配技能: {result['matched_skills']}")
    print(f"置信度: {result['confidence']}\n")
```

## 测试验证

### 1. 清理功能测试

```python
dirty_md = """以下是提取的内容：

# 标题

内容...


---
---
---

更多内容"""

cleaned = optimizer._clean_content(dirty_md)
assert "以下是提取的内容" not in cleaned
assert cleaned.count("---") == 1
```

### 2. 表格修复测试

```python
broken_table = """
| 列1|列2 |
|---|---|
|数据1 | 数据2|
"""

fixed = optimizer._fix_tables(broken_table)
assert "| 列1 | 列2 |" in fixed
```

### 3. 元数据生成测试

```python
markdown = "# 测试文档\n\n这是内容"
metadata = optimizer._generate_metadata(markdown, "test.pdf", "generic")

assert metadata["title"] == "测试文档"
assert metadata["source"] == "test.pdf"
assert "created_at" in metadata
```

### 4. 质量验证测试

```python
# 高质量文档
good_md = "# 标题\n\n## 章节\n\n内容很长很长..."
quality = optimizer.validate_quality(good_md)
assert quality["is_valid"] == True
assert quality["score"] >= 80

# 低质量文档
bad_md = "short"
quality = optimizer.validate_quality(bad_md)
assert quality["is_valid"] == False
```

## 注意事项

**元数据标准化：**
- 使用 YAML Front Matter 符合 Jekyll/Hugo 等标准
- 便于后续检索和过滤

**性能优化：**
- 使用正则表达式时注意性能
- 大文档分块处理
- 缓存常用操作结果

**可扩展性：**
- 预留自定义清理规则接口
- 支持插件式格式化规则
- 允许自定义元数据字段

**LLM 增强（可选）：**
使用 LLM 生成更好的摘要和关键词：
```python
def _generate_summary_with_llm(self, markdown: str) -> str:
    # 调用 GLM-4-Flash 生成摘要
    prompt = f"请用一句话总结以下文档的核心内容：\n\n{markdown[:1000]}"
    # ... LLM 调用
    return summary
```

## 依赖关系

**新增依赖：**
```toml
# 已在 pyproject.toml 中配置
PyMuPDF>=1.24.0          # PDF 处理
PyYAML>=6.0             # YAML 处理
```

**前置任务：**
- 任务05：PDF 文本提取模块
- 任务06：内容分类模块
- 任务07：Skill 生成模块

**后置任务：**
- 集成到后端 API 系统
- 与 MVP 系统兼容性测试
- CRA 文档更新维护流程

## 与 Skill Seeker 的关系

**技术栈继承：**
- 基于 Skill Seeker 的 PyMuPDF 处理方案
- 保留文本提取和表格检测的核心逻辑
- 适配 CRA 税务文档的特殊需求

**功能增强：**
- CRA 专用内容清理和格式化
- MVP Skill 系统兼容性
- 税务术语智能识别和高亮
- 双语内容处理支持

**输出格式统一：**
- 生成的 Skills 完全兼容现有 MVP 系统
- 支持 skill_loader.py 和 skill_router.py
- 提供统一的税务知识库接口

这个优化器完成了 CRA 文档处理的最后一公里，确保从原始 PDF 到可用 Skill 的整个流程都能产出高质量、标准化的知识库内容。

## Skill_Seekers AI 增强组件实现

### AI 模板增强器

```python
class AITemplateEnhancer:
    """AI 模板增强器（集成 Skill_Seekers 技术）"""

    def __init__(self):
        self.claude_max_available = self._check_claude_max()
        self.enhancement_prompts = self._load_enhancement_prompts()

    def enhance_content(self, content: str, source_file: Optional[str],
                       document_type: str, enhancement_level: str = "comprehensive") -> str:
        """使用 AI 增强内容"""

        if not self.claude_max_available:
            print("⚠️ Claude Code Max 不可用，跳过 AI 增强")
            return content

        # 根据增强级别选择提示词
        prompt = self._select_enhancement_prompt(content, document_type, enhancement_level)

        try:
            enhanced_content = self._call_claude_max(prompt)
            return self._post_process_enhancement(enhanced_content, content)

        except Exception as e:
            print(f"⚠️ AI 增强失败: {e}")
            return content

    def _check_claude_max(self) -> bool:
        """检查 Claude Code Max 是否可用"""
        try:
            import subprocess
            result = subprocess.run(
                ["claude-code-max", "--version"],
                capture_output=True,
                text=True,
                timeout=10
            )
            return result.returncode == 0
        except:
            return False

    def _load_enhancement_prompts(self) -> Dict[str, str]:
        """加载增强提示词库"""
        return {
            "tax_guide_basic": """
你是一位加拿大税务专家，请优化以下税务文档的 Markdown 格式和内容结构：

原始内容：
{content}

要求：
1. 改善 Markdown 格式的规范性
2. 优化标题层次结构
3. 修复表格格式问题
4. 增强列表的可读性
5. 确保语法正确

请返回优化后的 Markdown 内容，保持原有的技术信息不变。
""",

            "tax_guide_comprehensive": """
你是一位资深的加拿大税务专家，请全面优化以下税务文档：

原始内容：
{content}

优化要求：
1. **格式优化**：
   - 规范化 Markdown 语法
   - 优化标题层次结构
   - 修复表格和列表格式
   - 改善代码块格式

2. **内容增强**：
   - 添加实用的操作步骤
   - 提供具体的计算示例
   - 包含常见问题解答
   - 添加税务小贴士

3. **结构优化**：
   - 添加清晰的导航
   - 生成内容摘要
   - 创建快速参考部分
   - 优化章节组织

4. **专业性提升**：
   - 保持技术准确性
   - 使用专业术语
   - 引用相关法规
   - 提供实用建议

请返回全面优化后的 Markdown 内容。
""",

            "calculation_example": """
请优化以下税务计算示例的呈现方式：

原始内容：
{content}

优化要求：
1. 改进 Markdown 表格格式
2. 添加步骤说明
3. 增强可读性
4. 确保计算准确性
5. 添加结果解释

请返回优化后的计算示例。
""",

            "quick_reference": """
请将以下税务内容转换为快速参考指南：

原始内容：
{content}

转换要求：
1. 提取关键要点
2. 使用项目符号列表
3. 包含重要日期和截止时间
4. 添加相关表格编号
5. 简化语言表达

请返回简洁明了的快速参考格式。
"""
        }

    def _select_enhancement_prompt(self, content: str, document_type: str, level: str) -> str:
        """选择合适的增强提示词"""

        if level == "basic":
            prompt_template = self.enhancement_prompts["tax_guide_basic"]
        elif level == "comprehensive":
            prompt_template = self.enhancement_prompts["tax_guide_comprehensive"]
        elif document_type == "calculation_example":
            prompt_template = self.enhancement_prompts["calculation_example"]
        elif document_type == "quick_reference":
            prompt_template = self.enhancement_prompts["quick_reference"]
        else:
            prompt_template = self.enhancement_prompts["tax_guide_basic"]

        return prompt_template.format(content=content)

    def _call_claude_max(self, prompt: str) -> str:
        """调用 Claude Code Max"""
        import subprocess

        try:
            result = subprocess.run([
                "claude-code-max",
                "--prompt", prompt,
                "--temperature", "0.3",
                "--max-tokens", "3000"
            ], capture_output=True, text=True, timeout=120)

            if result.returncode == 0:
                return result.stdout.strip()
            else:
                raise Exception(f"Claude Max 失败: {result.stderr}")

        except subprocess.TimeoutExpired:
            raise Exception("Claude Max 处理超时")

    def _post_process_enhancement(self, enhanced: str, original: str) -> str:
        """后处理增强结果"""
        # 确保基础结构完整性
        if not enhanced.strip():
            return original

        # 检查关键元素是否保留
        original_elements = self._extract_key_elements(original)
        enhanced_elements = self._extract_key_elements(enhanced)

        # 如果关键元素丢失，尝试修复
        missing_elements = original_elements - enhanced_elements
        if missing_elements:
            enhanced = self._restore_missing_elements(enhanced, original, missing_elements)

        return enhanced

    def _extract_key_elements(self, content: str) -> set:
        """提取关键元素"""
        elements = set()

        # 提取标题
        headings = re.findall(r"^#{1,6}\s+(.+)$", content, re.MULTILINE)
        elements.update(headings)

        # 提取税务术语
        tax_terms = re.findall(r"\b(capital\s+gains|RRSP|GST/HST|tax\s+credits?)\b", content, re.IGNORECASE)
        elements.update(term.lower() for term in tax_terms)

        # 提取数值和金额
        amounts = re.findall(r"\$[\d,]+\.?\d*", content)
        elements.update(amounts)

        # 提取百分比
        percentages = re.findall(r"\d+\.?\d*%", content)
        elements.update(percentages)

        return elements

    def _restore_missing_elements(self, enhanced: str, original: str, missing_elements: set) -> str:
        """恢复缺失的关键元素"""
        # 简化实现：在增强内容后添加缺失元素
        restored_content = enhanced

        if missing_elements:
            restored_content += "\n\n## 📋 原始内容中的重要信息\n\n"
            for element in sorted(missing_elements):
                if element.startswith('$') or element.endswith('%'):
                    restored_content += f"- **{element}**\n"
                else:
                    restored_content += f"- {element}\n"

        return restored_content
```

### 智能模板引擎

```python
class IntelligentTemplateEngine:
    """智能模板引擎（来自 Skill_Seekers）"""

    def __init__(self):
        self.templates = self._load_templates()
        self.structure_analyzer = DocumentStructureAnalyzer()

    def optimize_template(self, content: str, document_type: str) -> str:
        """优化内容模板"""

        # 分析文档结构
        structure = self.structure_analyzer.analyze(content)

        # 选择最佳模板
        template = self._select_best_template(structure, document_type)

        # 应用模板优化
        optimized = self._apply_template_optimization(content, template, structure)

        return optimized

    def _load_templates(self) -> Dict[str, Dict]:
        """加载模板配置"""
        return {
            "tax_guide": {
                "required_sections": ["概述", "主要内容", "计算方法", "示例"],
                "optional_sections": ["注意事项", "相关资源", "常见问题"],
                "format_rules": {
                    "heading_style": "incremental",
                    "list_style": "bullet",
                    "table_style": "github"
                }
            },
            "calculation_example": {
                "required_sections": ["场景", "条件", "步骤", "结果"],
                "optional_sections": ["说明", "相关法规"],
                "format_rules": {
                    "heading_style": "consistent",
                    "list_style": "numbered",
                    "table_style": "github"
                }
            },
            "quick_reference": {
                "required_sections": ["要点", "日期", "表格"],
                "optional_sections": ["注意事项", "资源链接"],
                "format_rules": {
                    "heading_style": "simple",
                    "list_style": "bullet",
                    "table_style": "simple"
                }
            }
        }

    def _select_best_template(self, structure: Dict, document_type: str) -> Dict:
        """选择最佳模板"""
        # 基于文档结构和类型选择模板
        if document_type in self.templates:
            return self.templates[document_type]

        # 基于结构特征自动选择
        if structure.get('has_calculations', False):
            return self.templates["calculation_example"]
        elif structure.get('section_count', 0) <= 3:
            return self.templates["quick_reference"]
        else:
            return self.templates["tax_guide"]

    def _apply_template_optimization(self, content: str, template: Dict, structure: Dict) -> str:
        """应用模板优化"""

        optimized_content = content

        # 1. 优化标题结构
        optimized_content = self._optimize_heading_structure(optimized_content, template)

        # 2. 优化列表格式
        optimized_content = self._optimize_lists(optimized_content, template)

        # 3. 优化表格格式
        optimized_content = self._optimize_tables(optimized_content, template)

        # 4. 确保必需章节存在
        optimized_content = self._ensure_required_sections(optimized_content, template)

        return optimized_content

    def _optimize_heading_structure(self, content: str, template: Dict) -> str:
        """优化标题结构"""
        lines = content.split('\n')
        optimized_lines = []

        current_level = 0
        heading_style = template['format_rules']['heading_style']

        for line in lines:
            heading_match = re.match(r'^(#{1,6})\s+(.+)$', line)
            if heading_match:
                markers, title = heading_match.groups()
                level = len(markers)

                if heading_style == "incremental":
                    # 确保标题递增
                    if level > current_level + 1:
                        level = current_level + 1
                    current_level = level
                elif heading_style == "consistent":
                    # 保持一致的标题层级
                    if level == 1 and current_level > 0:
                        level = 2
                    current_level = level

                optimized_line = f"{'#' * level} {title}"
                optimized_lines.append(optimized_line)
            else:
                optimized_lines.append(line)

        return '\n'.join(optimized_lines)

    def _optimize_lists(self, content: str, template: Dict) -> str:
        """优化列表格式"""
        list_style = template['format_rules']['list_style']
        lines = content.split('\n')
        optimized_lines = []

        for line in lines:
            if re.match(r'^\s*[-*+]\s+', line):
                if list_style == "numbered":
                    # 转换为有序列表
                    number = self._get_list_number(line, lines)
                    optimized_line = re.sub(r'^\s*[-*+]\s+', f'{number}. ', line)
                    optimized_lines.append(optimized_line)
                else:
                    optimized_lines.append(line)
            elif re.match(r'^\s*\d+\.\s+', line):
                if list_style == "bullet":
                    # 转换为无序列表
                    optimized_line = re.sub(r'^\s*\d+\.\s+', '- ', line)
                    optimized_lines.append(optimized_line)
                else:
                    optimized_lines.append(line)
            else:
                optimized_lines.append(line)

        return '\n'.join(optimized_lines)

    def _get_list_number(self, current_line: str, all_lines: List[str]) -> int:
        """获取列表编号"""
        # 简化实现：计算前面的列表项数量
        list_count = 0
        for i, line in enumerate(all_lines):
            if line == current_line:
                break
            if re.match(r'^\s*\d+\.\s+', line):
                list_count += 1

        return list_count + 1

    def _optimize_tables(self, content: str, template: Dict) -> str:
        """优化表格格式"""
        table_style = template['format_rules']['table_style']
        lines = content.split('\n')
        optimized_lines = []

        i = 0
        while i < len(lines):
            line = lines[i]

            if '|' in line:
                # 检测表格开始
                table_lines = []
                while i < len(lines) and ('|' in lines[i] or re.match(r'^\s*$', lines[i])):
                    table_lines.append(lines[i])
                    i += 1

                # 优化表格
                optimized_table = self._optimize_table_format(table_lines, table_style)
                optimized_lines.extend(optimized_table)
            else:
                optimized_lines.append(line)
                i += 1

        return '\n'.join(optimized_lines)

    def _optimize_table_format(self, table_lines: List[str], style: str) -> List[str]:
        """优化表格格式"""
        # 移除空行
        table_lines = [line for line in table_lines if line.strip()]

        if not table_lines:
            return table_lines

        # 确保表格行格式正确
        optimized_table = []
        for line in table_lines:
            if not line.strip().startswith('|'):
                line = '| ' + line
            if not line.strip().endswith('|'):
                line = line + ' |'
            optimized_table.append(line)

        # 检查是否有分隔行
        has_separator = any(re.match(r'^\s*\|[\s\-:|]+\|$', line) for line in optimized_table)

        if not has_separator and len(optimized_table) > 1:
            # 在第一行后添加分隔行
            first_line = optimized_table[0]
            columns = len(first_line.split('|')) - 2
            separator = '|' + ' --- |' * columns + ' |'
            optimized_table.insert(1, separator)

        return optimized_table

    def _ensure_required_sections(self, content: str, template: Dict) -> str:
        """确保必需章节存在"""
        required_sections = template.get('required_sections', [])
        existing_headings = re.findall(r'^#{1,6}\s+(.+)$', content, re.MULTILINE)

        missing_sections = [section for section in required_sections if not any(section in heading for heading in existing_headings)]

        if missing_sections:
            # 在内容末尾添加缺失章节
            content += "\n\n## 缺失章节\n\n"
            for section in missing_sections:
                content += f"### {section}\n\n*此部分需要补充内容*\n\n"

        return content

class DocumentStructureAnalyzer:
    """文档结构分析器"""

    def analyze(self, content: str) -> Dict:
        """分析文档结构"""
        structure = {
            'section_count': 0,
            'has_tables': False,
            'has_lists': False,
            'has_calculations': False,
            'heading_levels': set(),
            'estimated_length': len(content)
        }

        # 分析标题
        headings = re.findall(r'^(#{1,6})\s+', content, re.MULTILINE)
        structure['section_count'] = len(headings)
        structure['heading_levels'] = set(len(h) for h in headings)

        # 分析表格
        if '|' in content:
            structure['has_tables'] = True

        # 分析列表
        if re.search(r'^\s*[-*+]\s+|^\s*\d+\.\s+', content, re.MULTILINE):
            structure['has_lists'] = True

        # 分析计算
        if re.search(r'\$[\d,]+\.?\d*|\d+\.?\d*%', content):
            structure['has_calculations'] = True

        return structure
```

## Skill_Seekers 集成使用示例

```python
# 完整的 CRA 文档优化示例
def optimize_cra_document_with_ai():
    """使用 AI 增强的 CRA 文档优化"""

    # 创建增强版优化器
    optimizer = CRADocumentOptimizer()

    # 配置 AI 增强
    optimizer.ai_config.update({
        "enable_ai_enhancement": True,
        "enable_template_optimization": True,
        "use_claude_max": True
    })

    # 示例内容
    sample_content = """
# Capital Gains

When you sell property you may have capital gains.

Calculate: Selling price minus cost base.

Rate: 50% inclusion rate.
"""

    # 执行优化
    optimized_content = optimizer.optimize_cra_content(
        raw_markdown=sample_content,
        source_file="t4012-sample.pdf",
        document_type="tax_guide",
        enable_ai_enhancement=True
    )

    print("✅ AI 增强优化完成")
    print(f"📊 处理统计: {optimizer.stats}")
    print("📝 优化结果:")
    print(optimized_content)

# 批量优化示例
def batch_optimize_cra_documents():
    """批量优化 CRA 文档"""

    optimizer = CRADocumentOptimizer()

    # 模拟多个文档
    documents = [
        {"content": "Business income guide...", "type": "tax_guide"},
        {"content": "RRSP contribution rules...", "type": "quick_reference"},
        {"content": "Capital gains calculation...", "type": "calculation_example"}
    ]

    results = []
    for doc in documents:
        optimized = optimizer.optimize_cra_content(
            raw_markdown=doc["content"],
            document_type=doc["type"],
            enable_ai_enhancement=True
        )
        results.append(optimized)

    print(f"✅ 批量优化完成，处理了 {len(results)} 个文档")
    print(f"📊 总计 AI 增强: {optimizer.stats['ai_enhanced']}")
    print(f"🎯 模板优化: {optimizer.stats['template_optimized']}")

    return results
```

## 性能优化建议

### 1. 缓存策略

```python
class CachedOptimizer:
    """带缓存的优化器"""

    def __init__(self):
        self.optimizer = CRADocumentOptimizer()
        self.content_cache = {}
        self.cache_ttl = 3600  # 1小时

    def optimize_with_cache(self, content: str, **kwargs) -> str:
        """使用缓存的优化"""
        content_hash = hashlib.md5(content.encode()).hexdigest()

        # 检查缓存
        if content_hash in self.content_cache:
            cached_result, timestamp = self.content_cache[content_hash]
            if time.time() - timestamp < self.cache_ttl:
                return cached_result

        # 执行优化
        result = self.optimizer.optimize_cra_content(content, **kwargs)

        # 缓存结果
        self.content_cache[content_hash] = (result, time.time())

        return result
```

### 2. 并行处理

```python
class ParallelOptimizer:
    """并行优化器"""

    def __init__(self, max_workers: int = 4):
        self.max_workers = max_workers
        self.optimizer = CRADocumentOptimizer()

    def optimize_batch_parallel(self, documents: List[Dict]) -> List[str]:
        """并行批量优化"""
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = []
            for doc in documents:
                future = executor.submit(
                    self.optimizer.optimize_cra_content,
                    doc["content"],
                    doc.get("source_file"),
                    doc.get("document_type", "tax_guide"),
                    doc.get("enable_ai_enhancement", True)
                )
                futures.append(future)

            results = [future.result() for future in futures]

        return results
```

## 测试验证

### AI 增强效果测试

```python
def test_ai_enhancement_effectiveness():
    """测试 AI 增强效果"""

    optimizer = CRADocumentOptimizer()

    # 测试数据
    test_cases = [
        {
            "name": "基础税务指南",
            "content": "Simple tax guide content...",
            "expected_improvements": ["structure", "readability", "completeness"]
        },
        {
            "name": "计算示例",
            "content": "Basic calculation example...",
            "expected_improvements": ["format", "clarity", "accuracy"]
        }
    ]

    for test_case in test_cases:
        print(f"\n🧪 测试: {test_case['name']}")

        # 不使用 AI 增强
        basic_result = optimizer.optimize_cra_content(
            test_case["content"],
            enable_ai_enhancement=False
        )

        # 使用 AI 增强
        enhanced_result = optimizer.optimize_cra_content(
            test_case["content"],
            enable_ai_enhancement=True
        )

        # 对比分析
        improvement_score = analyze_improvement(basic_result, enhanced_result)
        print(f"📈 改进评分: {improvement_score:.2f}")
        print(f"✨ 内容长度变化: {len(basic_result)} → {len(enhanced_result)}")

def analyze_improvement(original: str, enhanced: str) -> float:
    """分析改进效果"""
    # 简化的改进评分算法
    score = 0.0

    # 结构改进
    original_headings = len(re.findall(r'^#{1,6}', original, re.MULTILINE))
    enhanced_headings = len(re.findall(r'^#{1,6}', enhanced, re.MULTILINE))
    if enhanced_headings > original_headings:
        score += 0.2

    # 列表改进
    original_lists = len(re.findall(r'^\s*[-*+]|\d+\.', original, re.MULTILINE))
    enhanced_lists = len(re.findall(r'^\s*[-*+]|\d+\.', enhanced, re.MULTILINE))
    if enhanced_lists > original_lists:
        score += 0.2

    # 内容完整性
    if len(enhanced) > len(original) * 1.2:
        score += 0.3

    # 格式规范性
    enhanced_format_score = check_markdown_format(enhanced)
    score += enhanced_format_score * 0.3

    return min(score, 1.0)
```

## 依赖关系更新

**新增依赖：**
```toml
# Skill_Seekers AI 增强依赖
anthropic>=0.7.0          # Claude API（备选）
openai>=1.0.0             # OpenAI API（备选）
subprocess>=3.8.0         # 系统调用
hashlib                   # 内容哈希
threading                 # 并行处理

# Claude Code Max（外部工具）
# 需要单独安装 Claude Code Max 命令行工具
```

**工具依赖：**
```bash
# 安装 Claude Code Max
wget https://github.com/anthropics/claude-code-max/releases/latest/claude-code-max-linux
chmod +x claude-code-max-linux
sudo mv claude-code-max-linux /usr/local/bin/claude-code-max
```

**前置任务：**
- 任务05：PDF 文本提取模块
- 任务06：增强内容分类模块
- 任务07：AI 增强技能生成模块

**后置任务：**
- 集成测试和性能验证
- 与 MVP 系统的完整集成
- 生产环境部署和监控

这个增强版的 Markdown 优化器集成了 Skill_Seekers 的先进技术，能够将基础的 CRA 文档转换为高质量、智能化的税务知识指南，为 BlockMe 系统提供专业级的内容处理能力。
