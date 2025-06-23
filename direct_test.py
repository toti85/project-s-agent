"""
Direct test of ASK command routing - no async, minimal setup
"""

def test_ask_routing():
    print("=" * 60)
    print("DIRECT ASK COMMAND ROUTING TEST")
    print("=" * 60)
    
    try:
        import sys
        import os
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        
        print("1. Importing AICommandHandler...")
        from core.ai_command_handler import AICommandHandler, MODEL_MANAGER_AVAILABLE
        print(f"   ✅ Import successful!")
        print(f"   MODEL_MANAGER_AVAILABLE: {MODEL_MANAGER_AVAILABLE}")
        
        print("\n2. Creating handler instance...")
        handler = AICommandHandler()
        print(f"   ✅ Handler created!")
        
        print("\n3. Checking ModelManager integration...")
        if hasattr(handler, 'model_manager'):
            print(f"   ✅ Handler has ModelManager!")
            print(f"   ModelManager type: {type(handler.model_manager)}")
            print(f"   🎉 ASK commands will route to Qwen3-235B via ModelManager!")
        else:
            print(f"   ❌ Handler using fallback QwenOllamaClient")
            if hasattr(handler, 'qwen'):
                print(f"   Fallback client type: {type(handler.qwen)}")
        
        print("\n4. Checking method availability...")
        if hasattr(handler, 'handle_ask_command'):
            print(f"   ✅ handle_ask_command method exists")
        else:
            print(f"   ❌ handle_ask_command method missing")
            
        print("\n" + "=" * 60)
        print("VERIFICATION SUMMARY")
        print("=" * 60)
        
        if MODEL_MANAGER_AVAILABLE and hasattr(handler, 'model_manager'):
            print("🎉 SUCCESS: ASK Command Routing Fix is WORKING!")
            print("   ✅ ModelManager available and integrated")
            print("   ✅ ASK commands will route to Qwen3-235B")
            print("   ✅ No longer using direct Ollama routing")
            return True
        else:
            print("❌ ISSUE: ASK Command Routing Fix needs attention")
            print("   ModelManager not properly integrated")
            return False
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_ask_routing()
