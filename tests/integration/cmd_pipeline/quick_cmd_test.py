import sys
import os

print("=== CMD HANDLER TESZT ===")

# Add project root to path
sys.path.insert(0, '.')

try:
    from core.ai_command_handler import AICommandHandler
    print("✅ CMD handler import sikeres")
    
    ai_handler = AICommandHandler()
    print("✅ CMD handler példány létrehozva")
    
    # Egyszerű subprocess teszt
    import subprocess
    result = subprocess.run("dir", shell=True, capture_output=True, text=True)
    print(f"📋 Dir parancs return code: {result.returncode}")
    print(f"📄 Dir output preview: {result.stdout[:100]}...")
      # Security validator teszt
    from tools.system_tools import CommandValidator
    
    test_cmd = "dir"
    validation_result = CommandValidator.validate_command(test_cmd)
    is_valid = validation_result.get("valid", False)
    reason = validation_result.get("reason", "")
    print(f"🔒 '{test_cmd}' biztonsági ellenőrzés: {'✅ ENGEDÉLYEZETT' if is_valid else '❌ TILTOTT'}")
    if reason:
        print(f"📋 Indoklás: {reason}")
    
    print("✅ Minden komponens működik!")
    
except Exception as e:
    print(f"❌ HIBA: {e}")
    import traceback
    traceback.print_exc()

print("=== TESZT VÉGE ===")
