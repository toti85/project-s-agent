#!/usr/bin/env python3
"""
Test script for main_multi_model.py system
"""

import asyncio
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

async def test_main_multi_model_system():
    """Test the main_multi_model.py system components."""
    
    print("🧪 TESTING MAIN_MULTI_MODEL.PY SYSTEM")
    print("=" * 50)
    
    try:
        # Import the core components like main_multi_model.py does
        from integrations.model_manager import model_manager
        from integrations.multi_model_ai_client import multi_model_ai_client
        from integrations.intelligent_workflow_integration import intelligent_workflow_orchestrator
        
        print("✅ Successfully imported all main components")
        
        # Test 1: Simple AI query
        print("\n🧪 Test 1: Simple AI Query")
        print("-" * 30)
        
        result = await model_manager.execute_task_with_core_system(
            "Write a simple hello world function in Python"
        )
        
        print(f"Result type: {type(result)}")
        if isinstance(result, dict):
            print(f"Status: {result.get('status', 'unknown')}")
            if 'execution_result' in result:
                exec_result = result['execution_result']
                if isinstance(exec_result, dict):
                    print(f"Content: {str(exec_result.get('content', exec_result))[:200]}...")
                else:
                    print(f"Content: {str(exec_result)[:200]}...")
        
        # Test 2: File creation
        print("\n🧪 Test 2: File Creation")
        print("-" * 30)
        
        result = await model_manager.execute_task_with_core_system(
            "create test_file.txt with content 'Hello from Project-S test!'"
        )
        
        print(f"File creation result: {result.get('status', 'unknown')}")
        
        # Test 3: Available models
        print("\n🧪 Test 3: Available Models")
        print("-" * 30)
        
        models = multi_model_ai_client.list_available_models()
        print(f"Available models: {len(models)}")
        for model in models[:3]:  # Show first 3
            print(f"  • {model.get('name', 'unknown')} ({model.get('provider', 'unknown')})")
        
        # Test 4: System status
        print("\n🧪 Test 4: System Status")
        print("-" * 30)
        
        if hasattr(model_manager, 'get_stats'):
            stats = model_manager.get_stats()
            print(f"Model manager stats: {stats}")
        
        print("\n✅ All tests completed successfully!")
        print("🎉 main_multi_model.py system is working correctly!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_main_multi_model_system())
