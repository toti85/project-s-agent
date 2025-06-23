#!/usr/bin/env python3
"""
Test OpenRouter Integration with New API Key
Tests the complete OpenRouter integration for Project-S with Qwen models
"""

import os
import sys
import requests
import json
from typing import Dict, Any, Optional

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_api_key_loading():
    """Test API key loading from multiple sources"""
    print("🔑 Testing API Key Loading...")
    
    # Test environment variable
    env_key = os.getenv('OPENROUTER_API_KEY')
    print(f"Environment Variable: {'✅ Found' if env_key else '❌ Not found'}")
    
    # Test file loading
    try:
        from docs.openrouter_api_key import OPENROUTER_API_KEY
        file_key = OPENROUTER_API_KEY
        print(f"File Loading: {'✅ Found' if file_key else '❌ Not found'}")
    except ImportError as e:
        print(f"File Loading: ❌ Import error: {e}")
        file_key = None
    
    # Determine which key to use
    api_key = env_key or file_key
    if api_key:
        print(f"✅ Using API Key: {api_key[:20]}...{api_key[-10:]}")
        return api_key
    else:
        print("❌ No API key found!")
        return None

def test_openrouter_direct_api(api_key: str):
    """Test direct OpenRouter API call"""
    print("\n🌐 Testing Direct OpenRouter API...")
    
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "HTTP-Referer": "https://project-s-agent.local",
        "X-Title": "Project-S Multi-AI Agent System",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": "qwen/qwen-2.5-coder-32b-instruct",
        "messages": [
            {
                "role": "user", 
                "content": "Hello! Can you confirm you're working? Please respond with exactly: 'OpenRouter Qwen integration successful!'"
            }
        ],
        "max_tokens": 100,
        "temperature": 0.1
    }
    
    try:
        print(f"Sending request to: {url}")
        print(f"Model: {data['model']}")
        
        response = requests.post(url, headers=headers, json=data, timeout=30)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            result = response.json()
            if 'choices' in result and len(result['choices']) > 0:
                message = result['choices'][0]['message']['content']
                print(f"✅ API Response: {message}")
                
                # Check usage info
                if 'usage' in result:
                    usage = result['usage']
                    print(f"📊 Token Usage: {usage}")
                
                return True
            else:
                print(f"❌ Unexpected response format: {result}")
                return False
        else:
            print(f"❌ API Error: {response.status_code}")
            try:
                error_detail = response.json()
                print(f"Error Details: {json.dumps(error_detail, indent=2)}")
            except:
                print(f"Error Text: {response.text}")
            return False
    
    except requests.exceptions.Timeout:
        print("❌ Request timeout (30s)")
        return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Request error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_openrouter_client():
    """Test our OpenRouter client implementation"""
    print("\n🤖 Testing OpenRouter Client...")
    
    try:
        from llm_clients.openrouter_client import OpenRouterClient
        
        client = OpenRouterClient()
        print("✅ Client initialized successfully")
        
        # Test a simple completion
        response = client.generate_completion(
            prompt="Hello! Please respond with exactly: 'Project-S OpenRouter client working!'",
            max_tokens=50,
            temperature=0.1
        )
        
        if response:
            print(f"✅ Client Response: {response}")
            return True
        else:
            print("❌ Client returned empty response")
            return False
            
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Client error: {e}")
        return False

def test_multi_model_integration():
    """Test integration with multi-model AI system"""
    print("\n🧠 Testing Multi-Model AI Integration...")
    
    try:
        from integrations.multi_model_ai_client import MultiModelAIClient
        
        client = MultiModelAIClient()
        print("✅ Multi-model client initialized")
        
        # Test OpenRouter specifically
        response = client.generate_response(
            prompt="Test OpenRouter integration. Respond with: 'Multi-model OpenRouter integration successful!'",
            provider="openrouter",
            max_tokens=50
        )
        
        if response:
            print(f"✅ Multi-model Response: {response}")
            return True
        else:
            print("❌ Multi-model returned empty response")
            return False
            
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Multi-model error: {e}")
        return False

def main():
    """Run comprehensive OpenRouter integration tests"""
    print("🚀 Project-S OpenRouter Integration Test")
    print("=" * 50)
    
    # Test 1: API Key Loading
    api_key = test_api_key_loading()
    if not api_key:
        print("\n❌ Cannot proceed without API key!")
        return False
    
    # Test 2: Direct API Call
    direct_api_success = test_openrouter_direct_api(api_key)
    
    # Test 3: OpenRouter Client
    client_success = test_openrouter_client()
    
    # Test 4: Multi-Model Integration
    multi_model_success = test_multi_model_integration()
    
    # Results Summary
    print("\n" + "=" * 50)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 50)
    print(f"API Key Loading:      {'✅ PASS' if api_key else '❌ FAIL'}")
    print(f"Direct API Call:      {'✅ PASS' if direct_api_success else '❌ FAIL'}")
    print(f"OpenRouter Client:    {'✅ PASS' if client_success else '❌ FAIL'}")
    print(f"Multi-Model System:   {'✅ PASS' if multi_model_success else '❌ FAIL'}")
    
    overall_success = all([api_key, direct_api_success, client_success, multi_model_success])
    print(f"\n🎯 OVERALL RESULT:    {'✅ ALL TESTS PASSED' if overall_success else '❌ SOME TESTS FAILED'}")
    
    if overall_success:
        print("\n🎉 OpenRouter integration is fully functional!")
        print("The system is ready to use Qwen models as the primary AI controller.")
    else:
        print("\n⚠️  Some tests failed. Check the error messages above.")
    
    return overall_success

if __name__ == "__main__":
    main()
