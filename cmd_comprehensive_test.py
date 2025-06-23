#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
import asyncio

# Add current directory to path
sys.path.append(os.getcwd())

print("=== CMD HANDLER COMPREHENSIVE TEST ===")

async def test_cmd_handler():
    """Test the CMD handler with various commands"""
    try:
        from core.ai_command_handler import AICommandHandler
        print("✅ CMD handler imported successfully")
        
        handler = AICommandHandler()
        print("✅ CMD handler instance created")
        
        # Test commands
        test_commands = [
            {"cmd": "echo Hello CMD Test", "description": "Simple echo test"},
            {"cmd": "dir /b", "description": "Directory listing"},
            {"cmd": "hostname", "description": "System hostname"},
            {"cmd": "echo Current directory: %cd%", "description": "Current directory"}
        ]
        
        results = []
        
        for test in test_commands:
            print(f"\n🔍 Testing: {test['description']}")
            print(f"   Command: {test['cmd']}")
            
            try:
                result = await handler.handle_cmd_command(test)
                print(f"   ✅ Status: {result.get('status', 'unknown')}")
                print(f"   📊 Return code: {result.get('return_code', 'unknown')}")
                
                stdout = result.get('stdout', '').strip()
                stderr = result.get('stderr', '').strip()
                
                if stdout:
                    print(f"   📤 Output: {stdout[:100]}{'...' if len(stdout) > 100 else ''}")
                if stderr:
                    print(f"   ⚠️  Error: {stderr[:100]}{'...' if len(stderr) > 100 else ''}")
                    
                results.append({
                    'command': test['cmd'],
                    'success': result.get('return_code') == 0,
                    'status': result.get('status'),
                    'output_length': len(stdout)
                })
                
            except Exception as e:
                print(f"   ❌ Error: {e}")
                results.append({
                    'command': test['cmd'],
                    'success': False,
                    'error': str(e)
                })
        
        # Summary
        print(f"\n📊 TEST SUMMARY:")
        print(f"   Total tests: {len(results)}")
        successful = sum(1 for r in results if r.get('success', False))
        print(f"   Successful: {successful}")
        print(f"   Failed: {len(results) - successful}")
        
        if successful == len(results):
            print("🎉 ALL CMD TESTS PASSED!")
        else:
            print("⚠️  Some CMD tests failed")
            
        return results
        
    except Exception as e:
        print(f"❌ CMD Handler test failed: {e}")
        import traceback
        traceback.print_exc()
        return None

async def main():
    print("Starting comprehensive CMD handler test...\n")
    results = await test_cmd_handler()
    
    if results:
        print(f"\n✅ CMD handler testing completed successfully!")
        
        # Write results to file
        with open("cmd_comprehensive_test_results.txt", "w", encoding="utf-8") as f:
            f.write("CMD Handler Comprehensive Test Results\n")
            f.write("=" * 40 + "\n\n")
            for result in results:
                f.write(f"Command: {result.get('command', 'unknown')}\n")
                f.write(f"Success: {result.get('success', False)}\n")
                f.write(f"Status: {result.get('status', 'unknown')}\n")
                if 'error' in result:
                    f.write(f"Error: {result['error']}\n")
                f.write("-" * 20 + "\n")
        
        print("📝 Results saved to cmd_comprehensive_test_results.txt")
    else:
        print("❌ CMD handler testing failed")

if __name__ == "__main__":
    asyncio.run(main())
