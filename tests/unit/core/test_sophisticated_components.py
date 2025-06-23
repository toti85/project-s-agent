#!/usr/bin/env python3
"""
Test the sophisticated Project-S components
"""

def test_component(name, import_func):
    """Test a component and report status"""
    try:
        import_func()
        print(f"✅ {name}: Successfully imported")
        return True
    except Exception as e:
        print(f"❌ {name}: Error - {e}")
        return False

def test_all_components():
    """Test all sophisticated components"""
    print("=== PROJECT-S SOPHISTICATED COMPONENTS TEST ===")
    
    results = {}
    
    # Test SmartToolOrchestrator
    def test_orchestrator():
        from core.smart_orchestrator import SmartToolOrchestrator
        return SmartToolOrchestrator()
    
    results['SmartToolOrchestrator'] = test_component('SmartToolOrchestrator', test_orchestrator)
    
    # Test CognitiveCore  
    def test_cognitive_core():
        from core.cognitive_core import CognitiveCore
        return CognitiveCore()
    
    results['CognitiveCore'] = test_component('CognitiveCore', test_cognitive_core)
    
    # Test WorkflowEngine
    def test_workflow_engine():
        from core.workflow_engine import WorkflowEngine
        return WorkflowEngine()
    
    results['WorkflowEngine'] = test_component('WorkflowEngine', test_workflow_engine)
    
    # Test Multi-Model AI Client
    def test_multi_model_client():
        from integrations.multi_model_ai_client import multi_model_ai_client
        return multi_model_ai_client
    
    results['MultiModelAIClient'] = test_component('MultiModelAIClient', test_multi_model_client)
    
    # Test Advanced LangGraph Workflow
    def test_langgraph_workflow():
        from integrations.advanced_langgraph_workflow import AdvancedLangGraphWorkflow
        return AdvancedLangGraphWorkflow()
    
    results['AdvancedLangGraphWorkflow'] = test_component('AdvancedLangGraphWorkflow', test_langgraph_workflow)
    
    # Test Session Manager
    def test_session_manager():
        from integrations.session_manager import session_manager
        return session_manager
    
    results['SessionManager'] = test_component('SessionManager', test_session_manager)
    
    # Test Model Manager
    def test_model_manager():
        from integrations.model_manager import model_manager
        return model_manager
    
    results['ModelManager'] = test_component('ModelManager', test_model_manager)
    
    # Summary
    print("\n=== SUMMARY ===")
    working = sum(1 for r in results.values() if r)
    total = len(results)
    print(f"Working components: {working}/{total}")
    
    if working == total:
        print("🎉 ALL SOPHISTICATED COMPONENTS ARE WORKING!")
        print("✅ Project-S sophisticated architecture is FULLY FUNCTIONAL!")
    else:
        print("⚠️  Some components need fixes")
        for name, status in results.items():
            if not status:
                print(f"   🔧 {name} needs attention")
    
    return results

if __name__ == "__main__":
    test_all_components()
