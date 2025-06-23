#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project-S Status Checker
Simple Python script to check the status of Project-S components
"""
import os
import sys
import importlib.util

def print_header(text, color="cyan"):
    colors = {
        "cyan": "\033[96m",
        "yellow": "\033[93m", 
        "green": "\033[92m",
        "red": "\033[91m",
        "reset": "\033[0m"
    }
    print(f"\n{colors.get(color, '')}{text}{colors['reset']}")

def check_file(filepath, description):
    if os.path.exists(filepath):
        print(f"✅ {filepath} - {description}")
        return True
    else:
        print(f"❌ {filepath} - {description}: File not found")
        return False

def test_import(module_name, description):
    try:
        __import__(module_name)
        print(f"✅ {module_name} - {description}: Import successful")
        return True
    except Exception as e:
        print(f"❌ {module_name} - {description}: {str(e)}")
        return False

def main():
    print_header("="*60, "cyan")
    print_header("PROJECT-S SYSTEM STATUS CHECKER (Python)", "yellow")
    print_header("="*60, "cyan")
    
    # Check working directory
    current_dir = os.getcwd()
    print(f"\n📁 Working directory: {current_dir}")
    
    print_header("🔍 CHECKING CORE FILES:", "yellow")
    print("-" * 40)
    
    # Core files to check
    core_files = [
        ("WORKING_MINIMAL_VERSION.py", "Working minimal system"),
        ("main_multi_model.py", "Multi-model AI system"),
        ("core/cognitive_core.py", "Cognitive Core"),
        ("core/smart_orchestrator.py", "Smart Tool Orchestrator"),
        ("integrations/multi_model_ai_client.py", "Multi-model AI client"),
        ("integrations/advanced_langgraph_workflow.py", "Advanced LangGraph"),
        ("stable_website_analyzer.py", "Website Analyzer"),
        ("fix_unicode_encoding.py", "Unicode encoding fixes")
    ]
    
    files_found = 0
    for filepath, description in core_files:
        if check_file(filepath, description):
            files_found += 1
    
    print_header("🧪 TESTING PYTHON IMPORTS:", "yellow")
    print("-" * 40)
    
    # Test basic imports
    imports_working = 0
    total_imports = 0
    
    # Basic Python functionality
    basic_imports = [
        ("sys", "System functions"),
        ("os", "Operating system interface"),
        ("json", "JSON handling"),
        ("asyncio", "Async support"),
    ]
    
    for module, desc in basic_imports:
        total_imports += 1
        if test_import(module, desc):
            imports_working += 1
    
    # Project-S specific imports
    try:
        # Test fix_unicode_encoding
        total_imports += 1
        import fix_unicode_encoding
        print("✅ fix_unicode_encoding - Unicode fixes: Available")
        imports_working += 1
    except Exception as e:
        print(f"❌ fix_unicode_encoding - Unicode fixes: {e}")
    
    try:
        # Test WORKING_MINIMAL_VERSION
        total_imports += 1
        import WORKING_MINIMAL_VERSION
        print("✅ WORKING_MINIMAL_VERSION - Minimal system: Available")
        imports_working += 1
    except Exception as e:
        print(f"❌ WORKING_MINIMAL_VERSION - Minimal system: {e}")
    
    try:
        # Test stable_website_analyzer
        total_imports += 1
        import stable_website_analyzer
        print("✅ stable_website_analyzer - Website analyzer: Available")
        imports_working += 1
    except Exception as e:
        print(f"❌ stable_website_analyzer - Website analyzer: {e}")
    
    print_header("📊 SYSTEM STATUS SUMMARY:", "yellow")
    print("-" * 40)
    
    total_files = len(core_files)
    completion_percentage = round((files_found / total_files) * 100, 1)
    import_percentage = round((imports_working / total_imports) * 100, 1)
    
    print(f"Files Found: {files_found}/{total_files} ({completion_percentage}%)")
    print(f"Imports Working: {imports_working}/{total_imports} ({import_percentage}%)")
    
    overall_status = (completion_percentage + import_percentage) / 2
    
    if overall_status >= 90:
        print_header("🎉 PROJECT-S RESTORATION IS NEARLY COMPLETE!", "green")
        print("   Most sophisticated components are available.")
        print("   Focus: Fix remaining import/syntax issues.")
    elif overall_status >= 70:
        print_header("🚀 PROJECT-S RESTORATION IS WELL UNDERWAY!", "yellow")
        print("   Core components exist but may need fixes.")
        print("   Focus: Test and debug existing components.")
    else:
        print_header("⚡ PROJECT-S RESTORATION IN PROGRESS!", "yellow")
        print("   Foundation exists, building more components.")
    
    print_header("="*60, "cyan")
    print_header("STATUS CHECK COMPLETE", "yellow")
    print_header("="*60, "cyan")
    
    print("\n🎯 NEXT RECOMMENDED ACTIONS:")
    print("1. Test individual sophisticated components")
    print("2. Run the multi-model system demo")
    print("3. Add missing API keys for full functionality")
    print("4. Integration testing of all components")
    
    print("\n💡 TO TEST THE MULTI-MODEL SYSTEM:")
    print("   python main_multi_model.py")
    print("\n💡 TO TEST THE MINIMAL SYSTEM:")
    print("   python WORKING_MINIMAL_VERSION.py")

if __name__ == "__main__":
    main()
