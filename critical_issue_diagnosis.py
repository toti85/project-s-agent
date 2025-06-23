#!/usr/bin/env python3
"""
PROJECT-S CRITICAL ISSUE DIAGNOSIS
Quick validation of the major problems discovered in real-world testing
"""

import time
import asyncio
from datetime import datetime

def test_api_compatibility():
    """Test the API compatibility issues found"""
    print("🔍 DIAGNOSING API COMPATIBILITY ISSUES")
    print("=" * 50)
    
    issues = []
    
    # Test 1: ToolRegistry API
    try:
        from tools.tool_registry import ToolRegistry
        registry = ToolRegistry()
        
        # Check what methods actually exist
        methods = [method for method in dir(registry) if not method.startswith('_')]
        
        if 'get_available_tools' in methods:
            print("✅ ToolRegistry.get_available_tools() - EXISTS")
        else:
            print("❌ ToolRegistry.get_available_tools() - MISSING")
            print(f"   Available methods: {methods[:5]}...")
            issues.append("ToolRegistry API mismatch")
            
    except Exception as e:
        print(f"❌ ToolRegistry import failed: {e}")
        issues.append(f"ToolRegistry import error: {e}")
    
    # Test 2: CognitiveCoreWithLangGraph API
    try:
        from core.cognitive_core_langgraph import CognitiveCoreWithLangGraph
        core = CognitiveCoreWithLangGraph()
        
        methods = [method for method in dir(core) if not method.startswith('_')]
        
        if 'process_request' in methods:
            print("✅ CognitiveCoreWithLangGraph.process_request() - EXISTS")
        else:
            print("❌ CognitiveCoreWithLangGraph.process_request() - MISSING")
            print(f"   Available methods: {methods[:5]}...")
            issues.append("CognitiveCoreWithLangGraph API mismatch")
            
    except Exception as e:
        print(f"❌ CognitiveCoreWithLangGraph import failed: {e}")
        issues.append(f"CognitiveCoreWithLangGraph error: {e}")
    
    # Test 3: EnhancedExecutionCoordinator API
    try:
        from core.enhanced_execution_coordinator import EnhancedExecutionCoordinator
        coordinator = EnhancedExecutionCoordinator()
        
        methods = [method for method in dir(coordinator) if not method.startswith('_')]
        
        if 'execute_workflow' in methods:
            print("✅ EnhancedExecutionCoordinator.execute_workflow() - EXISTS")
            
            # Check method signature
            import inspect
            sig = inspect.signature(coordinator.execute_workflow)
            params = list(sig.parameters.keys())
            print(f"   Parameters: {params}")
            
            if len(params) == 1:  # Only 'self'
                issues.append("EnhancedExecutionCoordinator.execute_workflow() missing required parameters")
        else:
            print("❌ EnhancedExecutionCoordinator.execute_workflow() - MISSING")
            issues.append("EnhancedExecutionCoordinator API mismatch")
            
    except Exception as e:
        print(f"❌ EnhancedExecutionCoordinator import failed: {e}")
        issues.append(f"EnhancedExecutionCoordinator error: {e}")
    
    return issues

async def test_simple_ai_response():
    """Test if we can get a simple AI response without timeout"""
    print("\n🤖 TESTING SIMPLE AI RESPONSE")
    print("=" * 50)
    
    try:
        from core.universal_request_processor import UniversalRequestProcessor
        processor = UniversalRequestProcessor()
        
        start_time = time.time()
        
        # Very simple request
        result = await asyncio.wait_for(
            processor.process_request({
                "type": "ASK",
                "query": "Hello"
            }),
            timeout=30  # 30 second timeout instead of 60
        )
        
        execution_time = time.time() - start_time
        
        print(f"⏱️ Execution time: {execution_time:.2f}s")
        
        if result:
            print(f"📤 Result status: {result.get('status', 'unknown')}")
            response = result.get('response', 'No response field')
            print(f"📥 Response preview: {str(response)[:100]}...")
            
            if response and response.strip():
                print("✅ AI response received")
                return True, execution_time, response
            else:
                print("❌ Empty AI response")
                return False, execution_time, "Empty response"
        else:
            print("❌ No result returned")
            return False, execution_time, "No result"
            
    except asyncio.TimeoutError:
        print("❌ Request timed out after 30 seconds")
        return False, 30, "Timeout"
    except Exception as e:
        print(f"❌ Error: {e}")
        return False, 0, str(e)

def diagnose_performance_bottleneck():
    """Try to identify what's causing the 60-second delays"""
    print("\n⚡ DIAGNOSING PERFORMANCE BOTTLENECK")
    print("=" * 50)
    
    bottlenecks = []
    
    # Test import speeds
    imports = [
        ("core.universal_request_processor", "UniversalRequestProcessor"),
        ("core.ai_command_handler", "AICommandHandler"),
        ("integrations.simplified_model_manager", "model_manager"),
        ("llm_clients.qwen_client", "QwenOllamaClient")
    ]
    
    for module, class_name in imports:
        start_time = time.time()
        try:
            exec(f"from {module} import {class_name}")
            import_time = time.time() - start_time
            print(f"📦 {module}.{class_name}: {import_time:.3f}s")
            
            if import_time > 5:
                bottlenecks.append(f"Slow import: {module} ({import_time:.1f}s)")
        except Exception as e:
            print(f"❌ Failed to import {module}.{class_name}: {e}")
            bottlenecks.append(f"Import failed: {module}")
    
    return bottlenecks

async def main():
    """Run all diagnostic tests"""
    print("🔬 PROJECT-S CRITICAL ISSUE DIAGNOSIS")
    print("=" * 60)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Test 1: API Compatibility
    api_issues = test_api_compatibility()
    
    # Test 2: Simple AI Response
    ai_success, ai_time, ai_response = await test_simple_ai_response()
    
    # Test 3: Performance Bottlenecks
    performance_issues = diagnose_performance_bottleneck()
    
    # Summary
    print("\n📋 DIAGNOSIS SUMMARY")
    print("=" * 60)
    
    print(f"🔧 API Issues Found: {len(api_issues)}")
    for issue in api_issues:
        print(f"   • {issue}")
    
    print(f"\n🤖 AI Response Test:")
    print(f"   • Success: {'✅' if ai_success else '❌'}")
    print(f"   • Time: {ai_time:.2f}s")
    print(f"   • Response: {ai_response[:50]}...")
    
    print(f"\n⚡ Performance Issues: {len(performance_issues)}")
    for issue in performance_issues:
        print(f"   • {issue}")
    
    # Recommendations
    print(f"\n🎯 IMMEDIATE ACTION ITEMS:")
    if api_issues:
        print("   1. FIX API COMPATIBILITY - Update method signatures")
    if not ai_success:
        print("   2. INVESTIGATE AI PIPELINE - Debug response generation")
    if ai_time > 30:
        print("   3. OPTIMIZE PERFORMANCE - Reduce response latency")
    if performance_issues:
        print("   4. RESOLVE BOTTLENECKS - Fix slow imports/initialization")
    
    total_issues = len(api_issues) + len(performance_issues) + (0 if ai_success else 1)
    if total_issues == 0:
        print("   🎉 No critical issues found - System may be functional")
    else:
        print(f"   ⚠️ {total_issues} critical issues need immediate attention")

if __name__ == "__main__":
    asyncio.run(main())
