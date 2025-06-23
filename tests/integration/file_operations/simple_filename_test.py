#!/usr/bin/env python3
"""
Simple test for filename extraction method
"""

import sys
from pathlib import Path

# Add the project root to the path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_direct_extraction():
    """Test the filename extraction method directly."""
    try:
        from integrations.model_manager import ModelManager
        
        # Create instance
        manager = ModelManager()
        
        # Test cases
        test_cases = [
            ("Create a file called hello.txt", "hello.txt"),
            ("Írj egy test.py fájlt", "test.py"),
            ("Make a 'config.json' file", "config.json"),
            ("General request", "project_s_output.txt"),
        ]
        
        print("Testing filename extraction...")
        
        for query, expected in test_cases:
            try:
                result = manager._extract_filename_from_query(query)
                status = "✅" if result == expected else "❌"
                print(f"{status} '{query}' → Expected: '{expected}', Got: '{result}'")
            except Exception as e:
                print(f"❌ Error with '{query}': {e}")
                
        return True
        
    except Exception as e:
        print(f"❌ Import or initialization error: {e}")
        return False

if __name__ == "__main__":
    print("🔧 Testing filename extraction fix...")
    success = test_direct_extraction()
    if success:
        print("✅ Direct test completed!")
    else:
        print("❌ Direct test failed!")
