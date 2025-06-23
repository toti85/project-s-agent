#!/usr/bin/env python3
"""
Debug test for filename extraction method
"""

import sys
import os
from pathlib import Path

# Add the project root to the path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

print("🔧 Starting filename extraction debug test...")
print(f"📁 Working directory: {os.getcwd()}")
print(f"🛠️ Python path: {sys.path[0]}")

try:
    print("📦 Importing ModelManager...")
    from integrations.model_manager import ModelManager
    print("✅ ModelManager imported successfully")
    
    print("🏗️ Creating ModelManager instance...")
    manager = ModelManager()
    print("✅ ModelManager instance created")
    
    # Check if the method exists
    if hasattr(manager, '_extract_filename_from_query'):
        print("✅ _extract_filename_from_query method found")
        
        # Test cases
        test_cases = [
            ("Create a file called hello.txt", "hello.txt"),
            ("Írj egy test.py fájlt", "test.py"),
            ("Make a 'config.json' file", "config.json"),
            ("General request", "project_s_output.txt"),
        ]
        
        print("\n🧪 Testing filename extraction...")
        
        for i, (query, expected) in enumerate(test_cases):
            try:
                print(f"📝 Test {i+1}: '{query}'")
                result = manager._extract_filename_from_query(query)
                status = "✅" if result == expected else "❌"
                print(f"{status} Expected: '{expected}', Got: '{result}'")
            except Exception as e:
                print(f"❌ Error with test {i+1}: {e}")
                import traceback
                traceback.print_exc()
        
        print("\n✅ Testing completed!")
        
    else:
        print("❌ _extract_filename_from_query method not found")
        print("Available methods:")
        for attr in dir(manager):
            if not attr.startswith('__'):
                print(f"  - {attr}")
        
except ImportError as e:
    print(f"❌ Import error: {e}")
    import traceback
    traceback.print_exc()
except Exception as e:
    print(f"❌ General error: {e}")
    import traceback
    traceback.print_exc()

print("\n🎯 Debug test finished.")
