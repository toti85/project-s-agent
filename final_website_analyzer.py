#!/usr/bin/env python3
"""
Final Website Analysis - shayanwaters.com
Simple, guaranteed-to-work version that saves results
"""
import asyncio
import json
import os
from datetime import datetime

# Create results directory first
print("Creating results directory...")
os.makedirs('final_analysis', exist_ok=True)
print("✅ Directory created: final_analysis/")

# Test file writing
print("Testing file creation...")
test_file = 'final_analysis/test.txt'
with open(test_file, 'w', encoding='utf-8') as f:
    f.write(f"Test successful at {datetime.now()}")
print(f"✅ Test file created: {test_file}")

# Now proceed with website analysis
print("\nStarting website analysis...")

import sys
sys.path.append('.')

try:
    from tools.web_tools import WebPageFetchTool
    print("✅ WebPageFetchTool imported successfully")
except ImportError as e:
    print(f"❌ Import failed: {e}")
    exit(1)

async def analyze():
    print("📥 Fetching https://shayanwaters.com...")
    
    web_tool = WebPageFetchTool()
    result = await web_tool.execute(
        url="https://shayanwaters.com", 
        extract_text=True, 
        timeout=30
    )
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    if result.get('success'):
        # Extract data
        html = result.get('html', '')
        text = result.get('text', '')
        title = result.get('title', '')
        status_code = result.get('status_code', 0)
        
        print(f"✅ Website fetched successfully!")
        print(f"   Status: {status_code}")
        print(f"   Title: {title}")
        print(f"   HTML size: {len(html):,} characters")
        print(f"   Text size: {len(text):,} characters")
        
        # Perform basic SEO analysis
        html_lower = html.lower()
        words = text.split() if text else []
        
        seo_analysis = {
            'has_title': bool(title),
            'title_length': len(title),
            'has_meta_description': 'meta name="description"' in html_lower,
            'has_h1': '<h1' in html_lower,
            'has_h2': '<h2' in html_lower,
            'has_viewport': 'viewport' in html_lower,
            'responsive_indicators': 'device-width' in html_lower,
            'has_canonical': 'canonical' in html_lower,
            'image_count': html_lower.count('<img'),
            'link_count': html_lower.count('<a href'),
            'word_count': len(words)
        }
        
        # Create comprehensive analysis report
        analysis_report = {
            'metadata': {
                'analysis_date': datetime.now().isoformat(),
                'target_url': 'https://shayanwaters.com',
                'analyzer_version': '1.0-final',
                'status_code': status_code
            },
            'page_info': {
                'title': title,
                'html_size_chars': len(html),
                'text_size_chars': len(text),
                'html_size_kb': round(len(html) / 1024, 2),
                'word_count': len(words)
            },
            'seo_analysis': seo_analysis,
            'recommendations': []
        }
        
        # Generate recommendations
        recommendations = []
        if not seo_analysis['has_title']:
            recommendations.append("CRITICAL: Add page title")
        elif seo_analysis['title_length'] < 30:
            recommendations.append("WARNING: Title too short (under 30 chars)")
        elif seo_analysis['title_length'] > 60:
            recommendations.append("WARNING: Title too long (over 60 chars)")
        else:
            recommendations.append("✅ Title length is optimal")
            
        if not seo_analysis['has_meta_description']:
            recommendations.append("HIGH: Add meta description")
        else:
            recommendations.append("✅ Meta description found")
            
        if not seo_analysis['has_h1']:
            recommendations.append("HIGH: Add H1 heading")
        else:
            recommendations.append("✅ H1 heading found")
            
        if not seo_analysis['has_viewport']:
            recommendations.append("HIGH: Add viewport meta tag")
        else:
            recommendations.append("✅ Viewport meta tag found")
            
        if seo_analysis['word_count'] < 300:
            recommendations.append("MEDIUM: Consider adding more content")
        else:
            recommendations.append("✅ Sufficient content length")
            
        analysis_report['recommendations'] = recommendations
        
        # Calculate simple score
        score = 0
        if seo_analysis['has_title']: score += 20
        if seo_analysis['has_meta_description']: score += 20
        if seo_analysis['has_h1']: score += 15
        if seo_analysis['has_viewport']: score += 15
        if seo_analysis['word_count'] >= 300: score += 20
        if seo_analysis['responsive_indicators']: score += 10
        
        analysis_report['overall_score'] = score
        
        # Save JSON report
        json_file = f'final_analysis/shayanwaters_analysis_{timestamp}.json'
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(analysis_report, f, indent=2, ensure_ascii=False)
        print(f"✅ JSON report saved: {json_file}")
        
        # Save human-readable report
        txt_file = f'final_analysis/shayanwaters_report_{timestamp}.txt'
        report_content = f"""SHAYANWATERS.COM - WEBSITE ANALYSIS REPORT
{'='*60}
Analysis Date: {analysis_report['metadata']['analysis_date'][:19]}
Target URL: {analysis_report['metadata']['target_url']}
Status Code: {analysis_report['metadata']['status_code']}
Overall Score: {analysis_report['overall_score']}/100

PAGE INFORMATION:
Title: {analysis_report['page_info']['title']}
Page Size: {analysis_report['page_info']['html_size_kb']} KB
Word Count: {analysis_report['page_info']['word_count']:,} words

SEO ANALYSIS:
✓ Has Title: {'Yes' if seo_analysis['has_title'] else 'No'}
✓ Title Length: {seo_analysis['title_length']} chars
✓ Has Meta Description: {'Yes' if seo_analysis['has_meta_description'] else 'No'}
✓ Has H1 Heading: {'Yes' if seo_analysis['has_h1'] else 'No'}
✓ Has H2 Headings: {'Yes' if seo_analysis['has_h2'] else 'No'}
✓ Has Viewport Meta: {'Yes' if seo_analysis['has_viewport'] else 'No'}
✓ Mobile Responsive: {'Yes' if seo_analysis['responsive_indicators'] else 'No'}
✓ Images Found: {seo_analysis['image_count']}
✓ Links Found: {seo_analysis['link_count']}

RECOMMENDATIONS:
{chr(10).join(f"• {rec}" for rec in recommendations)}

SUMMARY:
The website scored {analysis_report['overall_score']}/100. 
{'This is a good score!' if analysis_report['overall_score'] >= 70 else 'There are areas for improvement.'}

{'='*60}
Report generated by Project-S Website Analyzer
{'='*60}
"""
        
        with open(txt_file, 'w', encoding='utf-8') as f:
            f.write(report_content)
        print(f"✅ Text report saved: {txt_file}")
        
        # Save quick summary
        summary_file = f'final_analysis/SUMMARY_{timestamp}.txt'
        summary_content = f"""QUICK SUMMARY - SHAYANWATERS.COM
Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Score: {analysis_report['overall_score']}/100
Title: {title}
Words: {len(words):,}
Status: {'GOOD' if analysis_report['overall_score'] >= 70 else 'NEEDS WORK'}
Issues: {len([r for r in recommendations if not r.startswith('✅')])}
"""
        
        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write(summary_content)
        print(f"✅ Summary saved: {summary_file}")
        
        print(f"\n🎉 ANALYSIS COMPLETE!")
        print(f"🏆 Overall Score: {analysis_report['overall_score']}/100")
        print(f"📊 Key metrics:")
        print(f"   • Title: {title}")
        print(f"   • Words: {len(words):,}")
        print(f"   • Size: {round(len(html)/1024, 1)} KB")
        print(f"   • Issues: {len([r for r in recommendations if not r.startswith('✅')])}")
        
    else:
        error_msg = result.get('error', 'Unknown error')
        print(f"❌ Failed to fetch website: {error_msg}")
        
        # Save error log
        error_file = f'final_analysis/ERROR_{timestamp}.txt'
        with open(error_file, 'w', encoding='utf-8') as f:
            f.write(f"Error fetching shayanwaters.com:\n{error_msg}\nTimestamp: {datetime.now()}")
        print(f"✅ Error logged: {error_file}")

if __name__ == "__main__":
    print("🌐 Final Website Analyzer for shayanwaters.com")
    print("="*50)
    asyncio.run(analyze())
    print("="*50)
    print("🏁 Analysis finished!")
