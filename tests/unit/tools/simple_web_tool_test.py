#!/usr/bin/env python3
"""
Simple WebPageFetchTool Test
---------------------------
"""

import asyncio
import sys
from pathlib import Path

# Setup paths
project_root = Path(__file__).parent.absolute()
sys.path.append(str(project_root))

async def test_web_tool():
    """Simple test for WebPageFetchTool."""
    print("Starting WebPageFetchTool test...")
    
    try:
        # Import and test the tool directly
        from tools.web_tools import WebPageFetchTool
        print("✅ WebPageFetchTool imported successfully")
        
        # Create tool instance
        web_tool = WebPageFetchTool()
        print("✅ WebPageFetchTool instance created")
        
        # Test with simple URL
        test_url = "https://httpbin.org/html"
        print(f"🧪 Testing with URL: {test_url}")
        
        result = await web_tool.execute(url=test_url, extract_text=True, timeout=10)
        
        if result.get("success"):
            print("✅ WebPageFetchTool test PASSED!")
            print(f"   - Status: {result.get('status_code')}")
            print(f"   - Title: {result.get('title', 'N/A')}")
            print(f"   - Content length: {len(result.get('html', ''))} chars")
            return True
        else:
            print(f"⚠️  WebPageFetchTool test failed: {result.get('error')}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    result = asyncio.run(test_web_tool())
    print(f"\nFinal result: {'PASS' if result else 'FAIL'}")
