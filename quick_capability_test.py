#!/usr/bin/env python3
"""
Quick PROJECT-S capability test with fixes
"""

import asyncio
import time
from datetime import datetime

async def quick_capability_test():
    print("🚀 QUICK PROJECT-S CAPABILITY TEST (POST-FIX)")
    print("="*60)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    results = []
    
    # Test 1: Basic AI Response
    print("🧪 Test 1: Basic AI Response")
    try:
        from core.universal_request_processor import UniversalRequestProcessor
        processor = UniversalRequestProcessor()
        
        start_time = time.time()
        result = await processor.process_request({
            "type": "ASK",
            "query": "What is 2+2?"
        })
        execution_time = time.time() - start_time
        
        success = result and result.get("status") == "success"
        response = result.get("response", "") if result else ""
        
        print(f"   ✅ Success: {success}")
        print(f"   ⏱️ Time: {execution_time:.2f}s") 
        print(f"   📝 Response: {response[:100]}...")
        results.append(("Basic AI Response", success, execution_time))
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        results.append(("Basic AI Response", False, 0))
    
    print()
      # Test 2: Tool Registry Access    print("🧪 Test 2: Tool Registry Access")
    try:
        from tools.tool_registry import tool_registry  # Use singleton instance
        from tools import register_all_tools
        import asyncio
        
        # Register tools first in the singleton instance
        await register_all_tools()
        
        available_tools = tool_registry.get_available_tools()
        tool_count = len(available_tools)
        
        success = tool_count > 0
        print(f"   ✅ Success: {success}")
        print(f"   🔧 Tool count: {tool_count}")
        print(f"   📋 Tools: {list(available_tools.keys())[:3]}...")
        results.append(("Tool Registry Access", success, 0))
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        results.append(("Tool Registry Access", False, 0))
    
    print()
    
    # Test 3: Cognitive Core Process Request
    print("🧪 Test 3: Cognitive Core Process Request")
    try:
        from core.cognitive_core_langgraph import CognitiveCoreWithLangGraph
        core = CognitiveCoreWithLangGraph()
        
        start_time = time.time()
        result = await core.process_request({
            "query": "Test cognitive processing",
            "conversation_id": "test_001"
        })
        execution_time = time.time() - start_time
        
        success = result and result.get("status") == "success"
        print(f"   ✅ Success: {success}")
        print(f"   ⏱️ Time: {execution_time:.2f}s")
        print(f"   📝 Response type: {type(result)}")
        results.append(("Cognitive Core Process", success, execution_time))
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        results.append(("Cognitive Core Process", False, 0))
    
    print()
    
    # Test 4: Multi-Step Workflow
    print("🧪 Test 4: Multi-Step Workflow")
    try:
        from core.enhanced_execution_coordinator import EnhancedExecutionCoordinator
        coordinator = EnhancedExecutionCoordinator()
        
        workflow_steps = [
            {"id": "step1", "action": "test_action_1"},
            {"id": "step2", "action": "test_action_2", "depends_on": ["step1"]}
        ]
        
        start_time = time.time()
        result = await coordinator.execute_workflow("test_workflow", workflow_steps, {})
        execution_time = time.time() - start_time
        
        success = result and result.get("status") == "success"
        print(f"   ✅ Success: {success}")
        print(f"   ⏱️ Time: {execution_time:.2f}s")
        print(f"   📝 Result: {str(result)[:100]}...")
        results.append(("Multi-Step Workflow", success, execution_time))
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        results.append(("Multi-Step Workflow", False, 0))
    
    print()
    
    # Summary
    print("📊 QUICK TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for _, success, _ in results if success)
    total = len(results)
    success_rate = (passed / total * 100) if total > 0 else 0
    
    for test_name, success, exec_time in results:
        status = "✅ PASS" if success else "❌ FAIL"
        time_str = f"({exec_time:.2f}s)" if exec_time > 0 else ""
        print(f"   {status} {test_name} {time_str}")
    
    print(f"\n🎯 QUICK TEST RESULTS:")
    print(f"   Success Rate: {success_rate:.1f}% ({passed}/{total})")
    
    if success_rate >= 75:
        print("   🎉 SYSTEM IS FUNCTIONAL!")
    elif success_rate >= 50:
        print("   ⚠️ System partially functional")
    else:
        print("   ❌ System needs more work")
    
    return success_rate

if __name__ == "__main__":
    asyncio.run(quick_capability_test())
