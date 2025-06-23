#!/usr/bin/env python3
"""
Terminal-Safe Website Analyzer - writes to analysis_results directory
"""
import asyncio
import json
import sys
import os
from datetime import datetime

def log_to_file(message):
    """Write log messages to file since terminal output is not visible"""
    log_file = 'analysis_results/analyzer_log.txt'
    with open(log_file, 'a', encoding='utf-8') as f:
        f.write(f"{datetime.now().strftime('%H:%M:%S')} - {message}\n")

def write_result(filename, content):
    """Write results to file"""
    filepath = f'analysis_results/{filename}'
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    log_to_file(f"Saved: {filepath}")

async def main():
    log_to_file("=== STARTING WEBSITE ANALYSIS ===")
    
    # Import the web tool
    sys.path.append('.')
    try:
        from tools.web_tools import WebPageFetchTool
        log_to_file("✅ WebPageFetchTool imported")
    except Exception as e:
        log_to_file(f"❌ Import failed: {e}")
        return
    
    # Fetch the website
    try:
        web_tool = WebPageFetchTool()
        log_to_file("🌐 Fetching shayanwaters.com...")
        
        result = await web_tool.execute(
            url="https://shayanwaters.com",
            extract_text=True,
            timeout=30
        )
        
        if result.get('success'):
            html = result.get('html', '')
            text = result.get('text', '')
            title = result.get('title', '')
            status_code = result.get('status_code', 0)
            
            log_to_file(f"✅ Fetch successful - Status: {status_code}")
            log_to_file(f"   Title: {title}")
            log_to_file(f"   HTML size: {len(html):,} chars")
            log_to_file(f"   Text size: {len(text):,} chars")
            
            # Quick SEO analysis
            html_lower = html.lower()
            words = text.split() if text else []
            
            analysis = {
                'title': title,
                'status_code': status_code,
                'html_size': len(html),
                'text_size': len(text),
                'word_count': len(words),
                'has_meta_description': 'meta name="description"' in html_lower,
                'has_h1': '<h1' in html_lower,
                'has_viewport': 'viewport' in html_lower,
                'image_count': html_lower.count('<img'),
                'link_count': html_lower.count('<a href')
            }
            
            # Create quick report
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            
            # JSON report
            write_result(f'shayanwaters_quick_{timestamp}.json', json.dumps(analysis, indent=2))
            
            # Human readable report
            report = f"""SHAYANWATERS.COM ANALYSIS REPORT
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

BASIC INFO:
- Title: {title}
- Status: {status_code}
- Size: {len(html):,} characters ({round(len(html)/1024, 1)} KB)
- Words: {len(words):,}

SEO CHECKS:
- Meta Description: {'✅ Yes' if analysis['has_meta_description'] else '❌ No'}
- H1 Heading: {'✅ Yes' if analysis['has_h1'] else '❌ No'}
- Viewport Meta: {'✅ Yes' if analysis['has_viewport'] else '❌ No'}
- Images: {analysis['image_count']}
- Links: {analysis['link_count']}

QUICK SCORE:
Score: {sum([analysis['has_meta_description'], analysis['has_h1'], analysis['has_viewport']]) * 25}/75

RECOMMENDATIONS:
{'' if analysis['has_meta_description'] else '• Add meta description tag\n'}{'' if analysis['has_h1'] else '• Add H1 heading\n'}{'' if analysis['has_viewport'] else '• Add viewport meta tag\n'}{'• Website looks good!' if all([analysis['has_meta_description'], analysis['has_h1'], analysis['has_viewport']]) else ''}

---
Report by Project-S Website Analyzer
"""
            
            write_result(f'shayanwaters_report_{timestamp}.txt', report)
            
            log_to_file("🎉 ANALYSIS COMPLETE!")
            log_to_file(f"Files saved with timestamp: {timestamp}")
            
        else:
            error = result.get('error', 'Unknown error')
            log_to_file(f"❌ Fetch failed: {error}")
            write_result(f'error_{datetime.now().strftime("%Y%m%d_%H%M%S")}.txt', f"Error: {error}")
            
    except Exception as e:
        log_to_file(f"❌ Exception occurred: {str(e)}")
        write_result(f'exception_{datetime.now().strftime("%Y%m%d_%H%M%S")}.txt', f"Exception: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main())
