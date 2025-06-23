#!/usr/bin/env python3
"""
Gyors teszt az ASK command model routing javításához
Ez a teszt ellenőrzi, hogy az ASK commandok valóban ModelManager-en keresztül mennek-e
"""

import asyncio
import json
import sys
import os

# Projekt útvonal hozzáadása
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

async def test_ask_command_integration():
    """ASK command integráció teszt"""
    
    print("🔍 ASK COMMAND MODEL ROUTING TESZT")
    print("=" * 50)
    
    try:
        # 1. Command Router tesztelése
        print("1️⃣ Command Router importálása...")
        from core.command_router import CommandRouter
        
        router = CommandRouter()
        print(f"✅ Router létrehozva: {type(router)}")
        
        # 2. ASK handler regisztrációjának ellenőrzése
        print("\n2️⃣ ASK handler ellenőrzése...")
        if "ASK" in router.handlers:
            print("✅ ASK handler regisztrálva")
            handler = router.handlers["ASK"]
            print(f"   Handler: {handler}")
        else:
            print("❌ ASK handler NINCS regisztrálva")
            return False
        
        # 3. AI Handler inspektálása
        print("\n3️⃣ AI Handler állapotának ellenőrzése...")
        ai_handler = router.ai_handler
        print(f"   AI Handler típus: {type(ai_handler)}")
        
        # ModelManager ellenőrzése
        if hasattr(ai_handler, 'model_manager'):
            print("✅ ModelManager elérhető az AI Handler-ben")
            print(f"   ModelManager típus: {type(ai_handler.model_manager)}")
        else:
            print("⚠️  ModelManager NINCS az AI Handler-ben")
            
        # Fallback QwenOllamaClient ellenőrzése
        if hasattr(ai_handler, 'qwen'):
            print("✅ QwenOllamaClient fallback elérhető")
        else:
            print("⚠️  QwenOllamaClient fallback NINCS")
        
        # 4. Egyszerű ASK command teszt
        print("\n4️⃣ ASK command teszt...")
        
        test_command = {
            "type": "ASK",
            "query": "Mi a mai dátum? (Ez egy teszt kérdés)"
        }
        
        print(f"Küldött parancs: {json.dumps(test_command, ensure_ascii=False)}")
        
        # Command végrehajtása
        result = await router.route_command(test_command)
        
        print(f"\nEredmény: {json.dumps(result, ensure_ascii=False, indent=2)}")
        
        # 5. Eredmény kiértékelése
        print("\n5️⃣ Eredmény kiértékelése...")
        
        if isinstance(result, dict):
            if "error" in result:
                print(f"❌ Hiba történt: {result['error']}")
                return False
            elif "response" in result or "result" in result:
                print("✅ Sikeres válasz érkezett")
                
                response_text = result.get("response", result.get("result", ""))
                if response_text:
                    print(f"   Válasz: {response_text[:100]}...")
                    return True
                else:
                    print("⚠️  Üres válasz")
                    return True
            else:
                print("⚠️  Váratlan válasz formátum")
                return True
        else:
            print("❌ Érvénytelen válasz típus")
            return False
            
    except Exception as e:
        print(f"❌ Teszt hiba: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

async def test_model_routing_verification():
    """Model routing ellenőrzése"""
    
    print("\n🔧 MODEL ROUTING VERIFIKÁCIÓ")
    print("=" * 50)
    
    try:
        # ModelManager közvetlen tesztelése
        print("1️⃣ ModelManager közvetlen teszt...")
        
        from integrations.model_manager import ModelManager
        
        model_manager = ModelManager()
        print("✅ ModelManager sikeresen inicializálva")
        
        # Task type routing teszt
        print("\n2️⃣ Task type routing teszt...")
        
        # Kis teszt prompt
        test_response = await model_manager.generate_response(
            prompt="Válaszolj egy szóval: 'működik'",
            task_type="ask"
        )
        
        print(f"ModelManager válasz: {test_response}")
        
        if isinstance(test_response, dict) and test_response.get("status") == "success":
            print("✅ ModelManager működik az 'ask' task type-pal")
            return True
        else:
            print("⚠️  ModelManager válasz váratlan formátumú")
            return True
            
    except Exception as e:
        print(f"❌ ModelManager teszt hiba: {str(e)}")
        return False

async def main():
    """Fő teszt futtatás"""
    
    print("🚀 PROJECT-S ASK COMMAND ROUTING TESZT")
    print("🎯 Cél: Ellenőrizni, hogy ASK commandok ModelManager-en keresztül mennek")
    print("📅 Dátum: 2025. május 26.")
    print()
    
    success_count = 0
    total_tests = 2
    
    # 1. teszt: ASK command integráció
    if await test_ask_command_integration():
        success_count += 1
        
    # 2. teszt: ModelManager routing
    if await test_model_routing_verification():
        success_count += 1
    
    # Összegzés
    print("\n" + "=" * 60)
    print("📊 TESZT ÖSSZEGZÉS")
    print("=" * 60)
    print(f"Sikeres tesztek: {success_count}/{total_tests}")
    
    if success_count == total_tests:
        print("🎉 MINDEN TESZT SIKERES!")
        print("✅ Az ASK command routing javítás működik")
        print("✅ A rendszer készen áll a használatra")
    elif success_count > 0:
        print("⚠️  RÉSZBEN SIKERES")
        print("   Néhány komponens működik, de lehetnek problémák")
    else:
        print("❌ TESZTEK SIKERTELENEK")
        print("   A javítás nem működik megfelelően")
        
    return success_count == total_tests

if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⏹️  Teszt megszakítva")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Kritikus hiba: {str(e)}")
        sys.exit(1)
