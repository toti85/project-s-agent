#!/usr/bin/env python3
"""
AI API Test Script for Project-S
Tests if the AI models are actually working and making API calls
"""

import asyncio
import os
import sys
import time
from pathlib import Path

# Set environment variable
os.environ["OPENROUTER_API_KEY"] = "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"

# Import Project-S components
try:
    from integrations.multi_model_ai_client import multi_model_ai_client
    from integrations.model_manager import model_manager
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)

async def test_ai_functionality():
    """Test AI functionality with real API calls."""
    print("🧪 TESTING PROJECT-S AI FUNCTIONALITY")
    print("=" * 60)
    
    # Test 1: Check available models
    print("📋 Test 1: Available Models")
    try:
        models = multi_model_ai_client.list_available_models()
        print(f"   Available models: {len(models)}")
        for model in models[:3]:  # Show first 3 models
            print(f"   • {model.get('name', 'Unknown')}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 2: Simple AI query
    print("\n📋 Test 2: Simple AI Query")
    test_query = "What is 2+2? Give a brief answer."
    
    try:
        print(f"   Query: '{test_query}'")
        print("   🔄 Making API call...")
        
        start_time = time.time()
        result = await multi_model_ai_client.ask(test_query)
        duration = time.time() - start_time
        
        print(f"   ✅ Response received in {duration:.2f}s")
        print(f"   📝 Response: {result}")
        
    except Exception as e:
        print(f"   ❌ API call failed: {e}")
    
    # Test 3: Model Manager integration
    print("\n📋 Test 3: Model Manager Integration")
    try:
        print("   🔄 Testing model manager...")
        result = await model_manager.execute_task_with_core_system("Hello, are you working?")
        print(f"   ✅ Model manager response: {result}")
    except Exception as e:
        print(f"   ❌ Model manager error: {e}")
    
    # Test 4: Check API key configuration
    print("\n📋 Test 4: API Key Configuration")
    print(f"   OPENROUTER_API_KEY set: {'✅ YES' if os.environ.get('OPENROUTER_API_KEY') else '❌ NO'}")
    
    if multi_model_ai_client.openrouter_api_key:
        print(f"   OpenRouter key loaded: ✅ YES (ending: ...{multi_model_ai_client.openrouter_api_key[-10:]})")
    else:
        print("   OpenRouter key loaded: ❌ NO")
    
    print("\n🎯 CONCLUSION:")
    print("   If you see API responses above, the AI system is working!")
    print("   If errors occur, check your API keys and internet connection.")

if __name__ == "__main__":
    asyncio.run(test_ai_functionality())
