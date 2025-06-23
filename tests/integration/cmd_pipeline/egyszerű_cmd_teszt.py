#!/usr/bin/env python3
"""
EGYSZERŰ CMD TESZT - Közvetlen debug
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

async def egyszerű_cmd_teszt():
    """Egyszerű debug CMD teszt"""
    print("🔧 EGYSZERŰ CMD TESZT DEBUG")
    print("=" * 40)
    
    try:
        from integrations.model_manager import ModelManager
        mm = ModelManager()
        print("✅ ModelManager loaded")
        
        # Egyszerű CMD parancs
        test_cmd = "list files in current directory"
        print(f"\n📝 Test command: {test_cmd}")
        
        # Filename extraction check
        filename = mm._extract_filename_from_query(test_cmd)
        print(f"📁 Extracted filename: {filename}")
        
        # Execute
        print("\n🚀 Executing command...")
        result = await mm.execute_task_with_core_system(test_cmd)
        
        print(f"\n📊 RESULT:")
        print(f"Status: {result.get('status', 'UNKNOWN')}")
        print(f"Command Type: {result.get('command_type', 'NONE')}")
        print(f"Command Action: {result.get('command_action', 'NONE')}")
        
        if 'execution_result' in result:
            exec_res = result['execution_result']
            print(f"\nExecution Result:")
            print(f"  Status: {exec_res.get('status', 'UNKNOWN')}")
            if 'output' in exec_res:
                print(f"  Output: {str(exec_res['output'])[:200]}...")
            if 'command' in exec_res:
                print(f"  Executed: {exec_res['command']}")
        
        if result.get('status') == 'success':
            print("\n✅ CMD TEST SUCCESSFUL!")
        else:
            print("\n⚠️ CMD TEST HAD ISSUES")
            
        return result
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    result = asyncio.run(egyszerű_cmd_teszt())
    if result:
        print(f"\n🎯 Final status: {result.get('status')}")
    else:
        print("\n❌ Test failed completely")
