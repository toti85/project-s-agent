#!/usr/bin/env python3
"""
Egyszerű teszt a fájlműveletek ellenőrzésére
"""
import asyncio
import logging
from pathlib import Path

# Beállítjuk a loggolást
logging.basicConfig(level=logging.DEBUG, format='%(levelname)s: %(message)s')

from tools.tool_registry import tool_registry

async def test_file_operations():
    """Egyszerű fájlművelet teszt"""
    try:
        print("=== FÁJLMŰVELET TESZT INDÍTÁSA ===")
          # 1. Tool registry inicializálás
        print("1. Tool registry státusz ellenőrzése...")
        await tool_registry.load_tools()
        print(f"   Betöltött eszköz osztályok: {len(tool_registry.tool_classes)}")
        print(f"   Elérhető osztályok: {list(tool_registry.tool_classes.keys())}")
        
        # 2. Próbáljuk meg lekérni a FileWriteTool-t
        print("\n2. FileWriteTool lekérése...")
        write_tool = tool_registry.get_tool("FileWriteTool")
        if write_tool:
            print(f"   FileWriteTool sikeresen létrehozva: {write_tool}")
        else:
            print("   FileWriteTool létrehozása sikertelen!")
        
        print(f"   Regisztrált tool példányok: {list(tool_registry.tools.keys())}")
          # 3. Biztonsági beállítások ellenőrzése
        print("\n3. Biztonsági beállítások ellenőrzése...")
        security = tool_registry.security_config
        print(f"   allow_file_write: {security.get('allow_file_write')}")
        print(f"   allow_system_commands: {security.get('allow_system_commands')}")
        print(f"   max_file_size: {security.get('max_file_size')}")
        
        # 4. Próba fájl írás
        print("\n4. Fájl írás teszt...")
        test_file = Path("test_output.txt")
        test_content = "Ez egy teszt fájl.\nMánia során készült."
        
        if write_tool:
            result = await write_tool.execute(
                path=str(test_file),
                content=test_content
            )
            print(f"   Írás eredmény: {result}")
        else:
            print("   FileWriteTool nem elérhető!")
        
        # 5. Próba fájl olvasás
        print("\n5. Fájl olvasás teszt...")
        read_tool = tool_registry.get_tool("FileReadTool")
        if test_file.exists() and read_tool:
            result = await read_tool.execute(path=str(test_file))
            print(f"   Olvasás eredmény: {result}")
        else:
            print(f"   FileReadTool nem elérhető vagy fájl nem létezik! (fájl létezik: {test_file.exists()})")
        
        # 6. System command teszt
        print("\n6. System command teszt...")
        system_tool = tool_registry.get_tool("SystemCommandTool")
        if system_tool and security.get("allow_system_commands"):
            result = await system_tool.execute(command="echo Hello from Project-S")
            print(f"   System command eredmény: {result}")
        else:
            print("   SystemCommandTool nem elérhető vagy system commands le vannak tiltva!")
        
        # 7. Tisztítás
        if test_file.exists():
            test_file.unlink()
            print("   Teszt fájl törölve")
            
        print("\n=== TESZT BEFEJEZVE ===")
        
    except Exception as e:
        print(f"HIBA a teszt során: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_file_operations())
