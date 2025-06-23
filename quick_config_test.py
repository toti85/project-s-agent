#!/usr/bin/env python3
import json
from pathlib import Path

print("=== GYORS BIZTONSÁGI KONFIGURÁCIÓ TESZT ===")

# 1. Ellenőrizzük a config fájl tartalmát
config_path = Path("config/tool_security.json")
print(f"Config fájl elérési út: {config_path.absolute()}")
print(f"Config fájl létezik: {config_path.exists()}")

if config_path.exists():
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
    print("Config fájl tartalma:")
    for key, value in config.items():
        print(f"   {key}: {value}")
else:
    print("❌ Config fájl nem található!")

# 2. Most próbáljuk meg betölteni a ToolRegistry-t
try:
    from tools.tool_registry import ToolRegistry
    registry = ToolRegistry()
    
    print("\nToolRegistry biztonsági beállítások:")
    for key, value in registry.security_config.items():
        print(f"   {key}: {value}")
    
    # Ellenőrizzük az allow_system_commands értékét
    allow_system = registry.security_config.get("allow_system_commands", False)
    print(f"\n🔍 Allow system commands: {allow_system}")
    
    if allow_system:
        print("✅ System commands ENGEDÉLYEZVE")
    else:
        print("❌ System commands LETILTVA")
        
except Exception as e:
    print(f"❌ Hiba a ToolRegistry betöltésekor: {e}")
    import traceback
    traceback.print_exc()

print("\n=== TESZT VÉGE ===")
