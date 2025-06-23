#!/usr/bin/env python3
"""
JSON fájl létrehozás teszt
"""

import asyncio
import sys
import os
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

async def test_json_file_creation():
    """JSON fájl létrehozás tesztelése"""
    print("🔧 JSON FÁJL LÉTREHOZÁS TESZT")
    print("=" * 40)
    
    try:
        from integrations.model_manager import ModelManager
        mm = ModelManager()
        
        # JSON fájl létrehozási parancs
        json_command = 'hozz létre egy config.json fájlt tartalommal: {"name": "Project-S", "version": "1.0", "status": "working"}'
        
        print(f"📝 Parancs: {json_command}")
        print("\n🔍 Fájlnév kinyerés tesztelése...")
        
        # Filename extraction
        extracted_filename = mm._extract_filename_from_query(json_command)
        print(f"📁 Kinyert fájlnév: {extracted_filename}")
        
        if extracted_filename == "config.json":
            print("✅ Fájlnév kinyerés SIKERES!")
        else:
            print(f"⚠️  Fájlnév: {extracted_filename}")
        
        # Core system execution
        print("\n🚀 Core system végrehajtás...")
        result = await mm.execute_task_with_core_system(json_command)
        
        print(f"📊 Eredmény: {result}")
        
        # Ellenőrzés
        if os.path.exists("config.json"):
            print("✅ JSON FÁJL LÉTREJÖTT!")
            with open("config.json", "r", encoding="utf-8") as f:
                content = f.read()
                print(f"📄 Tartalom: {content}")
        else:
            print("⚠️  JSON fájl nem található")
            
    except Exception as e:
        print(f"❌ Hiba: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_json_file_creation())
