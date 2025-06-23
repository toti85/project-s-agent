#!/usr/bin/env python3
"""
Test script specifically for OpenRouter Qwen3 235B A22B model integration
"""

import asyncio
import logging
import sys
import os
from pathlib import Path

# Add the project root to the path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from integrations.multi_model_ai_client import multi_model_ai_client

# Configure logging
logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(name)s - %(message)s')
logger = logging.getLogger(__name__)

async def test_qwen_model():
    """Test the Qwen3 235B A22B model through OpenRouter."""
    
    print("=" * 60)
    print("TESTING OPENROUTER QWEN3 235B A22B INTEGRATION")
    print("=" * 60)
    
    # List available models to confirm Qwen is available
    models = multi_model_ai_client.list_available_models()
    openrouter_models = [m for m in models if m['provider'] == 'openrouter']
    
    print(f"\nOpenRouter models available: {len(openrouter_models)}")
    for model in openrouter_models:
        print(f"  - {model['display_name']} ({model['model_id']})")
    
    # Find the Qwen3 235B model
    qwen_model = None
    for model in models:
        if 'qwen3-235b' in model['model_id']:
            qwen_model = model
            break
    
    if not qwen_model:
        print("\n❌ ERROR: Qwen3 235B model not found in available models!")
        return False
    
    print(f"\n✅ Found Qwen3 235B model: {qwen_model['display_name']}")
    print(f"   Model ID: {qwen_model['model_id']}")
    print(f"   Description: {qwen_model['description']}")
    
    # Test with a simple prompt
    test_prompt = "Explain the concept of machine learning in one paragraph. Be concise but informative."
    
    print(f"\n🔄 Testing Qwen3 235B with prompt: '{test_prompt}'")
    print("Sending request to OpenRouter...")
    
    try:
        response = await multi_model_ai_client.generate_response(
            prompt=test_prompt,
            model="qwen3-235b",
            provider="openrouter",
            temperature=0.7
        )
        
        if response:
            print("\n✅ SUCCESS! Qwen3 235B responded:")
            print("-" * 50)
            print(response)
            print("-" * 50)
            return True
        else:
            print("\n❌ ERROR: No response received from Qwen3 235B")
            return False
            
    except Exception as e:
        print(f"\n❌ ERROR: Exception while testing Qwen3 235B: {e}")
        return False

async def test_model_selection():
    """Test automatic model selection for different task types."""
    
    print("\n" + "=" * 60)
    print("TESTING AUTOMATIC MODEL SELECTION")
    print("=" * 60)
    
    # Test task types that should prioritize Qwen3 235B
    test_tasks = [
        ("tervezés", "Plan a simple web application architecture"),
        ("kódolás", "Write a Python function to calculate Fibonacci numbers"),
        ("dokumentáció", "Document the features of a REST API"),
        ("gyors_válasz", "What is the capital of Hungary?")
    ]
    
    for task_type, prompt in test_tasks:
        print(f"\n🔄 Testing task type: '{task_type}'")
        recommended_model = multi_model_ai_client.get_recommended_model(task_type)
        print(f"   Recommended model: {recommended_model}")
        
        try:
            response = await multi_model_ai_client.generate_response(
                prompt=prompt,
                task_type=task_type,
                temperature=0.5
            )
            
            if response:
                print(f"   ✅ Response received (length: {len(response)} chars)")
                # Show first 100 characters
                preview = response[:100] + "..." if len(response) > 100 else response
                print(f"   Preview: {preview}")
            else:
                print("   ❌ No response received")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")

async def main():
    """Main test function."""
    
    print("Starting OpenRouter Qwen3 235B integration tests...\n")
    
    # Check OpenRouter API key
    if not multi_model_ai_client.openrouter_api_key:
        print("❌ ERROR: OpenRouter API key not found!")
        print("Please check the API key configuration.")
        return
    
    print(f"✅ OpenRouter API key found (length: {len(multi_model_ai_client.openrouter_api_key)})")
    
    # Test basic Qwen model functionality
    success1 = await test_qwen_model()
    
    # Test automatic model selection
    await test_model_selection()
    
    print("\n" + "=" * 60)
    if success1:
        print("🎉 OPENROUTER QWEN3 235B INTEGRATION TEST COMPLETED SUCCESSFULLY!")
    else:
        print("⚠️  OPENROUTER QWEN3 235B INTEGRATION TEST HAD ISSUES")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(main())
