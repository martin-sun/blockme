# 任务09：Markdown 生成优化

## 任务目标

优化从 Vision API 提取的 Markdown 内容，进行清洗、格式化、增强和质量检查，确保生成的知识库文档结构清晰、格式统一、易于检索和阅读。

## 技术要求

**处理内容：**
- 清理 API 响应中的冗余内容
- 统一 Markdown 格式规范
- 修复表格对齐问题
- 优化代码块格式
- 生成文档元数据

**输出规范：**
- 符合 CommonMark 标准
- 添加 YAML Front Matter
- 自动生成目录（TOC）
- 提取关键词和摘要

## 实现步骤

### 1. 创建 Markdown 优化器模块

```bash
touch src/document_processor/markdown_optimizer.py
```

### 2. 实现清理功能

去除多余内容：
- 删除 API 可能添加的解释文字
- 去除重复的分隔线
- 统一换行符
- 清理空白字符

### 3. 实现格式化功能

标准化 Markdown 格式：
- 统一标题层级
- 规范列表缩进
- 修复表格分隔符
- 格式化代码块

### 4. 实现元数据生成

自动生成文档信息：
- 提取标题作为元数据
- 生成摘要（使用 LLM）
- 提取关键词
- 记录来源和时间

### 5. 实现质量检查

验证 Markdown 质量：
- 检查语法错误
- 验证链接完整性
- 检测空内容块
- 评估可读性

## 关键代码提示

**Markdown 优化器实现：**

```python
import re
from typing import Dict, List, Optional
from pathlib import Path
import yaml
from datetime import datetime

class MarkdownOptimizer:
    """Markdown 内容优化器"""

    def __init__(self):
        self.stats = {
            "cleaned": 0,
            "formatted": 0,
            "metadata_added": 0
        }

    def optimize(
        self,
        raw_markdown: str,
        source_file: Optional[str] = None,
        document_type: Optional[str] = None
    ) -> str:
        """
        全流程优化 Markdown

        Args:
            raw_markdown: 原始 Markdown 内容
            source_file: 源文件名
            document_type: 文档类型

        Returns:
            优化后的 Markdown
        """
        # 1. 清理内容
        cleaned = self._clean_content(raw_markdown)

        # 2. 格式化
        formatted = self._format_markdown(cleaned)

        # 3. 生成元数据
        metadata = self._generate_metadata(formatted, source_file, document_type)

        # 4. 组合最终输出
        final_markdown = self._combine_with_metadata(metadata, formatted)

        return final_markdown

    def _clean_content(self, markdown: str) -> str:
        """清理内容"""
        # 删除常见的 API 解释前缀
        prefixes_to_remove = [
            r"^以下是提取的内容：\n+",
            r"^这是转换后的 Markdown：\n+",
            r"^根据图片内容.*?：\n+",
        ]
        for pattern in prefixes_to_remove:
            markdown = re.sub(pattern, "", markdown, flags=re.MULTILINE | re.IGNORECASE)

        # 删除多余的分隔线（连续3个以上）
        markdown = re.sub(r"(\n---\n){3,}", "\n\n---\n\n", markdown)

        # 统一换行符
        markdown = markdown.replace("\r\n", "\n")

        # 清理多余空行（超过2个连续空行）
        markdown = re.sub(r"\n{4,}", "\n\n\n", markdown)

        # 清理行尾空格
        lines = [line.rstrip() for line in markdown.split("\n")]
        markdown = "\n".join(lines)

        self.stats["cleaned"] += 1
        return markdown

    def _format_markdown(self, markdown: str) -> str:
        """格式化 Markdown"""
        # 规范化标题（确保 # 后有空格）
        markdown = re.sub(r"^(#{1,6})([^ #])", r"\1 \2", markdown, flags=re.MULTILINE)

        # 规范化列表（确保 - 或 * 后有空格）
        markdown = re.sub(r"^([*\-])([^ ])", r"\1 \2", markdown, flags=re.MULTILINE)

        # 修复表格分隔符
        markdown = self._fix_tables(markdown)

        # 格式化代码块（确保语言标注）
        markdown = self._format_code_blocks(markdown)

        self.stats["formatted"] += 1
        return markdown

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

**使用示例：**

```python
# 基础优化
optimizer = MarkdownOptimizer()
raw_md = """# 文档标题
这是内容..."""

optimized = optimizer.optimize(
    raw_md,
    source_file="report.pdf",
    document_type="technical"
)

# 保存优化后的文档
with open("output.md", "w", encoding="utf-8") as f:
    f.write(optimized)

# 质量检查
quality = optimizer.validate_quality(optimized)
print(f"质量评分: {quality['score']}/100")
if not quality['is_valid']:
    print(f"问题: {quality['issues']}")
```

**集成到处理流程：**

```python
# 完整流程
from src.document_processor.pdf_converter import PDFToImageConverter
from src.document_processor.claude_vision import ClaudeVisionExtractor
from src.document_processor.markdown_optimizer import MarkdownOptimizer

# 1. PDF → 图像
pdf_converter = PDFToImageConverter()
images = pdf_converter.convert_pdf("document.pdf")

# 2. 图像 → 原始 Markdown
vision_extractor = ClaudeVisionExtractor(api_key=CLAUDE_KEY)
raw_markdown = vision_extractor.extract_from_images(images)

# 3. 优化 Markdown
optimizer = MarkdownOptimizer()
final_markdown = optimizer.optimize(
    raw_markdown,
    source_file="document.pdf",
    document_type="academic"
)

# 4. 保存到知识库
output_path = "knowledge_base/document.md"
with open(output_path, "w", encoding="utf-8") as f:
    f.write(final_markdown)

print(f"✅ 文档已保存: {output_path}")
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

**前置任务：**
- 任务07：Claude Vision API 集成
- 任务08：GLM Vision API 集成

**后置任务：**
- 任务11：Markdown 存储索引系统
- 任务12：文档元数据管理
