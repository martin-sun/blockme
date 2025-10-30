#!/usr/bin/env python3
"""测试 API 连接"""

import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

def test_claude_api():
    """测试 Claude API 连接"""
    print("\n[1/2] 测试 Claude API (Haiku 4.5)...")

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("  ✗ 未找到 ANTHROPIC_API_KEY")
        return False

    print(f"  ℹ️  API Key: {api_key[:20]}...")

    try:
        from anthropic import Anthropic

        client = Anthropic(api_key=api_key)
        response = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=256,
            messages=[{"role": "user", "content": "测试 BlockMe 开发环境，请简短回复"}]
        )

        reply = response.content[0].text
        print(f"  ✓ Claude API 连接成功")
        print(f"  ✓ 响应: {reply[:100]}...")
        return True

    except Exception as e:
        print(f"  ✗ Claude API 连接失败: {e}")
        return False

def test_glm_api():
    """测试 GLM API 连接"""
    print("\n[2/2] 测试 GLM API (GLM-4-Flash)...")

    api_key = os.environ.get("GLM_API_KEY")
    if not api_key:
        print("  ✗ 未找到 GLM_API_KEY")
        return False

    print(f"  ℹ️  API Key: {api_key[:20]}...")

    try:
        from zhipuai import ZhipuAI

        client = ZhipuAI(api_key=api_key)
        response = client.chat.completions.create(
            model="glm-4-flash",
            messages=[{"role": "user", "content": "测试 BlockMe 开发环境，请简短回复"}],
            temperature=0.2,
            max_tokens=512,
        )

        reply = response.choices[0].message.content
        print(f"  ✓ GLM API 连接成功")
        print(f"  ✓ 响应: {reply[:100]}...")
        return True

    except Exception as e:
        print(f"  ✗ GLM API 连接失败: {e}")
        return False

def main():
    print("=" * 60)
    print("BlockMe API 连接测试")
    print("=" * 60)

    claude_ok = test_claude_api()
    glm_ok = test_glm_api()

    print("\n" + "=" * 60)
    if claude_ok and glm_ok:
        print("✅ 所有 API 连接测试通过！")
        print("\n环境配置完成，可以开始开发了！")
    else:
        print("❌ 部分 API 连接失败")
        if not claude_ok:
            print("  - 请检查 .env 中的 ANTHROPIC_API_KEY")
        if not glm_ok:
            print("  - 请检查 .env 中的 GLM_API_KEY")
    print("=" * 60)

    return 0 if (claude_ok and glm_ok) else 1

if __name__ == "__main__":
    exit(main())
