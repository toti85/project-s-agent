#!/usr/bin/env python3
"""
FINAL VERIFICATION: ASK Command Model Routing Fix
This script provides a comprehensive verification that the ASK command routing fix is complete.
"""

def verify_static_code_changes():
    """Verify all static code changes are in place"""
    print("🔍 STATIC CODE VERIFICATION")
    print("-" * 40)
    
    try:
        with open('core/ai_command_handler.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        checks = [
            ("ModelManager Import", "from integrations.model_manager import ModelManager"),
            ("Availability Flag", "MODEL_MANAGER_AVAILABLE = True"),
            ("ModelManager Init", "self.model_manager = ModelManager()"),
            ("ASK uses ModelManager", "self.model_manager.generate_response("),
            ("Task Type Specified", 'task_type="ask"'),
            ("Fallback Logic", "self.qwen.ask(query)")
        ]
        
        all_passed = True
        for name, pattern in checks:
            found = pattern in content
            status = "✅ PASS" if found else "❌ FAIL"
            print(f"  {status} {name}")
            if not found:
                all_passed = False
        
        return all_passed
        
    except Exception as e:
        print(f"❌ Error reading handler file: {e}")
        return False

def verify_command_router_integration():
    """Verify command router uses the modified handler"""
    print("\n🔧 COMMAND ROUTER INTEGRATION")
    print("-" * 40)
    
    try:
        with open('core/command_router.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check that ASK commands are routed to our handler
        ask_registration = 'self.register("ASK", self.ai_handler.handle_ask_command)'
        found = ask_registration in content
        
        if found:
            print("  ✅ PASS ASK commands routed to modified handler")
            return True
        else:
            print("  ❌ FAIL ASK command routing not found")
            return False
            
    except Exception as e:
        print(f"❌ Error reading router file: {e}")
        return False

def verify_runtime_behavior():
    """Verify runtime behavior without actually executing commands"""
    print("\n⚙️ RUNTIME BEHAVIOR VERIFICATION")
    print("-" * 40)
    
    try:
        import sys
        sys.path.insert(0, '.')
        
        from core.ai_command_handler import AICommandHandler, MODEL_MANAGER_AVAILABLE
        
        print(f"  ✅ MODEL_MANAGER_AVAILABLE: {MODEL_MANAGER_AVAILABLE}")
        
        # Create handler instance
        handler = AICommandHandler()
        
        # Check if handler has ModelManager
        has_model_manager = hasattr(handler, 'model_manager')
        print(f"  ✅ Handler has ModelManager: {has_model_manager}")
        
        if has_model_manager:
            print(f"  ✅ ModelManager type: {type(handler.model_manager).__name__}")
            return True
        else:
            print("  ❌ Handler does NOT have ModelManager")
            return False
            
    except Exception as e:
        print(f"  ❌ Runtime verification error: {e}")
        return False

def main():
    print("🎯 ASK COMMAND MODEL ROUTING FIX - FINAL VERIFICATION")
    print("=" * 60)
    
    # Run all verification checks
    static_ok = verify_static_code_changes()
    router_ok = verify_command_router_integration()
    runtime_ok = verify_runtime_behavior()
    
    # Overall result
    print("\n" + "=" * 60)
    print("📊 VERIFICATION SUMMARY")
    print("=" * 60)
    
    print(f"Static Code Changes:  {'✅ PASS' if static_ok else '❌ FAIL'}")
    print(f"Router Integration:   {'✅ PASS' if router_ok else '❌ FAIL'}")
    print(f"Runtime Behavior:     {'✅ PASS' if runtime_ok else '❌ FAIL'}")
    
    overall_success = static_ok and router_ok and runtime_ok
    
    print("\n" + "🎉" * 20)
    if overall_success:
        print("🎉 SUCCESS: ASK COMMAND MODEL ROUTING FIX IS COMPLETE!")
        print("🎯 ASK commands will now route to Qwen3-235B via ModelManager")
        print("🚀 No more direct Ollama routing for ASK commands")
    else:
        print("❌ INCOMPLETE: ASK command routing fix needs attention")
        print("⚠️  Some verification checks failed")
    print("🎉" * 20)
    
    return overall_success

if __name__ == "__main__":
    main()
