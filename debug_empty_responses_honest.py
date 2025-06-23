#!/usr/bin/env python3
"""
HONEST AI RESPONSE DEBUGGING
No fake success stories - debug the actual empty response issue
"""
import asyncio
from core.universal_request_processor import UniversalRequestProcessor

async def debug_empty_responses():
    print("🔧 DEBUGGING EMPTY AI RESPONSES - HONEST VERSION")
    print("=" * 60)
    
    try:
        processor = UniversalRequestProcessor()
        
        print("1. Testing basic AI request...")
        result = await processor.process_request({
            "type": "ASK",
            "query": "What is 2+2?"
        })
        
        print(f"Raw result type: {type(result)}")
        print(f"Raw result: {result}")
        print()
        
        if result:
            response = result.get("response", "NO RESPONSE KEY")
            print(f"Response field: '{response}'")
            print(f"Response length: {len(str(response))}")
            print(f"Response is empty: {not response or response.strip() == ''}")
        else:
            print("❌ Result is None/False")
            
    except Exception as e:
        print(f"❌ Error during debugging: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(debug_empty_responses())
