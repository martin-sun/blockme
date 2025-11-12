#!/usr/bin/env python3
"""
Test script to verify thinking mode integration
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from app.document_processor.llm_cli_providers import get_provider

def test_glm_thinking_mode():
    """Test that GLM API provider properly enables thinking mode"""
    print("=" * 60)
    print("Testing GLM Thinking Mode Integration")
    print("=" * 60)

    # Test 1: GLM API without thinking mode
    print("\n[Test 1] GLM API without thinking mode")
    provider_no_thinking = get_provider("glm-api", enable_thinking=False)
    if provider_no_thinking:
        print(f"✓ Provider created: {provider_no_thinking.name}")
        print(f"  - Thinking mode: {provider_no_thinking.enable_thinking}")
        assert provider_no_thinking.enable_thinking == False, "Thinking should be disabled"
    else:
        print("✗ Failed to create provider")
        return False

    # Test 2: GLM API with thinking mode
    print("\n[Test 2] GLM API with thinking mode")
    provider_with_thinking = get_provider("glm-api", enable_thinking=True)
    if provider_with_thinking:
        print(f"✓ Provider created: {provider_with_thinking.name}")
        print(f"  - Thinking mode: {provider_with_thinking.enable_thinking}")
        assert provider_with_thinking.enable_thinking == True, "Thinking should be enabled"
    else:
        print("✗ Failed to create provider")
        return False

    # Test 3: Default behavior (no thinking)
    print("\n[Test 3] GLM API default behavior")
    provider_default = get_provider("glm-api")
    if provider_default:
        print(f"✓ Provider created: {provider_default.name}")
        print(f"  - Thinking mode: {provider_default.enable_thinking}")
        assert provider_default.enable_thinking == False, "Default should be False"
    else:
        print("✗ Failed to create provider")
        return False

    # Test 4: Other providers (should not break)
    print("\n[Test 4] Other providers compatibility")
    other_providers = ["claude", "gemini", "gemini-api", "codex"]
    for prov_name in other_providers:
        provider = get_provider(prov_name, enable_thinking=True)
        if provider:
            print(f"✓ Provider '{prov_name}' created successfully")
            # These providers don't have enable_thinking attribute, which is fine
        else:
            print(f"  - Provider '{prov_name}' not available (OK)")

    # Test 5: Dynamic Classifier
    print("\n[Test 5] Dynamic Classifier with thinking mode")
    try:
        from app.document_processor.dynamic_classifier import DynamicSemanticClassifier

        # Check if GLM API is available first
        glm_provider = get_provider("glm-api")
        if glm_provider and glm_provider.is_available():
            classifier = DynamicSemanticClassifier(provider_name="glm-api", enable_thinking=True)
            print(f"✓ Dynamic Classifier created with thinking mode")
            print(f"  - Provider: {classifier.provider.name}")
            print(f"  - Thinking enabled: {classifier.provider.enable_thinking}")
        else:
            print("  - Skipping (GLM API not available)")
    except Exception as e:
        print(f"✗ Failed to create classifier: {e}")
        return False

    print("\n" + "=" * 60)
    print("✓ All tests passed!")
    print("=" * 60)
    return True

if __name__ == "__main__":
    success = test_glm_thinking_mode()
    sys.exit(0 if success else 1)
