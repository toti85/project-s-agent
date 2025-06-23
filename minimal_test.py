#!/usr/bin/env python3
"""
Quick Test Script - Minimal Real Execution Test
===============================================
Simple test to verify that the system can execute real commands.
"""

import asyncio
import os
from tools.system_tools import SystemCommandTool, CommandValidator


async def minimal_real_execution_test():
    print("🔧 MINIMAL REAL EXECUTION TEST")
    print("=" * 40)
    
    tool = SystemCommandTool()
    current_dir = os.getcwd()
    
    # Test 1: Real directory listing
    print("\n1. Directory Listing Test")
    print("-" * 25)
    
    result = await tool.execute("dir", workdir=current_dir)
    success = result.get("success", False)
    stdout_lines = len(result.get("stdout", "").splitlines())
    
    print(f"Command: dir")
    print(f"Success: {success}")
    print(f"Output lines: {stdout_lines}")
    print(f"Status: {'✅ PASS' if success and stdout_lines > 0 else '❌ FAIL'}")
    
    # Test 2: Real folder creation
    print("\n2. Folder Creation Test")
    print("-" * 25)
    
    test_folder = "minimal_test_folder"
    result = await tool.execute(f"mkdir {test_folder}", workdir=current_dir)
    success = result.get("success", False)
    folder_exists = os.path.exists(os.path.join(current_dir, test_folder))
    
    print(f"Command: mkdir {test_folder}")
    print(f"Execute success: {success}")
    print(f"Folder actually exists: {folder_exists}")
    print(f"Status: {'✅ PASS' if success and folder_exists else '❌ FAIL'}")
    
    # Test 3: Cross-platform command translation
    print("\n3. Command Translation Test")
    print("-" * 30)
    
    unix_commands = ["ls", "cp source dest", "mkdir test"]
    for unix_cmd in unix_commands:
        windows_cmd = CommandValidator.translate_command(unix_cmd)
        print(f"  {unix_cmd:15} -> {windows_cmd}")
    
    # Summary
    print("\n📊 SUMMARY")
    print("-" * 15)
    
    dir_test_pass = success and stdout_lines > 0
    mkdir_test_pass = success and folder_exists
    
    total_tests = 2
    passed_tests = sum([dir_test_pass, mkdir_test_pass])
    
    print(f"Tests passed: {passed_tests}/{total_tests}")
    print(f"Success rate: {(passed_tests/total_tests)*100:.0f}%")
    
    if passed_tests == total_tests:
        print("🎉 ALL TESTS PASSED - Real execution is working!")
        return True
    else:
        print("⚠️ Some tests failed - Need further investigation")
        return False


if __name__ == "__main__":
    asyncio.run(minimal_real_execution_test())
