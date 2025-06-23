import asyncio
import sys
import json
import os
from datetime import datetime

sys.path.append('.')
from tools.web_tools import WebPageFetchTool

async def fetch():
    print("Starting website analysis...")
    
    # Create directory
    os.makedirs('shayanwaters_analysis', exist_ok=True)
    
    web_tool = WebPageFetchTool()
    result = await web_tool.execute(url='https://shayanwaters.com', extract_text=True, timeout=30)
    
    if result.get('success'):
        html = result.get('html', '')
        text = result.get('text', '')
        
        data = {
            'timestamp': datetime.now().isoformat(),
            'url': 'https://shayanwaters.com',
            'status_code': result.get('status_code'),
            'title': result.get('title', ''),
            'html_size': len(html),
            'text_size': len(text),
            'word_count': len(text.split()) if text else 0,
            'basic_seo': {
                'has_title': bool(result.get('title')),
                'has_meta_description': 'meta name="description"' in html.lower(),
                'has_h1': '<h1' in html.lower(),
                'has_viewport': 'viewport' in html.lower()
            }
        }
        
        # Save JSON
        json_file = 'shayanwaters_analysis/analysis_result.json'
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        # Save summary
        summary_file = 'shayanwaters_analysis/summary.txt'
        summary = f"""SHAYANWATERS.COM ANALYSIS SUMMARY
Date: {data['timestamp'][:19]}
Status: {data['status_code']}
Title: {data['title']}
Size: {data['html_size']:,} chars
Words: {data['word_count']:,}

SEO Check:
- Has Title: {'Yes' if data['basic_seo']['has_title'] else 'No'}
- Has Meta Description: {'Yes' if data['basic_seo']['has_meta_description'] else 'No'}
- Has H1: {'Yes' if data['basic_seo']['has_h1'] else 'No'}
- Has Viewport: {'Yes' if data['basic_seo']['has_viewport'] else 'No'}
"""
        
        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write(summary)
        
        print(f"SUCCESS!")
        print(f"Title: {data['title']}")
        print(f"Words: {data['word_count']:,}")
        print(f"Files saved in shayanwaters_analysis/")
        
    else:
        error_msg = result.get('error', 'Unknown error')
        print(f"FAILED: {error_msg}")
        
        # Save error
        with open('shayanwaters_analysis/error.txt', 'w', encoding='utf-8') as f:
            f.write(f"Error: {error_msg}\nTime: {datetime.now()}")

if __name__ == "__main__":
    asyncio.run(fetch())
