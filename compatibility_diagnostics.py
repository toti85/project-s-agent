#!/usr/bin/env python3
"""
Test script to diagnose the hanging issue and LangGraph compatibility
"""

import sys
import logging

# Set up basic logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def test_basic_imports():
    """Test basic imports"""
    try:
        logger.info("Testing basic LangGraph imports...")
        from langgraph.graph import StateGraph
        from langgraph.checkpoint.memory import MemorySaver
        logger.info("✅ Basic LangGraph imports successful")
        return True
    except Exception as e:
        logger.error(f"❌ Basic LangGraph imports failed: {e}")
        return False

def test_memory_saver():
    """Test MemorySaver instantiation"""
    try:
        logger.info("Testing MemorySaver instantiation...")
        from langgraph.checkpoint.memory import MemorySaver
        memory_saver = MemorySaver()
        logger.info("✅ MemorySaver instantiation successful")
        logger.info(f"MemorySaver methods: {[m for m in dir(memory_saver) if not m.startswith('_')]}")
        return True
    except Exception as e:
        logger.error(f"❌ MemorySaver instantiation failed: {e}")
        return False

def test_ai_handler_import():
    """Test AI handler import (which might be hanging)"""
    try:
        logger.info("Testing AI handler import...")
        from core.ai_command_handler import AICommandHandler
        logger.info("✅ AI handler class import successful")
        return True
    except Exception as e:
        logger.error(f"❌ AI handler import failed: {e}")
        return False

def test_ai_handler_init():
    """Test AI handler initialization"""
    try:
        logger.info("Testing AI handler initialization...")
        from core.ai_command_handler import AICommandHandler
        handler = AICommandHandler()
        logger.info("✅ AI handler initialization successful")
        return True
    except Exception as e:
        logger.error(f"❌ AI handler initialization failed: {e}")
        return False

def main():
    """Run all tests"""
    logger.info("Starting Project-S compatibility diagnostics...")
    
    tests = [
        ("Basic LangGraph imports", test_basic_imports),
        ("MemorySaver functionality", test_memory_saver),
        ("AI handler import", test_ai_handler_import),
        ("AI handler initialization", test_ai_handler_init),
    ]
    
    results = {}
    for test_name, test_func in tests:
        logger.info(f"\n--- Running: {test_name} ---")
        try:
            results[test_name] = test_func()
        except Exception as e:
            logger.error(f"Test '{test_name}' crashed: {e}")
            results[test_name] = False
    
    # Summary
    logger.info("\n=== COMPATIBILITY TEST RESULTS ===")
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        logger.info(f"{status}: {test_name}")
    
    total_passed = sum(results.values())
    total_tests = len(results)
    logger.info(f"\nSummary: {total_passed}/{total_tests} tests passed")
    
    if total_passed == total_tests:
        logger.info("🎉 All compatibility tests passed!")
    else:
        logger.warning("⚠️  Some compatibility issues detected")

if __name__ == "__main__":
    main()
