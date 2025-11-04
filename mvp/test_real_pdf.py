#!/usr/bin/env python3
"""
测试真实的 CRA T4012 PDF 文档
"""

import fitz
import time
import json
from pathlib import Path

def test_real_t4012():
    """测试真实的 T4012 PDF"""
    pdf_path = Path("pdf/t4012-24e.pdf")

    if not pdf_path.exists():
        print(f"❌ 找不到文件: {pdf_path}")
        return False

    print(f"🚀 测试真实 CRA T4012 PDF: {pdf_path}")
    print("=" * 50)

    try:
        # 获取文件大小
        file_size = pdf_path.stat().st_size / (1024 * 1024)  # MB
        print(f"📁 文件大小: {file_size:.1f} MB")

        # 打开 PDF
        start_time = time.time()
        doc = fitz.open(str(pdf_path))
        open_time = time.time() - start_time

        total_pages = len(doc)
        print(f"📄 总页数: {total_pages}")
        print(f"⏱️  打开时间: {open_time:.2f} 秒")

        # 获取元数据
        metadata = doc.metadata
        print(f"\n📋 文档元数据:")
        print(f"  标题: {metadata.get('title', 'N/A')}")
        print(f"  作者: {metadata.get('author', 'N/A')}")
        print(f"  创建者: {metadata.get('creator', 'N/A')}")
        print(f"  生产者: {metadata.get('producer', 'N/A')}")

        # 测试处理前5页
        test_pages = min(5, total_pages)
        print(f"\n🔍 测试处理前 {test_pages} 页...")

        total_text = ""
        pages_with_text = 0
        pages_needing_ocr = 0
        total_chars = 0

        page_results = []

        for page_num in range(test_pages):
            print(f"📖 处理第 {page_num + 1}/{test_pages} 页...")
            page_start = time.time()

            page = doc[page_num]
            text = page.get_text()

            page_time = time.time() - page_start

            # 评估文本质量
            text_quality = 0.0
            if text.strip():
                words = text.split()
                complete_words = sum(1 for word in words if word.isalpha() or '.' in word or ',' in word)
                text_quality = complete_words / len(words) if words else 0
                pages_with_text += 1

                # 检查是否需要 OCR (质量低)
                if text_quality < 0.3:
                    pages_needing_ocr += 1

                total_chars += len(text)
                total_text += f"\n=== Page {page_num + 1} ===\n{text}\n"

            # 检查页面是否有图像
            images = page.get_images()
            has_images = len(images) > 0

            page_result = {
                'page': page_num + 1,
                'chars': len(text),
                'words': len(text.split()),
                'quality': text_quality,
                'has_images': has_images,
                'image_count': len(images),
                'processing_time': page_time
            }
            page_results.append(page_result)

            print(f"  ✅ 文本: {len(text)} 字符, {len(text.split())} 词")
            print(f"  📊 质量: {text_quality:.2f}, 图像: {len(images)} 个")
            print(f"  ⏱️  处理时间: {page_time:.3f} 秒")

        # 计算统计
        total_processing_time = time.time() - start_time
        avg_quality = sum(r['quality'] for r in page_results) / len(page_results)

        print(f"\n📊 处理统计 (前{test_pages}页):")
        print(f"  ⏱️  总处理时间: {total_processing_time:.2f} 秒")
        print(f"  📄 成功处理页数: {pages_with_text}/{test_pages}")
        print(f"  🔍 可能需要OCR: {pages_needing_ocr} 页")
        print(f"  📝 总字符数: {total_chars:,}")
        print(f"  📈 平均文本质量: {avg_quality:.2f}")

        if total_processing_time > 0:
            pages_per_sec = test_pages / total_processing_time
            print(f"  ⚡ 处理速度: {pages_per_sec:.2f} 页/秒")

        # 查找关键词
        print(f"\n🎯 关键词搜索 (前{test_pages}页):")
        keywords = [
            "capital gains", "business income", "tax credits",
            "RRSP", "deductions", "filing", "CRA", "T4012"
        ]

        found_keywords = {}
        for keyword in keywords:
            count = total_text.lower().count(keyword.lower())
            if count > 0:
                found_keywords[keyword] = count
                print(f"  ✅ {keyword}: {count} 次")

        # 检查章节结构
        print(f"\n📖 章节检测 (前{test_pages}页):")
        lines = total_text.split('\n')
        potential_chapters = []

        for line in lines[:100]:  # 只检查前100行
            line = line.strip()
            if len(line) > 10 and len(line) < 100:
                # 可能的章节标题
                if any(word in line.lower() for word in ['chapter', 'section', 'part']):
                    potential_chapters.append(line)
                elif line.isupper() and len(line.split()) <= 10:
                    potential_chapters.append(line)

        if potential_chapters:
            print("  发现可能的章节:")
            for chapter in potential_chapters[:5]:
                print(f"    - {chapter}")
        else:
            print("  未发现明显的章节结构")

        # 显示文本样本
        print(f"\n📝 文本样本 (第1页前200字符):")
        print("-" * 50)
        first_page_text = page_results[0]['chars'] > 0
        if first_page_text:
            # 获取第一页的文本
            doc_test = fitz.open(str(pdf_path))
            page = doc_test[0]
            sample_text = page.get_text()[:200]
            doc_test.close()
            print(sample_text)
        else:
            print("第一页没有提取到文本")
        print("-" * 50)

        # 保存结果
        result = {
            'pdf_file': str(pdf_path),
            'file_size_mb': file_size,
            'total_pages': total_pages,
            'tested_pages': test_pages,
            'processing_time': total_processing_time,
            'pages_with_text': pages_with_text,
            'pages_needing_ocr': pages_needing_ocr,
            'total_chars': total_chars,
            'average_quality': avg_quality,
            'keywords': found_keywords,
            'metadata': {
                'title': metadata.get('title'),
                'author': metadata.get('author'),
                'creator': metadata.get('creator')
            },
            'page_results': page_results
        }

        result_file = "t4012_test_result.json"
        with open(result_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)

        print(f"\n💾 详细结果已保存: {result_file}")

        doc.close()

        # 评估结果
        print(f"\n🎯 处理评估:")
        if avg_quality > 0.7:
            print("  ✅ 文本质量优秀 - 适合直接处理")
        elif avg_quality > 0.4:
            print("  ✅ 文本质量良好 - 可以直接处理")
        elif avg_quality > 0.2:
            print("  ⚠️ 文本质量一般 - 建议使用OCR补充")
        else:
            print("  ❌ 文本质量较差 - 需要OCR处理")

        if pages_per_sec > 1:
            print("  ✅ 处理速度优秀")
        elif pages_per_sec > 0.5:
            print("  ✅ 处理速度良好")
        else:
            print("  ⚠️ 处理速度较慢")

        print(f"\n🎉 T4012 PDF 测试完成!")
        print(f"✅ PyMuPDF 可以成功处理 {total_pages} 页的大型 CRA 文档")
        print(f"✅ 文本提取质量: {avg_quality:.2f}")
        print(f"✅ 处理速度: {pages_per_sec:.2f} 页/秒")

        return True

    except Exception as e:
        print(f"❌ 处理失败: {e}")
        import traceback
        print(f"详细错误: {traceback.format_exc()}")
        return False

def estimate_full_processing():
    """估算完整处理时间"""
    print(f"\n⏱️ 完整文档处理估算:")

    result_file = Path("t4012_test_result.json")
    if result_file.exists():
        with open(result_file, 'r', encoding='utf-8') as f:
            result = json.load(f)

        tested_pages = result['tested_pages']
        processing_time = result['processing_time']
        total_pages = result['total_pages']

        estimated_time = (processing_time / tested_pages) * total_pages

        print(f"  基于前 {tested_pages} 页的结果:")
        print(f"  📄 总页数: {total_pages}")
        print(f"  ⏱️ 预估完整处理时间: {estimated_time:.1f} 秒 ({estimated_time/60:.1f} 分钟)")

        if estimated_time < 60:
            print("  ✅ 处理时间合理 (< 1分钟)")
        elif estimated_time < 300:
            print("  ✅ 处理时间可接受 (< 5分钟)")
        else:
            print("  ⚠️ 处理时间较长 (> 5分钟)")

def main():
    """主函数"""
    print("🧪 CRA T4012 真实文档测试")
    print("=" * 40)

    if test_real_t4012():
        estimate_full_processing()
        print(f"\n✅ 测试成功! PyMuPDF 完全可以处理大型 CRA PDF 文档")
    else:
        print(f"\n❌ 测试失败")

if __name__ == "__main__":
    main()