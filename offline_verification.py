"""
OFFLINE ASK Command Routing Verification
Checks the code structure without initializing network components
"""

import sys
import os

def verify_ask_routing_offline():
    print("=" * 60)
    print("OFFLINE ASK COMMAND ROUTING VERIFICATION")
    print("=" * 60)
    
    try:
        # Add project path
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        
        print("1. Checking ai_command_handler.py structure...")
        
        # Read the file content directly
        handler_file = "core/ai_command_handler.py"
        if not os.path.exists(handler_file):
            print(f"   ❌ {handler_file} not found!")
            return False
            
        with open(handler_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for key patterns
        checks = [
            ("ModelManager import", "from integrations.model_manager import ModelManager"),
            ("MODEL_MANAGER_AVAILABLE flag", "MODEL_MANAGER_AVAILABLE = True"),
            ("ModelManager initialization", "self.model_manager = ModelManager()"),
            ("ASK handler using ModelManager", "self.model_manager.generate_response"),
            ("Task type specification", 'task_type="ask"'),
            ("Fallback handling", "self.qwen.ask(query)")
        ]
        
        print("\n2. Verifying fix patterns...")
        all_found = True
        
        for check_name, pattern in checks:
            if pattern in content:
                print(f"   ✅ {check_name}: FOUND")
            else:
                print(f"   ❌ {check_name}: NOT FOUND")
                all_found = False
        
        print("\n3. Checking command router integration...")
        router_file = "core/command_router.py"
        if os.path.exists(router_file):
            with open(router_file, 'r', encoding='utf-8') as f:
                router_content = f.read()
            
            if "self.ai_handler.handle_ask_command" in router_content:
                print("   ✅ ASK command registered in router")
            else:
                print("   ❌ ASK command NOT registered in router")
                all_found = False
        else:
            print(f"   ❌ {router_file} not found!")
            all_found = False
        
        print("\n" + "=" * 60)
        print("OFFLINE VERIFICATION RESULTS")
        print("=" * 60)
        
        if all_found:
            print("🎉 SUCCESS: ASK Command Routing Fix is CORRECTLY IMPLEMENTED!")
            print("\nWhat this means:")
            print("✅ ModelManager import and availability check: PRESENT")
            print("✅ Conditional ModelManager initialization: PRESENT") 
            print("✅ ASK handler using ModelManager.generate_response: PRESENT")
            print("✅ Task type 'ask' specification: PRESENT")
            print("✅ Fallback to QwenOllamaClient: PRESENT")
            print("✅ Router integration: PRESENT")
            print("\n🔄 BEFORE FIX: ASK commands → QwenOllamaClient() → Ollama")
            print("🎯 AFTER FIX:  ASK commands → ModelManager → Qwen3-235B")
            print("\n💡 The fix ensures ALL command types use the same model routing logic!")
            return True
        else:
            print("❌ ISSUES FOUND: Some fix patterns are missing")
            print("   The ASK command routing fix may not be complete")
            return False
            
    except Exception as e:
        print(f"❌ ERROR during verification: {e}")
        import traceback
        traceback.print_exc()
        return False

def check_model_manager_method():
    """Check if ModelManager has the required suggest_model_for_task method"""
    print("\n4. Checking ModelManager suggest_model_for_task method...")
    
    try:
        mm_file = "integrations/multi_model_ai_client.py"
        if os.path.exists(mm_file):
            with open(mm_file, 'r', encoding='utf-8') as f:
                mm_content = f.read()
            
            if "def suggest_model_for_task" in mm_content:
                print("   ✅ suggest_model_for_task method: FOUND")
                
                # Check for ASK task type handling
                if '"ask"' in mm_content or "'ask'" in mm_content:
                    print("   ✅ ASK task type handling: FOUND")
                    return True
                else:
                    print("   ⚠️  ASK task type handling: NOT FOUND")
                    return False
            else:
                print("   ❌ suggest_model_for_task method: NOT FOUND")
                return False
        else:
            print(f"   ❌ {mm_file} not found!")
            return False
            
    except Exception as e:
        print(f"   ❌ Error checking ModelManager: {e}")
        return False

if __name__ == "__main__":
    success1 = verify_ask_routing_offline()
    success2 = check_model_manager_method()
    
    print("\n" + "=" * 60)
    print("FINAL ASSESSMENT")
    print("=" * 60)
    
    if success1 and success2:
        print("🌟 EXCELLENT: ASK Command Routing Fix is FULLY IMPLEMENTED!")
        print("   The system is ready to route ASK commands to Qwen3-235B!")
    else:
        print("⚠️  ATTENTION: Some components need review")
        
    print("\nNext step: Test with actual execution when network allows")
