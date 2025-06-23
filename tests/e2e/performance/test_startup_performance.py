#!/usr/bin/env python3
"""
Startup Performance Test - Identify bottlenecks in main.py loading
"""

import time
import logging

# Disable verbose logging
logging.basicConfig(level=logging.ERROR)

def time_import(module_name, import_statement):
    """Time a specific import."""
    start = time.time()
    try:
        exec(import_statement)
        elapsed = time.time() - start
        print(f"✅ {module_name}: {elapsed:.3f}s")
        return elapsed
    except Exception as e:
        elapsed = time.time() - start
        print(f"❌ {module_name}: {elapsed:.3f}s - ERROR: {e}")
        return elapsed

def main():
    """Test startup performance step by step."""
    print("🚀 STARTUP PERFORMANCE TEST")
    print("=" * 50)
    
    total_start = time.time()
    
    # Test core imports
    print("\n📦 CORE IMPORTS:")
    time_import("asyncio", "import asyncio")
    time_import("logging", "import logging") 
    time_import("datetime", "from datetime import datetime")
    
    # Test core components
    print("\n🔧 CORE COMPONENTS:")
    time_import("event_bus", "from core.event_bus import event_bus")
    time_import("error_handler", "from core.error_handler import ErrorHandler")
    time_import("memory_system", "from core.memory_system import MemorySystem")
    time_import("ai_command_handler", "from core.ai_command_handler import ai_handler")
    
    # Test model management
    print("\n🤖 MODEL MANAGEMENT:")
    time_import("simplified_model_manager", "from integrations.simplified_model_manager import model_manager")
    time_import("multi_model_ai_client", "from integrations.multi_model_ai_client import multi_model_ai_client")
    time_import("session_manager", "from integrations.session_manager import session_manager")
    time_import("persistent_state_manager", "from integrations.persistent_state_manager import persistent_state_manager")
    
    # Test tools
    print("\n🛠️  TOOLS:")
    time_import("tool_registry", "from tools.tool_registry import tool_registry")
    time_import("web_tools", "from tools.web_tools import WebTools")
    time_import("file_tools", "from tools.file_tools import FileTools")
    time_import("code_tools", "from tools.code_tools import CodeTools")
    time_import("system_tools", "from tools.system_tools import SystemTools")
    
    # Test workflows
    print("\n🔀 WORKFLOWS:")
    time_import("advanced_langgraph_workflow", "from integrations.advanced_langgraph_workflow import AdvancedLangGraphWorkflow")
    time_import("intelligent_workflow_integration", "from integrations.intelligent_workflow_integration import intelligent_workflow_orchestrator")
    
    total_elapsed = time.time() - total_start
    print("\n" + "=" * 50)
    print(f"🎯 TOTAL STARTUP TIME: {total_elapsed:.3f}s")
    
    if total_elapsed < 5.0:
        print("✅ TARGET ACHIEVED: <5s startup time!")
    else:
        print("❌ TARGET MISSED: Need optimization")
    
    print("=" * 50)

if __name__ == "__main__":
    main()
