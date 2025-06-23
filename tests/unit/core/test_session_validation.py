#!/usr/bin/env python3
"""
Test Interactive Session Validation
Validates that the interactive session can handle natural language commands properly.
"""

import asyncio
import sys
import os

# Add the project root to sys.path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from integrations.model_manager import ModelManager

async def test_interactive_session():
    print('=== Testing Interactive Session Validation ===')
    
    # Initialize model manager
    model_manager = ModelManager()
    
    # Test commands with proper syntax
    test_commands = [
        "create a file called session_test.txt with the content 'Interactive session working!'",
        "execute shell command: echo 'Shell execution working'",
        "write python code that calculates 2 + 2 and saves the result to calculation.txt"
    ]
    
    for i, command in enumerate(test_commands, 1):
        print(f'\n--- Test {i}: {command[:50]}... ---')
        try:
            result = await model_manager.execute_task_with_core_system(command)
            print(f'✅ Command executed successfully')
            print(f'Status: {result.get("status")}')
            print(f'Command Type: {result.get("command_type")}')
            print(f'Execution Type: {result.get("execution_type")}')
            if result.get("execution_result"):
                exec_result = result["execution_result"]
                if "stdout" in exec_result:
                    print(f'Stdout: {exec_result["stdout"]}')
                if "stderr" in exec_result:
                    print(f'Stderr: {exec_result["stderr"]}')
        except Exception as e:
            print(f'❌ Command failed: {e}')
    
    print('\n=== Session Validation Complete ===')
    
    # Check what files were created
    print('\n--- Checking created files ---')
    import glob
    txt_files = glob.glob('*.txt')
    recent_files = [f for f in txt_files if 'session' in f or 'calculation' in f or 'test' in f]
    print(f'Files found: {recent_files}')

if __name__ == "__main__":
    asyncio.run(test_interactive_session())
