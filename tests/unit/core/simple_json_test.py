#!/usr/bin/env python3
"""
Simple JSON file creation test for Project-S
"""

import asyncio
import os
from integrations.model_manager import model_manager

async def simple_json_test():
    """Simple test to create a JSON file"""
    print("🧪 SIMPLE JSON FILE TEST")
    print("=" * 30)
    
    # Test: Create a simple JSON file
    query = 'create file "test_simple.json" with content {"name": "test", "value": 123}'
    print(f"📝 Query: {query}")
    
    try:
        result = await model_manager.process_user_command(query)
        print(f"📊 Result status: {result.get('status', 'unknown')}")
        print(f"📊 Full result: {result}")
        
        # Check if file was created
        if os.path.exists("test_simple.json"):
            print("✅ test_simple.json created successfully!")
            with open("test_simple.json", "r") as f:
                content = f.read()
                print(f"📄 Content: {content}")
        else:
            print("❌ test_simple.json was not created")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(simple_json_test())
