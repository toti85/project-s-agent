#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Stable Website Analyzer
Based on the working Project-S v0.6.0 foundation
Analyzes shayanwaters.com and saves results to files
"""

import asyncio
import json
import os
import sys
import logging
from datetime import datetime
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='[%(asctime)s] [%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)

# Setup paths
project_root = Path(__file__).parent.absolute()
sys.path.append(str(project_root))

# Create output directories
os.makedirs('analysis_reports', exist_ok=True)
os.makedirs('logs', exist_ok=True)

# Import the working tools
try:
    from tools.web_tools import WebPageFetchTool
    from tools.file_tools import FileWriteTool
    logger.info("✅ Tools imported successfully")
except ImportError as e:
    logger.error(f"❌ Failed to import tools: {e}")
    sys.exit(1)

class WebsiteAnalyzer:
    """Simple but comprehensive website analyzer"""
    
    def __init__(self):
        self.web_tool = WebPageFetchTool()
        self.file_tool = FileWriteTool()
        self.report = {
            "timestamp": datetime.now().isoformat(),
            "analyzer_version": "1.0.0",
            "target_url": "",
            "analysis": {},
            "recommendations": [],
            "score": 0
        }
    
    async def analyze_website(self, url: str) -> dict:
        """Analyze a website comprehensively"""
        logger.info(f"🔍 Starting analysis of: {url}")
        self.report["target_url"] = url
        
        try:
            # Fetch webpage content
            result = await self.web_tool.execute(url=url, extract_text=True, timeout=30)
            
            if not result.get("success"):
                logger.error(f"❌ Failed to fetch webpage: {result.get('error', 'Unknown error')}")
                return {"success": False, "error": result.get('error', 'Failed to fetch webpage')}
            
            html_content = result.get("html", "")
            text_content = result.get("text", "")
            title = result.get("title", "")
            status_code = result.get("status_code", 0)
            
            logger.info(f"✅ Webpage fetched successfully (Status: {status_code})")
            logger.info(f"   - HTML length: {len(html_content)} chars")
            logger.info(f"   - Text length: {len(text_content)} chars")
            logger.info(f"   - Title: {title}")
            
            # Perform analysis
            analysis = await self._analyze_content(html_content, text_content, title, status_code)
            self.report["analysis"] = analysis
            
            # Generate recommendations and score
            self._generate_recommendations()
            self._calculate_score()
            
            # Save report
            report_file = f"analysis_reports/website_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            await self._save_report(report_file)
            
            logger.info(f"✅ Analysis complete. Report saved to: {report_file}")
            logger.info(f"🏆 Overall Score: {self.report['score']}/100")
            
            return {
                "success": True, 
                "report": self.report,
                "report_file": report_file
            }
            
        except Exception as e:
            logger.error(f"❌ Analysis failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def _analyze_content(self, html: str, text: str, title: str, status_code: int) -> dict:
        """Analyze webpage content"""
        analysis = {}
        
        # Basic metrics
        analysis["basic_metrics"] = {
            "status_code": status_code,
            "html_size_chars": len(html),
            "text_size_chars": len(text),
            "html_to_text_ratio": round(len(text) / len(html) * 100, 2) if len(html) > 0 else 0
        }
        
        # Title analysis
        analysis["title_analysis"] = {
            "title": title,
            "length": len(title),
            "has_title": bool(title),
            "optimal_length": 30 <= len(title) <= 60 if title else False
        }
        
        # Content analysis
        html_lower = html.lower()
        analysis["seo_analysis"] = {
            "has_meta_description": "meta name=\"description\"" in html_lower,
            "has_h1_tags": "<h1" in html_lower,
            "has_h2_tags": "<h2" in html_lower,
            "has_images": "<img" in html_lower,
            "has_links": "<a href" in html_lower,
            "has_canonical": "rel=\"canonical\"" in html_lower
        }
        
        # Technical analysis
        analysis["technical_analysis"] = {
            "has_viewport_meta": "viewport" in html_lower,
            "has_charset_meta": "charset" in html_lower,
            "has_css": "<link" in html_lower or "<style" in html_lower,
            "has_javascript": "<script" in html_lower,
            "responsive_indicators": "viewport" in html_lower and "device-width" in html_lower
        }
        
        # Content quality
        words = text.split() if text else []
        analysis["content_quality"] = {
            "word_count": len(words),
            "average_word_length": round(sum(len(word) for word in words) / len(words), 2) if words else 0,
            "has_sufficient_content": len(words) >= 300,
            "content_density": round(len(text) / len(html) * 100, 2) if len(html) > 0 else 0
        }
        
        return analysis
    
    def _generate_recommendations(self):
        """Generate SEO and improvement recommendations"""
        recommendations = []
        analysis = self.report["analysis"]
        
        # Title recommendations
        title_analysis = analysis.get("title_analysis", {})
        if not title_analysis.get("has_title"):
            recommendations.append("❌ CRITICAL: Add a page title")
        elif not title_analysis.get("optimal_length"):
            if title_analysis.get("length", 0) < 30:
                recommendations.append("⚠️  Title too short. Aim for 30-60 characters")
            elif title_analysis.get("length", 0) > 60:
                recommendations.append("⚠️  Title too long. Keep under 60 characters")
        else:
            recommendations.append("✅ Title length is optimal")
        
        # SEO recommendations
        seo = analysis.get("seo_analysis", {})
        if not seo.get("has_meta_description"):
            recommendations.append("❌ Add meta description for better SEO")
        if not seo.get("has_h1_tags"):
            recommendations.append("❌ Add H1 heading tags for better structure")
        if not seo.get("has_h2_tags"):
            recommendations.append("⚠️  Consider adding H2 subheadings")
        if seo.get("has_canonical"):
            recommendations.append("✅ Canonical URL is present")
        
        # Technical recommendations
        tech = analysis.get("technical_analysis", {})
        if not tech.get("has_viewport_meta"):
            recommendations.append("❌ Add viewport meta tag for mobile compatibility")
        if not tech.get("responsive_indicators"):
            recommendations.append("⚠️  Ensure responsive design implementation")
        if tech.get("has_css") and tech.get("has_javascript"):
            recommendations.append("✅ CSS and JavaScript resources detected")
        
        # Content recommendations
        content = analysis.get("content_quality", {})
        if not content.get("has_sufficient_content"):
            recommendations.append("⚠️  Consider adding more content (minimum 300 words recommended)")
        if content.get("word_count", 0) > 300:
            recommendations.append("✅ Good content length")
        
        self.report["recommendations"] = recommendations
    
    def _calculate_score(self):
        """Calculate overall website score"""
        score = 0
        analysis = self.report["analysis"]
        
        # Title scoring (20 points)
        title_analysis = analysis.get("title_analysis", {})
        if title_analysis.get("has_title"):
            score += 10
            if title_analysis.get("optimal_length"):
                score += 10
        
        # SEO scoring (40 points)
        seo = analysis.get("seo_analysis", {})
        seo_checks = ["has_meta_description", "has_h1_tags", "has_h2_tags", "has_images", "has_links"]
        for check in seo_checks:
            if seo.get(check):
                score += 8
        
        # Technical scoring (20 points)
        tech = analysis.get("technical_analysis", {})
        if tech.get("has_viewport_meta"):
            score += 10
        if tech.get("responsive_indicators"):
            score += 10
        
        # Content scoring (20 points)
        content = analysis.get("content_quality", {})
        if content.get("has_sufficient_content"):
            score += 20
        elif content.get("word_count", 0) > 100:
            score += 10
        
        self.report["score"] = min(score, 100)  # Cap at 100
    
    async def _save_report(self, filename: str):
        """Save analysis report to file"""
        try:
            report_json = json.dumps(self.report, indent=2, ensure_ascii=False)
            result = await self.file_tool.execute(path=filename, content=report_json)
            
            if result.get("success"):
                logger.info(f"✅ Report saved successfully: {filename}")
                
                # Also save a summary
                summary_file = filename.replace('.json', '_summary.txt')
                summary = self._generate_summary()
                await self.file_tool.execute(path=summary_file, content=summary)
                logger.info(f"✅ Summary saved: {summary_file}")
            else:
                logger.error(f"❌ Failed to save report: {result.get('error')}")
                
        except Exception as e:
            logger.error(f"❌ Error saving report: {e}")
    
    def _generate_summary(self) -> str:
        """Generate a human-readable summary"""
        summary_lines = [
            "=" * 60,
            f"WEBSITE ANALYSIS REPORT",
            "=" * 60,
            f"URL: {self.report['target_url']}",
            f"Analysis Date: {self.report['timestamp']}",
            f"Overall Score: {self.report['score']}/100",
            "",
            "📊 KEY METRICS:",
        ]
        
        # Add basic metrics
        basic = self.report["analysis"].get("basic_metrics", {})
        summary_lines.extend([
            f"  • Status Code: {basic.get('status_code', 'Unknown')}",
            f"  • Page Size: {basic.get('html_size_chars', 0):,} characters",
            f"  • Text Content: {basic.get('text_size_chars', 0):,} characters",
            f"  • Content Ratio: {basic.get('html_to_text_ratio', 0)}%",
            ""
        ])
        
        # Add title info
        title = self.report["analysis"].get("title_analysis", {})
        summary_lines.extend([
            "🏷️  TITLE ANALYSIS:",
            f"  • Title: {title.get('title', 'No title found')}",
            f"  • Length: {title.get('length', 0)} characters",
            ""
        ])
        
        # Add recommendations
        summary_lines.extend([
            "💡 RECOMMENDATIONS:",
        ])
        for rec in self.report.get("recommendations", []):
            summary_lines.append(f"  {rec}")
        
        summary_lines.extend([
            "",
            "=" * 60,
            f"Report generated by Project-S Website Analyzer v{self.report['analyzer_version']}",
            "=" * 60
        ])
        
        return "\n".join(summary_lines)

async def main():
    """Main function to run website analysis"""
    print("\n" + "=" * 60)
    print("🌐 Project-S Website Analyzer v1.0.0")
    print("=" * 60)
    
    # Target website
    target_url = "https://shayanwaters.com"
    
    # Create analyzer
    analyzer = WebsiteAnalyzer()
    
    try:
        # Run analysis
        result = await analyzer.analyze_website(target_url)
        
        if result.get("success"):
            print(f"\n✅ Analysis completed successfully!")
            print(f"📁 Report saved to: {result.get('report_file')}")
            print(f"🏆 Website Score: {result['report']['score']}/100")
            
            # Print quick summary
            print("\n📋 Quick Summary:")
            recommendations = result["report"].get("recommendations", [])
            for i, rec in enumerate(recommendations[:5]):  # Show first 5
                print(f"  {i+1}. {rec}")
            if len(recommendations) > 5:
                print(f"  ... and {len(recommendations) - 5} more recommendations")
            
        else:
            print(f"\n❌ Analysis failed: {result.get('error')}")
            
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        logger.error(f"Main function error: {e}")
    
    print("\n" + "=" * 60)
    print("🏁 Analysis Complete")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(main())
