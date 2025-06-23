#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
import asyncio
import subprocess

print("=== DIRECT CMD EXECUTION TEST ===")

def test_direct_cmd():
    """Test direct CMD execution to verify the basic functionality"""
    print("Testing direct subprocess CMD execution...")
    
    commands = [
        ("echo Hello CMD", "Simple echo test"),
        ("hostname", "Get system hostname"),
        ("date /t", "Get current date"),
        ("dir /b | findstr .py | head -5", "List Python files")
    ]
    
    results = []
    
    for cmd, description in commands:
        print(f"\n🔍 {description}")
        print(f"   Command: {cmd}")
        
        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            
            print(f"   ✅ Return code: {result.returncode}")
            
            if result.stdout.strip():
                output = result.stdout.strip()
                print(f"   📤 Output: {output[:100]}{'...' if len(output) > 100 else ''}")
            
            if result.stderr.strip():
                error = result.stderr.strip()
                print(f"   ⚠️  Error: {error[:100]}{'...' if len(error) > 100 else ''}")
            
            results.append({
                'command': cmd,
                'success': result.returncode == 0,
                'output': result.stdout,
                'error': result.stderr
            })
            
        except Exception as e:
            print(f"   ❌ Exception: {e}")
            results.append({
                'command': cmd,
                'success': False,
                'exception': str(e)
            })
    
    # Summary
    successful = sum(1 for r in results if r.get('success', False))
    print(f"\n📊 SUMMARY:")
    print(f"   Total: {len(results)}")
    print(f"   Successful: {successful}")
    print(f"   Failed: {len(results) - successful}")
    
    return results

def main():
    print("Starting direct CMD execution test...\n")
    results = test_direct_cmd()
    
    # Write results
    try:
        with open("direct_cmd_test_results.txt", "w", encoding="utf-8") as f:
            f.write("Direct CMD Test Results\n")
            f.write("=" * 30 + "\n\n")
            
            for result in results:
                f.write(f"Command: {result['command']}\n")
                f.write(f"Success: {result.get('success', False)}\n")
                if 'output' in result:
                    f.write(f"Output: {result['output'][:200]}\n")
                if 'error' in result:
                    f.write(f"Error: {result['error'][:200]}\n")
                if 'exception' in result:
                    f.write(f"Exception: {result['exception']}\n")
                f.write("-" * 20 + "\n")
        
        print(f"\n✅ Results saved to direct_cmd_test_results.txt")
        
    except Exception as e:
        print(f"❌ Could not save results: {e}")

if __name__ == "__main__":
    main()
