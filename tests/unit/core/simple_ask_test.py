#!/usr/bin/env python3
"""
Egyszerű ASK Command teszt a Project-S rendszerben
Csak az ASK command routing működését teszteli
"""

import asyncio
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

async def simple_ask_test():
    """Egyszerű ASK command teszt"""
    
    print("🧪 EGYSZERŰ ASK COMMAND TESZT")
    print("=" * 40)
    
    try:
        # Import command router
        print("1. Command Router importálása...")
        from core.command_router import router
        print("✅ Command Router sikeresen importálva")
        
        # Create test command
        test_command = {
            "type": "ASK",
            "query": "Mi a főváros Magyarországon?"
        }
        
        print(f"\n2. ASK command küldése...")
        print(f"   Parancs: {test_command}")
        
        # Execute command
        print("\n3. Parancs végrehajtása...")
        result = await router.route_command(test_command)
        
        print(f"\n4. Eredmény:")
        print(f"   {result}")
        
        # Check result
        if isinstance(result, dict):
            if "error" in result:
                print(f"\n❌ Hiba: {result['error']}")
                return False
            elif "response" in result:
                print(f"\n✅ Sikeres válasz!")
                print(f"   Válasz: {result['response']}")
                return True
            else:
                print(f"\n⚠️  Váratlan válasz formátum")
                return True
        else:
            print(f"\n❌ Érvénytelen válasz típus: {type(result)}")
            return False
            
    except Exception as e:
        print(f"\n❌ Teszt hiba: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    print("🚀 PROJECT-S ASK COMMAND TESZT")
    print("Tesztelő: ASK command routing ModelManager-rel")
    print()
    
    success = await simple_ask_test()
    
    print("\n" + "=" * 40)
    if success:
        print("🎉 TESZT SIKERES!")
        print("✅ ASK command routing működik")
    else:
        print("❌ TESZT SIKERTELEN")
        print("⚠️  Ellenőrizd a konfigurációt")
    
    return success

if __name__ == "__main__":
    try:
        result = asyncio.run(main())
        sys.exit(0 if result else 1)
    except KeyboardInterrupt:
        print("\n\n⏹️  Teszt megszakítva")
        sys.exit(1)
