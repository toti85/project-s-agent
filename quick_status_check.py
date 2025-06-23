#!/usr/bin/env python3
"""
Quick verification that the CMD system is still working 100%
"""

import sys
from pathlib import Path
import json

# Add project root to path
project_root = Path(__file__).parent.absolute()
sys.path.insert(0, str(project_root))

def test_cmd_system():
    """Test the proven CMD system"""
    print("🧪 Testing CMD System (Known Working)...")
    
    try:
        # Import the main components
        from core.ai_command_handler import ai_handler
        print("   ✅ AI Command Handler imported")
        
        # Test basic command processing
        test_command = {
            "type": "ASK",
            "command": "What is the current time?"
        }
        
        print(f"   🔄 Testing command: {test_command['command']}")
        
        # This should work since CMD system is 100% functional
        import asyncio
        
        async def run_test():
            result = await ai_handler.process_json_command(json.dumps(test_command))
            return result
        
        result = asyncio.run(run_test())
        print(f"   ✅ CMD System Response: {result}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ CMD System Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 Project-S Quick Status Check")
    print("="*50)
    
    cmd_working = test_cmd_system()
    
    print("\n📊 STATUS SUMMARY:")
    print(f"   CMD System: {'✅ WORKING' if cmd_working else '❌ ISSUES'}")
    print(f"   LangGraph: ⏳ Installation in progress")
    print(f"   Autonomous: ⏳ Waiting for LangGraph")
    
    if cmd_working:
        print("\n🎉 GOOD NEWS: Core CMD functionality is preserved!")
        print("   You can still use the CLI system while we resolve LangGraph.")
    
    print("="*50)
