#!/usr/bin/env python3
"""
INTERAKTÍV PROJECT-S TESZTELŐ
=============================
Különböző fájltípusok és parancsok tesztelése
"""

import asyncio
import os
from pathlib import Path
import sys

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

async def interaktiv_teszt():
    """Interaktív teszt különböző fájltípusokra"""
    print("🎮 INTERAKTÍV PROJECT-S TESZTELŐ")
    print("=" * 40)
    
    try:
        from integrations.model_manager import ModelManager
        mm = ModelManager()
        print("✅ ModelManager kész")
        
        # Test cases
        test_parancsok = [
            {
                "nev": "JSON Konfiguráció",
                "parancs": 'Hozz létre egy config.json fájlt ezzel a tartalommal: {"app": "Project-S", "version": "2.0", "debug": true}',
                "vart_fajl": "config.json"
            },
            {
                "nev": "Python Script", 
                "parancs": 'Create a hello.py file with: print("Hello from Project-S automated testing!")',
                "vart_fajl": "hello.py"
            },
            {
                "nev": "CSV Adatok",
                "parancs": 'Készíts egy adatok.csv fájlt "Név,Kor,Város\\nPéter,25,Budapest\\nAnna,30,Debrecen" tartalommal',
                "vart_fajl": "adatok.csv"
            },
            {
                "nev": "Markdown Dokumentáció",
                "parancs": 'Generate a README.md file with: # Project-S Test\\n\\nThis file was created automatically!',
                "vart_fajl": "README.md"
            },
            {
                "nev": "Egyszerű jegyzet",
                "parancs": 'csinálj egy jegyzet.txt fájlt "TODO: Tesztelni a Project-S rendszert ✅" tartalommal',
                "vart_fajl": "jegyzet.txt"
            }
        ]
        
        print(f"\n🔥 {len(test_parancsok)} TESZT ESETET FUTTATUNK:\n")
        
        sikeres_tesztek = 0
        
        for i, teszt in enumerate(test_parancsok, 1):
            print(f"📋 TESZT {i}/{len(test_parancsok)}: {teszt['nev']}")
            print(f"📝 Parancs: {teszt['parancs'][:60]}...")
            
            # Filename extraction
            filename = mm._extract_filename_from_query(teszt['parancs'])
            print(f"📁 Kinyert fájlnév: {filename}")
            
            # Execution
            try:
                result = await mm.execute_task_with_core_system(teszt['parancs'])
                
                if result and result.get('status') == 'success':
                    print("✅ Végrehajtás: SIKERES")
                    
                    # File check
                    if os.path.exists(filename):
                        print(f"✅ Fájl létezik: {filename}")
                        
                        # Quick content preview
                        try:
                            with open(filename, 'r', encoding='utf-8') as f:
                                content = f.read()
                                preview = content.replace('\n', '\\n')[:50]
                                print(f"📄 Tartalom előnézet: {preview}...")
                        except:
                            print("📄 Tartalom: [binary or encoding issue]")
                        
                        sikeres_tesztek += 1
                        print("🎯 TESZT EREDMÉNY: ✅ SIKERES\n")
                    else:
                        print(f"❌ Fájl nem található: {filename}")
                        print("🎯 TESZT EREDMÉNY: ❌ SIKERTELEN\n")
                else:
                    print(f"❌ Végrehajtás hiba: {result}")
                    print("🎯 TESZT EREDMÉNY: ❌ SIKERTELEN\n")
                    
            except Exception as e:
                print(f"❌ Exception: {e}")
                print("🎯 TESZT EREDMÉNY: ❌ SIKERTELEN\n")
        
        # Final summary
        print("🏆 VÉGSŐ EREDMÉNYEK:")
        print("=" * 40)
        print(f"✅ Sikeres tesztek: {sikeres_tesztek}/{len(test_parancsok)}")
        print(f"📊 Sikerességi arány: {(sikeres_tesztek/len(test_parancsok)*100):.1f}%")
        
        if sikeres_tesztek == len(test_parancsok):
            print("\n🎉 MINDEN TESZT SIKERES!")
            print("🚀 A Project-S rendszer TÖKÉLETESEN működik!")
        elif sikeres_tesztek > len(test_parancsok) * 0.8:
            print("\n🎊 NAGYSZERŰ EREDMÉNY!")
            print("📈 A rendszer stabilan működik!")
        else:
            print("\n⚠️ Néhány teszt sikertelen volt")
            print("🔧 További finomhangolás szükséges")
            
        print(f"\n📁 Létrehozott fájlok listája:")
        for teszt in test_parancsok:
            filename = mm._extract_filename_from_query(teszt['parancs'])
            if os.path.exists(filename):
                print(f"   ✅ {filename}")
            else:
                print(f"   ❌ {filename}")
        
        return sikeres_tesztek == len(test_parancsok)
        
    except Exception as e:
        print(f"❌ Kritikus hiba: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🎯 Project-S Interaktív Tesztelő indítása...")
    asyncio.run(interaktiv_teszt())
