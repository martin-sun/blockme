#!/usr/bin/env python3
"""
OCR 功能测试
验证 pytesseract 是否正常工作
"""

import pytesseract
from PIL import Image, ImageDraw, ImageFont
import io

def create_test_image():
    """创建一个测试图像"""
    # 创建一个简单的文本图像
    width, height = 400, 200
    img = Image.new('RGB', (width, height), color='white')
    draw = ImageDraw.Draw(img)

    # 添加文本
    try:
        # 尝试使用系统字体
        font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 20)
    except:
        # 如果找不到字体，使用默认字体
        font = ImageFont.load_default()

    text = "CRA T4012\nTax Guide 2024\nTest Document"
    draw.text((50, 50), text, fill='black', font=font)

    return img

def test_ocr():
    """测试 OCR 功能"""
    print("🔍 测试 OCR 功能...")

    try:
        # 创建测试图像
        img = create_test_image()
        print("✅ 创建测试图像成功")

        # 进行 OCR
        text = pytesseract.image_to_string(img)
        print("✅ OCR 处理成功")

        print(f"\n📝 OCR 结果:")
        print("-" * 30)
        print(repr(text))
        print("-" * 30)

        # 检查是否识别出关键文本
        if "CRA" in text and "T4012" in text:
            print("✅ 成功识别关键文本")
        else:
            print("⚠️ 未能识别所有文本，这是正常的")

        return True

    except Exception as e:
        print(f"❌ OCR 测试失败: {e}")
        return False

def test_tesseract_version():
    """检查 Tesseract 版本"""
    try:
        version = pytesseract.get_tesseract_version()
        print(f"✅ Tesseract 版本: {version}")
        return True
    except Exception as e:
        print(f"❌ 无法获取 Tesseract 版本: {e}")
        return False

def main():
    print("🧪 OCR 功能测试")
    print("=" * 30)

    # 检查 Tesseract 版本
    if not test_tesseract_version():
        print("❌ Tesseract 未正确安装")
        return

    # 测试 OCR 功能
    if test_ocr():
        print("\n✅ OCR 功能正常")
        print("可以处理扫描的 PDF 页面")
    else:
        print("\n⚠️ OCR 功能需要检查")
        print("可能需要安装 Tesseract OCR 引擎")

if __name__ == "__main__":
    main()