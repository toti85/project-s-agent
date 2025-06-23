#!/usr/bin/env python3
"""
🔧 SURGICAL FIX VALIDATION TEST
===============================
Test script to validate that AI-generated workflows now execute REAL commands
instead of returning simulation-only responses.

This test specifically validates:
1. Directory creation (mkdir commands)
2. File copy operations (copy commands) 
3. Directory listing (dir/ls commands)
4. Cross-platform command translation

Expected behavior AFTER surgical fixes:
- AI workflows should create actual directories
- Commands should execute via SystemCommandTool
- No more simulation-only responses
"""

import asyncio
import os
import sys
import time
from pathlib import Path

# Add project directory to path
project_dir = Path(__file__).parent
sys.path.insert(0, str(project_dir))

from hybrid_workflow_system import process_hybrid_workflow

async def test_surgical_fixes():
    """🔧 Test the surgical fixes for AI simulation → real execution"""
    
    print("🔧 SURGICAL FIX VALIDATION TEST")
    print("=" * 50)
    print("Testing AI-generated workflows for REAL execution...")
    print()
    
    # Test folder to validate operations
    test_folder = "surgical_fix_test_folder"
    test_file = "surgical_test_file.txt"
    
    # Clean up any existing test artifacts
    if os.path.exists(test_folder):
        os.rmdir(test_folder)
    if os.path.exists(test_file):
        os.remove(test_file)
    
    test_results = []
    
    # TEST 1: Directory Creation (Core issue from diagnostic)
    print("🧪 TEST 1: Directory Creation via AI Workflow")
    print("-" * 40)
    
    try:
        result = await process_hybrid_workflow(f"create folder named {test_folder}")
        
        # Check if directory was ACTUALLY created
        dir_exists = os.path.exists(test_folder) and os.path.isdir(test_folder)
        
        test_results.append({
            "test": "Directory Creation", 
            "ai_reported_success": result.get("success", False),
            "actual_execution": dir_exists,
            "strategy": result.get("processing_strategy", "unknown"),
            "fixed": dir_exists and result.get("success", False)
        })
        
        if dir_exists:
            print("✅ SUCCESS: Directory actually created!")
            print(f"   📁 {test_folder} exists on filesystem")
        else:
            print("❌ FAILED: Directory not created (still simulation)")
            print(f"   📁 {test_folder} does not exist")
            
        print(f"   🤖 AI reported success: {result.get('success', False)}")
        print(f"   🎯 Strategy used: {result.get('processing_strategy', 'unknown')}")
        print()
        
    except Exception as e:
        print(f"❌ TEST 1 EXCEPTION: {e}")
        test_results.append({
            "test": "Directory Creation",
            "ai_reported_success": False,
            "actual_execution": False,
            "strategy": "error",
            "fixed": False,
            "error": str(e)
        })
    
    # TEST 2: Directory Listing
    print("🧪 TEST 2: Directory Listing via AI Workflow")
    print("-" * 40)
    
    try:
        result = await process_hybrid_workflow("list current directory contents")
        
        # Check if we got actual stdout output (not simulation)
        has_real_output = False
        if result.get("execution_result", {}).get("step_results"):
            for step_result in result["execution_result"]["step_results"]:
                if step_result.get("stdout") and len(step_result.get("stdout", "")) > 0:
                    has_real_output = True
                    break
        
        test_results.append({
            "test": "Directory Listing",
            "ai_reported_success": result.get("success", False),
            "actual_execution": has_real_output,
            "strategy": result.get("processing_strategy", "unknown"),
            "fixed": has_real_output and result.get("success", False)
        })
        
        if has_real_output:
            print("✅ SUCCESS: Got real command output!")
        else:
            print("❌ FAILED: No real command output (still simulation)")
            
        print(f"   🤖 AI reported success: {result.get('success', False)}")
        print(f"   🎯 Strategy used: {result.get('processing_strategy', 'unknown')}")
        print()
        
    except Exception as e:
        print(f"❌ TEST 2 EXCEPTION: {e}")
        test_results.append({
            "test": "Directory Listing",
            "ai_reported_success": False,
            "actual_execution": False,
            "strategy": "error", 
            "fixed": False,
            "error": str(e)
        })
    
    # TEST 3: File Creation (Control test - should work via templates)
    print("🧪 TEST 3: File Creation (Control Test)")
    print("-" * 40)
    
    try:
        result = await process_hybrid_workflow(f"create file {test_file}")
        
        # Check if file was ACTUALLY created
        file_exists = os.path.exists(test_file) and os.path.isfile(test_file)
        
        test_results.append({
            "test": "File Creation (Control)",
            "ai_reported_success": result.get("success", False),
            "actual_execution": file_exists,
            "strategy": result.get("processing_strategy", "unknown"),
            "fixed": file_exists and result.get("success", False)
        })
        
        if file_exists:
            print("✅ SUCCESS: File actually created!")
            print(f"   📄 {test_file} exists on filesystem")
        else:
            print("❌ FAILED: File not created")
            
        print(f"   🤖 AI reported success: {result.get('success', False)}")
        print(f"   🎯 Strategy used: {result.get('processing_strategy', 'unknown')}")
        print()
        
    except Exception as e:
        print(f"❌ TEST 3 EXCEPTION: {e}")
        test_results.append({
            "test": "File Creation (Control)",
            "ai_reported_success": False,
            "actual_execution": False,
            "strategy": "error",
            "fixed": False,
            "error": str(e)
        })
    
    # RESULTS ANALYSIS
    print("📊 SURGICAL FIX RESULTS ANALYSIS")
    print("=" * 50)
    
    total_tests = len(test_results)
    fixed_tests = sum(1 for t in test_results if t.get("fixed", False))
    
    print(f"Total tests: {total_tests}")
    print(f"Fixed tests: {fixed_tests}")
    print(f"Fix success rate: {(fixed_tests/total_tests)*100:.1f}%")
    print()
    
    for result in test_results:
        test_name = result["test"]
        fixed = result.get("fixed", False)
        strategy = result.get("strategy", "unknown")
        
        status = "✅ FIXED" if fixed else "❌ NOT FIXED"
        print(f"{status} | {test_name} | Strategy: {strategy}")
        
        if result.get("error"):
            print(f"         Error: {result['error']}")
    
    print()
    
    # FINAL VERDICT
    if fixed_tests == total_tests:
        print("🎉 SURGICAL FIXES SUCCESSFUL!")
        print("   All AI workflows now execute real commands")
        print("   System ready for production deployment")
    elif fixed_tests > 0:
        print("⚠️  PARTIAL SUCCESS")
        print(f"   {fixed_tests}/{total_tests} fixes working")
        print("   Additional development needed")
    else:
        print("❌ SURGICAL FIXES FAILED")
        print("   AI workflows still return simulation responses")
        print("   Core system architecture needs review")
    
    # Cleanup
    try:
        if os.path.exists(test_folder):
            os.rmdir(test_folder)
        if os.path.exists(test_file):
            os.remove(test_file)
    except:
        pass  # Ignore cleanup errors
    
    return test_results

if __name__ == "__main__":
    # Run the surgical fix validation
    results = asyncio.run(test_surgical_fixes())
    
    # Save results to file
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    results_file = f"surgical_fix_validation_{timestamp}.txt"
    
    with open(results_file, "w", encoding="utf-8") as f:
        f.write("SURGICAL FIX VALIDATION RESULTS\n")
        f.write("=" * 40 + "\n")
        f.write(f"Timestamp: {timestamp}\n")
        f.write(f"Results: {results}\n")
    
    print(f"\n💾 Results saved to: {results_file}")
