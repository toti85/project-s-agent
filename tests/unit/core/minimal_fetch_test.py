#!/usr/bin/env python3
"""
Minimal Website Fetch Test
Test if we can fetch shayanwaters.com and save basic results
"""

import asyncio
import sys
import os
import json
from datetime import datetime
from pathlib import Path

# Setup project path
project_root = Path(__file__).parent.absolute()
sys.path.append(str(project_root))

async def test_website_fetch():
    """Test fetching a website and save results to file."""
    
    # Ensure output directory exists
    os.makedirs('test_outputs', exist_ok=True)
    
    # Log file
    log_file = 'test_outputs/fetch_test_log.txt'
    
    def log_message(msg):
        timestamp = datetime.now().strftime("%H:%M:%S")
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(f"[{timestamp}] {msg}\n")
        print(f"[{timestamp}] {msg}")
    
    try:
        log_message("Starting website fetch test...")
        
        # Try to import WebPageFetchTool
        try:
            from tools.web_tools import WebPageFetchTool
            log_message("✅ WebPageFetchTool imported successfully")
        except ImportError as e:
            log_message(f"❌ Failed to import WebPageFetchTool: {e}")
            return False
        
        # Test the tool
        url = "https://shayanwaters.com"
        log_message(f"Fetching: {url}")
        
        web_tool = WebPageFetchTool()
        result = await web_tool.execute(url=url, extract_text=True, timeout=30)
        
        if result.get("success"):
            html = result.get("html", "")
            text = result.get("text", "")
            title = result.get("title", "")
            status_code = result.get("status_code", 0)
            
            log_message(f"✅ Fetch successful!")
            log_message(f"   Status: {status_code}")
            log_message(f"   Title: {title}")
            log_message(f"   HTML length: {len(html)} chars")
            log_message(f"   Text length: {len(text)} chars")
            
            # Save basic analysis to file
            basic_analysis = {
                "url": url,
                "timestamp": datetime.now().isoformat(),
                "status_code": status_code,
                "title": title,
                "html_length": len(html),
                "text_length": len(text),
                "text_preview": text[:500] + "..." if len(text) > 500 else text,
                "success": True
            }
            
            # Save to JSON file
            result_file = 'test_outputs/shayanwaters_basic_analysis.json'
            with open(result_file, 'w', encoding='utf-8') as f:
                json.dump(basic_analysis, f, indent=2, ensure_ascii=False)
            
            log_message(f"✅ Basic analysis saved to: {result_file}")
            
            # Save raw HTML for inspection
            html_file = 'test_outputs/shayanwaters_raw.html'
            with open(html_file, 'w', encoding='utf-8') as f:
                f.write(html)
            
            log_message(f"✅ Raw HTML saved to: {html_file}")
            
            return True
            
        else:
            error_msg = result.get("error", "Unknown error")
            log_message(f"❌ Fetch failed: {error_msg}")
            return False
    
    except Exception as e:
        log_message(f"❌ Exception occurred: {e}")
        import traceback
        log_message(f"Traceback: {traceback.format_exc()}")
        return False

if __name__ == "__main__":
    print("Running minimal website fetch test...")
    result = asyncio.run(test_website_fetch())
    print(f"Test result: {'SUCCESS' if result else 'FAILED'}")
    print("Check test_outputs/fetch_test_log.txt for detailed logs")
    print("Check test_outputs/ directory for output files")
