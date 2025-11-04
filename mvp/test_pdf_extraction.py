#!/usr/bin/env python3
"""
PDF 提取测试脚本
模拟处理 CRA T4012 文档的场景
"""

import sys
import time
from pathlib import Path
from pdf_text_extractor import PDFTextExtractor, save_extraction_result

def create_sample_text():
    """创建一个模拟的 CRA 文档内容样本"""
    return """
CRA T4012 - T1 GENERAL INCOME TAX AND BENEFIT GUIDE

Chapter 1 - General Information
================================

This guide will help you complete the 2024 T1 General Income Tax and Benefit Return.

Who should use this guide?
- Canadian residents
- Newcomers to Canada
- Students
- Seniors

Important deadlines:
- April 30, 2025: Most filing deadline
- June 15, 2025: Self-employed deadline

Chapter 2 - Personal Income
===========================

Types of income you must report:
1. Employment income (T4 slips)
2. Investment income (T5 slips)
3. Business income (T2125)
4. Capital gains (Schedule 3)

Employment Income
-----------------
Report all employment income including:
- Salary and wages
- Bonuses and commissions
- Tips and gratuities
- Employment insurance benefits

Tax Deductions
--------------
Common deductions include:
- RRSP contributions (maximum $31,560)
- Child care expenses
- Moving expenses
- Union dues

Chapter 3 - Capital Gains
=========================

What are capital gains?
Capital gains are profits from selling:
- Real estate properties
- Stocks and bonds
- Mutual funds
- Other investments

Calculation
-----------
Capital Gain = Proceeds of Disposition - Adjusted Cost Base

Inclusion Rate
--------------
Only 50% of capital gains are taxable.

Example:
If you sold stocks for $10,000 and your cost was $6,000:
- Capital gain = $10,000 - $6,000 = $4,000
- Taxable capital gain = $4,000 × 50% = $2,000

Principal Residence Exemption
---------------------------
You may be able to claim a principal residence exemption for:
- Your main home
- One property per tax year
- No capital gains tax on qualifying properties

Chapter 4 - Tax Credits
======================

Non-refundable tax credits reduce your tax payable.

Common credits include:
- Basic personal amount ($15,705)
- Canada employment amount ($1,433)
- CPP/EI enhancement credit
- Climate action incentive

Child Benefits
--------------
- Canada Child Benefit (CCB)
- GST/HST credit
- Various provincial benefits

Chapter 5 - RRSP and Retirement
=============================

RRSP Contribution Limit
----------------------
2024 limit: 18% of earned income, maximum $31,560

Unused contribution room can be carried forward indefinitely.

RRSP Deduction
-------------
Deduct contributions in the year you make them, or carry forward.

Spousal RRSP
-----------
- Contribute to spouse's RRSP
- Claim deduction yourself
- Helps split retirement income

Chapter 6 - Filing Requirements
=============================

When to file
-----------
- By April 30, 2025 for most taxpayers
- By June 15, 2025 for self-employed individuals

How to file
-----------
- Online using NETFILE-certified software
- By mail using paper forms
- Through an authorized tax preparer

Documents needed
----------------
- Social Insurance Number (SIN)
- All income slips (T4, T5, T3, etc.)
- Receipts for deductions and credits
- Last year's return notice of assessment

After filing
-----------
Receive notice of assessment within 2-8 weeks.
Review for accuracy and file objections if needed.

This guide provides general information. For personalized advice, consult a tax professional or visit cra.gc.ca.
"""

def test_with_sample_data():
    """使用样本数据测试提取器功能"""
    print("🧪 测试 PDF 文本提取器 - 样本数据测试")
    print("=" * 50)

    # 创建样本文件
    sample_text = create_sample_text()
    sample_file = Path("cra_sample.txt")

    with open(sample_file, 'w', encoding='utf-8') as f:
        f.write(sample_text)

    print(f"📝 创建样本文件: {sample_file}")
    print(f"📄 样本长度: {len(sample_text)} 字符")
    print(f"📖 样本词数: {len(sample_text.split())} 词")

    # 分析样本内容
    print("\n📊 内容分析:")
    lines = sample_text.split('\n')
    print(f"  总行数: {len(lines)}")

    # 查找关键词
    keywords = ["capital gains", "RRSP", "tax credits", "filing", "deductions"]
    found_keywords = []
    for keyword in keywords:
        if keyword.lower() in sample_text.lower():
            found_keywords.append(keyword)
            count = sample_text.lower().count(keyword.lower())
            print(f"  ✓ {keyword}: {count} 次")

    print(f"\n🎯 找到关键词: {', '.join(found_keywords)}")

    # 模拟处理性能
    print("\n⚡ 性能测试:")
    start_time = time.time()

    # 模拟文本处理
    processed_text = sample_text.replace('\n\n', '\n').strip()

    end_time = time.time()
    print(f"  处理时间: {(end_time - start_time)*1000:.2f} ms")
    print(f"  处理速度: {len(processed_text)/(end_time - start_time):.0f} 字符/秒")

    # 清理
    sample_file.unlink()
    print(f"\n🧹 清理样本文件")

def test_dependencies():
    """测试依赖是否正常工作"""
    print("🔍 检查依赖库...")

    try:
        import fitz
        print(f"  ✅ PyMuPDF: {fitz.version}")
    except ImportError as e:
        print(f"  ❌ PyMuPDF: {e}")
        return False

    try:
        from PIL import Image
        print(f"  ✅ Pillow: {Image.__version__}")
    except ImportError as e:
        print(f"  ❌ Pillow: {e}")
        return False

    try:
        import pytesseract
        print(f"  ✅ pytesseract: 已安装")
    except ImportError as e:
        print(f"  ❌ pytesseract: {e}")
        return False

    try:
        import psutil
        print(f"  ✅ psutil: {psutil.__version__}")
    except ImportError as e:
        print(f"  ❌ psutil: {e}")
        return False

    return True

def test_memory_usage():
    """测试内存使用情况"""
    import psutil
    import os

    process = psutil.Process(os.getpid())
    memory_info = process.memory_info()

    print(f"\n🧠 内存使用情况:")
    print(f"  RSS: {memory_info.rss / 1024 / 1024:.1f} MB")
    print(f"  VMS: {memory_info.vms / 1024 / 1024:.1f} MB")
    print(f"  CPU: {process.cpu_percent():.1f}%")

def main():
    """主测试函数"""
    print("🚀 CRA PDF 文档处理 MVP 测试")
    print("=" * 60)

    # 1. 检查依赖
    if not test_dependencies():
        print("\n❌ 依赖检查失败，请安装所需的库")
        sys.exit(1)

    # 2. 内存使用检查
    test_memory_usage()

    # 3. 样本数据测试
    test_with_sample_data()

    # 4. 查找实际 PDF 文件
    print(f"\n📁 查找 PDF 文件...")
    current_dir = Path(".")

    # 常见的 CRA PDF 文件名
    possible_names = [
        "t4012-24e.pdf",
        "t4012.pdf",
        "T4012.pdf",
        "sample.pdf",
        "test.pdf"
    ]

    found_pdf = None
    for name in possible_names:
        if (current_dir / name).exists():
            found_pdf = current_dir / name
            break

    if found_pdf:
        print(f"📄 找到 PDF 文件: {found_pdf}")

        # 测试实际 PDF（只处理前3页）
        print(f"\n🔍 开始处理实际 PDF (前3页)...")
        try:
            extractor = PDFTextExtractor(enable_ocr=True)
            result = extractor.extract_pdf(str(found_pdf), max_pages=3)

            # 显示提取结果
            print(f"\n📝 提取结果:")
            print(f"  成功处理页数: {result.successful_pages}")
            print(f"  需要OCR的页数: {result.pages_needing_ocr}")
            print(f"  提取字符数: {len(result.total_text):,}")

            # 显示文本样本
            if result.total_text:
                sample = result.total_text[:500]
                print(f"\n📖 文本样本:")
                print("-" * 30)
                print(sample)
                print("-" * 30)

            # 保存结果
            save_extraction_result(result)

        except Exception as e:
            print(f"❌ PDF 处理失败: {e}")
            print(f"详细错误: {e}")
    else:
        print(f"📄 未找到 PDF 文件")
        print(f"请将 CRA T4012 PDF 文件放在当前目录下")
        print(f"支持的文件名: {', '.join(possible_names)}")

    print(f"\n✅ 测试完成!")

if __name__ == "__main__":
    main()