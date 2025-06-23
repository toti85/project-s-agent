#!/usr/bin/env python3
"""
COMPREHENSIVE PROJECT-S REAL-WORLD CAPABILITY TEST
Tests actual functionality vs claimed 62.5% operational status
"""

import asyncio
import json
import time
from datetime import datetime
from pathlib import Path

# Test results storage
test_results = {
    "test_session": {
        "start_time": datetime.now().isoformat(),
        "system_claimed_status": "62.5% operational",
        "restoration_claimed_status": "95%+ functional"
    },
    "tests": []
}

def log_test_result(test_name, success, details, execution_time=None):
    """Log test result to results structure"""
    result = {
        "test_name": test_name,
        "success": success,
        "timestamp": datetime.now().isoformat(),
        "execution_time_seconds": execution_time,
        "details": details
    }
    test_results["tests"].append(result)
    
    status = "✅ PASS" if success else "❌ FAIL"
    print(f"{status} {test_name}")
    if execution_time:
        print(f"    ⏱️ Execution time: {execution_time:.2f}s")
    print(f"    📝 {details}")
    print()

async def test_multi_ai_routing():
    """Test 1: Multi-AI Provider Routing Capabilities"""
    print("🧪 TEST 1: MULTI-AI PROVIDER ROUTING")
    print("=" * 50)
    
    from core.universal_request_processor import UniversalRequestProcessor
    processor = UniversalRequestProcessor()
    
    test_requests = [
        {
            "type": "reasoning",
            "query": "Explain quantum computing in simple terms",
            "expected_ai": "reasoning AI (Claude Opus)"
        },
        {
            "type": "coding", 
            "query": "Write a Python function to sort a list using quicksort",
            "expected_ai": "coding AI (CodeLlama)"
        },
        {
            "type": "creative",
            "query": "Write a haiku about artificial intelligence",
            "expected_ai": "creative AI (Claude Sonnet)"
        },
        {
            "type": "calculation",
            "query": "What is 847293 * 652847?",
            "expected_ai": "fast AI (Llama3)"
        }    ]
    
    results = []
    for i, request in enumerate(test_requests):
        start_time = time.time()
        try:
            result = await processor.process_request({
                "type": "ASK",
                "query": request["query"]
            })
            execution_time = time.time() - start_time
            
            success = result and result.get("status") == "success"
            # Get response from the correct location in the result structure
            if result and "execution_result" in result and "content" in result["execution_result"]:
                response = result["execution_result"]["content"]
            else:
                response = result.get("response", "No response") if result else "No result"
            
            log_test_result(
                f"Multi-AI Request {i+1} ({request['type']})",
                success,
                f"Expected: {request['expected_ai']}, Response: {response[:100]}...",
                execution_time
            )
            
            results.append({
                "request_type": request["type"],
                "success": success,
                "execution_time": execution_time,
                "response_preview": response[:200] if response else None
            })
            
        except Exception as e:
            execution_time = time.time() - start_time
            log_test_result(
                f"Multi-AI Request {i+1} ({request['type']})",
                False,
                f"Error: {str(e)}",
                execution_time
            )
            results.append({
                "request_type": request["type"], 
                "success": False,
                "error": str(e),
                "execution_time": execution_time
            })
    
    return results

async def test_tool_orchestration():
    """Test 2: Tool Orchestration (13 Tools)"""
    print("🧪 TEST 2: TOOL ORCHESTRATION")
    print("=" * 50)
    
    try:
        from tools.tool_registry import tool_registry  # Use singleton instance
        from tools import register_all_tools
        
        # Register tools first
        await register_all_tools()
        
        # Test tool availability
        available_tools = tool_registry.get_available_tools()
        tool_count = len(available_tools)
        
        log_test_result(
            "Tool Registry Initialization",
            tool_count > 0,
            f"Available tools: {tool_count}, Tools: {list(available_tools.keys())[:5]}..."
        )
        
        # Test complex automation scenario
        from core.universal_request_processor import UniversalRequestProcessor
        processor = UniversalRequestProcessor()
        
        start_time = time.time()
        result = await processor.process_request({
            "type": "WORKFLOW",
            "query": "Find all Python files in the current directory, analyze their structure, and create a summary report"
        })
        execution_time = time.time() - start_time
        
        success = result and result.get("status") == "success"
        log_test_result(
            "Complex Tool Automation",
            success,
            f"Multi-tool workflow result: {str(result)[:200]}...",
            execution_time
        )
        
        return {
            "tool_count": tool_count,
            "available_tools": list(available_tools.keys()) if available_tools else [],
            "complex_workflow_success": success,
            "workflow_execution_time": execution_time
        }
        
    except Exception as e:
        log_test_result(
            "Tool Orchestration Test",
            False,
            f"Error: {str(e)}"
        )
        return {"error": str(e)}

async def test_langgraph_state_management():
    """Test 3: LangGraph State Management (46 Sessions)"""
    print("🧪 TEST 3: LANGGRAPH STATE MANAGEMENT")
    print("=" * 50)
    
    try:
        from integrations.persistent_state_manager import PersistentStateManager
        from core.cognitive_core_langgraph import CognitiveCoreWithLangGraph
        
        # Test state manager
        state_manager = PersistentStateManager()
        active_sessions = getattr(state_manager, 'active_sessions', {})
        session_count = len(active_sessions)
        
        log_test_result(
            "LangGraph State Manager",
            session_count > 0,
            f"Active sessions: {session_count}, Expected: 46"
        )
        
        # Test cognitive core with state
        cognitive_core = CognitiveCoreWithLangGraph()
        
        # Test conversational workflow with state
        conversation_steps = [
            "Start analyzing this project structure",
            "What are the main components you found?", 
            "Which component has the most dependencies?",
            "Create a refactoring plan for that component"
        ]
        
        conversation_results = []
        for i, step in enumerate(conversation_steps):
            start_time = time.time()
            try:
                result = await cognitive_core.process_request({
                    "query": step,
                    "conversation_id": "test_conversation_001"
                })
                execution_time = time.time() - start_time
                
                # Check for proper success status (can be 'success' or 'completed')
                success = (result and 
                          isinstance(result, dict) and 
                          result.get("status") in ["success", "completed"])
                conversation_results.append({
                    "step": i+1,
                    "success": success,
                    "execution_time": execution_time
                })
                
                log_test_result(
                    f"Conversational Step {i+1}",
                    success,
                    f"State-aware response: {str(result)[:100]}...",
                    execution_time
                )
                
            except Exception as e:
                execution_time = time.time() - start_time
                log_test_result(
                    f"Conversational Step {i+1}",
                    False,
                    f"Error: {str(e)}",
                    execution_time
                )
                conversation_results.append({
                    "step": i+1,
                    "success": False,
                    "error": str(e),
                    "execution_time": execution_time
                })
        
        return {
            "session_count": session_count,
            "conversation_results": conversation_results,
            "state_preservation": any(r["success"] for r in conversation_results)
        }
        
    except Exception as e:
        log_test_result(
            "LangGraph State Management",
            False,
            f"Error: {str(e)}"
        )
        return {"error": str(e)}

async def test_multi_step_workflow():
    """Test 4: Multi-Step Workflow Automation"""
    print("🧪 TEST 4: MULTI-STEP WORKFLOW AUTOMATION")
    print("=" * 50)
    
    try:
        from core.enhanced_execution_coordinator import EnhancedExecutionCoordinator
        coordinator = EnhancedExecutionCoordinator()
        
        # Complex development setup scenario
        workflow_definition = {
            "name": "development_environment_setup",
            "description": "Set up a complete Python development environment",
            "steps": [
                {
                    "id": "create_directory",
                    "action": "create_project_directory",
                    "params": {"name": "test_project"}
                },
                {
                    "id": "init_git",
                    "action": "initialize_git_repository",
                    "depends_on": ["create_directory"]
                },
                {
                    "id": "create_venv",
                    "action": "create_virtual_environment", 
                    "depends_on": ["create_directory"]
                },
                {
                    "id": "install_packages",
                    "action": "install_common_packages",
                    "depends_on": ["create_venv"],
                    "params": {"packages": ["requests", "pytest", "black"]}
                },
                {
                    "id": "create_structure",
                    "action": "create_project_structure",
                    "depends_on": ["create_directory"]
                },
                {
                    "id": "init_readme",
                    "action": "create_readme_file",
                    "depends_on": ["create_directory"]
                }
            ]        }
        
        start_time = time.time()
        result = await coordinator.execute_workflow(
            workflow_id=workflow_definition["name"],
            steps=workflow_definition["steps"],
            context={"description": workflow_definition["description"]}
        )
        execution_time = time.time() - start_time
        
        success = result and result.get("status") == "success"
        completed_steps = result.get("completed_steps", []) if result else []
        
        log_test_result(
            "Multi-Step Development Setup",
            success,
            f"Completed {len(completed_steps)}/6 steps. Result: {str(result)[:200]}...",
            execution_time
        )
        
        return {
            "workflow_success": success,
            "completed_steps": len(completed_steps),
            "total_steps": 6,
            "execution_time": execution_time,
            "step_details": completed_steps
        }
        
    except Exception as e:
        log_test_result(
            "Multi-Step Workflow",
            False,
            f"Error: {str(e)}"
        )
        return {"error": str(e)}

async def test_performance_under_load():
    """Test 5: Performance Under Load"""
    print("🧪 TEST 5: PERFORMANCE UNDER LOAD")
    print("=" * 50)
    
    try:
        from core.universal_request_processor import UniversalRequestProcessor
        processor = UniversalRequestProcessor()
        
        # Concurrent request test
        concurrent_requests = [
            {"type": "ASK", "query": f"Simple calculation: {i} * {i+1}"} 
            for i in range(5)
        ]
        
        start_time = time.time()
        
        # Execute requests concurrently
        tasks = [processor.process_request(req) for req in concurrent_requests]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        execution_time = time.time() - start_time
        
        successful_results = [r for r in results if not isinstance(r, Exception) and r and r.get("status") == "success"]
        success_rate = len(successful_results) / len(concurrent_requests)
        
        log_test_result(
            "Concurrent Request Processing",
            success_rate >= 0.8,
            f"Success rate: {success_rate:.1%} ({len(successful_results)}/{len(concurrent_requests)})",
            execution_time
        )
        
        # Average response time test
        individual_times = []
        for i in range(3):
            start = time.time()
            result = await processor.process_request({
                "type": "ASK", 
                "query": "What is machine learning?"
            })
            individual_times.append(time.time() - start)
        
        avg_response_time = sum(individual_times) / len(individual_times)
        fast_enough = avg_response_time < 30  # Under 30 seconds
        
        log_test_result(
            "Average Response Time",
            fast_enough,
            f"Average: {avg_response_time:.2f}s (target: <30s)",
            avg_response_time
        )
        
        return {
            "concurrent_success_rate": success_rate,
            "concurrent_execution_time": execution_time,
            "average_response_time": avg_response_time,
            "performance_acceptable": success_rate >= 0.8 and avg_response_time < 30
        }
        
    except Exception as e:
        log_test_result(
            "Performance Under Load",
            False,
            f"Error: {str(e)}"
        )
        return {"error": str(e)}

async def run_comprehensive_tests():
    """Run all comprehensive tests and generate report"""
    print("🚀 COMPREHENSIVE PROJECT-S REAL-WORLD CAPABILITY TEST")
    print("=" * 60)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"System Claims: 62.5% operational, 95%+ functional after restoration")
    print()
    
    # Run all tests
    test_functions = [
        ("Multi-AI Provider Routing", test_multi_ai_routing),
        ("Tool Orchestration", test_tool_orchestration), 
        ("LangGraph State Management", test_langgraph_state_management),
        ("Multi-Step Workflow", test_multi_step_workflow),
        ("Performance Under Load", test_performance_under_load)
    ]
    
    detailed_results = {}
    
    for test_name, test_func in test_functions:
        print(f"🧪 Running: {test_name}")
        try:
            start_time = time.time()
            result = await test_func()
            execution_time = time.time() - start_time
            detailed_results[test_name] = {
                "result": result,
                "execution_time": execution_time
            }
        except Exception as e:
            print(f"❌ Test {test_name} crashed: {e}")
            detailed_results[test_name] = {
                "error": str(e),
                "execution_time": 0
            }
        print()
    
    # Calculate overall results
    total_tests = len(test_results["tests"])
    passed_tests = sum(1 for test in test_results["tests"] if test["success"])
    success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
    
    # Generate comprehensive report
    test_results["summary"] = {
        "total_tests": total_tests,
        "passed_tests": passed_tests,
        "failed_tests": total_tests - passed_tests,
        "success_rate_percent": success_rate,
        "detailed_results": detailed_results,
        "end_time": datetime.now().isoformat()
    }
    
    # Save results
    with open("REAL_validation_results.json", "w") as f:
        json.dump(test_results, f, indent=2)
    
    # Print final report
    print("📊 FINAL VALIDATION REPORT")
    print("=" * 60)
    print(f"📈 Overall Success Rate: {success_rate:.1f}% ({passed_tests}/{total_tests})")
    print(f"📋 System Claims vs Reality:")
    print(f"   • Claimed: 62.5% operational")
    print(f"   • Claimed: 95%+ functional (after restoration)")
    print(f"   • Actual Test Results: {success_rate:.1f}% functional")
    
    if success_rate >= 95:
        print("🎉 VERDICT: Claims validated - System is highly functional")
    elif success_rate >= 62.5:
        print("✅ VERDICT: Claims partially validated - System meets baseline")
    elif success_rate >= 40:
        print("⚠️ VERDICT: Claims overstated - System has significant issues")
    else:
        print("❌ VERDICT: Claims false - System largely non-functional")
    
    print(f"\n💾 Detailed results saved to: REAL_validation_results.json")
    
    return test_results

if __name__ == "__main__":
    asyncio.run(run_comprehensive_tests())
