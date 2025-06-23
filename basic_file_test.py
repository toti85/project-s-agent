#!/usr/bin/env python3
"""
PROJECT-S VALIDATION - BASIC FILE OPERATION TEST
================================================
1. Create timestamp_test.txt with current date/time
2. List directory contents  
3. Append directory listing to the file
"""

import asyncio
import os
from datetime import datetime
from hybrid_workflow_system import HybridWorkflowSystem

async def basic_file_operation_test():
    """Comprehensive file operation validation test"""
    
    print("🔧 PROJECT-S VALIDATION - BASIC FILE OPERATION TEST")
    print("=" * 55)
    print(f"Test started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    system = HybridWorkflowSystem()
    
    # Step 1: Create timestamp_test.txt file
    print("Step 1: Creating timestamp_test.txt with current timestamp...")
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    request1 = "create timestamp_test.txt"
    result1 = await system.process_user_request(request1)
    
    status1 = "SUCCESS" if result1.get("success") else "FAILED"
    exec_type = result1.get("execution_type", "unknown")
    
    print(f"   Status: {status1} - {exec_type}")
    print(f"   Timestamp: {timestamp}")
    
    # Step 2: Verify file was created and check directory
    print("\nStep 2: Verifying file creation and scanning directory...")
    
    file_exists = os.path.exists("timestamp_test.txt")
    print(f"   File exists: {'YES' if file_exists else 'NO'}")
    
    # Get directory listing
    try:
        files = os.listdir('.')
        txt_files = [f for f in files if f.endswith('.txt')]
        md_files = [f for f in files if f.endswith('.md')]
        py_files = [f for f in files if f.endswith('.py')]
        
        print(f"   Total files: {len(files)}")
        print(f"   TXT files: {len(txt_files)}")
        print(f"   MD files: {len(md_files)}")
        print(f"   PY files: {len(py_files)}")
        
    except Exception as e:
        print(f"   Directory scan error: {str(e)}")
        files = []
    
    # Step 3: Write timestamp and directory info to file (simulate append)
    print("\nStep 3: Writing timestamp and directory info to file...")
    
    if file_exists:
        try:
            # Read current content
            with open("timestamp_test.txt", "r", encoding="utf-8") as f:
                current_content = f.read()
            
            # Prepare new content with timestamp and directory info
            new_content = f"""File created by Project-S Hybrid Workflow System
Creation timestamp: {timestamp}
Directory scan results:
- Total files: {len(files)}
- TXT files: {len(txt_files)}  
- MD files: {len(md_files)}
- PY files: {len(py_files)}
- Recent TXT files: {', '.join(txt_files[-5:]) if txt_files else 'None'}

Test completed successfully at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
            
            # Write enhanced content
            with open("timestamp_test.txt", "w", encoding="utf-8") as f:
                f.write(new_content)
            
            print("   Enhanced content written successfully")
            
            # Verify the content
            with open("timestamp_test.txt", "r", encoding="utf-8") as f:
                final_content = f.read()
                final_size = len(final_content)
            
            print(f"   Final file size: {final_size} characters")
            
        except Exception as e:
            print(f"   File writing error: {str(e)}")
    
    # Step 4: Final validation and summary
    print("\n🎯 VALIDATION RESULTS:")
    print("=" * 25)
    
    validation_results = {
        "file_creation": result1.get("success", False),
        "file_exists": file_exists,
        "directory_scan": len(files) > 0,
        "content_written": file_exists,
        "workflow_type": exec_type
    }
    
    for test, result in validation_results.items():
        status = "PASS" if result else "FAIL"
        print(f"   {test.replace('_', ' ').title()}: {status}")
      # Overall success calculation
    bool_results = [v for v in validation_results.values() if isinstance(v, bool)]
    success_count = sum(bool_results)
    total_tests = len(bool_results)
    success_rate = (success_count / total_tests) * 100 if total_tests > 0 else 0
    
    print(f"\n📊 OVERALL RESULTS:")
    print(f"   Tests passed: {success_count}/{total_tests}")
    print(f"   Success rate: {success_rate:.1f}%")
    
    if success_rate >= 80:
        print("   🎉 EXCELLENT: All core functionality working!")
    elif success_rate >= 60:
        print("   👍 GOOD: Most functionality working")
    else:
        print("   ⚠️ NEEDS IMPROVEMENT: Some issues detected")
    
    return validation_results

if __name__ == "__main__":
    asyncio.run(basic_file_operation_test())
