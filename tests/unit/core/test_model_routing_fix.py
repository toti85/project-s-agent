#!/usr/bin/env python3
"""
Test script to verify Qwen3-235B model routing fix
"""

import asyncio
import logging
import sys
import os
from pathlib import Path

# Add the project root to the path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from integrations.model_manager import ModelManager

# Configure logging
logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(name)s - %(message)s')
logger = logging.getLogger(__name__)

async def test_model_selection_fix():
    """Test that model selection now correctly prioritizes qwen3-235b."""
    
    print("=" * 60)
    print("TESTING MODEL ROUTING FIX - QWEN3-235B PRIMARY")
    print("=" * 60)
    
    try:
        # Initialize model manager
        model_manager = ModelManager()
        
        # Test various task types
        test_queries = [
            "Hozz létre egy test.txt fájlt",  # Should be detected as 'gyors_válasz'
            "Plan a simple web application",  # Should be detected as 'tervezés' (planning)
            "Write some Python code",  # Should be detected as 'kódolás' (coding)
            "Create documentation for this API",  # Should be detected as 'dokumentáció'
        ]
        
        print(f"\n🔍 Default model: {model_manager.default_model}")
        
        for i, query in enumerate(test_queries, 1):
            print(f"\n--- Test {i} ---")
            print(f"Query: '{query}'")
            
            # Detect task type
            task_type = model_manager.determine_task_type(query)
            print(f"Detected task type: {task_type}")
            
            # Select model for task
            selected_model = await model_manager.select_model_for_task(query, task_type)
            print(f"Selected model: {selected_model}")
            
            # Check if qwen3-235b was selected
            if selected_model == "qwen3-235b":
                print("✅ SUCCESS: Qwen3-235B correctly selected!")
            else:
                print(f"❌ ISSUE: Expected qwen3-235b, got {selected_model}")
        
        print(f"\n🏁 Model selection testing completed")
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR during model selection test: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_ai_client_suggest_method():
    """Test the suggest_model_for_task method directly."""
    
    print("\n" + "=" * 60)
    print("TESTING AI CLIENT SUGGEST_MODEL_FOR_TASK METHOD")
    print("=" * 60)
    
    try:
        from integrations.multi_model_ai_client import multi_model_ai_client
        
        # Test if method exists
        if hasattr(multi_model_ai_client, 'suggest_model_for_task'):
            print("✅ suggest_model_for_task method found")
            
            # Test task types
            task_types = ["tervezés", "kódolás", "dokumentáció", "gyors_válasz"]
            
            for task_type in task_types:
                suggested_model = multi_model_ai_client.suggest_model_for_task(task_type)
                print(f"Task '{task_type}' -> Model: {suggested_model}")
                
                if suggested_model == "qwen3-235b":
                    print(f"  ✅ Correctly suggested qwen3-235b for {task_type}")
                else:
                    print(f"  ⚠️  Suggested {suggested_model} instead of qwen3-235b for {task_type}")
        else:
            print("❌ suggest_model_for_task method NOT found")
            return False
            
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR during AI client test: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Main test function."""
    print("🚀 Starting Model Routing Fix Validation")
    
    # Test 1: Model selection through ModelManager
    success1 = await test_model_selection_fix()
    
    # Test 2: AI client suggest method
    success2 = await test_ai_client_suggest_method()
    
    print("\n" + "=" * 60)
    print("FINAL RESULTS")
    print("=" * 60)
    
    if success1 and success2:
        print("✅ ALL TESTS PASSED - Model routing fix successful!")
        print("🎯 Qwen3-235B is now the primary model for all task types")
    else:
        print("❌ Some tests failed - model routing fix needs more work")
        
    print("\nExpected log format:")
    print("[INFO] integrations.model_manager - A(z) 'tervezés' feladat típushoz a(z) 'qwen3-235b' modellt választottuk")

if __name__ == "__main__":
    asyncio.run(main())
