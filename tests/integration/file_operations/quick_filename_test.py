#!/usr/bin/env python3
"""
Quick test for filename extraction with the fixed JSON parsing
"""
import asyncio
import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

async def test_filename_extraction():
    """Test the filename extraction with the latest fixes."""
    try:
        from integrations.model_manager import model_manager
        
        # Test queries that should extract proper filenames
        test_queries = [
            "hozz létre egy test_quick.txt fájlt Hello Quick Test tartalommal",
            "create file my_test.py with print('hello')",
            "write content to example.json with data",
        ]
        
        for query in test_queries:
            print(f"\n=== Testing query: {query} ===")
            
            # Test the filename extraction method directly
            filename = model_manager._extract_filename_from_query(query)
            print(f"Extracted filename: {filename}")
            
            # Test full processing (but don't actually execute)
            print("Full processing would be needed to test JSON parsing...")
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_filename_extraction())
