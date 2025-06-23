#!/usr/bin/env python3
"""
Direct test of the core functionality without CLI overhead.
"""

import asyncio
import sys
import os
from pathlib import Path

# Add the project root to the path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Suppress excessive logging
import logging
logging.getLogger('integrations').setLevel(logging.ERROR)
logging.getLogger('core').setLevel(logging.ERROR)
logging.getLogger('tools').setLevel(logging.ERROR)
logging.getLogger('intelligent_workflow').setLevel(logging.ERROR)

async def test_core_file_creation():
    """Test core file creation functionality directly."""
    print("🔧 Testing core file creation...")
    
    try:
        # Import only what we need
        from integrations.model_manager import ModelManager
        
        print("📦 Creating ModelManager...")
        manager = ModelManager()
        
        # Test 1: Filename extraction method
        print("\n🧪 Testing filename extraction method...")
        test_queries = [
            ("Create a file called direct_test.txt", "direct_test.txt"),
            ("Írj egy magyar_file.py fájlt", "magyar_file.py"),
            ("Make a 'quoted_file.json' file", "quoted_file.json"),
        ]
        
        for query, expected in test_queries:
            result = manager._extract_filename_from_query(query)
            status = "✅" if result == expected else "❌"
            print(f"{status} '{query}' → '{result}' (expected: '{expected}')")
        
        # Clean up any existing test files
        test_files = ["direct_test.txt", "magyar_file.py", "quoted_file.json"]
        for file in test_files:
            if os.path.exists(file):
                os.remove(file)
                print(f"🧹 Cleaned up {file}")
        
        # Test 2: Core execution
        print("\n🏗️ Testing core file creation...")
        query = "Create a file called direct_test.txt"
        
        # Use the execute_task_with_tools method that contains our fix
        result = await manager.execute_task_with_tools(query)
        
        print(f"📋 Execution result: {result}")
        
        # Check if the file was created with the correct name
        if os.path.exists("direct_test.txt"):
            print("✅ SUCCESS: File 'direct_test.txt' was created!")
            with open("direct_test.txt", 'r', encoding='utf-8') as f:
                content = f.read()
                print(f"📄 Content: {content[:100]}...")
            return True
        elif os.path.exists("project_s_output.txt"):
            print("❌ FAILURE: Default 'project_s_output.txt' was created instead!")
            return False
        else:
            print("❌ FAILURE: No file was created!")
            return False
            
    except Exception as e:
        print(f"❌ Error in test: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Main test function."""
    print("🚀 Direct Core Test for Filename Fix")
    print("=" * 50)
    
    success = await test_core_file_creation()
    
    print("=" * 50)
    if success:
        print("🎉 TEST SUCCESS: Filename extraction fix is working!")
    else:
        print("💥 TEST FAILURE: Issues remain in the system.")
    
    return 0 if success else 1

if __name__ == "__main__":
    # Set minimal logging to see our output clearly
    import logging
    logging.basicConfig(level=logging.CRITICAL)
    
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
