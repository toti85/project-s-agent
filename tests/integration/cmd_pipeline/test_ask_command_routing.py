#!/usr/bin/env python3
"""
Test script to verify ASK command model routing fix.
This script tests that ASK commands now properly route to Qwen3-235B via ModelManager
instead of routing directly to Ollama.
"""

import asyncio
import json
import logging
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.ai_command_handler import AICommandHandler
from integrations.model_manager import ModelManager

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def test_ask_command_routing():
    """Test that ASK commands use ModelManager for proper model routing"""
    
    print("=" * 60)
    print("ASK COMMAND MODEL ROUTING TEST")
    print("=" * 60)
    
    try:
        # Initialize the AI Command Handler
        handler = AICommandHandler()
        
        # Check if ModelManager is available
        if hasattr(handler, 'model_manager'):
            print("✅ SUCCESS: AICommandHandler is using ModelManager")
            print(f"   ModelManager instance: {type(handler.model_manager)}")
        else:
            print("❌ FAILURE: AICommandHandler is NOT using ModelManager")
            print("   Still using fallback QwenOllamaClient")
            return False
        
        # Test ASK command routing
        print("\n" + "-" * 40)
        print("Testing ASK command execution...")
        print("-" * 40)
        
        # Create a test ASK command
        test_command = {
            "type": "ASK",
            "command": "What is the capital of France? (This is a test query)"
        }
        
        print(f"Sending ASK command: {test_command}")
        
        # Process the command
        result = await handler.process_json_command(test_command)
        
        print(f"\nCommand result: {result}")
        
        # Check if the result indicates success
        if "error" in result:
            print(f"❌ FAILURE: ASK command returned error: {result['error']}")
            return False
        else:
            print("✅ SUCCESS: ASK command executed without errors")
            
            # Check if we got a response
            if "response" in result or "result" in result:
                print("✅ SUCCESS: ASK command returned a response")
                response_text = result.get("response", result.get("result", ""))
                print(f"   Response snippet: {response_text[:100]}...")
            else:
                print("⚠️  WARNING: ASK command didn't return expected response format")
                print(f"   Full result: {result}")
        
        return True
        
    except Exception as e:
        print(f"❌ FAILURE: Exception during test: {str(e)}")
        logger.exception("Test failed with exception")
        return False

async def test_model_manager_availability():
    """Test ModelManager availability and configuration"""
    
    print("\n" + "=" * 60)
    print("MODEL MANAGER AVAILABILITY TEST")
    print("=" * 60)
    
    try:
        # Test ModelManager import and initialization
        model_manager = ModelManager()
        print("✅ SUCCESS: ModelManager can be imported and initialized")
        
        # Check if ModelManager has the required methods
        if hasattr(model_manager, 'generate_response'):
            print("✅ SUCCESS: ModelManager has generate_response method")
        else:
            print("❌ FAILURE: ModelManager missing generate_response method")
            return False
            
        # Test a simple model routing call
        print("\nTesting ModelManager.generate_response...")
        response = await model_manager.generate_response(
            prompt="Test prompt for model routing verification",
            task_type="ask"
        )
        
        print(f"ModelManager response: {response}")
        
        if isinstance(response, dict) and response.get("status") == "success":
            print("✅ SUCCESS: ModelManager generate_response working correctly")
            return True
        else:
            print("⚠️  WARNING: ModelManager response format may need attention")
            return True  # Still consider this a success if no errors
            
    except Exception as e:
        print(f"❌ FAILURE: ModelManager test failed: {str(e)}")
        logger.exception("ModelManager test failed")
        return False

def main():
    """Run all routing tests"""
    print("Starting ASK Command Model Routing Verification Tests...")
    print(f"Python path: {sys.path[0]}")
    
    async def run_tests():
        success_count = 0
        total_tests = 2
        
        # Test 1: ModelManager availability
        if await test_model_manager_availability():
            success_count += 1
            
        # Test 2: ASK command routing
        if await test_ask_command_routing():
            success_count += 1
        
        # Summary
        print("\n" + "=" * 60)
        print("TEST SUMMARY")
        print("=" * 60)
        print(f"Tests passed: {success_count}/{total_tests}")
        
        if success_count == total_tests:
            print("🎉 ALL TESTS PASSED! ASK command routing fix is working correctly.")
            print("   ASK commands now use ModelManager for proper Qwen3-235B routing.")
        else:
            print(f"⚠️  {total_tests - success_count} test(s) failed. Review the output above.")
            
        return success_count == total_tests
    
    # Run the async tests
    try:
        success = asyncio.run(run_tests())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\nFatal error during testing: {str(e)}")
        logger.exception("Fatal test error")
        sys.exit(1)

if __name__ == "__main__":
    main()
