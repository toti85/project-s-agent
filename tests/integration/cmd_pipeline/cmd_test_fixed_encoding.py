#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
import subprocess
import asyncio

print("=== CMD TEST WITH FIXED ENCODING ===")

def safe_write_file(filename, content):
    """Write content to file with proper encoding handling"""
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    except Exception as e:
        print(f"File write error: {e}")
        return False

def test_basic_subprocess():
    """Test basic subprocess functionality"""
    print("Testing basic subprocess...")
    try:
        # Test with simple command
        result = subprocess.run(['echo', 'Hello World'], 
                              capture_output=True, text=True, encoding='utf-8')
        print(f"Echo test - Return code: {result.returncode}")
        print(f"Echo output: {result.stdout.strip()}")
        
        # Test with dir command using cmd
        result = subprocess.run('dir', shell=True, 
                              capture_output=True, text=True, encoding='utf-8')
        print(f"Dir test - Return code: {result.returncode}")
        print(f"Dir output length: {len(result.stdout)} characters")
        
        return True
    except Exception as e:
        print(f"Subprocess test failed: {e}")
        return False

def test_cmd_handler_import():
    """Test importing and using the CMD handler"""
    print("Testing CMD handler import...")
    try:
        sys.path.append(os.getcwd())
        from core.ai_command_handler import AICommandHandler
        print("✓ CMD handler imported successfully")
        
        handler = AICommandHandler()
        print("✓ CMD handler instance created")
        
        return handler
    except Exception as e:
        print(f"CMD handler import failed: {e}")
        import traceback
        print(traceback.format_exc())
        return None

async def test_cmd_handler_execution(handler):
    """Test actual CMD handler execution"""
    print("Testing CMD handler execution...")
    try:
        # Test with simple echo command
        test_command = {
            "cmd": "echo Testing CMD Handler"
        }
        
        result = await handler.handle_cmd_command(test_command)
        print(f"✓ CMD handler executed successfully")
        print(f"Status: {result.get('status', 'unknown')}")
        print(f"Return code: {result.get('return_code', 'unknown')}")
        print(f"Output: {result.get('stdout', 'no output')}")
        
        if result.get('stderr'):
            print(f"Error output: {result.get('stderr')}")
            
        return result
    except Exception as e:
        print(f"CMD handler execution failed: {e}")
        import traceback
        print(traceback.format_exc())
        return None

def main():
    # Test basic functionality
    if not test_basic_subprocess():
        print("❌ Basic subprocess test failed")
        return
    
    print("\n" + "="*50)
    
    # Test CMD handler import
    handler = test_cmd_handler_import()
    if not handler:
        print("❌ CMD handler import failed")
        return
        
    print("\n" + "="*50)
    
    # Test CMD handler execution
    try:
        result = asyncio.run(test_cmd_handler_execution(handler))
        if result:
            print("✅ All CMD tests passed!")
            
            # Write results to file
            output = f"""CMD Test Results:
Status: {result.get('status', 'unknown')}
Return Code: {result.get('return_code', 'unknown')}
Output: {result.get('stdout', 'no output')}
Error: {result.get('stderr', 'no error')}
"""
            if safe_write_file('cmd_test_results.txt', output):
                print("✓ Results saved to cmd_test_results.txt")
        else:
            print("❌ CMD handler execution failed")
    except Exception as e:
        print(f"❌ Async test failed: {e}")

if __name__ == "__main__":
    main()
