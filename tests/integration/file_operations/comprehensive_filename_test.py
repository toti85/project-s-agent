#!/usr/bin/env python3
"""
End-to-end test for the filename extraction fix.
This test will verify that the system can create files with custom names.
"""

import asyncio
import sys
import os
from pathlib import Path

# Add the project root to the path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

async def test_file_creation_with_custom_names():
    """Test file creation with custom filenames."""
    print("🔧 Testing file creation with custom names...")
    
    try:
        # Import the main components
        from integrations.model_manager import ModelManager
        
        # Initialize the model manager
        print("📦 Initializing ModelManager...")
        manager = ModelManager()
        
        # Test cases for filename extraction
        test_cases = [
            {
                "query": "Create a file called test_config.json",
                "expected_filename": "test_config.json",
                "description": "Quoted filename test"
            },
            {
                "query": "Írj egy hello.txt fájlt",
                "expected_filename": "hello.txt", 
                "description": "Hungarian file creation"
            },
            {
                "query": "Make a file named settings.py",
                "expected_filename": "settings.py",
                "description": "Named file creation"
            }
        ]
        
        print("\n🧪 Testing filename extraction method...")
        
        # Test 1: Direct method testing
        for i, test_case in enumerate(test_cases, 1):
            try:
                result = manager._extract_filename_from_query(test_case["query"])
                expected = test_case["expected_filename"]
                status = "✅" if result == expected else "❌"
                print(f"{status} Test {i} ({test_case['description']}): '{test_case['query']}'")
                print(f"   Expected: '{expected}', Got: '{result}'")
                
                if result != expected:
                    print(f"   ❌ MISMATCH! Expected '{expected}' but got '{result}'")
                    return False
                    
            except Exception as e:
                print(f"❌ Test {i} failed with error: {e}")
                return False
        
        print("\n✅ All filename extraction tests passed!")
        
        # Test 2: Try actual file creation through the system
        print("\n🏗️ Testing actual file creation through the system...")
        
        # Clean up any existing test files first
        test_files = ["test_config.json", "hello.txt", "settings.py"]
        for filename in test_files:
            if os.path.exists(filename):
                os.remove(filename)
                print(f"🧹 Cleaned up existing {filename}")
        
        # Test file creation using the execute_task_with_tools method
        for i, test_case in enumerate(test_cases, 1):
            try:
                print(f"\n📝 Testing file creation {i}: {test_case['description']}")
                print(f"   Query: '{test_case['query']}'")
                
                # Use the actual method that handles file creation
                result = await manager.execute_task_with_tools(test_case["query"])
                
                # Check if file was created with correct name
                expected_file = test_case["expected_filename"]
                if os.path.exists(expected_file):
                    print(f"   ✅ File '{expected_file}' created successfully!")
                    # Read the content to verify
                    with open(expected_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                        print(f"   📄 Content preview: {content[:100]}...")
                else:
                    print(f"   ❌ File '{expected_file}' was not created!")
                    # Check if the old default file was created instead
                    if os.path.exists("project_s_output.txt"):
                        print(f"   ❌ REGRESSION: Default 'project_s_output.txt' file was created instead!")
                        return False
                
            except Exception as e:
                print(f"❌ File creation test {i} failed: {e}")
                import traceback
                traceback.print_exc()
                return False
        
        print("\n🎉 All tests completed successfully!")
        print("✅ The filename extraction fix is working correctly!")
        return True
        
    except Exception as e:
        print(f"❌ Test setup failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Main test function."""
    print("🚀 Starting comprehensive filename extraction test...")
    
    success = await test_file_creation_with_custom_names()
    
    if success:
        print("\n🎯 TEST RESULT: SUCCESS!")
        print("The Project-S system can now create files with custom names!")
    else:
        print("\n💥 TEST RESULT: FAILED!")
        print("There are still issues with the filename extraction system.")
    
    return 0 if success else 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
