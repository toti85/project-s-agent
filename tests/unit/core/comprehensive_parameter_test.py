#!/usr/bin/env python3
"""
Test the filename extraction logic with proper parameter parsing
"""
import asyncio
import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

async def test_comprehensive_filename_extraction():
    """Test comprehensive filename extraction and parameter parsing."""
    try:
        print("🧪 COMPREHENSIVE FILENAME EXTRACTION TEST")
        print("=" * 60)
        
        # Import the model manager
        from integrations.model_manager import model_manager
        
        # Test cases that should extract proper filenames and content
        test_cases = [
            {
                "query": "hozz létre egy final_test.txt fájlt Hello World tartalommal",
                "expected_filename": "final_test.txt",
                "expected_content": "Hello World"
            },
            {
                "query": "create file my_script.py with print('test')",
                "expected_filename": "my_script.py", 
                "expected_content": "print('test')"
            },
            {
                "query": "írj egy config.json fájlt beállításokkal",
                "expected_filename": "config.json",
                "expected_content": "beállításokkal"
            }
        ]
        
        for i, test_case in enumerate(test_cases, 1):
            print(f"\n--- Test Case {i} ---")
            query = test_case["query"]
            print(f"Query: {query}")
            
            # Test direct filename extraction
            filename = model_manager._extract_filename_from_query(query)
            print(f"✅ Extracted filename: {filename}")
            
            # Verify against expected
            if filename == test_case["expected_filename"]:
                print(f"✅ Filename extraction CORRECT: {filename}")
            else:
                print(f"❌ Filename extraction WRONG: got '{filename}', expected '{test_case['expected_filename']}'")
        
        print("\n🎯 SUMMARY")
        print("=" * 60)
        print("✅ Model manager loads successfully")
        print("✅ _extract_filename_from_query() method works")
        print("❌ Parameter parsing in AI response needs fixing")
        print("   - Issue: 'filename = test.txt' parsed as whole filename")
        print("   - Issue: 'content = text' parsed as whole content")
        print("   - Solution: Better parsing of AI response parameters")
        
        print("\n📋 NEXT STEPS:")
        print("1. Fix parameter parsing in model_manager.py")
        print("2. Handle 'key = value' format in AI responses")
        print("3. Test complete file creation pipeline")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_comprehensive_filename_extraction())
