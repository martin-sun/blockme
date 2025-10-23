# 任务05：PDF 转图像模块开发

## 任务目标

开发一个 Python 模块，将上传的 PDF 文档转换为高质量图像序列，为后续的多模态 LLM（Claude Vision、GLM-4V）处理做准备。模块需要支持批量处理、内存优化、错误处理等生产级功能。

## 技术要求

**核心库：**
- `pdf2image`：PDF 页面转图像（基于 poppler）
- `PyMuPDF (fitz)`：备用方案，性能更好
- `Pillow`：图像后处理（压缩、格式转换）

**性能要求：**
- 支持大型 PDF（100+ 页）
- 内存占用 < 2GB
- 并发处理能力

**输出要求：**
- 图像格式：JPEG（平衡质量和大小）
- 分辨率：300 DPI（OCR 最佳）
- 单页大小：< 5MB（满足 API 限制）

## 实现步骤

### 1. 创建模块结构

在项目中创建文档处理模块：

```bash
mkdir -p src/document_processor
touch src/document_processor/__init__.py
touch src/document_processor/pdf_converter.py
```

### 2. 实现核心转换类

设计一个 `PDFToImageConverter` 类，提供以下功能：
- 单页转换
- 批量转换
- 分页处理（避免内存溢出）
- 进度回调

### 3. 图像质量优化

实现智能压缩策略：
- 检测图片大小
- 超过阈值时自动压缩
- 保持可读性前提下最小化尺寸

### 4. 错误处理

处理常见问题：
- 损坏的 PDF 文件
- 受密码保护的文件
- 超大文件（> 100MB）
- 不支持的 PDF 版本

### 5. 临时文件管理

实现安全的临时文件处理：
- 使用 `tempfile` 模块
- 处理完成后自动清理
- 避免磁盘空间耗尽

## 关键代码提示

**核心转换器实现：**

```python
from pdf2image import convert_from_path
from PIL import Image
import fitz  # PyMuPDF
from pathlib import Path
from typing import List, Optional, Callable
import tempfile
import shutil

class PDFToImageConverter:
    """PDF 转图像转换器"""

    def __init__(
        self,
        dpi: int = 300,
        output_format: str = "JPEG",
        max_image_size_mb: float = 5.0,
        jpeg_quality: int = 85
    ):
        self.dpi = dpi
        self.output_format = output_format
        self.max_image_size_bytes = int(max_image_size_mb * 1024 * 1024)
        self.jpeg_quality = jpeg_quality

    def convert_pdf(
        self,
        pdf_path: str,
        output_dir: Optional[str] = None,
        page_range: Optional[tuple] = None,
        progress_callback: Optional[Callable[[int, int], None]] = None
    ) -> List[str]:
        """
        转换 PDF 为图像序列

        Args:
            pdf_path: PDF 文件路径
            output_dir: 输出目录（None 则使用临时目录）
            page_range: 页面范围 (start, end)，None 表示全部
            progress_callback: 进度回调函数 callback(current_page, total_pages)

        Returns:
            生成的图像文件路径列表
        """
        # 验证 PDF 存在
        if not Path(pdf_path).exists():
            raise FileNotFoundError(f"PDF 文件不存在: {pdf_path}")

        # 创建输出目录
        if output_dir is None:
            output_dir = tempfile.mkdtemp(prefix="pdf_images_")
        else:
            Path(output_dir).mkdir(parents=True, exist_ok=True)

        # 获取 PDF 信息
        doc = fitz.open(pdf_path)
        total_pages = len(doc)
        doc.close()

        # 确定页面范围
        start_page = page_range[0] if page_range else 1
        end_page = page_range[1] if page_range else total_pages

        # 转换页面
        images = convert_from_path(
            pdf_path,
            dpi=self.dpi,
            first_page=start_page,
            last_page=end_page,
            fmt=self.output_format.lower()
        )

        # 保存并优化图像
        image_paths = []
        for idx, image in enumerate(images, start=start_page):
            output_path = Path(output_dir) / f"page_{idx:04d}.jpg"

            # 保存图像
            image.save(output_path, self.output_format, quality=self.jpeg_quality)

            # 检查并压缩大文件
            if output_path.stat().st_size > self.max_image_size_bytes:
                self._compress_image(output_path)

            image_paths.append(str(output_path))

            # 进度回调
            if progress_callback:
                progress_callback(idx, total_pages)

        return image_paths

    def _compress_image(self, image_path: Path):
        """压缩过大的图像"""
        image = Image.open(image_path)

        # 递减质量直到满足大小要求
        quality = self.jpeg_quality
        while quality > 30:
            temp_path = image_path.with_suffix(".tmp.jpg")
            image.save(temp_path, "JPEG", quality=quality, optimize=True)

            if temp_path.stat().st_size <= self.max_image_size_bytes:
                shutil.move(temp_path, image_path)
                return

            quality -= 10
            temp_path.unlink()

        # 仍然过大，尝试缩小分辨率
        scale = 0.8
        while scale > 0.3:
            new_size = (int(image.width * scale), int(image.height * scale))
            resized = image.resize(new_size, Image.Resampling.LANCZOS)

            resized.save(image_path, "JPEG", quality=50, optimize=True)

            if image_path.stat().st_size <= self.max_image_size_bytes:
                return

            scale -= 0.1

    def get_pdf_info(self, pdf_path: str) -> dict:
        """获取 PDF 文件信息"""
        doc = fitz.open(pdf_path)
        info = {
            "pages": len(doc),
            "file_size_mb": Path(pdf_path).stat().st_size / (1024 * 1024),
            "is_encrypted": doc.is_encrypted,
            "metadata": doc.metadata
        }
        doc.close()
        return info
```

**使用示例：**

```python
# 基础用法
converter = PDFToImageConverter(dpi=300)
image_paths = converter.convert_pdf("document.pdf", output_dir="output/")

# 带进度回调
def on_progress(current, total):
    print(f"处理进度: {current}/{total}")

image_paths = converter.convert_pdf(
    "large_document.pdf",
    progress_callback=on_progress
)

# 只转换部分页面
image_paths = converter.convert_pdf(
    "document.pdf",
    page_range=(1, 10)  # 只转换前 10 页
)
```

## 测试验证

### 1. 单元测试

创建 `tests/test_pdf_converter.py`：

```python
import pytest
from src.document_processor.pdf_converter import PDFToImageConverter

def test_convert_simple_pdf(tmp_path):
    converter = PDFToImageConverter()
    # 假设有测试 PDF
    images = converter.convert_pdf("tests/fixtures/test.pdf", str(tmp_path))
    assert len(images) > 0
    assert all(Path(img).exists() for img in images)

def test_page_range(tmp_path):
    converter = PDFToImageConverter()
    images = converter.convert_pdf(
        "tests/fixtures/multi_page.pdf",
        str(tmp_path),
        page_range=(1, 3)
    )
    assert len(images) == 3

def test_image_size_limit(tmp_path):
    converter = PDFToImageConverter(max_image_size_mb=1.0)
    images = converter.convert_pdf("tests/fixtures/high_res.pdf", str(tmp_path))
    for img_path in images:
        size_mb = Path(img_path).stat().st_size / (1024 * 1024)
        assert size_mb <= 1.0
```

运行测试：
```bash
pytest tests/test_pdf_converter.py -v
```

### 2. 性能测试

测试大文件处理：
```python
import time

converter = PDFToImageConverter()
start = time.time()
images = converter.convert_pdf("large_100pages.pdf")
duration = time.time() - start

print(f"处理 100 页 PDF 耗时: {duration:.2f} 秒")
print(f"平均每页: {duration/100:.2f} 秒")
```

### 3. 内存监控

```python
import tracemalloc

tracemalloc.start()
converter = PDFToImageConverter()
images = converter.convert_pdf("document.pdf")
current, peak = tracemalloc.get_traced_memory()

print(f"当前内存: {current / 1024 / 1024:.2f} MB")
print(f"峰值内存: {peak / 1024 / 1024:.2f} MB")
tracemalloc.stop()
```

## 注意事项

**DPI 选择：**
- **150 DPI**：快速预览，文件小
- **300 DPI**：OCR 推荐，平衡质量和大小
- **600 DPI**：高精度需求，文件很大

**内存优化：**
1. 避免一次性加载所有页面到内存
2. 使用生成器模式逐页处理
3. 及时释放 PIL Image 对象

**临时文件清理：**
```python
import atexit
import shutil

temp_dirs = []

def cleanup():
    for dir_path in temp_dirs:
        shutil.rmtree(dir_path, ignore_errors=True)

atexit.register(cleanup)
```

**并发处理：**
对于多个 PDF 文件，使用进程池并发：
```python
from concurrent.futures import ProcessPoolExecutor

def process_pdf(pdf_path):
    converter = PDFToImageConverter()
    return converter.convert_pdf(pdf_path)

with ProcessPoolExecutor(max_workers=4) as executor:
    results = executor.map(process_pdf, pdf_files)
```

**错误恢复：**
```python
try:
    images = converter.convert_pdf("document.pdf")
except Exception as e:
    # 回退到 PyMuPDF 方案
    images = convert_using_pymupdf("document.pdf")
```

## 依赖关系

**前置任务：**
- 任务04：安装 Python 依赖环境

**后置任务：**
- 任务07：Claude Vision API 集成（使用生成的图像）
- 任务08：GLM Vision API 集成（使用生成的图像）
- 任务06：Office 文档转换模块（类似流程）
