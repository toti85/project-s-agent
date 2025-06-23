#!/usr/bin/env python3
"""
Egyszerű teszt a biztonsági konfiguráció betöltésének ellenőrzésére
"""
import asyncio
import logging
from pathlib import Path

# Beállítjuk a loggolást
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

from tools.tool_registry import tool_registry

async def test_security_config():
    """Biztonsági konfiguráció teszt"""
    try:
        print("=== BIZTONSÁGI KONFIGURÁCIÓ TESZT ===")
        
        # Tool registry inicializálás és betöltés
        await tool_registry.load_tools()
        
        print("\nBiztonsági beállítások:")
        security = tool_registry.security_config
        for key, value in security.items():
            print(f"   {key}: {value}")
        
        # Ellenőrizzük, hogy a SystemCommandTool elérhető-e
        print("\nSystemCommandTool ellenőrzése:")
        system_tool = tool_registry.get_tool("SystemCommandTool")
        if system_tool:
            print(f"   SystemCommandTool sikeresen betöltve: {system_tool}")
            
            # Próba parancs végrehajtás (biztonságos)
            if security.get("allow_system_commands"):
                print("   System commands engedélyezve, próba parancs...")
                result = await system_tool.execute(command="echo 'Teszt parancs'")
                print(f"   Eredmény: {result}")
            else:
                print("   System commands le vannak tiltva")
        else:
            print("   SystemCommandTool nem elérhető!")
        
        print("\n=== TESZT BEFEJEZVE ===")
        
    except Exception as e:
        print(f"HIBA a teszt során: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_security_config())
