#!/usr/bin/env python3
"""
Test Corrected Workflows with Proper Shell Commands
Tests the system with correct command syntax.
"""

import asyncio
import sys
import os
from integrations.model_manager import ModelManager

async def test_corrected_workflows():
    print('=== Testing Corrected Workflows with Proper Commands ===')
    
    # Initialize model manager
    model_manager = ModelManager()
    
    # Test 1: Proper shell command
    print('\n--- Test 1: Correct shell command for listing Python files ---')
    task1 = '''execute this shell command: dir *.py /b'''
    
    result1 = await model_manager.execute_task_with_core_system(task1)
    print(f'Shell command result: {result1}')
    
    # Test 2: File creation with specific content
    print('\n--- Test 2: Create a specific file with content ---')
    task2 = '''create a file named workflow_test_results.md with content that lists:
1. System successfully detects workflow intents
2. Intelligent workflow orchestrator is working
3. Core execution bridge routes commands correctly
4. File operations create actual files on the filesystem'''
    
    result2 = await model_manager.execute_task_with_core_system(task2)
    print(f'File creation result: {result2}')
    
    # Test 3: Simple code execution
    print('\n--- Test 3: Python code execution ---')
    task3 = '''write and execute a python script that prints "Project-S Complex Workflows Working!" and the current timestamp'''
    
    result3 = await model_manager.execute_task_with_core_system(task3)
    print(f'Code execution result: {result3}')
    
    print('\n=== Corrected Workflow Testing Complete ===')

if __name__ == "__main__":
    asyncio.run(test_corrected_workflows())
