#!/usr/bin/env python3
"""
Debug script to test workflow execution and identify why tasks don't complete
"""

import asyncio
import logging
import sys
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='[%(levelname)s] %(name)s - %(message)s')
logger = logging.getLogger(__name__)

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

async def test_model_manager_only():
    """Test model_manager.execute_task_with_model to see what it actually does"""
    print("\n" + "="*60)
    print("TESTING MODEL MANAGER EXECUTION")
    print("="*60)
    
    try:
        from integrations.model_manager import model_manager
        
        # Test with a system task that should create a file
        test_query = "Create a file called debug_test.txt with the content 'Hello World from Project-S'"
        
        print(f"\nTest Query: {test_query}")
        print("\nCalling model_manager.execute_task_with_model()...")
        
        result = await model_manager.execute_task_with_model(
            query=test_query,
            task_type="system",
            system_message="You are a helpful assistant that can execute system commands and create files."
        )
        
        print("\nResult received:")
        print(f"Result type: {type(result)}")
        print(f"Result keys: {list(result.keys()) if isinstance(result, dict) else 'Not a dict'}")
        
        if isinstance(result, dict):
            content = result.get('content', 'No content key')
            print(f"\nContent preview: {content[:300]}...")
            
            # Check if it's just text or actual tool execution
            if 'debug_test.txt' in content and 'Hello World' in content:
                print("\n❌ ISSUE CONFIRMED: Model only generated TEXT about the task, didn't execute it!")
            else:
                print("\n🤔 Content doesn't seem to address the file creation task")
                
        # Check if the file was actually created
        test_file = Path("debug_test.txt")
        if test_file.exists():
            print("\n✅ File was actually created!")
            print(f"File content: {test_file.read_text()}")
        else:
            print("\n❌ CONFIRMED: No file was created - model only generated text response!")
            
        return result
        
    except Exception as e:
        print(f"\n❌ Error testing model manager: {e}")
        logger.exception("Error in test_model_manager_only")
        return None

async def test_tool_registry_direct():
    """Test if tools can be executed directly through tool_registry"""
    print("\n" + "="*60)
    print("TESTING DIRECT TOOL EXECUTION")
    print("="*60)
    
    try:
        from tools.tool_registry import tool_registry
        
        print(f"\nAvailable tools: {list(tool_registry.tools.keys())}")
        
        # Test file write tool directly
        if 'file_write' in tool_registry.tools:
            print("\n🔄 Testing FileWriteTool directly...")
            
            result = await tool_registry.execute_tool(
                'file_write',
                path='debug_direct_test.txt',
                content='Hello from direct tool execution!'
            )
            
            print(f"Direct tool result: {result}")
            
            # Check if file was created
            test_file = Path("debug_direct_test.txt")
            if test_file.exists():
                print("✅ Direct tool execution WORKS - file was created!")
                print(f"File content: {test_file.read_text()}")
                return True
            else:
                print("❌ Direct tool execution failed")
                return False
        else:
            print("❌ file_write tool not available")
            return False
            
    except Exception as e:
        print(f"\n❌ Error testing direct tool execution: {e}")
        logger.exception("Error in test_tool_registry_direct")
        return False

async def test_workflow_vs_direct():
    """Compare workflow execution vs direct tool execution"""
    print("\n" + "="*60)
    print("WORKFLOW vs DIRECT TOOL COMPARISON")
    print("="*60)
    
    # Test 1: Model manager (workflow path)
    print("\n1. Testing workflow path (model_manager)...")
    workflow_result = await test_model_manager_only()
    
    # Test 2: Direct tool execution
    print("\n2. Testing direct tool execution...")
    direct_result = await test_tool_registry_direct()
    
    # Summary
    print("\n" + "="*60)
    print("DIAGNOSIS SUMMARY")
    print("="*60)
    
    if workflow_result and not direct_result:
        print("❌ Both workflow and direct tools are broken")
    elif not workflow_result and direct_result:
        print("✅ DIAGNOSIS CONFIRMED:")
        print("   - Direct tool execution WORKS")
        print("   - Workflow only generates TEXT responses")
        print("   - The workflow needs to be modified to call tools!")
    elif workflow_result and direct_result:
        print("🤔 Both seem to work - need deeper investigation")
    else:
        print("❌ Both failed - system configuration issue")

async def main():
    """Main test function"""
    print("Starting Project-S Workflow Execution Debugging...")
    
    # Clean up any existing test files
    for test_file in ["debug_test.txt", "debug_direct_test.txt"]:
        file_path = Path(test_file)
        if file_path.exists():
            file_path.unlink()
            print(f"Cleaned up existing {test_file}")
    
    await test_workflow_vs_direct()
    
    print("\n" + "="*60)
    print("DEBUG COMPLETE")
    print("="*60)

if __name__ == "__main__":
    asyncio.run(main())
