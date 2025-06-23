#!/usr/bin/env python3
"""
Simple verification script to check if ASK command routing fix is applied.
This script just checks the code structure without running the full system.
"""

import os
import sys

def check_ai_command_handler_fix():
    """Check if the ASK command routing fix is properly applied"""
    
    print("=" * 60)
    print("ASK COMMAND ROUTING FIX VERIFICATION")
    print("=" * 60)
    
    # Read the ai_command_handler.py file
    handler_file = "core/ai_command_handler.py"
    
    if not os.path.exists(handler_file):
        print(f"❌ FAILURE: {handler_file} not found")
        return False
    
    try:
        with open(handler_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for key indicators that the fix is applied
        checks = [
            ("ModelManager import", "from integrations.model_manager import ModelManager"),
            ("MODEL_MANAGER_AVAILABLE", "MODEL_MANAGER_AVAILABLE = True"),
            ("ModelManager initialization", "self.model_manager = ModelManager()"),
            ("ASK command using ModelManager", "self.model_manager.generate_response"),
            ("Task type specification", 'task_type="ask"')
        ]
        
        all_passed = True
        
        for check_name, pattern in checks:
            if pattern in content:
                print(f"✅ {check_name}: FOUND")
            else:
                print(f"❌ {check_name}: NOT FOUND")
                all_passed = False
        
        # Check for old direct QwenOllamaClient usage in ASK commands
        if "self.qwen.ask(" in content:
            # This should only be in the fallback path, let's check context
            ask_lines = [line for line in content.split('\n') if 'self.qwen.ask(' in line]
            if ask_lines:
                print("ℹ️  Found self.qwen.ask() usage - checking if it's in fallback path...")
                # Look for the context around these lines
                for line in ask_lines:
                    print(f"   Line: {line.strip()}")
        
        # Additional check: Look for the specific fix pattern
        if "if MODEL_MANAGER_AVAILABLE and hasattr(self, 'model_manager'):" in content:
            print("✅ Conditional ModelManager usage: FOUND")
        else:
            print("❌ Conditional ModelManager usage: NOT FOUND")
            all_passed = False
        
        print("\n" + "-" * 40)
        if all_passed:
            print("🎉 SUCCESS: All ASK command routing fix indicators are present!")
            print("   The ASK commands should now route to Qwen3-235B via ModelManager.")
        else:
            print("⚠️  WARNING: Some fix indicators are missing.")
            print("   The ASK command routing fix may not be complete.")
        
        return all_passed
        
    except Exception as e:
        print(f"❌ FAILURE: Error reading {handler_file}: {str(e)}")
        return False

def main():
    """Run the verification"""
    print("ASK Command Model Routing Fix Verification\n")
    
    success = check_ai_command_handler_fix()
    
    print("\n" + "=" * 60)
    print("VERIFICATION SUMMARY")
    print("=" * 60)
    
    if success:
        print("✅ VERIFICATION PASSED!")
        print("   The ASK command routing fix appears to be correctly implemented.")
        print("   ASK commands should now use ModelManager → Qwen3-235B instead of Ollama.")
    else:
        print("❌ VERIFICATION FAILED!")
        print("   The ASK command routing fix may need additional work.")
    
    print("\nFor full functional testing, use a complete integration test.")
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
