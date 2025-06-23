import os
import requests
import json
import sys

# Redirect output to file and console
class Tee:
    def __init__(self, *files):
        self.files = files
    def write(self, obj):
        for f in self.files:
            f.write(obj)
            f.flush()
    def flush(self):
        for f in self.files:
            f.flush()

# Open log file
log_file = open('openrouter_test_results.txt', 'w')
original_stdout = sys.stdout
sys.stdout = Tee(sys.stdout, log_file)

try:
    print("🚀 OpenRouter API Test - " + "2025-05-25")
    print("=" * 50)
    
    # Check API key
    print("1. Checking API Key...")
    api_key = os.getenv('OPENROUTER_API_KEY')
    if not api_key:
        try:
            sys.path.append('.')
            from docs.openrouter_api_key import OPENROUTER_API_KEY
            api_key = OPENROUTER_API_KEY
            print("   ✅ API Key loaded from file")
        except Exception as e:
            print(f"   ❌ Failed to load from file: {e}")
    else:
        print("   ✅ API Key loaded from environment")
    
    if api_key:
        print(f"   🔑 Key: {api_key[:20]}...{api_key[-10:]}")
    else:
        print("   ❌ No API key found!")
        sys.exit(1)
    
    # Test API call
    print("\n2. Testing OpenRouter API...")
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "HTTP-Referer": "https://project-s-agent.local",
        "X-Title": "Project-S Multi-AI System",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": "qwen/qwen-2.5-coder-32b-instruct",
        "messages": [
            {
                "role": "user", 
                "content": "Hello! Please respond with exactly: 'OpenRouter API test successful!'"
            }
        ],
        "max_tokens": 100,
        "temperature": 0.1
    }
    
    print(f"   📡 Sending request to: {url}")
    print(f"   🤖 Using model: {data['model']}")
    
    response = requests.post(url, headers=headers, json=data, timeout=30)
    
    print(f"   📊 Status Code: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"   ✅ API call successful!")
        
        if 'choices' in result and len(result['choices']) > 0:
            message = result['choices'][0]['message']['content']
            print(f"   💬 Response: {message}")
            
            if 'usage' in result:
                usage = result['usage']
                print(f"   📈 Tokens used: {usage.get('total_tokens', 'N/A')}")
        else:
            print(f"   ⚠️  Unexpected response format")
            print(f"   📄 Raw response: {json.dumps(result, indent=2)}")
    else:
        print(f"   ❌ API call failed!")
        try:
            error_data = response.json()
            print(f"   📄 Error details: {json.dumps(error_data, indent=2)}")
        except:
            print(f"   📄 Error text: {response.text}")
    
    # Test model availability
    print("\n3. Checking model availability...")
    models_url = "https://openrouter.ai/api/v1/models"
    models_response = requests.get(models_url, headers={"Authorization": f"Bearer {api_key}"})
    
    if models_response.status_code == 200:
        models_data = models_response.json()
        qwen_models = [m for m in models_data.get('data', []) if 'qwen' in m.get('id', '').lower()]
        print(f"   ✅ Found {len(qwen_models)} Qwen models available")
        for model in qwen_models[:5]:  # Show first 5
            print(f"      - {model.get('id', 'Unknown')}")
    else:
        print(f"   ⚠️  Could not fetch models list: {models_response.status_code}")
    
    print("\n" + "=" * 50)
    print("🎯 TEST COMPLETED")
    print("Check openrouter_test_results.txt for full output")
    
except Exception as e:
    print(f"\n❌ Test failed with exception: {e}")
    import traceback
    traceback.print_exc()

finally:
    sys.stdout = original_stdout
    log_file.close()
    print("Test completed - results saved to openrouter_test_results.txt")
