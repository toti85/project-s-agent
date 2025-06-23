#!/usr/bin/env python3
"""
Minimal direct test of the filename extraction method only.
"""

import sys
import os
from pathlib import Path

# Add the project root to the path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Suppress logging
import logging
logging.getLogger().setLevel(logging.CRITICAL)

def direct_method_test():
    """Test just the filename extraction method directly."""
    print("🔧 Direct method test starting...")
    
    try:
        # Just import the specific class we need
        sys.path.insert(0, str(project_root / "integrations"))
        
        # Minimal import and test
        from model_manager import ModelManager
        
        print("✅ ModelManager imported")
        
        # Create a minimal instance
        manager = ModelManager()
        print("✅ ModelManager instance created")
        
        # Test the method directly
        test_cases = [
            ("Create a file called hello.txt", "hello.txt"),
            ("Make a 'config.json' file", "config.json"),
            ("Írj egy test.py fájlt", "test.py"),
            ("General request without filename", "project_s_output.txt"),
        ]
        
        print("\n🧪 Testing extraction method...")
        
        success_count = 0
        for query, expected in test_cases:
            try:
                result = manager._extract_filename_from_query(query)
                if result == expected:
                    print(f"✅ '{query}' → '{result}' (correct)")
                    success_count += 1
                else:
                    print(f"❌ '{query}' → Expected: '{expected}', Got: '{result}'")
            except Exception as e:
                print(f"❌ Error testing '{query}': {e}")
        
        print(f"\n📊 Results: {success_count}/{len(test_cases)} tests passed")
        
        if success_count == len(test_cases):
            print("🎉 ALL TESTS PASSED! The filename extraction method works correctly!")
            return True
        else:
            print("💥 SOME TESTS FAILED!")
            return False
            
    except Exception as e:
        print(f"❌ Import/setup error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 Minimal filename extraction test")
    print("=" * 50)
    
    success = direct_method_test()
    
    if success:
        print("\n✅ SUCCESS: Filename extraction fix is working!")
    else:
        print("\n❌ FAILURE: There are still issues.")
    
    print("=" * 50)
