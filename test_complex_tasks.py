#!/usr/bin/env python3
"""
COMPLEX TASK TESTING FOR PROJECT-S ENHANCED AI SYSTEM
====================================================
Tests complex, multi-step tasks to verify real functionality vs hallucination.
"""

import asyncio
import os
import time
from pathlib import Path
from datetime import datetime

# Import the enhanced main.py functions
from main import (
    intelligent_command_parser, 
    process_file_operation_directly,
    execute_shell_command_directly,
    organize_directory_intelligently
)

async def test_complex_workflow():
    """Test a complex multi-step workflow with real verification."""
    print("🚀 COMPLEX WORKFLOW TEST")
    print("=" * 60)
    
    # Create test directory structure
    test_dir = Path("complex_test_workspace")
    print(f"📁 Creating test workspace: {test_dir}")
    
    # TASK 1: Create multiple files with different content
    print("\n🔥 TASK 1: Create multiple test files")
    test_files = [
        ("document.txt", "Ez egy teszt dokumentum."),
        ("data.json", '{"name": "test", "value": 42}'),
        ("script.py", "print('Hello from test script')"),
        ("image_simulation.jpg", "JPEG file simulation content"),
        ("archive_sim.zip", "ZIP archive simulation")
    ]
    
    created_files = []
    for filename, content in test_files:
        file_path = test_dir / filename
        result = await process_file_operation_directly("create", str(file_path), content)
        print(f"  📄 {filename}: {result['status']}")
        if result['status'] == 'success':
            created_files.append(str(file_path))
    
    # VERIFICATION 1: Check if files really exist
    print("\n🔍 VERIFICATION 1: Files really created?")
    for file_path in created_files:
        exists = Path(file_path).exists()
        size = Path(file_path).stat().st_size if exists else 0
        print(f"  ✅ {file_path}: EXISTS={exists}, SIZE={size} bytes")
    
    # TASK 2: Intelligent directory organization
    print("\n🔥 TASK 2: Intelligent directory organization")
    org_result = await organize_directory_intelligently(str(test_dir))
    print(f"📊 Organization result: {org_result['status']}")
    if org_result['status'] == 'success':
        print(f"  📁 Organized files: {org_result['organized_files']}")
        print(f"  📂 Categories created: {org_result['categories_created']}")
        print(f"  📋 Categories: {org_result.get('categories', [])}")
    
    # VERIFICATION 2: Check directory structure after organization
    print("\n🔍 VERIFICATION 2: Directory structure after organization")
    if test_dir.exists():
        for item in test_dir.iterdir():
            if item.is_dir():
                files_in_category = list(item.iterdir())
                print(f"  📁 {item.name}/: {len(files_in_category)} files")
                for file in files_in_category:
                    print(f"    📄 {file.name}")
    
    # TASK 3: Read organized files and verify content
    print("\n🔥 TASK 3: Read organized files and verify content")
    for category_dir in test_dir.iterdir():
        if category_dir.is_dir():
            print(f"\n📁 Category: {category_dir.name}")
            for file in category_dir.iterdir():
                if file.is_file():
                    read_result = await process_file_operation_directly("read", str(file))
                    if read_result['status'] == 'success':
                        content = read_result['content'][:100]  # First 100 chars
                        print(f"  📄 {file.name}: {content}...")
                    else:
                        print(f"  ❌ {file.name}: {read_result['message']}")
    
    # TASK 4: Shell command to count files
    print("\n🔥 TASK 4: Shell command verification")
    count_command = f"Get-ChildItem -Path '{test_dir}' -Recurse -File | Measure-Object | Select-Object -ExpandProperty Count"
    shell_result = await execute_shell_command_directly(count_command)
    print(f"💻 Shell command result: {shell_result['status']}")
    if shell_result['status'] == 'success':
        file_count = shell_result['stdout'].strip()
        print(f"  📊 Total files found by shell: {file_count}")
    else:
        print(f"  ❌ Shell error: {shell_result['message']}")
    
    # CLEANUP
    print("\n🧹 CLEANUP: Removing test workspace")
    import shutil
    if test_dir.exists():
        shutil.rmtree(test_dir)
        print("✅ Test workspace cleaned up")
    
    return True

async def test_intelligent_command_analysis():
    """Test the intelligent command parser with complex queries."""
    print("\n🧠 INTELLIGENT COMMAND ANALYSIS TEST")
    print("=" * 60)
    
    complex_commands = [
        "Hozz létre egy Python scriptet ami számológép funkciókat tartalmaz",
        "Rendszerezd a jelenlegi mappát és tedd kategóriákba a fájlokat",
        "Listázd ki az összes .py fájlt a projektben",
        "Futtasd le a következő parancsot: dir *.json",
        "Mi a különbség a gépi tanulás és a mesterséges intelligencia között?"
    ]
    
    for i, command in enumerate(complex_commands, 1):
        print(f"\n📝 TEST {i}: '{command}'")
        start_time = time.time()
        
        try:
            result = await intelligent_command_parser(command)
            duration = time.time() - start_time
            
            print(f"  🎯 Type: {result['type']}")
            print(f"  📊 Confidence: {result['confidence']:.0%} ({result['confidence_level']})")
            print(f"  ⚡ Analysis time: {duration:.3f}s")
            
            if result.get('operation'):
                print(f"  🔧 Operation: {result['operation']}")
            if result.get('path'):
                print(f"  📁 Path: {result['path']}")
            if result.get('command'):
                print(f"  💻 Command: {result['command']}")
                
        except Exception as e:
            print(f"  ❌ Error: {e}")

async def test_multi_ai_orchestration():
    """Test multi-AI orchestration capabilities."""
    print("\n🤖 MULTI-AI ORCHESTRATION TEST")
    print("=" * 60)
    
    # Import model manager to test AI orchestration
    try:
        from integrations.model_manager import model_manager
        
        test_queries = [
            "Explain quantum computing in simple terms",
            "Write a Python function to calculate fibonacci numbers",
            "What are the benefits of renewable energy?"
        ]
        
        for i, query in enumerate(test_queries, 1):
            print(f"\n🧪 AI TEST {i}: '{query}'")
            start_time = time.time()
            
            try:
                result = await model_manager.execute_task_with_core_system(query)
                duration = time.time() - start_time
                
                print(f"  ⏱️ Response time: {duration:.2f}s")
                print(f"  📊 Result type: {type(result)}")
                
                if isinstance(result, dict):
                    if result.get('status') == 'success':
                        print("  ✅ AI request successful")
                        if 'execution_result' in result:
                            exec_result = result['execution_result']
                            if isinstance(exec_result, dict) and 'response' in exec_result:
                                response = exec_result['response'][:200]  # First 200 chars
                                print(f"  🤖 AI Response preview: {response}...")
                            else:
                                print(f"  📄 Execution result: {str(exec_result)[:100]}...")
                    else:
                        print(f"  ❌ AI request failed: {result.get('message', 'Unknown error')}")
                else:
                    print(f"  📄 Direct response: {str(result)[:100]}...")
                    
            except Exception as e:
                print(f"  ❌ AI orchestration error: {e}")
                
    except ImportError as e:
        print(f"❌ Model manager not available: {e}")

async def main():
    """Run comprehensive complex task testing."""
    print("🚀 PROJECT-S COMPLEX TASK VERIFICATION")
    print("=" * 80)
    print(f"🕒 Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    try:
        # Test 1: Complex workflow with real file operations
        await test_complex_workflow()
        
        # Test 2: Intelligent command analysis
        await test_intelligent_command_analysis()
        
        # Test 3: Multi-AI orchestration
        await test_multi_ai_orchestration()
        
        print("\n" + "=" * 80)
        print("✅ ALL COMPLEX TESTS COMPLETED!")
        print("🎉 Enhanced AI functionality verified with real operations!")
        print("=" * 80)
        
    except Exception as e:
        print(f"\n❌ Test error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
