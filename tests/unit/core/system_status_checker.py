#!/usr/bin/env python3
"""
Project-S System Status Checker
===============================
This script checks the current status of all Project-S components without
requiring terminal interaction. It provides a comprehensive overview.
"""

import sys
import os
import traceback
from pathlib import Path

def check_import(module_name, description=""):
    """Check if a module can be imported successfully"""
    try:
        __import__(module_name)
        return True, f"✅ {module_name} - {description}"
    except Exception as e:
        return False, f"❌ {module_name} - {description}: {str(e)}"

def check_file_exists(file_path, description=""):
    """Check if a file exists"""
    if os.path.exists(file_path):
        return True, f"✅ {file_path} - {description}"
    else:
        return False, f"❌ {file_path} - {description}: File not found"

def main():
    print("=" * 60)
    print("PROJECT-S SYSTEM STATUS CHECKER")
    print("=" * 60)
    print()
    
    # Check core files existence
    print("🔍 CHECKING CORE FILES:")
    print("-" * 30)
    
    core_files = [
        ("WORKING_MINIMAL_VERSION.py", "Working minimal system"),
        ("main_multi_model.py", "Multi-model AI system"),
        ("core/cognitive_core.py", "Cognitive Core"),
        ("core/smart_orchestrator.py", "Smart Tool Orchestrator"),
        ("core/workflow_engine.py", "Workflow Engine"),
        ("integrations/multi_model_ai_client.py", "Multi-model AI client"),
        ("integrations/advanced_langgraph_workflow.py", "Advanced LangGraph"),
        ("stable_website_analyzer.py", "Website Analyzer"),
    ]
    
    for file_path, description in core_files:
        exists, message = check_file_exists(file_path, description)
        print(message)
    
    print()
    print("🧪 CHECKING IMPORTS:")
    print("-" * 30)
    
    # Test basic imports without running anything
    imports_to_test = [
        ("fix_unicode_encoding", "Unicode encoding fixes"),
        ("yaml", "YAML configuration"),
        ("asyncio", "Async support"),
        ("pathlib", "Path utilities"),
    ]
    
    for module, description in imports_to_test:
        success, message = check_import(module, description)
        print(message)
    
    print()
    print("🔧 CHECKING SOPHISTICATED COMPONENTS:")
    print("-" * 40)
    
    # Test sophisticated component imports individually
    sophisticated_tests = [
        # Core components
        ("core.event_bus", "Event Bus System"),
        ("core.error_handler", "Error Handler"),
        ("tools.file_tools", "File Tools"),
        ("tools.web_tools", "Web Tools"),
    ]
    
    for module, description in sophisticated_tests:
        try:
            __import__(module)
            print(f"✅ {module} - {description}")
        except Exception as e:
            print(f"❌ {module} - {description}: {str(e)}")
    
    print()
    print("📊 ADVANCED COMPONENT STATUS:")
    print("-" * 35)
    
    # Test the most complex components
    try:
        # Test Unicode fixes
        import fix_unicode_encoding
        print("✅ Unicode encoding fixes applied")
    except Exception as e:
        print(f"❌ Unicode encoding fixes: {e}")
    
    try:
        # Test multi-model system parts
        from integrations import multi_model_ai_client
        print("✅ Multi-model AI client available")
    except Exception as e:
        print(f"❌ Multi-model AI client: {e}")
    
    try:
        # Test LangGraph integration
        from integrations import advanced_langgraph_workflow
        print("✅ Advanced LangGraph workflow available")
    except Exception as e:
        print(f"❌ Advanced LangGraph workflow: {e}")
    
    try:
        # Test working minimal version
        import WORKING_MINIMAL_VERSION
        print("✅ Working minimal version available")
    except Exception as e:
        print(f"❌ Working minimal version: {e}")
    
    print()
    print("📈 RESTORATION PROGRESS:")
    print("-" * 25)
    
    # Calculate restoration status
    components_found = 0
    total_components = 8
    
    if os.path.exists("core/cognitive_core.py"):
        components_found += 1
        print("✅ Cognitive Core exists")
    else:
        print("❌ Cognitive Core missing")
    
    if os.path.exists("core/smart_orchestrator.py"):
        components_found += 1
        print("✅ Smart Orchestrator exists")
    else:
        print("❌ Smart Orchestrator missing")
    
    if os.path.exists("main_multi_model.py"):
        components_found += 1
        print("✅ Multi-model system exists")
    else:
        print("❌ Multi-model system missing")
    
    if os.path.exists("integrations/advanced_langgraph_workflow.py"):
        components_found += 1
        print("✅ Advanced LangGraph exists")
    else:
        print("❌ Advanced LangGraph missing")
    
    if os.path.exists("WORKING_MINIMAL_VERSION.py"):
        components_found += 1
        print("✅ Working minimal version exists")
    else:
        print("❌ Working minimal version missing")
    
    if os.path.exists("stable_website_analyzer.py"):
        components_found += 1
        print("✅ Website analyzer exists")
    else:
        print("❌ Website analyzer missing")
    
    if os.path.exists("fix_unicode_encoding.py"):
        components_found += 1
        print("✅ Unicode fixes exist")
    else:
        print("❌ Unicode fixes missing")
    
    if os.path.exists("intelligent_workflow_system_FIXED.py"):
        components_found += 1
        print("✅ Fixed workflow system exists")
    else:
        print("❌ Fixed workflow system missing")
    
    completion_percentage = (components_found / total_components) * 100
    
    print()
    print("=" * 60)
    print(f"RESTORATION STATUS: {completion_percentage:.1f}% Complete")
    print(f"Components Found: {components_found}/{total_components}")
    print("=" * 60)
    
    if completion_percentage >= 90:
        print("🎉 PROJECT-S RESTORATION IS NEARLY COMPLETE!")
        print("   Most sophisticated components are available.")
        print("   Focus: Fix remaining import/syntax issues.")
    elif completion_percentage >= 70:
        print("🚀 PROJECT-S RESTORATION IS WELL UNDERWAY!")
        print("   Core components exist but may need fixes.")
        print("   Focus: Test and debug existing components.")
    elif completion_percentage >= 50:
        print("⚡ PROJECT-S RESTORATION IN PROGRESS!")
        print("   Foundation exists, building more components.")
        print("   Focus: Complete core architecture.")
    else:
        print("🔨 PROJECT-S RESTORATION JUST STARTING!")
        print("   Basic components need to be built.")
        print("   Focus: Create fundamental architecture.")
    
    print()
    print("NEXT RECOMMENDED ACTIONS:")
    print("1. Fix import/syntax errors in existing files")
    print("2. Test individual components")
    print("3. Create integration tests")
    print("4. Update documentation")

if __name__ == "__main__":
    main()
