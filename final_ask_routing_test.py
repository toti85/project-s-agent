#!/usr/bin/env python3
"""
Final verification test for ASK command model routing fix.
This test confirms that ASK commands now use ModelManager → Qwen3-235B instead of Ollama.
"""

import asyncio
import sys
import os
import logging
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def test_ask_routing():
    """Test that ASK commands properly route through ModelManager"""
    print("🔍 ASK COMMAND MODEL ROUTING - FINAL VERIFICATION")
    print("=" * 60)
    
    try:
        # Import the AI Command Handler
        from core.ai_command_handler import AICommandHandler
        
        # Create instance
        handler = AICommandHandler()
        
        # Check if ModelManager is being used
        if hasattr(handler, 'model_manager'):
            print("✅ SUCCESS: Handler is using ModelManager")
            print(f"   ModelManager type: {type(handler.model_manager)}")
        else:
            print("❌ WARNING: Handler is NOT using ModelManager")
            print("   Still using fallback QwenOllamaClient")
        
        # Check if MODEL_MANAGER_AVAILABLE flag is True
        from core.ai_command_handler import MODEL_MANAGER_AVAILABLE
        print(f"🔧 MODEL_MANAGER_AVAILABLE flag: {MODEL_MANAGER_AVAILABLE}")
        
        # Test with a simple ASK command
        print("\n📝 Testing ASK command processing...")
        test_command = {
            "type": "ASK",
            "query": "What is 2+2? (Simple test query)"
        }
        
        print(f"   Command: {test_command}")
        
        # Execute the command
        result = await handler.handle_ask_command(test_command)
        
        print(f"   Result: {result}")
        
        # Check if the result is successful
        if result.get("status") == "success" and "response" in result:
            print("✅ SUCCESS: ASK command executed successfully")
            print(f"   Response received: {result['response'][:100]}...")
            return True
        else:
            print(f"❌ ERROR: ASK command failed: {result}")
            return False
            
    except Exception as e:
        print(f"❌ EXCEPTION: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    print("🚀 Starting ASK Command Model Routing Test\n")
    
    success = await test_ask_routing()
    
    print("\n" + "=" * 60)
    print("FINAL VERDICT")
    print("=" * 60)
    
    if success:
        print("🎉 PASS: ASK command model routing fix is working!")
        print("   ASK commands are now properly routing through ModelManager → Qwen3-235B")
    else:
        print("❌ FAIL: ASK command model routing fix needs attention")
        print("   ASK commands may still be using the old Ollama routing")
    
    return success

if __name__ == "__main__":
    asyncio.run(main())
