#!/usr/bin/env python3
"""
OpenRouter SDK Integráció Teszt
"""

import os
import sys

def test_openai_sdk_import():
    """OpenAI SDK elérhetőség tesztelése"""
    try:
        import openai
        print("✅ OpenAI SDK elérhető")
        return True
    except ImportError:
        print("❌ OpenAI SDK hiányzik - telepítsd: pip install openai")
        return False

def test_api_key():
    """API kulcs elérhetőség tesztelése"""
    api_key = os.environ.get("OPENROUTER_API_KEY")
    if api_key:
        print(f"✅ OpenRouter API kulcs elérhető: {api_key[:20]}...{api_key[-10:]}")
        return True
    else:
        print("❌ OpenRouter API kulcs nem található")
        return False

def test_openrouter_with_openai_sdk():
    """OpenRouter tesztelése OpenAI SDK-val"""
    if not test_openai_sdk_import():
        return False
    
    if not test_api_key():
        return False
    
    try:
        from openai import OpenAI
        
        # OpenRouter kliens létrehozása OpenAI SDK-val
        client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=os.environ.get("OPENROUTER_API_KEY")
        )
        
        print("✅ OpenRouter kliens létrehozva OpenAI SDK-val")
        
        # Teszt üzenet küldése
        response = client.chat.completions.create(
            model="qwen/qwen3-235b-a22b",
            messages=[
                {
                    "role": "user",
                    "content": "Hello! Please respond with exactly: 'OpenRouter SDK integration successful!'"
                }
            ],
            max_tokens=50,
            temperature=0.1,
            extra_headers={
                "HTTP-Referer": "https://project-s-agent.local",
                "X-Title": "Project-S Multi-AI Agent System"
            }
        )
        
        result = response.choices[0].message.content
        print(f"✅ OpenRouter válasz: {result}")
        
        # Token használat ellenőrzése
        if hasattr(response, 'usage'):
            print(f"📊 Token használat: {response.usage}")
        
        return True
        
    except Exception as e:
        print(f"❌ OpenRouter SDK teszt sikertelen: {e}")
        return False

def test_multi_model_client():
    """Project-S multi-model kliens tesztelése"""
    try:
        from integrations.multi_model_ai_client import multi_model_ai_client
        print("✅ Multi-model kliens importálva")
        
        # Elérhető modellek listázása
        models = multi_model_ai_client.list_available_models()
        print(f"✅ Elérhető modellek: {len(models)}")
        for model in models:
            print(f"   - {model['provider']}: {model['model_id']}")
        
        # Ajánlott modell lekérése
        recommended = multi_model_ai_client.get_recommended_model()
        print(f"✅ Ajánlott modell: {recommended}")
        
        # Kapcsolat tesztelése
        print("\n🧪 Kapcsolat tesztelése...")
        test_results = multi_model_ai_client.test_connection()
        
        for provider, result in test_results.items():
            status = "✅" if result["success"] else "❌"
            print(f"{status} {provider}: {result['message']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Multi-model kliens teszt sikertelen: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("🚀 OpenRouter OpenAI SDK Integráció Teszt")
    print("=" * 50)
    
    success_count = 0
    total_tests = 3
    
    print("\n1. OpenAI SDK Teszt:")
    if test_openai_sdk_import():
        success_count += 1
    
    print("\n2. Közvetlen OpenRouter SDK Teszt:")
    if test_openrouter_with_openai_sdk():
        success_count += 1
    
    print("\n3. Project-S Multi-Model Kliens Teszt:")
    if test_multi_model_client():
        success_count += 1
    
    print("\n" + "=" * 50)
    print(f"📊 Eredmény: {success_count}/{total_tests} teszt sikeres")
    
    if success_count == total_tests:
        print("🎉 Minden teszt sikeres! OpenRouter integráció működik!")
    else:
        print("⚠️ Néhány teszt sikertelen. Ellenőrizd a hibaüzeneteket.")
    
    return success_count == total_tests

if __name__ == "__main__":
    main()
