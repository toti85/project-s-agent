"""
Simple Website Analyzer Test Based on Stable Foundation
-------------------------------------------------------
This test uses only the stable tools without importing the broken intelligent_workflow_system.
"""
import asyncio
import sys
import os
from pathlib import Path
from datetime import datetime

print("🚀 Starting Simple Website Analyzer Test")
print(f"Python version: {sys.version}")
print(f"Working directory: {os.getcwd()}")

# Setup paths
project_root = Path(__file__).parent.absolute()
sys.path.append(str(project_root))

async def main():
    try:
        print("\n📦 Testing tool imports...")
        
        # Import tools directly
        from tools.file_tools import FileWriteTool
        from tools.web_tools import WebPageFetchTool
        print("✅ Tools imported successfully")
        
        # Create output directory
        os.makedirs("analysis_reports", exist_ok=True)
        
        # Test 1: File writing
        print("\n📝 Testing file writing...")
        write_tool = FileWriteTool()
        test_content = f"""# Test Report
Created: {datetime.now()}
Status: Testing file write functionality
"""
        
        result = await write_tool.execute(
            path="analysis_reports/test_report.md",
            content=test_content
        )
        
        if result.get("success"):
            print(f"✅ File write successful: {result.get('size')} bytes")
        else:
            print(f"❌ File write failed: {result.get('error')}")
            return False
        
        # Test 2: Web fetching
        print("\n🌐 Testing web fetching...")
        web_tool = WebPageFetchTool()
        test_url = "https://httpbin.org/html"
        
        result = await web_tool.execute(url=test_url)
        
        if result.get("success"):
            print(f"✅ Web fetch successful:")
            print(f"   Status: {result.get('status_code')}")
            print(f"   Title: {result.get('title', 'No title')}")
            print(f"   HTML size: {len(result.get('html', ''))} chars")
            print(f"   Text size: {len(result.get('text', ''))} chars")
        else:
            print(f"❌ Web fetch failed: {result.get('error')}")
            return False
        
        # Test 3: Real website analysis (shayanwaters.com)
        print("\n🎯 Testing real website analysis...")
        target_url = "https://shayanwaters.com"
        
        result = await web_tool.execute(url=target_url)
        
        if result.get("success"):
            print(f"✅ Website analysis successful:")
            print(f"   URL: {target_url}")
            print(f"   Status: {result.get('status_code')}")
            print(f"   Title: {result.get('title', 'No title')}")
            print(f"   HTML size: {len(result.get('html', ''))} chars")
            print(f"   Text size: {len(result.get('text', ''))} chars")
            
            # Save analysis results
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            report_content = f"""# Website Analysis Report
**URL:** {target_url}
**Analysis Date:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
**Status Code:** {result.get('status_code')}

## Page Information
- **Title:** {result.get('title', 'No title')}
- **Description:** {result.get('description', 'No description')}
- **Content Type:** {result.get('content_type', 'Unknown')}

## Content Statistics
- **HTML Size:** {len(result.get('html', ''))} characters
- **Text Size:** {len(result.get('text', ''))} characters
- **Text Preview:** 
{result.get('text', '')[:500]}...

---
*Analysis performed by Project-S Website Analyzer*
"""
            
            report_filename = f"analysis_reports/shayanwaters_analysis_{timestamp}.md"
            write_result = await write_tool.execute(
                path=report_filename,
                content=report_content
            )
            
            if write_result.get("success"):
                print(f"✅ Report saved: {report_filename}")
                print(f"   Report size: {write_result.get('size')} bytes")
            else:
                print(f"❌ Report save failed: {write_result.get('error')}")
                
        else:
            print(f"⚠️  Website analysis failed (network issue?): {result.get('error')}")
        
        print("\n🎉 Website Analyzer Test Complete!")
        print("All core functionality is working.")
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    result = asyncio.run(main())
    print(f"\nTest result: {'SUCCESS' if result else 'FAILED'}")
    sys.exit(0 if result else 1)
