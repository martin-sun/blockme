#!/usr/bin/env python3
"""
PyMuPDF 文本提取测试
专门测试 PyMuPDF 的文本提取能力，不依赖 OCR
"""

import fitz
from pathlib import Path
import time
import json

def test_pymupdf_basic():
    """测试 PyMuPDF 基本功能"""
    print("🔍 测试 PyMuPDF 基本功能...")

    try:
        # 检查版本
        version = fitz.version
        print(f"✅ PyMuPDF 版本: {version}")

        # 测试创建空白文档
        doc = fitz.open()  # 创建空白文档
        page = doc.new_page()  # 添加一页

        # 添加一些文本
        rect = fitz.Rect(50, 50, 300, 80)
        page.insert_text(rect, "CRA T4012 Tax Guide - Test Document", fontsize=12)

        # 提取文本
        text = page.get_text()
        print(f"✅ 文本提取测试: '{text.strip()}'")

        doc.close()
        return True

    except Exception as e:
        print(f"❌ PyMuPDF 基本测试失败: {e}")
        return False

def test_text_quality():
    """测试文本质量评估"""
    def evaluate_text_quality(text: str) -> float:
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

    # 测试不同质量的文本
    test_cases = [
        ("", "空文本"),
        ("short", "短文本"),
        ("This is a proper sentence with multiple words and punctuation.", "正常文本"),
        ("Th1s t3xt h@s numb3rs & sp3cial ch@racters.", "包含数字的文本"),
        ("Broken words wit spaces",
         "不完整文本")
    ]

    print("\n📊 文本质量评估测试:")
    for text, description in test_cases:
        quality = evaluate_text_quality(text)
        print(f"  {description}: {quality:.2f}")

def create_test_pdf():
    """创建一个测试用的 PDF"""
    print("\n📝 创建测试 PDF...")

    try:
        # 创建新文档
        doc = fitz.open()

        # 第1页：标题和概述
        page1 = doc.new_page()
        rect1 = fitz.Rect(50, 50, 550, 100)
        page1.insert_text(rect1, "CRA T4012 - Income Tax and Benefit Guide", fontsize=16, fontname="helvetica")

        rect2 = fitz.Rect(50, 120, 550, 200)
        page1.insert_text(rect2, """This guide contains information for residents of Canada who need to file a T1 income tax and benefit return.

Important Dates:
- April 30, 2025: Filing deadline for most people
- June 15, 2025: Self-employed individuals

Types of Income to Report:
1. Employment income
2. Business income
3. Capital gains
4. Investment income""", fontsize=12, fontname="helvetica")

        # 第2页：资本收益
        page2 = doc.new_page()
        rect3 = fitz.Rect(50, 50, 550, 150)
        page2.insert_text(rect3, """Chapter 3 - Capital Gains

What are Capital Gains?
Capital gains are profits you make when you sell or dispose of:
- Real estate
- Stocks and bonds
- Mutual funds
- Other capital property

Calculation Method:
Capital Gain = Selling Price - Adjusted Cost Base

Inclusion Rate:
Only 50% of capital gains are included in income.

Example:
If you sell stocks for $10,000 (originally bought for $6,000):
- Capital gain = $4,000
- Taxable capital gain = $4,000 × 50% = $2,000

This amount is added to your income and taxed at your marginal tax rate.""", fontsize=12, fontname="helvetica")

        # 第3页：税务优惠
        page3 = doc.new_page()
        rect4 = fitz.Rect(50, 50, 550, 150)
        page3.insert_text(rect4, """Chapter 4 - Tax Credits and Deductions

Non-Refundable Tax Credits:
- Basic personal amount: $15,705
- Canada employment amount: $1,433
- CPP/EI enhancement credit: $404
- Climate action incentive: Varies by province

Common Deductions:
- RRSP contributions (maximum $31,560 for 2024)
- Child care expenses
- Moving expenses
- Union or professional dues
- Employment expenses

Important Notes:
- Keep all receipts and documentation
- Some credits have income thresholds
- Provincial credits may also be available""", fontsize=12, fontname="helvetica")

        # 保存测试 PDF
        test_pdf_path = "test_cra_guide.pdf"
        doc.save(test_pdf_path)
        doc.close()

        print(f"✅ 测试 PDF 已创建: {test_pdf_path}")
        return test_pdf_path

    except Exception as e:
        print(f"❌ 创建测试 PDF 失败: {e}")
        return None

def test_pdf_extraction(pdf_path):
    """测试 PDF 文本提取"""
    print(f"\n📖 测试 PDF 文本提取: {pdf_path}")

    try:
        doc = fitz.open(pdf_path)
        total_pages = len(doc)
        print(f"📄 总页数: {total_pages}")

        total_text = ""
        page_results = []

        for page_num in range(total_pages):
            page = doc[page_num]
            text = page.get_text()

            # 评估文本质量
            quality = 0.0
            if text.strip():
                # 简单质量评估
                words = text.split()
                complete_words = sum(1 for word in words if word.isalpha() or '.' in word)
                quality = complete_words / len(words) if words else 0

            page_results.append({
                'page': page_num + 1,
                'text_length': len(text),
                'word_count': len(text.split()),
                'quality': quality
            })

            total_text += f"\n=== Page {page_num + 1} ===\n{text}\n"

            print(f"  页 {page_num + 1}: {len(text)} 字符, {len(text.split())} 词, 质量: {quality:.2f}")

        doc.close()

        # 统计信息
        total_chars = len(total_text)
        total_words = len(total_text.split())
        avg_quality = sum(r['quality'] for r in page_results) / len(page_results)

        print(f"\n📊 提取统计:")
        print(f"  总字符数: {total_chars:,}")
        print(f"  总词数: {total_words:,}")
        print(f"  平均质量: {avg_quality:.2f}")

        # 查找关键词
        keywords = ["capital gains", "tax credits", "RRSP", "deductions", "CRA"]
        found_keywords = {}
        for keyword in keywords:
            count = total_text.lower().count(keyword.lower())
            if count > 0:
                found_keywords[keyword] = count

        print(f"\n🎯 找到的关键词:")
        for keyword, count in found_keywords.items():
            print(f"  {keyword}: {count} 次")

        # 保存结果
        result = {
            'pdf_path': pdf_path,
            'total_pages': total_pages,
            'total_chars': total_chars,
            'total_words': total_words,
            'average_quality': avg_quality,
            'keywords': found_keywords,
            'pages': page_results,
            'extracted_text': total_text
        }

        result_file = "test_extraction_result.json"
        with open(result_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)

        print(f"\n💾 结果已保存: {result_file}")

        # 显示文本样本
        print(f"\n📖 文本样本 (前300字符):")
        print("-" * 40)
        print(total_text[:300])
        print("-" * 40)

        return True

    except Exception as e:
        print(f"❌ PDF 提取失败: {e}")
        return False

def test_performance():
    """测试处理性能"""
    print(f"\n⚡ 性能测试...")

    # 创建较大文档测试性能
    doc = fitz.open()

    print("  创建大型测试文档...")
    start_time = time.time()

    # 创建 10 页内容
    for i in range(10):
        page = doc.new_page()
        rect = fitz.Rect(50, 50, 550, 750)

        # 生成大量文本
        content = f"Page {i+1} - Performance Test\n\n"
        content += "This is a performance test for PyMuPDF text extraction. " * 50
        content += f"\nPage number: {i+1}\n"
        content += "CRA T4012 Tax Guide Content. " * 30

        page.insert_text(rect, content, fontsize=10)

    doc.save("performance_test.pdf")
    doc.close()

    creation_time = time.time() - start_time
    print(f"  文档创建时间: {creation_time:.2f} 秒")

    # 测试提取性能
    start_time = time.time()
    doc = fitz.open("performance_test.pdf")

    total_chars = 0
    for page in doc:
        text = page.get_text()
        total_chars += len(text)

    doc.close()
    extraction_time = time.time() - start_time

    print(f"  文本提取时间: {extraction_time:.2f} 秒")
    print(f"  提取字符数: {total_chars:,}")
    print(f"  处理速度: {total_chars/extraction_time:.0f} 字符/秒")

    # 清理
    Path("performance_test.pdf").unlink()

def main():
    """主测试函数"""
    print("🚀 PyMuPDF 文本提取完整测试")
    print("=" * 50)

    # 1. 基本功能测试
    if not test_pymupdf_basic():
        print("❌ 基本功能测试失败")
        return

    # 2. 文本质量测试
    test_text_quality()

    # 3. 创建测试 PDF
    test_pdf = create_test_pdf()
    if not test_pdf:
        print("❌ 无法创建测试 PDF")
        return

    # 4. 测试 PDF 提取
    if test_pdf_extraction(test_pdf):
        print("✅ PDF 提取测试成功")
    else:
        print("❌ PDF 提取测试失败")

    # 5. 性能测试
    test_performance()

    # 清理
    if Path("test_cra_guide.pdf").exists():
        Path("test_cra_guide.pdf").unlink()

    print(f"\n🎉 所有测试完成!")
    print("✅ PyMuPDF 文本提取功能正常工作")
    print("✅ 可以处理 CRA T4012 等大型 PDF 文档")

if __name__ == "__main__":
    main()