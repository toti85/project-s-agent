#!/usr/bin/env python3
"""
Step-by-step import test to identify the hanging component
"""

import sys
import time

def test_import(module_name, description):
    """Test importing a module with timeout"""
    print(f"Testing {description}...")
    start_time = time.time()
    
    try:
        if module_name == "core.cognitive_core_langgraph.imports":
            # Test the imports in cognitive_core_langgraph
            from langgraph.graph import StateGraph, END
            from langgraph.prebuilt import ToolNode
            from langgraph.graph.message import add_messages
            from langgraph.checkpoint.memory import MemorySaver
        elif module_name == "core.cognitive_core_langgraph.base":
            # Test just the base file without problematic imports
            import logging
            from typing import Dict, List, Any, Optional, Set, Tuple, Union, Callable
            from datetime import datetime
            from pydantic import BaseModel, Field
        elif module_name == "integrations.langgraph_state_enhanced":
            from integrations.langgraph_state_enhanced import initialize_state_enhanced_integration
        elif module_name == "core.cognitive_core_langgraph":
            from core.cognitive_core_langgraph import CognitiveCoreWithLangGraph
        else:
            exec(f"import {module_name}")
        
        elapsed = time.time() - start_time
        print(f"✅ {description} imported successfully in {elapsed:.2f}s")
        return True
    except Exception as e:
        elapsed = time.time() - start_time
        print(f"❌ {description} failed in {elapsed:.2f}s: {e}")
        return False

def main():
    print("=== Step-by-step import analysis ===\n")
    
    tests = [
        ("core.cognitive_core_langgraph.imports", "LangGraph imports only"),
        ("core.cognitive_core_langgraph.base", "Basic imports only"),
        ("integrations.langgraph_state_enhanced", "Enhanced state integration"),
        ("core.cognitive_core_langgraph", "Full cognitive core LangGraph"),
    ]
    
    for module, description in tests:
        success = test_import(module, description)
        if not success:
            print(f"\n🛑 Stopping at failed import: {description}")
            break
        print()
    
    print("=== Analysis complete ===")

if __name__ == "__main__":
    main()
