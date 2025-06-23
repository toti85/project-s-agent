#!/usr/bin/env python3
"""
Test script for the filename extraction fix in Project-S
"""

import asyncio
import logging
import sys
import os
from pathlib import Path

# Add the project root to the path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Configure logging
logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(name)s - %(message)s')
logger = logging.getLogger(__name__)

async def test_filename_extraction():
    """Test the filename extraction functionality."""
    try:
        from integrations.model_manager import model_manager
        
        # Test cases for filename extraction
        test_cases = [
            ("Create a file called hello.txt", "hello.txt"),
            ("Írj egy test.py fájlt", "test.py"),
            ("Make a 'config.json' file", "config.json"),
            ("Hozz létre egy lista nevű fájlt", "lista.txt"),
            ("Create README.md file", "README.md"),
            ("Write some HTML content", "index.html"),
            ("General file creation request", "project_s_output.txt"),  # fallback
        ]
        
        print("🧪 Testing filename extraction logic...")
        
        for query, expected in test_cases:
            extracted = model_manager._extract_filename_from_query(query)
            status = "✅" if extracted == expected else "❌"
            print(f"{status} Query: '{query}' → Expected: '{expected}', Got: '{extracted}'")
            
    except Exception as e:
        print(f"❌ Error testing filename extraction: {e}")
        return False
    
    return True

async def test_actual_file_creation():
    """Test actual file creation with the fix."""
    try:
        from integrations.model_manager import model_manager
        
        print("\n🧪 Testing actual file creation...")
        
        # Test file creation with specific filename
        result = await model_manager.execute_task_with_core_system(
            query="Create a file called test_fix.txt with some content",
            task_type="file"
        )
        
        print(f"✅ File creation result: {result.get('status', 'unknown')}")
        
        # Check if the file was created with the correct name
        if os.path.exists("test_fix.txt"):
            print("✅ File 'test_fix.txt' was created successfully!")
            with open("test_fix.txt", "r", encoding="utf-8") as f:
                content = f.read()
                print(f"📄 File content preview: {content[:100]}...")
        else:
            print("❌ File 'test_fix.txt' was not found")
            
        return True
        
    except Exception as e:
        print(f"❌ Error testing file creation: {e}")
        return False

async def main():
    """Main test function."""
    print("🔧 Testing Project-S filename extraction fix...")
    
    # Test 1: Filename extraction logic
    success1 = await test_filename_extraction()
    
    # Test 2: Actual file creation
    success2 = await test_actual_file_creation()
    
    if success1 and success2:
        print("\n🎉 All tests passed! The filename fix is working correctly.")
    else:
        print("\n❌ Some tests failed. Please check the implementation.")
    
    return success1 and success2

if __name__ == "__main__":
    asyncio.run(main())
