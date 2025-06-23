#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simple Website Analysis Test
Direct output version for debugging
"""

import asyncio
import sys
from pathlib import Path

# Setup paths
project_root = Path(__file__).parent.absolute()
sys.path.append(str(project_root))

print("🔧 DEBUG: Starting website analysis test...")
print("🔧 DEBUG: Importing tools...")

try:
    from tools.web_tools import WebPageFetchTool
    print("✅ WebPageFetchTool imported")
except ImportError as e:
    print(f"❌ Failed to import WebPageFetchTool: {e}")
    sys.exit(1)

async def simple_test():
    print("🔧 DEBUG: Creating WebPageFetchTool instance...")
    web_tool = WebPageFetchTool()
    
    print("🔧 DEBUG: Fetching shayanwaters.com...")
    try:
        result = await web_tool.execute(url="https://shayanwaters.com", extract_text=True, timeout=30)
        
        if result.get("success"):
            print("✅ SUCCESS: Website fetched successfully!")
            print(f"   Status: {result.get('status_code')}")
            print(f"   Title: {result.get('title', 'No title')}")
            print(f"   HTML length: {len(result.get('html', ''))} chars")
            print(f"   Text length: {len(result.get('text', ''))} chars")
            
            # Simple analysis
            html = result.get('html', '').lower()
            has_meta_desc = 'meta name="description"' in html
            has_h1 = '<h1' in html
            has_viewport = 'viewport' in html
            
            print("\n📊 QUICK ANALYSIS:")
            print(f"   Has meta description: {'✅' if has_meta_desc else '❌'}")
            print(f"   Has H1 tags: {'✅' if has_h1 else '❌'}")
            print(f"   Has viewport: {'✅' if has_viewport else '❌'}")
            
        else:
            print(f"❌ FAILED: {result.get('error', 'Unknown error')}")
            
    except Exception as e:
        print(f"❌ EXCEPTION: {e}")

if __name__ == "__main__":
    print("🌐 Simple Website Analysis Test")
    print("=" * 40)
    asyncio.run(simple_test())
    print("=" * 40)
    print("🏁 Test Complete")
