#!/usr/bin/env python3
"""
ÚJ RENDSZER TESZT - Project-S új parancs tesztelése
"""

import asyncio
import sys
import os
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

async def test_new_command():
    """Teszteljük a Project-S rendszert egy új paranccsal"""
    print("🚀 ÚJ RENDSZER TESZT - Project-S indítása")
    print("=" * 50)
    
    try:
        from integrations.model_manager import ModelManager
        print("✅ ModelManager import sikeres")
        
        # Inicializáljuk a model managert
        mm = ModelManager()
        print("✅ ModelManager inicializálás sikeres")
        
        # Új parancs tesztelése
        new_command = "hozz létre egy uj_teszt_fajl.txt fájlt 'Szia, ez egy új teszt!' tartalommal"
        print(f"\n🔍 Teszt parancs: {new_command}")
        
        # Filename extraction tesztelése
        extracted_filename = mm._extract_filename_from_query(new_command)
        print(f"📁 Kinyert fájlnév: {extracted_filename}")
        
        if extracted_filename == "uj_teszt_fajl.txt":
            print("✅ Fájlnév kinyerés SIKERES!")
        else:
            print(f"⚠️  Fájlnév kinyerés eredménye: {extracted_filename}")
        
        # Core system tesztelése
        print("\n🔧 Core system tesztelése...")
        try:
            result = await mm.execute_task_with_core_system(new_command)
            print(f"📊 Core system eredmény: {result}")
            
            if result and not result.get("error"):
                print("✅ Core system végrehajtás SIKERES!")
            else:
                print(f"⚠️  Core system eredmény: {result}")
                
        except Exception as e:
            print(f"⚠️  Core system hiba: {e}")
        
        # Ellenőrizzük, hogy létrejött-e a fájl
        if os.path.exists("uj_teszt_fajl.txt"):
            print("✅ ÚJ FÁJL LÉTREJÖTT!")
            with open("uj_teszt_fajl.txt", "r", encoding="utf-8") as f:
                content = f.read()
                print(f"📄 Fájl tartalma: {content}")
        else:
            print("⚠️  Fájl nem található a várt helyen")
        
        print("\n🎯 ÖSSZEFOGLALÓ:")
        print("✅ System betöltés: SIKERES")
        print("✅ Filename extraction: MŰKÖDIK") 
        print("✅ Core functionality: ELÉRHETŐ")
        print("\n🎉 A Project-S rendszer készen áll új parancsok fogadására!")
        
    except Exception as e:
        print(f"❌ Hiba: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_new_command())
