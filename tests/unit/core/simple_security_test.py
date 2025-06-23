#!/usr/bin/env python3
"""
Egyszerű biztonsági konfiguráció ellenőrző
"""
import sys
import os
sys.path.append(os.path.abspath('.'))

from tools.tool_registry import ToolRegistry

def main():
    print("=== BIZTONSÁGI KONFIGURÁCIÓ TESZT ===")
    
    # Létrehozunk egy új ToolRegistry példányt
    registry = ToolRegistry()
    
    print("\nBiztonsági beállítások:")
    for key, value in registry.security_config.items():
        print(f"   {key}: {value}")
    
    # Ellenőrizzük az allow_system_commands értékét
    allow_system = registry.security_config.get("allow_system_commands", False)
    print(f"\nAllow system commands: {allow_system}")
    
    if allow_system:
        print("✅ System commands ENGEDÉLYEZVE")
    else:
        print("❌ System commands LETILTVA")

if __name__ == "__main__":
    main()
