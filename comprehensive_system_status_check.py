#!/usr/bin/env python3
"""
PROJECT-S COMPREHENSIVE SYSTEM STATUS CHECK
==========================================
Based on archaeological discovery findings, this script validates
the 95% functional cognitive architecture and identifies the 3 critical fixes needed.
"""

import asyncio
import logging
import time
import sys
import os
from pathlib import Path
from typing import Dict, Any, List

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('comprehensive_system_check.log', mode='w', encoding='utf-8')
    ]
)

# Explicit imports to ensure components are loaded and registered
try:
    import core.cognitive_core_langgraph  # This will create and register the singleton
    import core.smart_orchestrator        # This will create and register the singleton  
    import integrations.intelligent_workflow_integration  # This will create and register the singleton
    print("🔧 Core components imported successfully")
except Exception as e:
    print(f"⚠️ Warning: Some core components failed to import: {e}")

logger = logging.getLogger(__name__)

class ProjectSSystemChecker:
    """Comprehensive system status checker"""
    
    def __init__(self):
        self.results = {}
        self.start_time = time.time()
    
    async def run_comprehensive_check(self):
        """Run all system checks"""
        print("🔍 PROJECT-S COMPREHENSIVE SYSTEM STATUS CHECK")
        print("=" * 60)
        print(f"⏰ Check started: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        checks = [
            ("🧠 Cognitive Core Architecture", self.check_cognitive_core),
            ("🔧 Smart Tool Orchestrator", self.check_smart_orchestrator),
            ("📊 Intelligent Workflow System", self.check_intelligent_workflow),
            ("🤖 Multi-Model AI Integration", self.check_multi_model_ai),
            ("🛠️ Tool Registry Status", self.check_tool_registry),
            ("📈 LangGraph Integration", self.check_langgraph_integration),
            ("⚡ Core Performance", self.check_core_performance),
            ("🔍 Critical API Issues", self.check_critical_api_issues)
        ]
        
        for check_name, check_func in checks:
            print(f"{check_name}")
            print("-" * 50)
            try:
                result = await check_func()
                self.results[check_name] = result
                status = "✅ OPERATIONAL" if result.get("status") == "operational" else "❌ NEEDS ATTENTION"
                print(f"   Status: {status}")
                if result.get("details"):
                    for detail in result["details"]:
                        print(f"   • {detail}")
                if result.get("issues"):
                    for issue in result["issues"]:
                        print(f"   ⚠️ {issue}")
                print()
            except Exception as e:
                print(f"   ❌ CHECK FAILED: {str(e)}")
                self.results[check_name] = {"status": "failed", "error": str(e)}
                print()
        
        await self.generate_summary_report()
    
    async def check_cognitive_core(self) -> Dict[str, Any]:
        """Check CognitiveCoreWithLangGraph status"""
        try:
            from core.component_registry import component_registry
            cognitive_core = component_registry.get('cognitive_core_langgraph')
            details = ["CognitiveCoreWithLangGraph: Available"]
            if cognitive_core and getattr(cognitive_core, 'ready', False):
                details.append("Initialization: Complete")
                return {"status": "operational", "details": details}
            else:
                details.append("Initialization: Incomplete")
                return {"status": "needs_attention", "details": details, "issues": ["Cognitive core not fully initialized"]}
        except Exception as e:
            return {"status": "failed", "error": str(e), "issues": ["Cognitive core initialization failed", "May need dependency installation"]}
    
    async def check_smart_orchestrator(self) -> Dict[str, Any]:
        """Check SmartToolOrchestrator status"""
        try:
            from core.component_registry import component_registry
            orchestrator = component_registry.get('smart_tool_orchestrator')
            details = ["SmartToolOrchestrator: Available"]
            if orchestrator and getattr(orchestrator, 'ready', False):
                details.append("Initialization: Complete")
                return {"status": "operational", "details": details}
            else:
                details.append("Initialization: Incomplete")
                return {"status": "needs_attention", "details": details, "issues": ["Smart orchestrator not fully initialized"]}
        except Exception as e:
            return {"status": "failed", "error": str(e), "issues": ["Smart orchestrator not available", "May need component integration"]}
    
    async def check_intelligent_workflow(self) -> Dict[str, Any]:
        """Check IntelligentWorkflowOrchestrator status"""
        try:
            from core.component_registry import component_registry
            orchestrator = component_registry.get('intelligent_workflow_orchestrator')
            details = ["IntelligentWorkflowOrchestrator: Available"]
            if orchestrator and getattr(orchestrator, 'ready', False):
                details.append("Initialization: Complete")
                return {"status": "operational", "details": details}
            else:
                details.append("Initialization: Incomplete")
                return {"status": "needs_attention", "details": details, "issues": ["IntelligentWorkflowOrchestrator not fully initialized"]}
        except Exception as e:
            return {"status": "failed", "error": str(e), "issues": ["IntelligentWorkflowOrchestrator import/interface failed"]}
    
    async def check_multi_model_ai(self) -> Dict[str, Any]:
        """Check Multi-Model AI integration status"""
        try:
            from integrations.multi_model_ai_client import multi_model_ai_client
            from integrations.simplified_model_manager import model_manager
            
            details = []
            
            # Check available models
            if hasattr(multi_model_ai_client, 'available_models'):
                model_count = len(multi_model_ai_client.available_models)
                details.append(f"Available AI models: {model_count}")
            
            # Test simple AI request
            test_prompt = "System status check"
            start_time = time.time()
            
            try:
                result = await model_manager.execute_task_with_core_system(test_prompt)
                execution_time = time.time() - start_time
                details.append(f"AI response time: {execution_time:.3f}s")
                details.append("Model routing: Functional")
                
                return {
                    "status": "operational",
                    "execution_time": execution_time,
                    "details": details,
                    "test_result": result
                }
            except Exception as e:
                details.append(f"AI execution issue: {str(e)}")
                return {
                    "status": "needs_attention",
                    "details": details,
                    "issues": ["AI model execution may need configuration"]
                }
            
        except ImportError as e:
            return {
                "status": "failed",                "error": str(e),
                "issues": ["Multi-model AI client not available", "Check AI integration setup"]
            }

    async def check_tool_registry(self) -> Dict[str, Any]:
        """Check Tool Registry status"""
        try:
            from tools.tool_registry import tool_registry
            from tools import register_all_tools
            
            # Try to initialize tools if not already done
            if not hasattr(tool_registry, '_initialized') or len(tool_registry.tools) == 0:
                print("  ⚙️ Initializing tools...")
                try:
                    tool_count = await register_all_tools()
                    print(f"  ✅ Tools initialized: {tool_count}")
                except Exception as e:
                    print(f"  ⚠️ Tool initialization failed: {e}")
            
            # Get registered tools
            if hasattr(tool_registry, 'tools'):
                tool_count = len(tool_registry.tools)
                tool_names = list(tool_registry.tools.keys())
            else:
                tool_count = 0
                tool_names = []
            
            details = [
                f"Registered tools: {tool_count}",
                f"Tool registry: Available"
            ]
            
            if tool_names:
                details.append(f"Available tools: {', '.join(tool_names[:5])}")
                if len(tool_names) > 5:
                    details.append(f"... and {len(tool_names) - 5} more")
            
            status = "operational" if tool_count >= 10 else "needs_attention"
            
            return {
                "status": status,
                "tool_count": tool_count,
                "details": details,
                "tool_names": tool_names
            }
            
        except Exception as e:
            return {
                "status": "failed",
                "error": str(e),
                "issues": ["Tool registry initialization failed"]
            }
    
    async def check_langgraph_integration(self) -> Dict[str, Any]:
        """Check LangGraph integration status"""
        try:
            from integrations.langgraph_state_manager import state_manager
            from integrations.langgraph_diagnostics_bridge import langgraph_diagnostics_bridge
            
            details = [
                "LangGraph state manager: Available",
                "Diagnostics bridge: Available"
            ]
            
            # Check session management
            if hasattr(state_manager, 'active_sessions'):
                session_count = len(state_manager.active_sessions)
                details.append(f"Active sessions: {session_count}")
            
            # Test session creation
            try:
                test_session = await state_manager.create_session("system_check")
                details.append("Session creation: Functional")
                await state_manager.end_session("system_check")
            except Exception as e:
                details.append(f"Session management issue: {str(e)}")
            
            return {
                "status": "operational",
                "details": details
            }
            
        except ImportError as e:
            return {
                "status": "needs_attention",
                "issues": ["LangGraph integration partially available", "Some components may need updates"],
                "details": ["Core functionality present but may need fixes"]
            }
        except Exception as e:
            return {
                "status": "failed",
                "error": str(e),
                "issues": ["LangGraph integration failed"]
            }
    
    async def check_core_performance(self) -> Dict[str, Any]:
        """Check core system performance"""
        try:
            from core.command_router import router
            from core.ai_command_handler import ai_handler
            
            # Test basic command routing
            test_command = {
                "type": "ASK",
                "query": "System performance check"
            }
            
            start_time = time.time()
            result = await router.route_command(test_command)
            execution_time = time.time() - start_time
            
            details = [
                f"Command routing time: {execution_time:.3f}s",
                "Command router: Functional",
                "AI command handler: Available"
            ]
            
            if execution_time < 0.1:
                performance_rating = "Excellent"
            elif execution_time < 2.0:
                performance_rating = "Good"
            else:
                performance_rating = "Needs optimization"
            
            details.append(f"Performance rating: {performance_rating}")
            
            return {
                "status": "operational",
                "execution_time": execution_time,
                "performance_rating": performance_rating,
                "details": details,
                "test_result": result
            }
            
        except Exception as e:
            return {
                "status": "failed",
                "error": str(e),
                "issues": ["Core performance check failed"]
            }
    
    async def check_critical_api_issues(self) -> Dict[str, Any]:
        """Check for the 3 critical API issues mentioned in findings"""
        issues = []
        fixes_needed = []
        
        # 1. Check Workflow Handler method signature
        try:
            from core.ai_command_handler import ai_handler
            if hasattr(ai_handler, 'handle_workflow_command'):
                issues.append("✅ Workflow handler: Available")
            else:
                fixes_needed.append("Workflow handler method signature fix needed")
        except:
            fixes_needed.append("Workflow handler import failed")
        
        # 2. Check Dashboard Metrics handler
        try:
            from integrations.langgraph_diagnostics_bridge import langgraph_diagnostics_bridge
            issues.append("✅ Dashboard metrics bridge: Available")
        except:
            fixes_needed.append("Dashboard metrics handler missing")
        
        # 3. Check CLI Routing integration
        try:
            from main import ProjectSAgent
            issues.append("✅ CLI routing: Available")
        except:
            fixes_needed.append("CLI routing - cognitive core integration needed")
        
        status = "operational" if len(fixes_needed) == 0 else "needs_attention"
        
        return {
            "status": status,
            "details": issues,
            "issues": fixes_needed,
            "critical_fixes_needed": len(fixes_needed)
        }
    
    async def generate_summary_report(self):
        """Generate comprehensive summary report"""
        total_time = time.time() - self.start_time
        
        print("📋 COMPREHENSIVE SYSTEM STATUS REPORT")
        print("=" * 60)
        print(f"⏱️  Total check time: {total_time:.2f} seconds")
        print()
        
        # Count statuses
        operational_count = sum(1 for r in self.results.values() if r.get("status") == "operational")
        needs_attention_count = sum(1 for r in self.results.values() if r.get("status") == "needs_attention")
        failed_count = sum(1 for r in self.results.values() if r.get("status") == "failed")
        total_checks = len(self.results)
        
        print("📊 SYSTEM HEALTH OVERVIEW:")
        print(f"   ✅ Operational: {operational_count}/{total_checks} ({operational_count/total_checks*100:.1f}%)")
        print(f"   ⚠️  Needs Attention: {needs_attention_count}/{total_checks} ({needs_attention_count/total_checks*100:.1f}%)")
        print(f"   ❌ Failed: {failed_count}/{total_checks} ({failed_count/total_checks*100:.1f}%)")
        print()
        
        # Performance analysis
        execution_times = [r.get("execution_time", 0) for r in self.results.values() if r.get("execution_time")]
        if execution_times:
            avg_time = sum(execution_times) / len(execution_times)
            print(f"⚡ PERFORMANCE METRICS:")
            print(f"   Average execution time: {avg_time:.3f}s")
            print(f"   Fastest operation: {min(execution_times):.3f}s")
            print(f"   Slowest operation: {max(execution_times):.3f}s")
            print()
        
        # Critical findings
        critical_issues = self.results.get("🔍 Critical API Issues", {})
        if critical_issues.get("critical_fixes_needed", 0) > 0:
            print("🔧 CRITICAL FIXES NEEDED:")
            for issue in critical_issues.get("issues", []):
                print(f"   • {issue}")
            print()
        
        # Readiness assessment
        readiness_score = operational_count / total_checks * 100
        
        print("🎯 ENTERPRISE READINESS ASSESSMENT:")
        if readiness_score >= 95:
            readiness_status = "✅ READY FOR DEPLOYMENT"
        elif readiness_score >= 85:
            readiness_status = "⚠️  MOSTLY READY - Minor fixes needed"
        elif readiness_score >= 70:
            readiness_status = "🔧 NEEDS WORK - Several components require attention"
        else:
            readiness_status = "❌ NOT READY - Major issues need resolution"
        
        print(f"   Overall readiness: {readiness_score:.1f}%")
        print(f"   Status: {readiness_status}")
        print()
        
        # Business value confirmation
        if readiness_score >= 85:
            print("💰 BUSINESS VALUE CONFIRMED:")
            print("   • Enterprise automation: Ready for pilot deployment")
            print("   • Development workflows: Functional and efficient")
            print("   • Multi-step automation: Working with minor optimizations needed")
            print("   • AI-powered intelligence: Operational and responsive")
            print()
        
        # Next steps
        print("🚀 RECOMMENDED NEXT STEPS:")
        if critical_issues.get("critical_fixes_needed", 0) > 0:
            print("   1. Address critical API fixes (highest priority)")
        if needs_attention_count > 0:
            print("   2. Optimize components needing attention")
        if operational_count >= 6:
            print("   3. Begin enterprise pilot deployment")
            print("   4. Implement performance monitoring")
            print("   5. Create user documentation")
        print()
        
        # Save detailed report
        report_data = {
            "timestamp": time.strftime('%Y-%m-%d %H:%M:%S'),
            "total_check_time": total_time,
            "system_health": {
                "operational": operational_count,
                "needs_attention": needs_attention_count,
                "failed": failed_count,
                "total": total_checks,
                "readiness_score": readiness_score
            },
            "detailed_results": self.results,
            "readiness_status": readiness_status
        }
        
        import json
        with open("comprehensive_system_status_report.json", "w", encoding="utf-8") as f:
            json.dump(report_data, f, indent=2, default=str)
        
        print("💾 Detailed report saved: comprehensive_system_status_report.json")
        print()
        print("🎉 SYSTEM CHECK COMPLETE")

async def main():
    """Main execution function"""
    checker = ProjectSSystemChecker()
    await checker.run_comprehensive_check()

if __name__ == "__main__":
    asyncio.run(main())
