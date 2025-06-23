#!/usr/bin/env python3
"""
PROJECT-S CMD PARANCSOK TESZTELÉSI STRATÉGIA
===========================================

Teszteljük a CMD command routing és végrehajtási pipeline-t
"""

import asyncio
import os
import time
from pathlib import Path
import sys

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

async def cmd_teszt_egyszerű():
    """Egyszerű CMD parancsok tesztelése"""
    print("🚀 PROJECT-S CMD TESZTELÉSI STRATÉGIA")
    print("=" * 50)
    
    try:
        from integrations.model_manager import ModelManager
        mm = ModelManager()
        print("✅ ModelManager betöltve")
        
        # FASE 1: Egyszerű rendszer lekérdezések
        print("\n📋 FASE 1: EGYSZERŰ RENDSZER LEKÉRDEZÉSEK")
        print("-" * 40)
        
        cmd_tesztek = [
            "list all files in current directory",
            "show current directory", 
            "what's the current time",
            "show running processes"
        ]
        
        eredmenyek = []
        
        for i, cmd in enumerate(cmd_tesztek, 1):
            print(f"\n🔧 TESZT {i}: {cmd}")
            print("-" * 30)
            
            start_time = time.time()
            
            try:
                # 1. Filename extraction ellenőrzés
                filename = mm._extract_filename_from_query(cmd)
                print(f"📁 Filename extraction: {filename}")
                
                # 2. Core system végrehajtás
                result = await mm.execute_task_with_core_system(cmd)
                
                execution_time = time.time() - start_time
                
                print(f"⏱️ Végrehajtási idő: {execution_time:.2f} másodperc")
                print(f"📊 Státusz: {result.get('status', 'ISMERETLEN')}")
                print(f"🤖 Command Type: {result.get('command_type', 'NINCS')}")
                print(f"⚡ Command Action: {result.get('command_action', 'NINCS')}")
                
                # Részletes eredmény elemzés
                if result.get('execution_result'):
                    exec_result = result['execution_result']
                    print(f"✅ Execution Status: {exec_result.get('status', 'NINCS')}")
                    if 'output' in exec_result:
                        output = exec_result['output']
                        print(f"📄 Output preview: {str(output)[:100]}...")
                    if 'command' in exec_result:
                        print(f"💻 Executed Command: {exec_result['command']}")
                
                eredmenyek.append({
                    'cmd': cmd,
                    'status': result.get('status'),
                    'command_type': result.get('command_type'),
                    'execution_time': execution_time,
                    'success': result.get('status') == 'success'
                })
                
                if result.get('status') == 'success':
                    print("✅ SIKERES")
                else:
                    print("⚠️ PROBLÉMÁS")
                    
            except Exception as e:
                print(f"❌ HIBA: {e}")
                eredmenyek.append({
                    'cmd': cmd,
                    'status': 'error',
                    'error': str(e),
                    'execution_time': time.time() - start_time,
                    'success': False
                })
            
            print("=" * 30)
        
        # ÖSSZEFOGLALÓ
        print("\n🎯 CMD TESZTELÉSI ÖSSZEFOGLALÓ:")
        print("=" * 50)
        
        sikeres = sum(1 for r in eredmenyek if r['success'])
        osszes = len(eredmenyek)
        
        print(f"📊 Sikeres tesztek: {sikeres}/{osszes}")
        print(f"📈 Sikerességi arány: {(sikeres/osszes)*100:.1f}%")
        
        print("\n📋 RÉSZLETES EREDMÉNYEK:")
        for r in eredmenyek:
            status_icon = "✅" if r['success'] else "❌"
            print(f"{status_icon} {r['cmd'][:30]}... - {r.get('command_type', 'NINCS')} - {r['execution_time']:.2f}s")
        
        # KÖVETKEZŐ LÉPÉSEK
        print("\n🔮 KÖVETKEZŐ TESZTELÉSI LÉPÉSEK:")
        if sikeres > 0:
            print("✅ CMD pipeline alapok működnek")
            print("🚀 Próbálhatjuk a fájl/mappa műveleteket")
            print("🔧 Tesztelhetnénk a fejlettebb parancsokat")
        else:
            print("⚠️ CMD pipeline problémák detektálva")
            print("🔍 Szükséges a CMD handler ellenőrzése")
            print("🛠️ Esetleg hiányzó CMD routing")
        
        return eredmenyek
        
    except Exception as e:
        print(f"❌ Kritikus hiba a tesztelés során: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    asyncio.run(cmd_teszt_egyszerű())
