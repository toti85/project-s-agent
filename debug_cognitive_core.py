#!/usr/bin/env python3
"""
Debug cognitive core response
"""
import asyncio
from core.cognitive_core_langgraph import CognitiveCoreWithLangGraph

async def debug_cognitive_core():
    print("🧪 Debugging Cognitive Core Response")
    
    try:
        core = CognitiveCoreWithLangGraph()
        
        result = await core.process_request({
            "query": "Test cognitive processing",
            "conversation_id": "test_001"
        })
        
        print(f"Result type: {type(result)}")
        print(f"Result content: {result}")
        print(f"Has 'status' key: {'status' in result if isinstance(result, dict) else False}")
        if isinstance(result, dict) and 'status' in result:
            print(f"Status value: {result['status']}")
            print(f"Status == 'success': {result['status'] == 'success'}")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(debug_cognitive_core())
