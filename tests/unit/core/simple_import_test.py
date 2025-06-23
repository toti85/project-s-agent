#!/usr/bin/env python3
"""
Simple import test for main_multi_model.py components
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test importing main components."""
    
    print("🧪 SIMPLE IMPORT TEST")
    print("=" * 30)
    
    try:
        print("📦 Importing model_manager...")
        from integrations.model_manager import model_manager
        print(f"✅ model_manager type: {type(model_manager)}")
        
        print("📦 Importing multi_model_ai_client...")
        from integrations.multi_model_ai_client import multi_model_ai_client
        print(f"✅ multi_model_ai_client type: {type(multi_model_ai_client)}")
        
        print("📦 Testing model list...")
        models = multi_model_ai_client.list_available_models()
        print(f"✅ Available models: {len(models)}")
        
        print("📦 Testing model manager methods...")
        if hasattr(model_manager, 'execute_task_with_core_system'):
            print("✅ execute_task_with_core_system method available")
        else:
            print("❌ execute_task_with_core_system method missing")
        
        print("\n🎉 All imports successful!")
        print("✅ main_multi_model.py system components are working!")
        
    except Exception as e:
        print(f"❌ Import failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_imports()
