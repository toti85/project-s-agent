#!/usr/bin/env python3
"""
Quick ASK Command Test
Simple test to verify ASK routing works
"""

import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

async def quick_ask_test():
    print("🚀 Quick ASK Command Test")
    print("-" * 40)
    
    try:
        from core.ai_command_handler import AICommandHandler
        
        handler = AICommandHandler()
        
        # Check ModelManager
        if hasattr(handler, 'model_manager'):
            print("✅ Using ModelManager")
        else:
            print("❌ Using fallback")
            
        # Simple test
        command = {"query": "What is 1+1?"}
        print(f"Query: {command['query']}")
        
        result = await handler.handle_ask_command(command)
        print(f"Result: {result}")
        
        if result.get("status") == "success":
            print("✅ SUCCESS!")
        else:
            print("❌ FAILED!")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(quick_ask_test())
