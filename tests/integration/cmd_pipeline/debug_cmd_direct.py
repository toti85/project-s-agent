#!/usr/bin/env python3
"""
KÖZVETLEN CMD HANDLER DEBUG TESZT
================================
Közvetlenül hívjuk meg a CMD handler komponenseket
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

async def debug_cmd_direct():
    """Közvetlen CMD handler hívás debug módban"""
    print("🔧 KÖZVETLEN CMD HANDLER DEBUG")
    print("=" * 50)
    
    try:
        # 1. Command router ellenőrzés
        print("1️⃣ Command Router ellenőrzés...")
        from core.command_router import CommandRouter
        router = CommandRouter()
        print("✅ CommandRouter betöltve")
        
        # 2. AI Command Handler ellenőrzés
        print("\n2️⃣ AI Command Handler ellenőrzés...")
        from core.ai_command_handler import AICommandHandler
        ai_handler = AICommandHandler()
        print("✅ AICommandHandler betöltve")
        
        # 3. System Tools biztonsági ellenőrzés
        print("\n3️⃣ System Tools Security ellenőrzés...")
        from tools.system_tools import CommandValidator
        validator = CommandValidator()
        print("✅ CommandValidator betöltve")
        
        # 4. Teszt parancs validáció
        test_commands = [
            "dir",
            "ls",  
            "echo hello",
            "time"
        ]
        
        print("\n4️⃣ CMD Parancs validáció tesztek:")
        for cmd in test_commands:
            is_valid = validator.is_command_allowed(cmd)
            print(f"  📝 '{cmd}' -> {'✅ ENGEDÉLYEZETT' if is_valid else '❌ TILTOTT'}")
        
        # 5. Közvetlen CMD handler hívás
        print("\n5️⃣ Közvetlen CMD handler hívás teszt:")
        
        test_cmd = "dir"
        print(f"🚀 Teszt parancs: {test_cmd}")
        
        try:
            result = await ai_handler.handle_cmd_command(test_cmd)
            print("📊 CMD Handler eredmény:")
            print(f"  Status: {result.get('status', 'NINCS')}")
            print(f"  Output: {str(result.get('output', 'NINCS'))[:200]}...")
            print(f"  Command: {result.get('command', 'NINCS')}")
            
            if result.get('status') == 'success':
                print("✅ CMD HANDLER SIKERES!")
            else:
                print("⚠️ CMD HANDLER PROBLÉMA")
                if 'error' in result:
                    print(f"❌ Hiba: {result['error']}")
                    
        except Exception as e:
            print(f"❌ CMD Handler hiba: {e}")
            import traceback
            traceback.print_exc()
        
        # 6. Command Type Detection teszt
        print("\n6️⃣ Command Type Detection teszt:")
        from core.command_detector import detect_command_type
        
        test_queries = [
            "list files in directory",
            "create a new file called test.txt", 
            "what is the weather today",
            "execute dir command"
        ]
        
        for query in test_queries:
            cmd_type = detect_command_type(query)
            print(f"  📝 '{query[:30]}...' -> {cmd_type}")
        
        print("\n🎯 DEBUG ÖSSZEFOGLALÓ:")
        print("=" * 50)
        print("✅ Command Router: BETÖLTVE")
        print("✅ AI Command Handler: BETÖLTVE") 
        print("✅ Security Validator: BETÖLTVE")
        print("🔍 CMD pipeline komponensek elérhetők")
        
    except Exception as e:
        print(f"❌ Kritikus hiba: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(debug_cmd_direct())
