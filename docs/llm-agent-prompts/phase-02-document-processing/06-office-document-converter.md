# 任务06：Office 文档转换模块

## 任务目标

开发一个统一的 Office 文档处理模块，支持将 Word (.docx)、Excel (.xlsx)、PowerPoint (.pptx) 文档转换为 PDF，然后再转为图像序列。提供直接文本提取选项用于简单文档，复杂排版文档则通过图像方式处理。

## 技术要求

**核心库：**
- `python-docx`：Word 文档文本提取
- `openpyxl`：Excel 数据读取
- `python-pptx`：PowerPoint 内容提取
- `LibreOffice`：Office → PDF 转换（headless 模式）
- `unoconv`：命令行转换工具

**转换策略：**
- **简单文本文档** → 直接提取文本
- **复杂排版文档** → Office → PDF → 图像 → LLM

## 实现步骤

### 1. 安装系统依赖

确保 LibreOffice 已安装（用于无头转换）：

```bash
# macOS
brew install libreoffice

# Linux
sudo apt-get install libreoffice
```

### 2. 实现 Office 转 PDF 模块

创建通用转换接口：
```bash
touch src/document_processor/office_converter.py
```

核心功能：
- 自动检测文档类型
- 调用 LibreOffice headless 转换
- 处理转换超时和错误
- 返回 PDF 文件路径

### 3. 实现文本提取功能

为简单文档提供快速路径：
- Word 文档直接提取段落和表格
- Excel 提取工作表数据
- PowerPoint 提取幻灯片文字

### 4. 智能路由逻辑

判断使用哪种处理方式：
- 检测文档复杂度（图片数量、表格复杂度）
- 简单文档 → 文本提取
- 复杂文档 → 图像处理

## 关键代码提示

**Office 转 PDF 核心实现：**

```python
import subprocess
from pathlib import Path
from typing import Optional
import tempfile
import platform

class OfficeConverter:
    """Office 文档转换器"""

    def __init__(self, timeout: int = 60):
        """
        Args:
            timeout: 转换超时时间（秒）
        """
        self.timeout = timeout
        self.libreoffice_path = self._find_libreoffice()

    def _find_libreoffice(self) -> str:
        """查找 LibreOffice 可执行文件"""
        system = platform.system()

        if system == "Darwin":  # macOS
            paths = [
                "/Applications/LibreOffice.app/Contents/MacOS/soffice",
                "/usr/local/bin/soffice"
            ]
        elif system == "Linux":
            paths = [
                "/usr/bin/libreoffice",
                "/usr/bin/soffice"
            ]
        else:  # Windows
            paths = [
                "C:\\Program Files\\LibreOffice\\program\\soffice.exe",
                "C:\\Program Files (x86)\\LibreOffice\\program\\soffice.exe"
            ]

        for path in paths:
            if Path(path).exists():
                return path

        raise RuntimeError("LibreOffice 未安装或未找到")

    def to_pdf(
        self,
        office_file: str,
        output_dir: Optional[str] = None
    ) -> str:
        """
        转换 Office 文档为 PDF

        Args:
            office_file: Office 文件路径（.docx/.xlsx/.pptx）
            output_dir: 输出目录（None 则使用临时目录）

        Returns:
            生成的 PDF 文件路径
        """
        input_path = Path(office_file)
        if not input_path.exists():
            raise FileNotFoundError(f"文件不存在: {office_file}")

        # 验证文件类型
        supported_exts = {".docx", ".xlsx", ".pptx", ".doc", ".xls", ".ppt"}
        if input_path.suffix.lower() not in supported_exts:
            raise ValueError(f"不支持的文件类型: {input_path.suffix}")

        # 创建输出目录
        if output_dir is None:
            output_dir = tempfile.mkdtemp(prefix="office_pdf_")
        else:
            Path(output_dir).mkdir(parents=True, exist_ok=True)

        # 调用 LibreOffice 转换
        cmd = [
            self.libreoffice_path,
            "--headless",
            "--convert-to", "pdf",
            "--outdir", output_dir,
            str(input_path)
        ]

        try:
            result = subprocess.run(
                cmd,
                timeout=self.timeout,
                capture_output=True,
                text=True,
                check=True
            )

            # 查找生成的 PDF 文件
            pdf_name = input_path.stem + ".pdf"
            pdf_path = Path(output_dir) / pdf_name

            if not pdf_path.exists():
                raise RuntimeError(f"PDF 生成失败: {result.stderr}")

            return str(pdf_path)

        except subprocess.TimeoutExpired:
            raise RuntimeError(f"转换超时（{self.timeout}秒）")
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"转换失败: {e.stderr}")

    def extract_text_simple(self, office_file: str) -> str:
        """
        简单文本提取（不保留格式）

        适用于纯文本文档，速度快但丢失排版
        """
        input_path = Path(office_file)
        ext = input_path.suffix.lower()

        if ext == ".docx":
            return self._extract_docx_text(office_file)
        elif ext == ".xlsx":
            return self._extract_xlsx_text(office_file)
        elif ext == ".pptx":
            return self._extract_pptx_text(office_file)
        else:
            raise ValueError(f"不支持的文件类型: {ext}")

    def _extract_docx_text(self, docx_file: str) -> str:
        """提取 Word 文档文本"""
        from docx import Document

        doc = Document(docx_file)
        paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]

        # 提取表格内容
        tables_text = []
        for table in doc.tables:
            for row in table.rows:
                row_text = " | ".join(cell.text.strip() for cell in row.cells)
                tables_text.append(row_text)

        all_text = "\n\n".join(paragraphs)
        if tables_text:
            all_text += "\n\n## 表格内容\n" + "\n".join(tables_text)

        return all_text

    def _extract_xlsx_text(self, xlsx_file: str) -> str:
        """提取 Excel 数据"""
        from openpyxl import load_workbook

        wb = load_workbook(xlsx_file, data_only=True)
        sheets_text = []

        for sheet_name in wb.sheetnames:
            ws = wb[sheet_name]
            sheets_text.append(f"## {sheet_name}\n")

            for row in ws.iter_rows(values_only=True):
                row_text = " | ".join(str(cell) if cell is not None else "" for cell in row)
                if row_text.strip():
                    sheets_text.append(row_text)

            sheets_text.append("")  # 空行分隔

        return "\n".join(sheets_text)

    def _extract_pptx_text(self, pptx_file: str) -> str:
        """提取 PowerPoint 文本"""
        from pptx import Presentation

        prs = Presentation(pptx_file)
        slides_text = []

        for idx, slide in enumerate(prs.slides, 1):
            slides_text.append(f"## 幻灯片 {idx}\n")

            for shape in slide.shapes:
                if hasattr(shape, "text") and shape.text.strip():
                    slides_text.append(shape.text)

            slides_text.append("")  # 空行分隔

        return "\n".join(slides_text)

    def analyze_complexity(self, office_file: str) -> dict:
        """
        分析文档复杂度，决定使用文本提取还是图像处理

        Returns:
            {
                "is_simple": bool,  # 是否适合简单文本提取
                "image_count": int,
                "table_count": int,
                "page_count": int
            }
        """
        input_path = Path(office_file)
        ext = input_path.suffix.lower()

        if ext == ".docx":
            return self._analyze_docx(office_file)
        elif ext == ".pptx":
            return self._analyze_pptx(office_file)
        else:
            # Excel 默认使用文本提取
            return {"is_simple": True, "image_count": 0, "table_count": 1, "page_count": 1}

    def _analyze_docx(self, docx_file: str) -> dict:
        """分析 Word 文档复杂度"""
        from docx import Document

        doc = Document(docx_file)
        image_count = sum(
            len([r for r in p.runs if r._element.xpath('.//a:blip')])
            for p in doc.paragraphs
        )
        table_count = len(doc.tables)

        # 简单文档判断：图片少、表格简单
        is_simple = image_count < 5 and table_count < 3

        return {
            "is_simple": is_simple,
            "image_count": image_count,
            "table_count": table_count,
            "page_count": len(doc.sections)
        }

    def _analyze_pptx(self, pptx_file: str) -> dict:
        """分析 PowerPoint 复杂度"""
        from pptx import Presentation

        prs = Presentation(pptx_file)
        slide_count = len(prs.slides)

        # PPT 通常包含大量图片和排版，默认使用图像方式
        return {
            "is_simple": False,
            "image_count": -1,  # 难以统计
            "table_count": 0,
            "page_count": slide_count
        }
```

**统一处理流程：**

```python
from src.document_processor.office_converter import OfficeConverter
from src.document_processor.pdf_converter import PDFToImageConverter

class DocumentProcessor:
    """统一文档处理器"""

    def __init__(self):
        self.office_converter = OfficeConverter()
        self.pdf_converter = PDFToImageConverter()

    def process_document(self, file_path: str) -> dict:
        """
        智能处理文档

        Returns:
            {
                "method": "text" | "image",
                "content": str or List[str],  # 文本或图像路径列表
                "metadata": dict
            }
        """
        ext = Path(file_path).suffix.lower()

        # PDF 直接转图像
        if ext == ".pdf":
            images = self.pdf_converter.convert_pdf(file_path)
            return {"method": "image", "content": images}

        # Office 文档
        if ext in {".docx", ".xlsx", ".pptx"}:
            complexity = self.office_converter.analyze_complexity(file_path)

            if complexity["is_simple"]:
                # 简单文档 → 文本提取
                text = self.office_converter.extract_text_simple(file_path)
                return {"method": "text", "content": text, "metadata": complexity}
            else:
                # 复杂文档 → PDF → 图像
                pdf_path = self.office_converter.to_pdf(file_path)
                images = self.pdf_converter.convert_pdf(pdf_path)
                return {"method": "image", "content": images, "metadata": complexity}

        raise ValueError(f"不支持的文件类型: {ext}")
```

## 测试验证

### 1. Office 转 PDF 测试

```python
converter = OfficeConverter()

# 测试 Word
pdf = converter.to_pdf("test.docx")
assert Path(pdf).exists()

# 测试 Excel
pdf = converter.to_pdf("data.xlsx")
assert Path(pdf).exists()

# 测试 PowerPoint
pdf = converter.to_pdf("slides.pptx")
assert Path(pdf).exists()
```

### 2. 文本提取测试

```python
text = converter.extract_text_simple("simple_document.docx")
assert len(text) > 0
assert "表格内容" in text  # 确保表格被提取
```

### 3. 复杂度分析测试

```python
complexity = converter.analyze_complexity("complex_report.docx")
assert "is_simple" in complexity
assert complexity["image_count"] >= 0
```

## 注意事项

**LibreOffice 并发限制：**
- 多个进程同时调用可能冲突
- 使用锁机制或队列顺序处理

**旧格式兼容：**
- `.doc`, `.xls`, `.ppt` 也支持
- 但建议提示用户升级到新格式

**超时设置：**
- 大文件转换可能很慢
- 根据文件大小动态调整超时时间

**内存清理：**
- 及时删除临时 PDF 文件
- 避免磁盘占用过多

## 依赖关系

**前置任务：**
- 任务04：安装 Python 依赖环境
- 任务05：PDF 转图像模块

**后置任务：**
- 任务07：Claude Vision API 集成
- 任务08：GLM Vision API 集成
