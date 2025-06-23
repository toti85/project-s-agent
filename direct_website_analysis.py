#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Direct Website Analysis Runner
==============================
Directly analyzes shayanwaters.com and saves results to files.
Bypasses terminal issues completely.
"""

import asyncio
import json
import sys
import os
from datetime import datetime
from pathlib import Path

# Ensure UTF-8 encoding
import io
if sys.platform.startswith('win'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Setup paths
project_root = Path(__file__).parent.absolute()
sys.path.append(str(project_root))

def write_log(message, filename='direct_analysis.log'):
    """Write log message to file."""
    timestamp = datetime.now().strftime('%H:%M:%S')
    log_entry = f"[{timestamp}] {message}"
    
    os.makedirs('logs', exist_ok=True)
    with open(f'logs/{filename}', 'a', encoding='utf-8') as f:
        f.write(log_entry + '\n')

def save_json(data, filename):
    """Save data as JSON."""
    os.makedirs('analysis_reports', exist_ok=True)
    with open(f'analysis_reports/{filename}', 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

async def run_direct_analysis():
    """Run direct website analysis."""
    analysis_results = {
        "timestamp": datetime.now().isoformat(),
        "status": "starting",
        "target_url": "https://shayanwaters.com",
        "logs": [],
        "analysis": {},
        "errors": []
    }
    
    try:
        write_log("=== DIRECT WEBSITE ANALYSIS STARTING ===")
        write_log("Target: https://shayanwaters.com")
        
        # Try to import WebPageFetchTool
        write_log("Importing WebPageFetchTool...")
        from tools.web_tools import WebPageFetchTool
        write_log("✅ WebPageFetchTool imported successfully")
        
        # Create tool instance
        web_tool = WebPageFetchTool()
        write_log("WebPageFetchTool instance created")
        
        # Fetch the website
        write_log("Fetching shayanwaters.com...")
        result = await web_tool.execute(
            url="https://shayanwaters.com",
            extract_text=True,
            timeout=30
        )
        
        if result.get("success"):
            write_log("✅ Website fetch successful")
            
            # Extract key information
            html_content = result.get("html", "")
            text_content = result.get("text", "")
            title = result.get("title", "")
            status_code = result.get("status_code", 0)
            
            write_log(f"Status Code: {status_code}")
            write_log(f"Title: {title}")
            write_log(f"HTML Length: {len(html_content)} chars")
            write_log(f"Text Length: {len(text_content)} chars")
            
            # Perform basic analysis
            analysis = {
                "fetch_info": {
                    "url": "https://shayanwaters.com",
                    "status_code": status_code,
                    "fetch_timestamp": datetime.now().isoformat(),
                    "success": True
                },
                "content_info": {
                    "title": title,
                    "title_length": len(title) if title else 0,
                    "html_size": len(html_content),
                    "text_size": len(text_content),
                    "has_substantial_content": len(text_content) > 500
                },
                "seo_basic": {
                    "has_title": bool(title),
                    "title_length_ok": 30 <= len(title) <= 60 if title else False,
                    "estimated_word_count": len(text_content.split()) if text_content else 0
                }
            }
            
            # Count HTML elements
            if html_content:
                html_lower = html_content.lower()
                analysis["html_structure"] = {
                    "h1_count": html_lower.count('<h1'),
                    "h2_count": html_lower.count('<h2'),
                    "h3_count": html_lower.count('<h3'),
                    "img_count": html_lower.count('<img'),
                    "link_count": html_lower.count('<a '),
                    "meta_count": html_lower.count('<meta'),
                    "script_count": html_lower.count('<script'),
                    "style_count": html_lower.count('<style')
                }
            
            analysis_results["analysis"] = analysis
            analysis_results["status"] = "completed"
            
            write_log("✅ Analysis completed successfully")
            
            # Save detailed results
            timestamp_str = datetime.now().strftime('%Y%m%d_%H%M%S')
            
            # Save analysis results
            save_json(analysis_results, f'shayanwaters_analysis_{timestamp_str}.json')
            write_log(f"Analysis saved to: shayanwaters_analysis_{timestamp_str}.json")
            
            # Save raw content (truncated)
            raw_data = {
                "html_content": html_content[:10000] + "..." if len(html_content) > 10000 else html_content,
                "text_content": text_content[:5000] + "..." if len(text_content) > 5000 else text_content,
                "full_result": result
            }
            save_json(raw_data, f'raw_content_{timestamp_str}.json')
            write_log(f"Raw content saved to: raw_content_{timestamp_str}.json")
            
            # Create summary report
            summary = f"""
SHAYANWATERS.COM ANALYSIS REPORT
===============================
Analysis Time: {analysis['fetch_info']['fetch_timestamp']}
Status: SUCCESS

BASIC INFORMATION:
- URL: {analysis['fetch_info']['url']}
- HTTP Status: {analysis['fetch_info']['status_code']}
- Page Title: {analysis['content_info']['title']}
- Title Length: {analysis['content_info']['title_length']} characters

CONTENT ANALYSIS:
- HTML Size: {analysis['content_info']['html_size']:,} characters
- Text Content: {analysis['content_info']['text_size']:,} characters
- Word Count: ~{analysis['seo_basic']['estimated_word_count']:,} words
- Substantial Content: {'Yes' if analysis['content_info']['has_substantial_content'] else 'No'}

SEO BASICS:
- Has Title: {'Yes' if analysis['seo_basic']['has_title'] else 'No'}
- Title Length Good: {'Yes' if analysis['seo_basic']['title_length_ok'] else 'No'}

HTML STRUCTURE:
- H1 Tags: {analysis.get('html_structure', {}).get('h1_count', 'N/A')}
- H2 Tags: {analysis.get('html_structure', {}).get('h2_count', 'N/A')}
- H3 Tags: {analysis.get('html_structure', {}).get('h3_count', 'N/A')}
- Images: {analysis.get('html_structure', {}).get('img_count', 'N/A')}
- Links: {analysis.get('html_structure', {}).get('link_count', 'N/A')}
- Meta Tags: {analysis.get('html_structure', {}).get('meta_count', 'N/A')}

TECHNICAL:
- Scripts: {analysis.get('html_structure', {}).get('script_count', 'N/A')}
- Style Tags: {analysis.get('html_structure', {}).get('style_count', 'N/A')}

ASSESSMENT:
The website appears to be {'properly structured' if analysis.get('html_structure', {}).get('h1_count', 0) > 0 else 'missing proper heading structure'}.
Content volume is {'adequate' if analysis['content_info']['has_substantial_content'] else 'limited'}.
SEO title is {'optimized' if analysis['seo_basic']['title_length_ok'] else 'needs optimization'}.
"""
            
            with open('analysis_reports/ANALYSIS_SUMMARY.txt', 'w', encoding='utf-8') as f:
                f.write(summary)
            
            write_log("✅ Summary report created: ANALYSIS_SUMMARY.txt")
            write_log("=== ANALYSIS COMPLETE ===")
            
            return True
            
        else:
            error_msg = result.get('error', 'Unknown error')
            write_log(f"❌ Website fetch failed: {error_msg}")
            analysis_results["status"] = "fetch_failed"
            analysis_results["errors"].append(error_msg)
            save_json(analysis_results, 'failed_analysis.json')
            return False
            
    except ImportError as e:
        write_log(f"❌ Import error: {e}")
        analysis_results["status"] = "import_error"
        analysis_results["errors"].append(f"Import error: {str(e)}")
        save_json(analysis_results, 'import_error.json')
        return False
        
    except Exception as e:
        write_log(f"❌ Unexpected error: {e}")
        analysis_results["status"] = "unexpected_error"
        analysis_results["errors"].append(f"Unexpected error: {str(e)}")
        save_json(analysis_results, 'unexpected_error.json')
        return False

def main():
    """Main function."""
    try:
        write_log("Starting direct analysis script")
        result = asyncio.run(run_direct_analysis())
        write_log(f"Analysis result: {'SUCCESS' if result else 'FAILED'}")
        
        # Always create a completion marker
        with open('analysis_reports/COMPLETION_STATUS.txt', 'w', encoding='utf-8') as f:
            f.write(f"Analysis completed at: {datetime.now().isoformat()}\n")
            f.write(f"Result: {'SUCCESS' if result else 'FAILED'}\n")
            f.write("Check logs/direct_analysis.log for details\n")
        
    except Exception as e:
        write_log(f"Fatal error in main: {e}")
        with open('analysis_reports/FATAL_ERROR.txt', 'w', encoding='utf-8') as f:
            f.write(f"Fatal error: {str(e)}\n")
            f.write(f"Time: {datetime.now().isoformat()}\n")

if __name__ == "__main__":
    main()
