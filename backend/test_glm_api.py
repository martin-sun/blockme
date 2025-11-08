#!/usr/bin/env python3
"""Test GLM API connection and model."""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_glm_api():
    """Test GLM API connection."""
    try:
        from zhipuai import ZhipuAI

        api_key = os.environ.get("GLM_API_KEY")
        model = os.environ.get("GLM_MODEL", "glm-4.6")

        print(f"Testing GLM API...")
        print(f"Model: {model}")
        print(f"API Key: {api_key[:10]}...{api_key[-10:] if api_key else 'None'}")

        if not api_key:
            print("❌ GLM_API_KEY not found")
            return False

        client = ZhipuAI(api_key=api_key)

        # Test simple request
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "user", "content": "Hello, this is a test. Please respond with 'API working'"}
            ],
            max_tokens=50,
        )

        result = response.choices[0].message.content
        print(f"✅ API Response: {result}")
        return True

    except ImportError:
        print("❌ zhipuai package not installed")
        return False
    except Exception as e:
        print(f"❌ API Error: {e}")
        return False

if __name__ == "__main__":
    test_glm_api()