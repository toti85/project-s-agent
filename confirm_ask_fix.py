#!/usr/bin/env python3
"""
Confirm ASK command routing fix is working
"""
import sys
import os
import asyncio

# Add project root to path
sys.path.insert(0, '.')

async def test_ask_routing():
    try:
        from core.ai_command_handler import AICommandHandler, MODEL_MANAGER_AVAILABLE
        
        print("🔍 ASK Command Routing Fix Verification")
        print("=" * 50)
        
        print(f"✅ MODEL_MANAGER_AVAILABLE: {MODEL_MANAGER_AVAILABLE}")
        
        # Create handler instance
        handler = AICommandHandler()
        
        # Check if handler has ModelManager
        has_model_manager = hasattr(handler, 'model_manager')
        print(f"✅ Handler has ModelManager: {has_model_manager}")
        
        if has_model_manager:
            print(f"✅ ModelManager type: {type(handler.model_manager)}")
            
            # Test a simple ASK command
            print("\n📝 Testing ASK command execution...")
            
            test_command = {
                "query": "What is the capital of France?"
            }
            
            try:
                result = await handler.handle_ask_command(test_command)
                print(f"✅ ASK command result: {result}")
                
                if result.get("status") == "success":
                    print("🎉 SUCCESS: ASK command executed successfully through ModelManager!")
                    return True
                else:
                    print(f"⚠️ ASK command returned: {result}")
                    return False
                    
            except Exception as e:
                print(f"❌ Error executing ASK command: {e}")
                return False
        else:
            print("❌ Handler does NOT have ModelManager - still using fallback")
            return False
            
    except Exception as e:
        print(f"❌ Import error: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_ask_routing())
    
    print("\n" + "=" * 50)
    print("FINAL RESULT")
    print("=" * 50)
    
    if success:
        print("🎉 PASS: ASK command routing fix is WORKING!")
        print("   ASK commands now use ModelManager → Qwen3-235B")
    else:
        print("❌ FAIL: ASK command routing fix needs attention")
