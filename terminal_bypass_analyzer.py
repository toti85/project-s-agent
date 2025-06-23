#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Terminal Bypass Website Analyzer
================================
This script bypasses terminal output issues by writing everything to files.
Uses the stable v0.6.0 foundation to analyze shayanwaters.com.
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

class TerminalBypassAnalyzer:
    """
    Website analyzer that bypasses terminal issues by writing everything to files.
    """
    
    def __init__(self):
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "status": "starting",
            "logs": [],
            "analysis": {},
            "errors": []
        }
        
        # Create output directories
        os.makedirs('analysis_reports', exist_ok=True)
        os.makedirs('logs', exist_ok=True)
        
        self.log("TerminalBypassAnalyzer initialized")
    
    def log(self, message):
        """Log a message to both memory and file."""
        timestamp = datetime.now().strftime('%H:%M:%S')
        log_entry = f"[{timestamp}] {message}"
        self.results["logs"].append(log_entry)
        
        # Write to file immediately
        with open('logs/terminal_bypass.log', 'a', encoding='utf-8') as f:
            f.write(log_entry + '\n')
    
    def save_status(self):
        """Save current status to file."""
        with open('analysis_reports/current_status.json', 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)
    
    async def test_web_tool(self):
        """Test if WebPageFetchTool is available and working."""
        try:
            self.log("Testing WebPageFetchTool availability...")
            
            # Try to import the tool
            from tools.web_tools import WebPageFetchTool
            self.log("✅ WebPageFetchTool imported successfully")
            
            # Test with a simple URL first
            tool = WebPageFetchTool()
            test_url = "https://httpbin.org/html"
            
            self.log(f"Testing with URL: {test_url}")
            result = await tool.execute(url=test_url, extract_text=True, timeout=10)
            
            if result.get("success"):
                self.log("✅ WebPageFetchTool test successful")
                self.log(f"   Status: {result.get('status_code', 'unknown')}")
                self.log(f"   Title: {result.get('title', 'none')}")
                return True
            else:
                self.log(f"❌ WebPageFetchTool test failed: {result.get('error', 'unknown')}")
                return False
                
        except ImportError as e:
            self.log(f"❌ WebPageFetchTool not available: {e}")
            return False
        except Exception as e:
            self.log(f"❌ WebPageFetchTool test exception: {e}")
            return False
    
    async def analyze_website(self, url="https://shayanwaters.com"):
        """Analyze the target website."""
        try:
            self.log(f"Starting website analysis: {url}")
            
            # Import and use WebPageFetchTool
            from tools.web_tools import WebPageFetchTool
            tool = WebPageFetchTool()
            
            # Fetch the website
            self.log("Fetching website content...")
            result = await tool.execute(url=url, extract_text=True, timeout=30)
            
            if not result.get("success"):
                error_msg = result.get('error', 'Unknown error')
                self.log(f"❌ Failed to fetch website: {error_msg}")
                self.results["errors"].append(f"Fetch failed: {error_msg}")
                return False
            
            # Extract data
            html_content = result.get("html", "")
            text_content = result.get("text", "")
            title = result.get("title", "")
            status_code = result.get("status_code", 0)
            
            self.log(f"✅ Website fetched successfully")
            self.log(f"   Status: {status_code}")
            self.log(f"   Title: {title}")
            self.log(f"   HTML length: {len(html_content)} chars")
            self.log(f"   Text length: {len(text_content)} chars")
            
            # Perform basic analysis
            analysis = {
                "url": url,
                "fetch_timestamp": datetime.now().isoformat(),
                "status_code": status_code,
                "title": title,
                "content_stats": {
                    "html_length": len(html_content),
                    "text_length": len(text_content),
                    "has_content": len(text_content) > 100
                },
                "basic_seo": {
                    "has_title": bool(title and len(title) > 0),
                    "title_length": len(title) if title else 0,
                    "title_in_good_range": 30 <= len(title) <= 60 if title else False
                }
            }
            
            # Count basic elements in HTML
            if html_content:
                analysis["html_elements"] = {
                    "h1_tags": html_content.lower().count('<h1'),
                    "h2_tags": html_content.lower().count('<h2'),
                    "img_tags": html_content.lower().count('<img'),
                    "link_tags": html_content.lower().count('<a '),
                    "meta_tags": html_content.lower().count('<meta')
                }
            
            self.results["analysis"] = analysis
            self.log("✅ Basic analysis completed")
            
            # Save detailed results
            report_file = f"analysis_reports/shayanwaters_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump({
                    "analysis": analysis,
                    "raw_data": {
                        "html": html_content[:5000] + "..." if len(html_content) > 5000 else html_content,
                        "text": text_content[:2000] + "..." if len(text_content) > 2000 else text_content
                    }
                }, f, indent=2, ensure_ascii=False)
            
            self.log(f"✅ Detailed report saved: {report_file}")
            return True
            
        except Exception as e:
            self.log(f"❌ Website analysis failed: {e}")
            self.results["errors"].append(f"Analysis failed: {str(e)}")
            return False
    
    async def run_analysis(self):
        """Run the complete analysis workflow."""
        try:
            self.log("=" * 50)
            self.log("Terminal Bypass Website Analyzer Starting")
            self.log("=" * 50)
            
            self.results["status"] = "running"
            self.save_status()
            
            # Test web tool first
            web_tool_ok = await self.test_web_tool()
            if not web_tool_ok:
                self.log("❌ Cannot proceed - WebPageFetchTool not working")
                self.results["status"] = "failed_web_tool"
                self.save_status()
                return False
            
            # Analyze the target website
            analysis_ok = await self.analyze_website()
            if not analysis_ok:
                self.log("❌ Website analysis failed")
                self.results["status"] = "failed_analysis"
                self.save_status()
                return False
            
            self.log("✅ Analysis completed successfully")
            self.results["status"] = "completed"
            self.save_status()
            
            # Create summary report
            self.create_summary_report()
            
            return True
            
        except Exception as e:
            self.log(f"❌ Fatal error: {e}")
            self.results["status"] = "fatal_error"
            self.results["errors"].append(f"Fatal: {str(e)}")
            self.save_status()
            return False
    
    def create_summary_report(self):
        """Create a human-readable summary report."""
        try:
            analysis = self.results.get("analysis", {})
            
            summary = f"""
SHAYANWATERS.COM ANALYSIS SUMMARY
================================
Timestamp: {self.results['timestamp']}
Status: {self.results['status']}

BASIC INFORMATION:
- URL: {analysis.get('url', 'N/A')}
- Status Code: {analysis.get('status_code', 'N/A')}
- Title: {analysis.get('title', 'N/A')}

CONTENT STATISTICS:
- HTML Length: {analysis.get('content_stats', {}).get('html_length', 'N/A')} characters
- Text Length: {analysis.get('content_stats', {}).get('text_length', 'N/A')} characters
- Has Content: {analysis.get('content_stats', {}).get('has_content', 'N/A')}

SEO ANALYSIS:
- Has Title: {analysis.get('basic_seo', {}).get('has_title', 'N/A')}
- Title Length: {analysis.get('basic_seo', {}).get('title_length', 'N/A')} characters
- Title Length OK: {analysis.get('basic_seo', {}).get('title_in_good_range', 'N/A')}

HTML ELEMENTS:
- H1 Tags: {analysis.get('html_elements', {}).get('h1_tags', 'N/A')}
- H2 Tags: {analysis.get('html_elements', {}).get('h2_tags', 'N/A')}
- Images: {analysis.get('html_elements', {}).get('img_tags', 'N/A')}
- Links: {analysis.get('html_elements', {}).get('link_tags', 'N/A')}
- Meta Tags: {analysis.get('html_elements', {}).get('meta_tags', 'N/A')}

LOGS:
{chr(10).join(self.results.get('logs', []))}

ERRORS:
{chr(10).join(self.results.get('errors', ['None']))}
"""
            
            summary_file = 'analysis_reports/SUMMARY_REPORT.txt'
            with open(summary_file, 'w', encoding='utf-8') as f:
                f.write(summary)
            
            self.log(f"✅ Summary report created: {summary_file}")
            
        except Exception as e:
            self.log(f"❌ Failed to create summary: {e}")

async def main():
    """Main entry point."""
    analyzer = TerminalBypassAnalyzer()
    
    try:
        success = await analyzer.run_analysis()
        if success:
            analyzer.log("=" * 50)
            analyzer.log("ANALYSIS COMPLETED SUCCESSFULLY")
            analyzer.log("Check analysis_reports/ directory for results")
            analyzer.log("=" * 50)
        else:
            analyzer.log("=" * 50)
            analyzer.log("ANALYSIS FAILED")
            analyzer.log("Check logs/ directory for error details")
            analyzer.log("=" * 50)
    
    except Exception as e:
        analyzer.log(f"Fatal error in main: {e}")
    
    finally:
        analyzer.save_status()

if __name__ == "__main__":
    asyncio.run(main())
