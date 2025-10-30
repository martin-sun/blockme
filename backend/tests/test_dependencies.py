#!/usr/bin/env python3
"""验证所有依赖是否正确安装"""

def test_imports():
    """测试所有依赖库的导入"""
    print("=" * 60)
    print("BlockMe 依赖验证测试")
    print("=" * 60)

    all_passed = True

    # AI API 客户端
    print("\n[1/5] 测试 AI API 客户端...")
    try:
        import anthropic
        import zhipuai
        import openai
        print("  ✓ anthropic:", anthropic.__version__)
        print("  ✓ zhipuai:", zhipuai.__version__)
        print("  ✓ openai:", openai.__version__)
    except ImportError as e:
        print(f"  ✗ AI API 客户端导入失败: {e}")
        all_passed = False

    # 文档处理
    print("\n[2/5] 测试文档处理库...")
    try:
        import fitz  # PyMuPDF
        from pdf2image import convert_from_path
        from docx import Document
        from PIL import Image
        print("  ✓ PyMuPDF (fitz):", fitz.version)
        print("  ✓ pdf2image: 已安装")
        print("  ✓ python-docx: 已安装")
        print("  ✓ Pillow (PIL):", Image.__version__)
    except ImportError as e:
        print(f"  ✗ 文档处理库导入失败: {e}")
        all_passed = False

    # Web 框架
    print("\n[3/5] 测试 Web 框架...")
    try:
        from fastapi import FastAPI
        from pydantic import BaseModel
        import uvicorn
        print("  ✓ FastAPI: 已安装")
        print("  ✓ Pydantic: 已安装")
        print("  ✓ Uvicorn: 已安装")
    except ImportError as e:
        print(f"  ✗ Web 框架导入失败: {e}")
        all_passed = False

    # 工具库
    print("\n[4/5] 测试工具库...")
    try:
        import yaml
        import requests
        from dotenv import load_dotenv
        import httpx
        print("  ✓ PyYAML:", yaml.__version__)
        print("  ✓ requests:", requests.__version__)
        print("  ✓ python-dotenv: 已安装")
        print("  ✓ httpx:", httpx.__version__)
    except ImportError as e:
        print(f"  ✗ 工具库导入失败: {e}")
        all_passed = False

    # 可选：语义缓存
    print("\n[5/5] 测试可选依赖（语义缓存）...")
    try:
        from sentence_transformers import SentenceTransformer
        print("  ✓ sentence-transformers: 已安装（可选）")
    except ImportError:
        print("  ⚠️  sentence-transformers 未安装（可选功能，可忽略）")

    # 总结
    print("\n" + "=" * 60)
    if all_passed:
        print("✅ 所有核心依赖安装成功！")
        print("\n下一步：")
        print("  1. 确认 .env 文件已配置 API keys")
        print("  2. 运行 test_api_connections.py 测试 API 连接")
        print("=" * 60)
        return 0
    else:
        print("❌ 部分依赖安装失败，请检查错误信息")
        print("=" * 60)
        return 1

if __name__ == "__main__":
    exit(test_imports())
