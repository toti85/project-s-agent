#!/usr/bin/env python3
"""
Debug AI response pipeline - mi történik a Qwen3 választal?
"""
import asyncio
import logging
import sys
import os

# Add the parent directory to sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

async def debug_ai_response():
    print("🔍 DEBUG: AI Response Pipeline")
    
    try:
        from integrations.multi_model_ai_client import multi_model_ai_client
        
        print("1. Multi-model AI client loaded")
        
        # Test direct call
        response = await multi_model_ai_client.generate_response(
            prompt="Hello, test response",
            model="qwen3-235b",
            task_type="general"
        )
        
        print(f"2. AI Response: {type(response)}")
        print(f"3. AI Content: {response}")
        print(f"4. AI Length: {len(response) if response else 'None'}")
          # Test through model manager
        from integrations.simplified_model_manager import model_manager
        
        result = await model_manager.execute_task_with_core_system("Hello test")
        
        print(f"5. Model manager result: {type(result)}")
        print(f"6. Result keys: {result.keys() if isinstance(result, dict) else 'Not dict'}")
        print(f"7. Result content: {result}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(debug_ai_response())
