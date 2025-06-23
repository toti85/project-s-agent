#!/usr/bin/env python3
"""
Live System Test - Project-S AI Agent
Test the complete system with ASK command routing fix
"""

import asyncio
import json
import logging
import sys
import os
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('live_test_output.log')
    ]
)
logger = logging.getLogger(__name__)

def print_header(title):
    """Print a formatted header"""
    print("\n" + "=" * 70)
    print(f" {title}")
    print("=" * 70)

def print_subheader(title):
    """Print a formatted subheader"""
    print(f"\n--- {title} ---")

async def test_ask_command_direct():
    """Test ASK command directly through AICommandHandler"""
    print_subheader("Testing ASK Command Direct Routing")
    
    try:
        from core.ai_command_handler import AICommandHandler, MODEL_MANAGER_AVAILABLE
        
        # Create handler instance
        handler = AICommandHandler()
        
        # Check ModelManager availability
        print(f"MODEL_MANAGER_AVAILABLE: {MODEL_MANAGER_AVAILABLE}")
        
        if hasattr(handler, 'model_manager'):
            print("✅ Handler uses ModelManager")
            print(f"   ModelManager type: {type(handler.model_manager)}")
        else:
            print("❌ Handler uses fallback QwenOllamaClient")
            
        # Test ASK command
        test_query = "Mi Magyarország fővárosa? Adj rövid választ."
        command = {"query": test_query}
        
        print(f"\nTesting query: '{test_query}'")
        print("Executing ASK command...")
        
        result = await handler.handle_ask_command(command)
        
        print(f"Result: {result}")
        
        if result.get("status") == "success":
            print("✅ ASK command executed successfully!")
            response = result.get("response", "No response")
            print(f"Response: {response}")
            return True
        else:
            print(f"❌ ASK command failed: {result}")
            return False
            
    except Exception as e:
        print(f"❌ Error in direct ASK test: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_command_router():
    """Test ASK command through CommandRouter"""
    print_subheader("Testing ASK Command via CommandRouter")
    
    try:
        from core.command_router import CommandRouter
        
        # Create router instance
        router = CommandRouter()
        
        # Check if ASK handler is registered
        if "ASK" in router.handlers:
            print("✅ ASK handler is registered in CommandRouter")
        else:
            print("❌ ASK handler NOT registered in CommandRouter")
            return False
            
        # Test full command routing
        command = {
            "type": "ASK",
            "query": "What is 2+2? Give a brief answer."
        }
        
        print(f"Testing command: {command}")
        print("Routing through CommandRouter...")
        
        result = await router.route_command(command)
        
        print(f"Router result: {result}")
        
        if "error" not in result and (result.get("status") == "success" or "response" in result):
            print("✅ CommandRouter successfully processed ASK command!")
            return True
        else:
            print(f"❌ CommandRouter failed: {result}")
            return False
            
    except Exception as e:
        print(f"❌ Error in CommandRouter test: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_json_command_processing():
    """Test JSON command processing"""
    print_subheader("Testing JSON Command Processing")
    
    try:
        from core.ai_command_handler import AICommandHandler
        
        handler = AICommandHandler()
        
        # Test JSON command processing
        json_command = {
            "type": "ASK",
            "command": "What programming language is Python based on? Keep it short."
        }
        
        print(f"Testing JSON command: {json_command}")
        print("Processing through process_json_command...")
        
        result = await handler.process_json_command(json_command)
        
        print(f"JSON processing result: {result}")
        
        if result.get("status") == "success":
            print("✅ JSON command processing successful!")
            return True
        else:
            print(f"❌ JSON command processing failed: {result}")
            return False
            
    except Exception as e:
        print(f"❌ Error in JSON processing test: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_model_manager_integration():
    """Test ModelManager integration directly"""
    print_subheader("Testing ModelManager Integration")
    
    try:
        from integrations.model_manager import ModelManager
        
        # Create ModelManager instance
        model_manager = ModelManager()
        
        print("✅ ModelManager created successfully")
        print(f"   ModelManager type: {type(model_manager)}")
        
        # Test model suggestion
        if hasattr(model_manager, 'suggest_model_for_task'):
            suggested_model = model_manager.suggest_model_for_task("ask")
            print(f"   Suggested model for 'ask' task: {suggested_model}")
        
        # Test direct response generation
        print("Testing direct ModelManager response generation...")
        
        response = await model_manager.generate_response(
            prompt="What is the capital of France? Be brief.",
            task_type="ask"
        )
        
        print(f"ModelManager response: {response}")
        
        if response and (isinstance(response, dict) and response.get("status") == "success" or isinstance(response, str)):
            print("✅ ModelManager integration working!")
            return True
        else:
            print(f"❌ ModelManager integration failed: {response}")
            return False
            
    except Exception as e:
        print(f"❌ Error in ModelManager test: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Run the complete live system test"""
    print_header("PROJECT-S AI AGENT - LIVE SYSTEM TEST")
    print(f"Test started at: {datetime.now()}")
    print("Testing ASK command routing fix implementation...")
    
    test_results = []
    
    # Test 1: Direct ASK command
    print_header("TEST 1: Direct ASK Command")
    result1 = await test_ask_command_direct()
    test_results.append(("Direct ASK Command", result1))
    
    # Test 2: CommandRouter integration
    print_header("TEST 2: CommandRouter Integration")
    result2 = await test_command_router()
    test_results.append(("CommandRouter Integration", result2))
    
    # Test 3: JSON command processing
    print_header("TEST 3: JSON Command Processing")
    result3 = await test_json_command_processing()
    test_results.append(("JSON Command Processing", result3))
    
    # Test 4: ModelManager integration
    print_header("TEST 4: ModelManager Integration")
    result4 = await test_model_manager_integration()
    test_results.append(("ModelManager Integration", result4))
    
    # Summary
    print_header("TEST RESULTS SUMMARY")
    
    passed = 0
    total = len(test_results)
    
    for test_name, result in test_results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")
        if result:
            passed += 1
    
    print(f"\nOverall Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED!")
        print("✅ ASK command routing fix is working correctly!")
        print("✅ System is ready for production use!")
    else:
        print(f"\n⚠️  {total - passed} tests failed.")
        print("❌ System needs attention before production use.")
    
    print(f"\nTest completed at: {datetime.now()}")
    print("Check 'live_test_output.log' for detailed logs.")
    
    return passed == total

if __name__ == "__main__":
    asyncio.run(main())
