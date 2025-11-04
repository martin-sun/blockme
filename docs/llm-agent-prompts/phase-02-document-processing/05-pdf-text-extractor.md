# 任务05：PDF 文本提取模块开发（基于 Skill Seeker）

## 任务目标

开发一个 Python 模块，将 PDF 文档转换为结构化文本内容，为构建可搜索的知识库做准备。本模块基于 Skill Seeker 项目的 PyMuPDF 处理方案，专门针对 CRA 税务文档优化。

## 技术要求

**核心库：**
- `PyMuPDF (fitz)`：主要的 PDF 文本提取库（基于 Skill Seeker 方案）
- `Pillow`：图像处理（可选，用于嵌入图像）
- `pytesseract`：OCR 功能（可选，用于扫描文档）

**性能要求：**
- 支持大型 PDF（100+ 页，如 T4012 的 152 页）
- 内存占用 < 2GB
- 并发处理能力
- 智能内容分类

**输出要求：**
- 结构化文本内容
- 表格数据提取
- 章节结构识别
- 元数据提取

## 实现步骤

### 1. 创建模块结构

在项目中创建文档处理模块：

```bash
mkdir -p backend/src/document_processor
mkdir -p backend/src/skills
touch backend/src/document_processor/__init__.py
touch backend/src/document_processor/pdf_extractor.py
touch backend/src/document_processor/content_classifier.py
touch backend/src/document_processor/skill_generator.py
```

### 2. 实现核心提取类

设计一个 `PDFTextExtractor` 类，提供以下功能：
- 文本提取（基于 Skill Seeker 的 pdf_extractor_poc.py）
- 表格检测和数据提取
- 章节结构识别
- 图像提取（可选）
- OCR 处理（可选）

### 3. 内容质量优化

实现智能内容处理策略：
- 章节边界检测
- 表格数据结构化
- 代码块识别
- 页眉页脚过滤
- 重复内容合并

### 4. 错误处理

处理常见问题：
- 损坏的 PDF 文件
- 受密码保护的文件
- 超大文件（> 100MB）
- 扫描文档 OCR 处理
- 编码问题

### 5. CRA 文档专用优化

针对加拿大税务文档的特殊处理：
- 税务术语识别
- 表格分类（税务表格、计算表格）
- 法规条款结构化
- 交叉引用链接

## 关键代码提示

**核心提取器实现（基于 Skill Seeker）：**

```python
import fitz  # PyMuPDF
import json
import re
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass

@dataclass
class ChapterInfo:
    """章节信息"""
    title: str
    start_page: int
    end_page: int
    level: int

@dataclass
class TableData:
    """表格数据"""
    title: str
    rows: List[List[str]]
    page: int
    bbox: Tuple[float, float, float, float]

class PDFTextExtractor:
    """PDF 文本提取器（基于 Skill Seeker 方案）"""

    def __init__(
        self,
        pdf_path: str,
        verbose: bool = True,
        extract_images: bool = False,
        extract_tables: bool = True,
        ocr_enabled: bool = False
    ):
        self.pdf_path = pdf_path
        self.verbose = verbose
        self.extract_images = extract_images
        self.extract_tables = extract_tables
        self.ocr_enabled = ocr_enabled

        # CRA 文档专用配置
        self.tax_keywords = [
            "capital gains", "business income", "tax credits",
            "deductions", "RRSP", "GST/HST", "T4012"
        ]

        # 初始化 PyMuPDF
        self.doc = None
        self.total_pages = 0

    def open_document(self) -> bool:
        """打开 PDF 文档"""
        try:
            self.doc = fitz.open(self.pdf_path)
            self.total_pages = len(self.doc)
            if self.verbose:
                print(f"✅ 打开 PDF: {self.pdf_path}")
                print(f"📄 总页数: {self.total_pages}")
            return True
        except Exception as e:
            print(f"❌ 无法打开 PDF: {e}")
            return False

    def extract_all(self) -> Dict:
        """提取所有内容"""
        if not self.doc:
            self.open_document()

        result = {
            "metadata": self._extract_metadata(),
            "chapters": self._detect_chapters(),
            "pages": [],
            "tables": [],
            "images": []
        }

        # 按章节提取内容
        for chapter in result["chapters"]:
            chapter_content = self._extract_chapter_content(chapter)
            result["pages"].extend(chapter_content)

        # 提取表格
        if self.extract_tables:
            result["tables"] = self._extract_tables()

        # 提取图像
        if self.extract_images:
            result["images"] = self._extract_images()

        return result

    def _extract_metadata(self) -> Dict:
        """提取 PDF 元数据"""
        if not self.doc:
            return {}

        metadata = self.doc.metadata
        return {
            "title": metadata.get("title", ""),
            "author": metadata.get("author", ""),
            "subject": metadata.get("subject", ""),
            "creator": metadata.get("creator", ""),
            "producer": metadata.get("producer", ""),
            "creation_date": metadata.get("creationDate", ""),
            "modification_date": metadata.get("modDate", ""),
            "page_count": self.total_pages,
            "is_encrypted": self.doc.is_encrypted
        }

    def _detect_chapters(self) -> List[ChapterInfo]:
        """检测章节结构（CRA 文档专用）"""
        chapters = []
        current_chapter = None

        # CRA 文档章节模式
        chapter_patterns = [
            r"^Chapter\s+(\d+)\s*[:\-]\s*(.+)$",
            r"^第(\d+)章\s*[:\-]\s*(.+)$",
            r"^(\d+)\.\s*(.+)$",  # 数字编号
            r"^(.+)\s*\n\s*=+$",  # 标题 + 下划线
        ]

        for page_num in range(self.total_pages):
            page = self.doc[page_num]
            text = page.get_text()

            for pattern in chapter_patterns:
                matches = re.finditer(pattern, text, re.MULTILINE)
                for match in matches:
                    if current_chapter:
                        current_chapter.end_page = page_num
                        chapters.append(current_chapter)

                    chapter_num = match.group(1) if match.groups() else str(len(chapters) + 1)
                    chapter_title = match.group(2) if len(match.groups()) > 1 else match.group(1)

                    current_chapter = ChapterInfo(
                        title=chapter_title.strip(),
                        start_page=page_num,
                        end_page=self.total_pages - 1,
                        level=0
                    )

                    if self.verbose:
                        print(f"📖 发现章节: {chapter_title} (页 {page_num})")

        # 处理最后一章
        if current_chapter and current_chapter not in chapters:
            chapters.append(current_chapter)

        # 如果没有检测到章节，创建默认章节
        if not chapters:
            chapters.append(ChapterInfo(
                title="完整文档",
                start_page=0,
                end_page=self.total_pages - 1,
                level=0
            ))

        return chapters

    def _extract_chapter_content(self, chapter: ChapterInfo) -> List[Dict]:
        """提取章节内容"""
        content_pages = []

        for page_num in range(chapter.start_page, chapter.end_page + 1):
            page = self.doc[page_num]

            # 提取文本
            text = page.get_text()

            # 清理文本
            cleaned_text = self._clean_text(text)

            # 提取关键信息
            page_data = {
                "page_number": page_num + 1,
                "chapter": chapter.title,
                "text": cleaned_text,
                "keywords": self._extract_keywords(cleaned_text),
                "sections": self._detect_sections(cleaned_text),
                "has_tables": self._page_has_tables(page),
                "word_count": len(cleaned_text.split())
            }

            content_pages.append(page_data)

        return content_pages

    def _clean_text(self, text: str) -> str:
        """清理提取的文本"""
        # 移除页眉页脚（CRA 文档常见模式）
        text = re.sub(r'^.*?Canada Revenue Agency.*?\n', '', text, flags=re.MULTILINE)
        text = re.sub(r'^.*?Agence du revenu du Canada.*?\n', '', text, flags=re.MULTILINE)

        # 移除页码
        text = re.sub(r'^\s*\d+\s*$', '', text, flags=re.MULTILINE)

        # 清理多余空行
        text = re.sub(r'\n\s*\n\s*\n', '\n\n', text)

        # 移除特殊字符
        text = re.sub(r'[^\w\s\n\t\.\,\;\:\!\?\-\(\)\/\$\%\[\]]+', ' ', text)

        return text.strip()

    def _extract_keywords(self, text: str) -> List[str]:
        """提取关键词（税务专用）"""
        keywords = []
        text_lower = text.lower()

        for keyword in self.tax_keywords:
            if keyword in text_lower:
                keywords.append(keyword)

        # 提取大写术语（可能是法律术语）
        uppercase_terms = re.findall(r'\b[A-Z]{2,}\b', text)
        keywords.extend([term.lower() for term in uppercase_terms if len(term) > 3])

        return list(set(keywords))

    def _detect_sections(self, text: str) -> List[Dict]:
        """检测段落结构"""
        sections = []

        # 检测标题模式
        heading_patterns = [
            r'^([A-Z][^.!?]*)\s*$',  # 全大写标题
            r'^(\d+\.\d+)\s+(.+)$',   # 数字编号
            r'^([A-Z][a-z]+[^.!?]*)\s*$',  # 首字母大写标题
        ]

        lines = text.split('\n')
        current_section = None

        for line in lines:
            line = line.strip()
            if not line:
                continue

            for pattern in heading_patterns:
                if re.match(pattern, line):
                    if current_section:
                        sections.append(current_section)

                    current_section = {
                        "title": line,
                        "content": "",
                        "level": 0
                    }
                    break
            else:
                if current_section:
                    current_section["content"] += line + " "

        if current_section:
            sections.append(current_section)

        return sections

    def _extract_tables(self) -> List[TableData]:
        """提取表格数据"""
        tables = []

        for page_num in range(self.total_pages):
            page = self.doc[page_num]

            # 使用 PyMuPDF 的表格检测
            table_list = page.find_tables()

            for table in table_list:
                try:
                    # 提取表格数据
                    table_data = table.extract()

                    # 转换为字符串格式
                    rows = []
                    for row in table_data:
                        rows.append([str(cell) for cell in row])

                    table_info = TableData(
                        title=f"表格_页{page_num + 1}_{len(tables) + 1}",
                        rows=rows,
                        page=page_num + 1,
                        bbox=table.bbox
                    )

                    tables.append(table_info)

                    if self.verbose:
                        print(f"📊 提取表格: {table_info.title} ({len(rows)} 行)")

                except Exception as e:
                    if self.verbose:
                        print(f"⚠️ 表格提取失败 (页 {page_num + 1}): {e}")

        return tables

    def _page_has_tables(self, page) -> bool:
        """检查页面是否包含表格"""
        try:
            table_list = page.find_tables()
            return len(table_list) > 0
        except:
            return False

    def _extract_images(self) -> List[Dict]:
        """提取图像信息"""
        images = []

        for page_num in range(self.total_pages):
            page = self.doc[page_num]
            image_list = page.get_images()

            for img_index, img in enumerate(image_list):
                try:
                    xref = img[0]
                    base_image = self.doc.extract_image(xref)

                    image_info = {
                        "page": page_num + 1,
                        "index": img_index,
                        "xref": xref,
                        "width": base_image.get("width", 0),
                        "height": base_image.get("height", 0),
                        "colorspace": base_image.get("colorspace", ""),
                        "size": len(base_image.get("image", b""))
                    }

                    images.append(image_info)

                    if self.verbose:
                        print(f"🖼️ 发现图像: 页 {page_num + 1}, 尺寸 {image_info['width']}x{image_info['height']}")

                except Exception as e:
                    if self.verbose:
                        print(f"⚠️ 图像提取失败 (页 {page_num + 1}): {e}")

        return images

    def close_document(self):
        """关闭文档"""
        if self.doc:
            self.doc.close()
            self.doc = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close_document()


# 使用示例
def extract_cra_document(pdf_path: str, output_dir: str = "output") -> Dict:
    """提取 CRA 文档的完整流程"""

    extractor = PDFTextExtractor(
        pdf_path=pdf_path,
        verbose=True,
        extract_tables=True,
        extract_images=False
    )

    try:
        # 提取内容
        result = extractor.extract_all()

        # 保存结果
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)

        # 保存 JSON 格式
        json_path = output_path / f"{Path(pdf_path).stem}_extracted.json"
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)

        print(f"✅ 提取完成，结果保存到: {json_path}")

        # 打印统计信息
        print(f"\n📊 提取统计:")
        print(f"  - 章节: {len(result['chapters'])}")
        print(f"  - 页面: {len(result['pages'])}")
        print(f"  - 表格: {len(result['tables'])}")
        print(f"  - 总字数: {sum(p['word_count'] for p in result['pages'])}")

        return result

    finally:
        extractor.close_document()


if __name__ == "__main__":
    # 测试示例
    pdf_path = "t4012-24e.pdf"
    result = extract_cra_document(pdf_path)
```

**使用示例：**

```python
# 基础用法
extractor = PDFTextExtractor("t4012-24e.pdf", extract_tables=True)
result = extractor.extract_all()

# 只提取特定页面范围
extractor = PDFTextExtractor("document.pdf")
chapters = extractor._detect_chapters()
for chapter in chapters:
    if "Capital Gains" in chapter.title:
        content = extractor._extract_chapter_content(chapter)

# 获取文档信息
metadata = extractor._extract_metadata()
print(f"文档标题: {metadata['title']}")
print(f"页数: {metadata['page_count']}")
```

## 测试验证

### 1. 单元测试

创建 `tests/test_pdf_extractor.py`：

```python
import pytest
import tempfile
import json
from backend.src.document_processor.pdf_extractor import PDFTextExtractor

def test_extract_simple_pdf(tmp_path):
    # 假设有测试 PDF
    extractor = PDFTextExtractor("tests/fixtures/t4012_sample.pdf")
    result = extractor.extract_all()

    assert len(result['pages']) > 0
    assert len(result['chapters']) > 0
    assert 'metadata' in result
    extractor.close_document()

def test_chapter_detection(tmp_path):
    extractor = PDFTextExtractor("tests/fixtures/t4012_sample.pdf")
    chapters = extractor._detect_chapters()

    assert len(chapters) > 0
    assert all(isinstance(chapter.start_page, int) for chapter in chapters)
    assert all(isinstance(chapter.end_page, int) for chapter in chapters)
    extractor.close_document()

def test_table_extraction(tmp_path):
    extractor = PDFTextExtractor("tests/fixtures/t4012_sample.pdf", extract_tables=True)
    tables = extractor._extract_tables()

    # T4012 应该包含表格
    assert len(tables) > 0
    assert all(len(table.rows) > 0 for table in tables)
    extractor.close_document()

def test_cra_keywords(tmp_path):
    extractor = PDFTextExtractor("tests/fixtures/t4012_sample.pdf")

    # 测试税务关键词提取
    test_text = "This document discusses capital gains and RRSP contributions."
    keywords = extractor._extract_keywords(test_text)

    assert "capital gains" in keywords
    assert "rrsp" in keywords
    extractor.close_document()
```

运行测试：
```bash
pytest tests/test_pdf_extractor.py -v
```

### 2. 性能测试

测试大文件处理：
```python
import time
import psutil
import os

def test_large_pdf_performance():
    process = psutil.Process(os.getpid())

    extractor = PDFTextExtractor("t4012-24e.pdf")

    # 监控内存
    mem_before = process.memory_info().rss / 1024 / 1024  # MB

    start_time = time.time()
    result = extractor.extract_all()
    duration = time.time() - start_time

    mem_after = process.memory_info().rss / 1024 / 1024  # MB
    mem_peak = max(mem_before, mem_after)

    print(f"处理 {result['metadata']['page_count']} 页 PDF 耗时: {duration:.2f} 秒")
    print(f"平均每页: {duration/result['metadata']['page_count']:.2f} 秒")
    print(f"内存峰值: {mem_peak:.2f} MB")

    # 性能要求检查
    assert duration < 300  # 5分钟内完成
    assert mem_peak < 2048  # 内存小于 2GB

    extractor.close_document()
```

### 3. CRA 文档专用测试

```python
def test_t4012_specific_features():
    extractor = PDFTextExtractor("t4012-24e.pdf")
    result = extractor.extract_all()

    # 检查是否包含 T4012 特定内容
    all_text = " ".join(page['text'] for page in result['pages'])

    # T4012 应该包含的关键内容
    required_terms = [
        "T4012",
        "Capital Gains",
        "Business Income",
        "Tax Guide",
        "CRA"
    ]

    for term in required_terms:
        assert term.lower() in all_text.lower(), f"缺少必要术语: {term}"

    # 检查章节结构
    assert len(result['chapters']) >= 3, "T4012 应该至少有 3 个章节"

    # 检查表格
    if result['tables']:
        assert len(result['tables']) > 0, "T4012 应该包含表格"

    extractor.close_document()
```

## 注意事项

**CRA 文档特点：**
- **双语内容**：英语和法语混合
- **复杂表格**：税务计算表格
- **法律条款**：精确的法律文本
- **交叉引用**：大量内部链接

**处理策略：**
1. **语言检测**：区分英语/法语内容
2. **表格保留**：保持表格数据的完整性
3. **法律术语**：精确提取，不做简化
4. **引用处理**：维护章节间的引用关系

**内存优化：**
1. 分页处理避免一次性加载
2. 及时释放不需要的页面数据
3. 大型表格单独处理
4. 图像提取可选（节省内存）

**错误恢复：**
```python
try:
    extractor = PDFTextExtractor("document.pdf")
    result = extractor.extract_all()
except Exception as e:
    # 回退策略：使用备用提取方法
    result = fallback_extraction("document.pdf")
```

## 与 Skill Seeker 的集成

**代码复用：**
- 基于 Skill Seeker 的 `pdf_extractor_poc.py` 核心逻辑
- 保留表格检测和章节识别功能
- 适配 CRA 文档的特殊需求

**增强功能：**
- CRA 专用关键词库
- 税务术语识别
- 法规条款结构化
- 双语内容处理

**输出格式：**
- 兼容 Skill Seeker 的 JSON 格式
- 增加税务专用字段
- 保持向后兼容性

## 依赖关系

**新增依赖：**
```toml
# 已在 pyproject.toml 中确认
PyMuPDF>=1.24.0          # 核心 PDF 处理
Pillow>=10.0.0           # 图像处理
pytesseract>=0.3.13      # OCR（可选）
```

**前置任务：**
- 任务04：Python 依赖环境安装

**后置任务：**
- 任务06：内容分类模块（使用提取的内容）
- 任务07：Skill 生成模块（转换为 Skill 格式）

这个模块为 CRA 文档处理提供了完整的解决方案，基于 Skill Seeker 的成熟技术栈，专门针对税务文档的特点进行了优化。