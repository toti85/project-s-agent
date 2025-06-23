#!/usr/bin/env python3
"""
Enhanced OpenRouter test script with proper message format
Run this after you get your new API key
"""
import os
import asyncio
import httpx
from docs.openrouter_api_key import OPENROUTER_API_KEY

async def test_openrouter_direct():
    """Test OpenRouter API directly with proper message format"""
    
    # Try environment variable first, then file
    api_key = os.environ.get("OPENROUTER_API_KEY", OPENROUTER_API_KEY)
    
    if not api_key:
        print("❌ No API key found!")
        return
    
    print(f"🔑 API Key: {api_key[:10]}...")
    
    # Proper OpenRouter message format
    payload = {
        "model": "qwen/qwen-72b-chat",  # Updated model name
        "messages": [
            {
                "role": "user", 
                "content": "What is the capital of France? Please answer in one sentence."
            }
        ],
        "temperature": 0.7,
        "max_tokens": 100
    }
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://project-s-agent.local",  # OpenRouter requires this
        "X-Title": "Project-S Multi-Model AI System"  # Optional but good practice
    }
    
    async with httpx.AsyncClient() as client:
        try:
            print("🚀 Making request to OpenRouter...")
            response = await client.post(
                "https://openrouter.ai/api/v1/chat/completions", 
                json=payload, 
                headers=headers, 
                timeout=30
            )
            
            print(f"📊 Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                if "choices" in data and data["choices"]:
                    message = data["choices"][0]["message"]["content"]
                    print(f"✅ Success! Response: {message}")
                else:
                    print(f"⚠️ Unexpected response format: {data}")
            else:
                print(f"❌ Error: {response.status_code}")
                print(f"Response: {response.text}")
                
        except Exception as e:
            print(f"❌ Exception: {e}")

async def test_available_models():
    """Test which models are available"""
    api_key = os.environ.get("OPENROUTER_API_KEY", OPENROUTER_API_KEY)
    
    if not api_key:
        print("❌ No API key for model check")
        return
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                "https://openrouter.ai/api/v1/models",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                models = response.json()
                qwen_models = [m for m in models.get("data", []) if "qwen" in m.get("id", "").lower()]
                print(f"🤖 Available Qwen models: {len(qwen_models)}")
                for model in qwen_models[:5]:  # Show first 5
                    print(f"  - {model.get('id', 'Unknown')}")
            else:
                print(f"❌ Model list error: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Model check exception: {e}")

if __name__ == "__main__":
    print("🧪 Testing OpenRouter with new API key format...")
    asyncio.run(test_available_models())
    asyncio.run(test_openrouter_direct())
