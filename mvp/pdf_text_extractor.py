#!/usr/bin/env python3
"""
PDF 文本提取器 MVP 版本
基于 Skill Seeker 的 PyMuPDF 方案，支持 OCR 和分页处理
用于验证 CRA T4012 等大型 PDF 的处理能力
"""

import os
import time
import psutil
import traceback
import io
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime

# PDF 处理库
import fitz  # PyMuPDF
from PIL import Image
import pytesseract

@dataclass
class PageResult:
    """单页处理结果"""
    page_number: int
    text: str
    text_quality: float  # 文本质量评分
    has_images: bool
    needs_ocr: bool
    processing_time: float
    word_count: int
    char_count: int

@dataclass
class ExtractionResult:
    """完整提取结果"""
    file_path: str
    total_pages: int
    successful_pages: int
    pages_needing_ocr: int
    total_text: str
    processing_time: float
    memory_peak_mb: float
    pages: List[PageResult]
    metadata: Dict

class PDFTextExtractor:
    """PDF 文本提取器 - MVP 版本"""

    def __init__(self, enable_ocr: bool = True, ocr_language: str = "eng"):
        self.enable_ocr = enable_ocr
        self.ocr_language = ocr_language
        self.process = psutil.Process(os.getpid())

        # 统计信息
        self.stats = {
            "pages_processed": 0,
            "ocr_used": 0,
            "errors": 0
        }

    def extract_pdf(self, pdf_path: str, max_pages: Optional[int] = None) -> ExtractionResult:
        """
        提取 PDF 文本

        Args:
            pdf_path: PDF 文件路径
            max_pages: 最大处理页数（None 表示全部）

        Returns:
            ExtractionResult: 提取结果
        """
        print(f"\n🚀 开始处理 PDF: {pdf_path}")

        # 记录开始时间和内存
        start_time = time.time()
        start_memory = self.process.memory_info().rss / 1024 / 1024  # MB

        try:
            # 打开 PDF
            doc = fitz.open(pdf_path)
            total_pages = len(doc)

            if max_pages:
                total_pages = min(total_pages, max_pages)
                print(f"📄 限制处理页数: {total_pages}")
            else:
                print(f"📄 总页数: {total_pages}")

            # 检查 PDF 是否加密
            if doc.is_encrypted:
                print("⚠️ PDF 文件已加密，尝试解密...")
                if not doc.authenticate(""):
                    raise ValueError("无法解密 PDF 文件")

            # 获取 PDF 元数据
            metadata = self._extract_metadata(doc)

            # 逐页处理
            pages = []
            successful_pages = 0
            pages_needing_ocr = 0

            for page_num in range(total_pages):
                try:
                    print(f"📖 处理第 {page_num + 1}/{total_pages} 页...")
                    page_result = self._process_page(doc, page_num)

                    pages.append(page_result)

                    if page_result.text_quality > 0.1:  # 文本质量阈值
                        successful_pages += 1

                    if page_result.needs_ocr:
                        pages_needing_ocr += 1

                    # 更新统计
                    self.stats["pages_processed"] += 1
                    if page_result.needs_ocr:
                        self.stats["ocr_used"] += 1

                    # 内存检查
                    current_memory = self.process.memory_info().rss / 1024 / 1024
                    if current_memory > 1024:  # 超过 1GB
                        print(f"⚠️ 内存使用较高: {current_memory:.1f} MB")

                except Exception as e:
                    print(f"❌ 处理第 {page_num + 1} 页时出错: {e}")
                    self.stats["errors"] += 1
                    continue

            # 合并所有文本
            total_text = self._combine_pages_text(pages)

            # 计算处理时间
            end_time = time.time()
            end_memory = self.process.memory_info().rss / 1024 / 1024

            processing_time = end_time - start_time
            memory_peak = max(start_memory, end_memory)

            # 关闭文档
            doc.close()

            # 创建结果对象
            result = ExtractionResult(
                file_path=pdf_path,
                total_pages=total_pages,
                successful_pages=successful_pages,
                pages_needing_ocr=pages_needing_ocr,
                total_text=total_text,
                processing_time=processing_time,
                memory_peak_mb=memory_peak,
                pages=pages,
                metadata=metadata
            )

            self._print_summary(result)
            return result

        except Exception as e:
            print(f"❌ PDF 处理失败: {e}")
            print(f"错误详情: {traceback.format_exc()}")
            raise

    def _process_page(self, doc, page_num: int) -> PageResult:
        """处理单个页面"""
        start_time = time.time()

        page = doc[page_num]

        # 尝试直接文本提取
        text = page.get_text()
        text_quality = self._evaluate_text_quality(text)

        needs_ocr = False
        has_images = False

        # 如果文本质量太低，尝试 OCR
        if text_quality < 0.3 and self.enable_ocr:
            print(f"  🔄 文本质量较低 ({text_quality:.2f})，尝试 OCR...")
            try:
                ocr_text = self._ocr_page(page)
                if ocr_text and len(ocr_text.strip()) > len(text.strip()):
                    text = ocr_text
                    needs_ocr = True
                    text_quality = self._evaluate_text_quality(text)
                    print(f"  ✅ OCR 成功，新文本质量: {text_quality:.2f}")
                else:
                    print(f"  ⚠️ OCR 未改善文本质量")
            except Exception as e:
                print(f"  ❌ OCR 失败: {e}")

        # 检查页面是否有图像
        image_list = page.get_images()
        has_images = len(image_list) > 0

        processing_time = time.time() - start_time

        return PageResult(
            page_number=page_num + 1,
            text=text.strip(),
            text_quality=text_quality,
            has_images=has_images,
            needs_ocr=needs_ocr,
            processing_time=processing_time,
            word_count=len(text.split()),
            char_count=len(text)
        )

    def _evaluate_text_quality(self, text: str) -> float:
        """评估文本质量"""
        if not text or len(text.strip()) < 10:
            return 0.0

        score = 0.0

        # 1. 文本长度
        text_length = len(text.strip())
        if text_length > 100:
            score += 0.3
        elif text_length > 50:
            score += 0.2
        else:
            score += 0.1

        # 2. 单词完整性
        words = text.split()
        if words:
            complete_words = sum(1 for word in words if word.isalpha() or '.' in word or ',' in word)
            word_completeness = complete_words / len(words)
            score += word_completeness * 0.3

        # 3. 句子结构
        sentences = text.split('.')
        if len(sentences) > 1:
            score += 0.2

        # 4. 常见字符检查
        common_chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789.,!?;:()-"
        char_ratio = sum(1 for c in text if c in common_chars) / len(text) if text else 0
        score += char_ratio * 0.2

        return min(score, 1.0)

    def _ocr_page(self, page) -> str:
        """对页面进行 OCR"""
        try:
            # 将页面转换为图像
            pix = page.get_pixmap(matrix=fitz.Matrix(2.0, 2.0))  # 2x 分辨率
            img_data = pix.tobytes("png")
            img = Image.open(io.BytesIO(img_data))

            # 进行 OCR
            text = pytesseract.image_to_string(img, lang=self.ocr_language)
            return text

        except Exception as e:
            print(f"    OCR 错误: {e}")
            return ""

    def _extract_metadata(self, doc) -> Dict:
        """提取 PDF 元数据"""
        metadata = doc.metadata
        return {
            "title": metadata.get("title", ""),
            "author": metadata.get("author", ""),
            "subject": metadata.get("subject", ""),
            "creator": metadata.get("creator", ""),
            "producer": metadata.get("producer", ""),
            "creation_date": metadata.get("creationDate", ""),
            "modification_date": metadata.get("modDate", ""),
            "page_count": len(doc),
            "is_encrypted": doc.is_encrypted
        }

    def _combine_pages_text(self, pages: List[PageResult]) -> str:
        """合并所有页面的文本"""
        combined_text = []

        for page in pages:
            if page.text:
                combined_text.append(f"\n=== 第 {page.page_number} 页 ===\n")
                combined_text.append(page.text)
                combined_text.append("\n")

        return "\n".join(combined_text)

    def _print_summary(self, result: ExtractionResult):
        """打印处理摘要"""
        print(f"\n📊 处理完成摘要:")
        print(f"  📁 文件: {Path(result.file_path).name}")
        print(f"  📄 总页数: {result.total_pages}")
        print(f"  ✅ 成功处理: {result.successful_pages}")
        print(f"  🔍 OCR 使用: {result.pages_needing_ocr}")
        print(f"  ⏱️  处理时间: {result.processing_time:.2f} 秒")
        print(f"  🧠 内存峰值: {result.memory_peak_mb:.1f} MB")
        print(f"  📝 总字符数: {len(result.total_text):,}")
        print(f"  📖 总词数: {len(result.total_text.split()):,}")

        if result.processing_time > 0:
            pages_per_second = result.total_pages / result.processing_time
            print(f"  ⚡ 处理速度: {pages_per_second:.2f} 页/秒")

        # 计算平均文本质量
        if result.pages:
            avg_quality = sum(p.text_quality for p in result.pages) / len(result.pages)
            print(f"  📈 平均文本质量: {avg_quality:.2f}")

def save_extraction_result(result: ExtractionResult, output_dir: str = "output"):
    """保存提取结果"""
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)

    # 生成文件名
    base_name = Path(result.file_path).stem
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # 保存完整文本
    text_file = output_path / f"{base_name}_extracted_{timestamp}.txt"
    with open(text_file, 'w', encoding='utf-8') as f:
        f.write(result.total_text)
    print(f"💾 文本已保存: {text_file}")

    # 保存摘要信息
    summary_file = output_path / f"{base_name}_summary_{timestamp}.json"
    import json
    summary_data = {
        "file_path": result.file_path,
        "total_pages": result.total_pages,
        "successful_pages": result.successful_pages,
        "pages_needing_ocr": result.pages_needing_ocr,
        "processing_time": result.processing_time,
        "memory_peak_mb": result.memory_peak_mb,
        "total_chars": len(result.total_text),
        "total_words": len(result.total_text.split()),
        "metadata": result.metadata,
        "stats": {
            "pages_processed": len(result.pages),
            "ocr_used": sum(1 for p in result.pages if p.needs_ocr),
            "errors": 0
        }
    }

    with open(summary_file, 'w', encoding='utf-8') as f:
        json.dump(summary_data, f, indent=2, ensure_ascii=False)
    print(f"📊 摘要已保存: {summary_file}")

    return text_file, summary_file

# 测试函数
def test_pdf_extraction():
    """测试 PDF 提取功能"""
    print("🧪 PDF 文本提取器测试")
    print("=" * 50)

    # 创建提取器
    extractor = PDFTextExtractor(enable_ocr=True)

    # 查找测试 PDF 文件
    test_files = [
        # CRA T4012 文档
        "pdf/t4012-24e.pdf",
        "t4012-24e.pdf",
        "sample.pdf",
        "test.pdf"
    ]

    test_file = None
    for file_path in test_files:
        if Path(file_path).exists():
            test_file = file_path
            break

    if not test_file:
        print("❌ 未找到测试 PDF 文件")
        print("请将测试 PDF 文件放在以下位置之一：")
        for file_path in test_files:
            print(f"  - {file_path}")
        return

    try:
        # 限制处理前10页进行测试
        result = extractor.extract_pdf(test_file, max_pages=10)

        # 保存结果
        text_file, summary_file = save_extraction_result(result)

        # 显示一些提取的文本样本
        print(f"\n📝 文本样本 (前500字符):")
        print("-" * 30)
        print(result.total_text[:500])
        print("-" * 30)

        return result

    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return None

if __name__ == "__main__":
    test_pdf_extraction()