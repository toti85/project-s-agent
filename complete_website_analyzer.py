#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Complete Website Analyzer v2.0
Comprehensive analysis of shayanwaters.com with detailed reporting
"""

import asyncio
import json
import os
import sys
import re
from datetime import datetime
from pathlib import Path

# Setup paths
project_root = Path(__file__).parent.absolute()
sys.path.append(str(project_root))

# Create output directories
os.makedirs('analysis_reports', exist_ok=True)
os.makedirs('logs', exist_ok=True)

print("🌐 Complete Website Analyzer v2.0")
print("=" * 50)

try:
    from tools.web_tools import WebPageFetchTool
    from tools.file_tools import FileWriteTool
    print("✅ Tools imported successfully")
except ImportError as e:
    print(f"❌ Failed to import tools: {e}")
    sys.exit(1)

class CompleteWebsiteAnalyzer:
    """Advanced website analyzer with comprehensive reporting"""
    
    def __init__(self):
        self.web_tool = WebPageFetchTool()
        self.file_tool = FileWriteTool()
        self.report = {
            "metadata": {
                "analyzer_version": "2.0.0",
                "analysis_date": datetime.now().isoformat(),
                "target_url": "",
                "analysis_duration_seconds": 0
            },
            "fetch_results": {},
            "seo_analysis": {},
            "technical_analysis": {},
            "content_analysis": {},
            "performance_analysis": {},
            "accessibility_analysis": {},
            "recommendations": [],
            "scores": {},
            "overall_score": 0
        }
    
    async def analyze_website(self, url: str) -> dict:
        """Perform comprehensive website analysis"""
        start_time = datetime.now()
        print(f"🔍 Starting comprehensive analysis of: {url}")
        self.report["metadata"]["target_url"] = url
        
        try:
            # Step 1: Fetch website content
            print("📥 Step 1: Fetching website content...")
            fetch_result = await self.web_tool.execute(url=url, extract_text=True, timeout=30)
            
            if not fetch_result.get("success"):
                error_msg = fetch_result.get('error', 'Unknown error')
                print(f"❌ Failed to fetch website: {error_msg}")
                return {"success": False, "error": error_msg}
            
            self.report["fetch_results"] = {
                "success": True,
                "status_code": fetch_result.get("status_code"),
                "title": fetch_result.get("title", ""),
                "html_size": len(fetch_result.get("html", "")),
                "text_size": len(fetch_result.get("text", "")),
                "fetch_time": str(datetime.now())
            }
            
            html_content = fetch_result.get("html", "")
            text_content = fetch_result.get("text", "")
            
            print(f"✅ Website fetched successfully")
            print(f"   📊 Status: {fetch_result.get('status_code')}")
            print(f"   📏 HTML: {len(html_content):,} chars")
            print(f"   📄 Text: {len(text_content):,} chars")
            
            # Step 2: SEO Analysis
            print("🔍 Step 2: SEO Analysis...")
            await self._analyze_seo(html_content, text_content)
            
            # Step 3: Technical Analysis
            print("⚙️ Step 3: Technical Analysis...")
            await self._analyze_technical(html_content)
            
            # Step 4: Content Analysis
            print("📝 Step 4: Content Analysis...")
            await self._analyze_content(html_content, text_content)
            
            # Step 5: Performance Analysis
            print("🚀 Step 5: Performance Analysis...")
            await self._analyze_performance(html_content)
            
            # Step 6: Accessibility Analysis
            print("♿ Step 6: Accessibility Analysis...")
            await self._analyze_accessibility(html_content)
            
            # Step 7: Generate Recommendations
            print("💡 Step 7: Generating Recommendations...")
            await self._generate_recommendations()
            
            # Step 8: Calculate Scores
            print("🏆 Step 8: Calculating Scores...")
            await self._calculate_scores()
            
            # Step 9: Save Reports
            print("💾 Step 9: Saving Reports...")
            report_files = await self._save_reports()
            
            # Calculate duration
            duration = (datetime.now() - start_time).total_seconds()
            self.report["metadata"]["analysis_duration_seconds"] = round(duration, 2)
            
            print(f"✅ Analysis completed in {duration:.2f} seconds")
            print(f"🏆 Overall Score: {self.report['overall_score']}/100")
            
            return {
                "success": True,
                "report": self.report,
                "files": report_files,
                "duration": duration
            }
            
        except Exception as e:
            print(f"❌ Analysis failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def _analyze_seo(self, html: str, text: str):
        """Comprehensive SEO analysis"""
        html_lower = html.lower()
        
        # Title analysis
        title_match = re.search(r'<title[^>]*>([^<]+)</title>', html, re.IGNORECASE)
        title = title_match.group(1).strip() if title_match else ""
        
        # Meta description
        meta_desc_match = re.search(r'<meta[^>]*name=["\']description["\'][^>]*content=["\']([^"\']+)["\']', html, re.IGNORECASE)
        meta_description = meta_desc_match.group(1) if meta_desc_match else ""
        
        # Keywords
        meta_keywords_match = re.search(r'<meta[^>]*name=["\']keywords["\'][^>]*content=["\']([^"\']+)["\']', html, re.IGNORECASE)
        meta_keywords = meta_keywords_match.group(1) if meta_keywords_match else ""
        
        # Headings analysis
        h1_tags = re.findall(r'<h1[^>]*>([^<]+)</h1>', html, re.IGNORECASE)
        h2_tags = re.findall(r'<h2[^>]*>([^<]+)</h2>', html, re.IGNORECASE)
        h3_tags = re.findall(r'<h3[^>]*>([^<]+)</h3>', html, re.IGNORECASE)
        
        # Links analysis
        internal_links = len(re.findall(r'<a[^>]*href=["\'][^"\']*["\']', html, re.IGNORECASE))
        external_links = len(re.findall(r'<a[^>]*href=["\']https?://[^"\']*["\']', html, re.IGNORECASE))
        
        # Images analysis
        images = re.findall(r'<img[^>]*>', html, re.IGNORECASE)
        images_with_alt = len([img for img in images if 'alt=' in img.lower()])
        
        self.report["seo_analysis"] = {
            "title": {
                "content": title,
                "length": len(title),
                "exists": bool(title),
                "optimal_length": 30 <= len(title) <= 60 if title else False
            },
            "meta_description": {
                "content": meta_description,
                "length": len(meta_description),
                "exists": bool(meta_description),
                "optimal_length": 120 <= len(meta_description) <= 160 if meta_description else False
            },
            "meta_keywords": {
                "content": meta_keywords,
                "exists": bool(meta_keywords)
            },
            "headings": {
                "h1_count": len(h1_tags),
                "h2_count": len(h2_tags),
                "h3_count": len(h3_tags),
                "h1_tags": h1_tags[:5],  # First 5
                "has_h1": len(h1_tags) > 0,
                "has_multiple_h1": len(h1_tags) > 1
            },
            "links": {
                "internal_links": internal_links,
                "external_links": external_links,
                "total_links": internal_links + external_links
            },
            "images": {
                "total_images": len(images),
                "images_with_alt": images_with_alt,
                "alt_text_coverage": round((images_with_alt / len(images)) * 100, 1) if images else 0
            },
            "other": {
                "has_canonical": "rel=\"canonical\"" in html_lower,
                "has_robots_meta": "name=\"robots\"" in html_lower,
                "has_sitemap": "sitemap" in html_lower
            }
        }
    
    async def _analyze_technical(self, html: str):
        """Technical SEO and structure analysis"""
        html_lower = html.lower()
        
        # Meta tags
        charset_match = re.search(r'<meta[^>]*charset=["\']?([^"\'>\s]+)', html, re.IGNORECASE)
        viewport_match = re.search(r'<meta[^>]*name=["\']viewport["\'][^>]*content=["\']([^"\']+)["\']', html, re.IGNORECASE)
        
        # HTML5 semantic elements
        semantic_elements = {
            "header": "<header" in html_lower,
            "nav": "<nav" in html_lower,
            "main": "<main" in html_lower,
            "article": "<article" in html_lower,
            "section": "<section" in html_lower,
            "aside": "<aside" in html_lower,
            "footer": "<footer" in html_lower
        }
        
        # Resources
        css_files = len(re.findall(r'<link[^>]*href=["\'][^"\']*\.css[^"\']*["\']', html, re.IGNORECASE))
        js_files = len(re.findall(r'<script[^>]*src=["\'][^"\']*\.js[^"\']*["\']', html, re.IGNORECASE))
        inline_css = len(re.findall(r'<style[^>]*>', html, re.IGNORECASE))
        inline_js = len(re.findall(r'<script[^>]*>[^<]+</script>', html, re.IGNORECASE))
        
        self.report["technical_analysis"] = {
            "doctype": html.strip().lower().startswith('<!doctype html>'),
            "charset": {
                "exists": bool(charset_match),
                "value": charset_match.group(1) if charset_match else None
            },
            "viewport": {
                "exists": bool(viewport_match),
                "content": viewport_match.group(1) if viewport_match else None,
                "responsive": "width=device-width" in html_lower
            },
            "html5_semantic": semantic_elements,
            "semantic_score": sum(semantic_elements.values()),
            "resources": {
                "external_css": css_files,
                "external_js": js_files,
                "inline_css": inline_css,
                "inline_js": inline_js,
                "total_resources": css_files + js_files
            },
            "other": {
                "has_favicon": "favicon" in html_lower,
                "has_apple_touch_icon": "apple-touch-icon" in html_lower,
                "has_manifest": "manifest.json" in html_lower
            }
        }
    
    async def _analyze_content(self, html: str, text: str):
        """Content quality and structure analysis"""
        # Word analysis
        words = text.split() if text else []
        sentences = re.split(r'[.!?]+', text) if text else []
        sentences = [s.strip() for s in sentences if s.strip()]
        
        # Language detection (simple)
        cyrillic_chars = len(re.findall(r'[а-яёА-ЯЁ]', text))
        latin_chars = len(re.findall(r'[a-zA-Z]', text))
        
        # Content structure
        paragraphs = len(re.findall(r'<p[^>]*>', html, re.IGNORECASE))
        lists = len(re.findall(r'<[uo]l[^>]*>', html, re.IGNORECASE))
        
        self.report["content_analysis"] = {
            "text_metrics": {
                "word_count": len(words),
                "sentence_count": len(sentences),
                "character_count": len(text),
                "avg_words_per_sentence": round(len(words) / len(sentences), 1) if sentences else 0,
                "avg_word_length": round(sum(len(word) for word in words) / len(words), 1) if words else 0
            },
            "language": {
                "cyrillic_chars": cyrillic_chars,
                "latin_chars": latin_chars,
                "primary_language": "Cyrillic" if cyrillic_chars > latin_chars else "Latin" if latin_chars > 0 else "Unknown"
            },
            "structure": {
                "paragraphs": paragraphs,
                "lists": lists,
                "content_density": round((len(text) / len(html)) * 100, 2) if html else 0
            },
            "readability": {
                "sufficient_content": len(words) >= 300,
                "good_sentence_length": 10 <= (len(words) / len(sentences) if sentences else 0) <= 20,
                "content_quality_score": min(100, (len(words) / 300) * 50 + 50) if words else 0
            }
        }
    
    async def _analyze_performance(self, html: str):
        """Basic performance indicators"""
        # File size estimates
        html_size_kb = len(html) / 1024
        
        # Resource counting
        images = len(re.findall(r'<img[^>]*>', html, re.IGNORECASE))
        css_files = len(re.findall(r'<link[^>]*\.css', html, re.IGNORECASE))
        js_files = len(re.findall(r'<script[^>]*src=', html, re.IGNORECASE))
        
        self.report["performance_analysis"] = {
            "page_size": {
                "html_size_kb": round(html_size_kb, 2),
                "size_category": "Small" if html_size_kb < 50 else "Medium" if html_size_kb < 200 else "Large"
            },
            "resource_count": {
                "images": images,
                "css_files": css_files,
                "js_files": js_files,
                "total_requests": images + css_files + js_files
            },
            "optimization": {
                "minified_likely": "min.js" in html.lower() or "min.css" in html.lower(),
                "compression_indicators": "gzip" in html.lower() or "deflate" in html.lower()
            }
        }
    
    async def _analyze_accessibility(self, html: str):
        """Accessibility analysis"""
        html_lower = html.lower()
        
        # ARIA and accessibility attributes
        aria_labels = len(re.findall(r'aria-label=', html, re.IGNORECASE))
        aria_roles = len(re.findall(r'role=', html, re.IGNORECASE))
        
        # Form accessibility
        form_labels = len(re.findall(r'<label[^>]*>', html, re.IGNORECASE))
        form_inputs = len(re.findall(r'<input[^>]*>', html, re.IGNORECASE))
        
        self.report["accessibility_analysis"] = {
            "aria": {
                "aria_labels": aria_labels,
                "aria_roles": aria_roles,
                "has_aria_attributes": aria_labels > 0 or aria_roles > 0
            },
            "forms": {
                "labels": form_labels,
                "inputs": form_inputs,
                "label_input_ratio": round(form_labels / form_inputs, 2) if form_inputs > 0 else 0
            },
            "other": {
                "has_skip_links": "skip" in html_lower and "content" in html_lower,
                "has_lang_attribute": "html lang=" in html_lower
            }
        }
    
    async def _generate_recommendations(self):
        """Generate comprehensive recommendations"""
        recommendations = []
        
        # SEO Recommendations
        seo = self.report["seo_analysis"]
        if not seo["title"]["exists"]:
            recommendations.append({"priority": "CRITICAL", "category": "SEO", "issue": "Missing page title", "fix": "Add a descriptive <title> tag"})
        elif not seo["title"]["optimal_length"]:
            recommendations.append({"priority": "HIGH", "category": "SEO", "issue": "Title length not optimal", "fix": "Keep title between 30-60 characters"})
        
        if not seo["meta_description"]["exists"]:
            recommendations.append({"priority": "HIGH", "category": "SEO", "issue": "Missing meta description", "fix": "Add meta description (120-160 characters)"})
        
        if not seo["headings"]["has_h1"]:
            recommendations.append({"priority": "HIGH", "category": "SEO", "issue": "Missing H1 heading", "fix": "Add H1 heading for page structure"})
        elif seo["headings"]["has_multiple_h1"]:
            recommendations.append({"priority": "MEDIUM", "category": "SEO", "issue": "Multiple H1 tags", "fix": "Use only one H1 per page"})
        
        # Technical Recommendations
        tech = self.report["technical_analysis"]
        if not tech["viewport"]["exists"]:
            recommendations.append({"priority": "HIGH", "category": "Technical", "issue": "Missing viewport meta tag", "fix": "Add viewport meta tag for mobile compatibility"})
        
        if tech["semantic_score"] < 4:
            recommendations.append({"priority": "MEDIUM", "category": "Technical", "issue": "Poor HTML5 semantic structure", "fix": "Use semantic HTML5 elements (header, nav, main, footer)"})
        
        # Content Recommendations
        content = self.report["content_analysis"]
        if not content["readability"]["sufficient_content"]:
            recommendations.append({"priority": "MEDIUM", "category": "Content", "issue": "Insufficient content", "fix": "Add more content (minimum 300 words recommended)"})
        
        # Accessibility Recommendations
        access = self.report["accessibility_analysis"]
        if not access["aria"]["has_aria_attributes"]:
            recommendations.append({"priority": "MEDIUM", "category": "Accessibility", "issue": "No ARIA attributes", "fix": "Add ARIA labels and roles for better accessibility"})
        
        self.report["recommendations"] = recommendations
    
    async def _calculate_scores(self):
        """Calculate detailed scores for each category"""
        scores = {}
        
        # SEO Score (0-100)
        seo = self.report["seo_analysis"]
        seo_score = 0
        if seo["title"]["exists"]: seo_score += 20
        if seo["title"]["optimal_length"]: seo_score += 10
        if seo["meta_description"]["exists"]: seo_score += 20
        if seo["meta_description"]["optimal_length"]: seo_score += 10
        if seo["headings"]["has_h1"]: seo_score += 15
        if not seo["headings"]["has_multiple_h1"]: seo_score += 5
        if seo["images"]["alt_text_coverage"] > 80: seo_score += 10
        if seo["other"]["has_canonical"]: seo_score += 10
        scores["seo_score"] = min(seo_score, 100)
        
        # Technical Score (0-100)
        tech = self.report["technical_analysis"]
        tech_score = 0
        if tech["doctype"]: tech_score += 10
        if tech["charset"]["exists"]: tech_score += 10
        if tech["viewport"]["exists"]: tech_score += 20
        if tech["viewport"]["responsive"]: tech_score += 15
        tech_score += tech["semantic_score"] * 5  # 5 points per semantic element
        if tech["other"]["has_favicon"]: tech_score += 5
        scores["technical_score"] = min(tech_score, 100)
        
        # Content Score (0-100)
        content = self.report["content_analysis"]
        content_score = int(content["readability"]["content_quality_score"])
        if content["structure"]["paragraphs"] > 0: content_score += 10
        if content["structure"]["lists"] > 0: content_score += 5
        scores["content_score"] = min(content_score, 100)
        
        # Performance Score (0-100)
        perf = self.report["performance_analysis"]
        perf_score = 100
        if perf["page_size"]["html_size_kb"] > 200: perf_score -= 30
        elif perf["page_size"]["html_size_kb"] > 100: perf_score -= 15
        if perf["resource_count"]["total_requests"] > 50: perf_score -= 20
        elif perf["resource_count"]["total_requests"] > 20: perf_score -= 10
        if perf["optimization"]["minified_likely"]: perf_score += 10
        scores["performance_score"] = max(perf_score, 0)
        
        # Accessibility Score (0-100)
        access = self.report["accessibility_analysis"]
        access_score = 50  # Base score
        if access["aria"]["has_aria_attributes"]: access_score += 20
        if access["forms"]["label_input_ratio"] >= 0.8: access_score += 15
        if access["other"]["has_lang_attribute"]: access_score += 10
        if access["other"]["has_skip_links"]: access_score += 5
        scores["accessibility_score"] = min(access_score, 100)
        
        # Overall Score (weighted average)
        overall = (
            scores["seo_score"] * 0.3 +
            scores["technical_score"] * 0.25 +
            scores["content_score"] * 0.2 +
            scores["performance_score"] * 0.15 +
            scores["accessibility_score"] * 0.1
        )
        
        scores["overall_score"] = round(overall, 1)
        self.report["scores"] = scores
        self.report["overall_score"] = scores["overall_score"]
    
    async def _save_reports(self):
        """Save comprehensive reports to multiple files"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        files_created = []
        
        try:
            # 1. Full JSON Report
            json_file = f"analysis_reports/complete_analysis_{timestamp}.json"
            json_content = json.dumps(self.report, indent=2, ensure_ascii=False)
            result = await self.file_tool.execute(path=json_file, content=json_content)
            if result.get("success"):
                files_created.append(json_file)
                print(f"✅ JSON report saved: {json_file}")
            
            # 2. Executive Summary
            summary_file = f"analysis_reports/executive_summary_{timestamp}.txt"
            summary_content = self._generate_executive_summary()
            result = await self.file_tool.execute(path=summary_file, content=summary_content)
            if result.get("success"):
                files_created.append(summary_file)
                print(f"✅ Executive summary saved: {summary_file}")
            
            # 3. Recommendations Report
            rec_file = f"analysis_reports/recommendations_{timestamp}.txt"
            rec_content = self._generate_recommendations_report()
            result = await self.file_tool.execute(path=rec_file, content=rec_content)
            if result.get("success"):
                files_created.append(rec_file)
                print(f"✅ Recommendations saved: {rec_file}")
            
            return files_created
            
        except Exception as e:
            print(f"❌ Error saving reports: {e}")
            return files_created
    
    def _generate_executive_summary(self) -> str:
        """Generate executive summary"""
        lines = [
            "=" * 70,
            "EXECUTIVE SUMMARY - WEBSITE ANALYSIS REPORT",
            "=" * 70,
            f"Website: {self.report['metadata']['target_url']}",
            f"Analysis Date: {self.report['metadata']['analysis_date'][:19]}",
            f"Duration: {self.report['metadata']['analysis_duration_seconds']} seconds",
            "",
            "🏆 OVERALL SCORE: {}/100".format(self.report['overall_score']),
            "",
            "📊 CATEGORY SCORES:",
            f"   SEO Score:          {self.report['scores']['seo_score']}/100",
            f"   Technical Score:    {self.report['scores']['technical_score']}/100",
            f"   Content Score:      {self.report['scores']['content_score']}/100",
            f"   Performance Score:  {self.report['scores']['performance_score']}/100",
            f"   Accessibility Score: {self.report['scores']['accessibility_score']}/100",
            "",
            "📈 KEY METRICS:",
            f"   Page Title: {self.report['seo_analysis']['title']['content'] or 'Missing'}",
            f"   Page Size: {self.report['performance_analysis']['page_size']['html_size_kb']} KB",
            f"   Word Count: {self.report['content_analysis']['text_metrics']['word_count']:,}",
            f"   Images: {self.report['seo_analysis']['images']['total_images']}",
            f"   Links: {self.report['seo_analysis']['links']['total_links']}",
            "",
            "🚨 CRITICAL ISSUES:",
        ]
        
        critical_recs = [r for r in self.report['recommendations'] if r['priority'] == 'CRITICAL']
        if critical_recs:
            for rec in critical_recs:
                lines.append(f"   • {rec['issue']}")
        else:
            lines.append("   ✅ No critical issues found")
        
        lines.extend([
            "",
            "⚠️  HIGH PRIORITY ISSUES:",
        ])
        
        high_recs = [r for r in self.report['recommendations'] if r['priority'] == 'HIGH']
        if high_recs:
            for rec in high_recs[:5]:  # Top 5
                lines.append(f"   • {rec['issue']}")
        else:
            lines.append("   ✅ No high priority issues found")
        
        lines.extend([
            "",
            "=" * 70,
            f"Report generated by Complete Website Analyzer v{self.report['metadata']['analyzer_version']}",
            "=" * 70
        ])
        
        return "\n".join(lines)
    
    def _generate_recommendations_report(self) -> str:
        """Generate detailed recommendations report"""
        lines = [
            "=" * 70,
            "DETAILED RECOMMENDATIONS REPORT",
            "=" * 70,
            f"Website: {self.report['metadata']['target_url']}",
            f"Total Recommendations: {len(self.report['recommendations'])}",
            "",
        ]
        
        for priority in ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW']:
            recs = [r for r in self.report['recommendations'] if r['priority'] == priority]
            if recs:
                lines.extend([
                    f"🔥 {priority} PRIORITY ({len(recs)} issues):",
                    "-" * 50,
                ])
                
                for i, rec in enumerate(recs, 1):
                    lines.extend([
                        f"{i}. {rec['issue']}",
                        f"   Category: {rec['category']}",
                        f"   Fix: {rec['fix']}",
                        ""
                    ])
        
        lines.extend([
            "=" * 70,
            "END OF RECOMMENDATIONS",
            "=" * 70
        ])
        
        return "\n".join(lines)

async def main():
    """Main function"""
    print("🌐 Complete Website Analyzer v2.0")
    print("🎯 Target: shayanwaters.com")
    print("=" * 50)
    
    analyzer = CompleteWebsiteAnalyzer()
    result = await analyzer.analyze_website("https://shayanwaters.com")
    
    if result.get("success"):
        print("\n✅ ANALYSIS COMPLETED SUCCESSFULLY!")
        print(f"📁 Files created: {len(result.get('files', []))}")
        for file in result.get('files', []):
            print(f"   📄 {file}")
        print(f"⏱️  Duration: {result.get('duration', 0):.2f} seconds")
        print(f"🏆 Overall Score: {result['report']['overall_score']}/100")
    else:
        print(f"\n❌ ANALYSIS FAILED: {result.get('error')}")

if __name__ == "__main__":
    asyncio.run(main())
