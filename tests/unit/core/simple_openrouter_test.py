import os
import requests
import json

print("🚀 Simple OpenRouter API Test")
print("=" * 40)

# Get API key
api_key = os.getenv('OPENROUTER_API_KEY')
if not api_key:
    try:
        from docs.openrouter_api_key import OPENROUTER_API_KEY
        api_key = OPENROUTER_API_KEY
    except:
        pass

if api_key:
    print(f"✅ API Key found: {api_key[:20]}...{api_key[-10:]}")
else:
    print("❌ No API key found!")
    exit(1)

# Test API call
print("\n🌐 Testing OpenRouter API...")
url = "https://openrouter.ai/api/v1/chat/completions"
headers = {
    "Authorization": f"Bearer {api_key}",
    "HTTP-Referer": "https://project-s-agent.local",
    "X-Title": "Project-S",
    "Content-Type": "application/json"
}

data = {
    "model": "qwen/qwen-2.5-coder-32b-instruct",
    "messages": [{"role": "user", "content": "Say 'Hello from OpenRouter!'"}],
    "max_tokens": 50
}

try:
    response = requests.post(url, headers=headers, json=data, timeout=30)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        message = result['choices'][0]['message']['content']
        print(f"✅ Response: {message}")
    else:
        print(f"❌ Error: {response.text}")
        
except Exception as e:
    print(f"❌ Exception: {e}")
