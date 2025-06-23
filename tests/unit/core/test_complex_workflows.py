#!/usr/bin/env python3
"""
Test Complex Workflows for Project-S AI Agent System
Tests multi-step intelligent workflows and complex command execution.
"""

import asyncio
import sys
import os
from integrations.model_manager import ModelManager

async def test_complex_workflow():
    print('=== Testing Complex Code Generation Workflow ===')
    
    # Initialize model manager
    model_manager = ModelManager()
    
    # Test 1: Code generation with multiple files
    print('\n--- Test 1: Multi-file web server generation ---')
    task = '''create a simple Python web server that:
1. has a /hello endpoint that returns 'Hello World'
2. has a /status endpoint that returns server status
3. saves all files in a 'webserver' directory
4. includes a requirements.txt file'''
    
    result = await model_manager.execute_task_with_core_system(task)
    print(f'Multi-file web server result: {result}')
    
    # Test 2: Shell command execution 
    print('\n--- Test 2: Shell command execution ---')
    task2 = 'list all Python files in the current directory and show their sizes'
    result2 = await model_manager.execute_task_with_core_system(task2)
    print(f'Shell command result: {result2}')
    
    # Test 3: Mixed workflow (code + file operations)
    print('\n--- Test 3: Mixed workflow (analysis + file creation) ---')
    task3 = '''analyze the Project-S codebase structure:
1. find all Python files in core/ directory 
2. create a summary file listing each file and its purpose
3. save the summary as codebase_analysis.md'''
    
    result3 = await model_manager.execute_task_with_core_system(task3)
    print(f'Mixed workflow result: {result3}')
    
    print('\n=== Complex Workflow Testing Complete ===')

if __name__ == "__main__":
    asyncio.run(test_complex_workflow())
