#!/usr/bin/env python3
"""
AI Response debugging - Check why responses are empty
"""

import asyncio
import json

async def debug_ai_response():
    print("🔍 DEBUGGING AI RESPONSE PIPELINE")
    print("="*50)
    
    # Test 1: Direct AI handler test
    try:
        from core.ai_command_handler import AICommandHandler
        handler = AICommandHandler()
        
        result = await handler.handle_ask_command({
            "query": "Hello, please respond with 'Hello back!'"
        })
        
        print(f"📤 AI Handler Result: {result}")
        print(f"📥 Result type: {type(result)}")
        if result:
            print(f"📝 Result keys: {list(result.keys()) if isinstance(result, dict) else 'Not a dict'}")
            response = result.get('response') if isinstance(result, dict) else None
            print(f"📄 Response content: '{response}'")
            
    except Exception as e:
        print(f"❌ AI Handler error: {e}")
    
    print("\n" + "="*50)
    
    # Test 2: Direct model manager test  
    try:
        from integrations.simplified_model_manager import model_manager
        
        result = await model_manager.execute_task_with_core_system("Hello, please respond with 'Hello back!'")
        
        print(f"📤 Model Manager Result: {result}")
        print(f"📥 Result type: {type(result)}")
        if result:
            print(f"📝 Result keys: {list(result.keys()) if isinstance(result, dict) else 'Not a dict'}")
            
    except Exception as e:
        print(f"❌ Model Manager error: {e}")
    
    print("\n" + "="*50)
    
    # Test 3: Direct Qwen client test
    try:
        from llm_clients.qwen_client import QwenOllamaClient
        client = QwenOllamaClient()
        
        result = await client.ask("Hello, please respond with 'Hello back!'")
        
        print(f"📤 Qwen Client Result: {result}")
        print(f"📥 Result type: {type(result)}")
        print(f"📄 Response length: {len(str(result)) if result else 0}")
        
    except Exception as e:
        print(f"❌ Qwen Client error: {e}")

if __name__ == "__main__":
    asyncio.run(debug_ai_response())
