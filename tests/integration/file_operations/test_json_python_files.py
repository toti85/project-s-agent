#!/usr/bin/env python3
"""
Test JSON and Python file creation with Project-S
This test verifies the fixed filename extraction works for different file types
"""

import asyncio
import os
import json
from integrations.model_manager import model_manager

async def test_json_file_creation():
    """Test creating JSON files with proper filenames"""
    print("🧪 TESTING JSON FILE CREATION")
    print("=" * 50)
    
    # Test 1: Create a config.json file
    json_query = 'create file "config.json" with content {"app": "Project-S", "version": "1.0", "debug": true}'
    print(f"📝 Query: {json_query}")
    
    result = await model_manager.process_user_command(json_query)
    print(f"📊 Result: {result}")
    
    # Check if file was created
    if os.path.exists("config.json"):
        print("✅ config.json created successfully!")
        with open("config.json", "r") as f:
            content = f.read()
            print(f"📄 Content: {content}")
    else:
        print("❌ config.json was not created")
    
    print()

async def test_python_file_creation():
    """Test creating Python files with proper filenames"""
    print("🐍 TESTING PYTHON FILE CREATION")
    print("=" * 50)
    
    # Test 2: Create a hello.py file
    python_query = 'create file "hello.py" with content print("Hello from Project-S!")'
    print(f"📝 Query: {python_query}")
    
    result = await model_manager.process_user_command(python_query)
    print(f"📊 Result: {result}")
    
    # Check if file was created
    if os.path.exists("hello.py"):
        print("✅ hello.py created successfully!")
        with open("hello.py", "r") as f:
            content = f.read()
            print(f"📄 Content: {content}")
    else:
        print("❌ hello.py was not created")
    
    print()

async def test_complex_python_file():
    """Test creating a more complex Python file"""
    print("🔧 TESTING COMPLEX PYTHON FILE CREATION")
    print("=" * 50)
    
    # Test 3: Create a calculator.py file
    calc_query = '''create file "calculator.py" with content:
def add(a, b):
    return a + b

def multiply(a, b):
    return a * b

if __name__ == "__main__":
    print("Calculator ready!")
    print(f"2 + 3 = {add(2, 3)}")
    print(f"4 * 5 = {multiply(4, 5)}")
'''
    print(f"📝 Query: {calc_query}")
    
    result = await model_manager.process_user_command(calc_query)
    print(f"📊 Result: {result}")
    
    # Check if file was created
    if os.path.exists("calculator.py"):
        print("✅ calculator.py created successfully!")
        with open("calculator.py", "r") as f:
            content = f.read()
            print(f"📄 Content: {content}")
    else:
        print("❌ calculator.py was not created")
    
    print()

async def test_data_json_file():
    """Test creating a data JSON file"""
    print("📊 TESTING DATA JSON FILE CREATION")
    print("=" * 50)
    
    # Test 4: Create a data.json file
    data_query = '''create file "data.json" with content {
    "users": [
        {"id": 1, "name": "Alice", "role": "admin"},
        {"id": 2, "name": "Bob", "role": "user"}
    ],
    "settings": {
        "theme": "dark",
        "language": "en"
    }
}'''
    print(f"📝 Query: {data_query}")
    
    result = await model_manager.process_user_command(data_query)
    print(f"📊 Result: {result}")
    
    # Check if file was created
    if os.path.exists("data.json"):
        print("✅ data.json created successfully!")
        with open("data.json", "r") as f:
            content = f.read()
            print(f"📄 Content: {content}")
            
            # Try to parse as JSON to verify it's valid
            try:
                parsed = json.loads(content)
                print("✅ JSON is valid!")
                print(f"📊 Parsed data keys: {list(parsed.keys())}")
            except json.JSONDecodeError as e:
                print(f"❌ JSON parsing failed: {e}")
    else:
        print("❌ data.json was not created")
    
    print()

async def run_all_tests():
    """Run all file creation tests"""
    print("🚀 PROJECT-S JSON & PYTHON FILE CREATION TESTS")
    print("=" * 60)
    print()
    
    try:
        await test_json_file_creation()
        await test_python_file_creation()
        await test_complex_python_file()
        await test_data_json_file()
        
        print("🎉 ALL TESTS COMPLETED!")
        print("=" * 60)
        
        # Summary
        created_files = []
        test_files = ["config.json", "hello.py", "calculator.py", "data.json"]
        
        for filename in test_files:
            if os.path.exists(filename):
                created_files.append(filename)
        
        print(f"📁 Created files: {created_files}")
        print(f"✅ Success rate: {len(created_files)}/{len(test_files)} ({len(created_files)/len(test_files)*100:.1f}%)")
        
        if len(created_files) == len(test_files):
            print("🎯 PERFECT SUCCESS! All filename extraction working correctly!")
        else:
            print("⚠️  Some files were not created as expected")
            
    except Exception as e:
        print(f"❌ Test error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(run_all_tests())
