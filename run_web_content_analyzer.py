#!/usr/bin/env python
"""
Web Content Analyzer - Runner Script
-----------------------------------
Ez a script egyszerűen elindítja a Web Content Analyzer-t egy adott URL-lel.
"""

import asyncio
import sys
import os
import argparse
import logging
from pathlib import Path
from datetime import datetime

# Konfiguráljuk a naplózást
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger("web_analyzer_runner")

# Projekt gyökér hozzáadása a Python keresési útvonalhoz
project_root = Path(__file__).parent
if str(project_root) not in sys.path:
    sys.path.append(str(project_root))

# Importáljuk a Web Content Analyzer-t
try:
    from intelligent_workflow_system import WebContentAnalyzer
except ImportError as e:
    logger.error(f"❌ Nem sikerült importálni a WebContentAnalyzer-t: {e}")
    sys.exit(1)

async def run_web_content_analyzer(url: str, analysis_type: str = "comprehensive") -> bool:
    """
    Futtatja a Web Content Analyzer-t egy adott URL-lel és elemzési típussal.
    
    Args:
        url (str): Az elemzendő URL
        analysis_type (str, optional): Az elemzés típusa. Alapértelmezett: "comprehensive"
    
    Returns:
        bool: True, ha sikeres, False egyébként
    """
    logger.info("=" * 70)
    logger.info(f"Web Content Analyzer - {datetime.now().isoformat()}")
    logger.info("=" * 70)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    url_name = url.replace("https://", "").replace("http://", "").replace("/", "_").replace(".", "_")
    output_dir = os.path.join(project_root, "analysis_results", f"{url_name}")
    
    logger.info(f"🔍 URL elemzése: {url}")
    logger.info(f"📊 Elemzés típusa: {analysis_type}")
    logger.info(f"📁 Kimeneti könyvtár: {output_dir}")
    
    try:
        # Analyzer inicializálása
        analyzer = WebContentAnalyzer(output_dir=output_dir)
        logger.info("⚙️ Web Content Analyzer inicializálása...")
        init_success = await analyzer.initialize()
        
        if not init_success:
            logger.error("❌ A Web Content Analyzer inicializálása sikertelen")
            return False
        
        # URL elemzése
        logger.info(f"🚀 {url} elemzésének indítása...")
        start_time = datetime.now()
        result = await analyzer.analyze_url(url)
        end_time = datetime.now()
        
        # Teljesítményadatok
        elapsed_time = (end_time - start_time).total_seconds()
        
        # Eredmények kiértékelése
        if result["success"]:
            logger.info("✅ Elemzés sikeresen befejezve!")
            logger.info(f"⏱️ Feldolgozási idő: {elapsed_time:.2f} másodperc")
            
            logger.info(f"🔍 Tartalom típusa: {result.get('content_type', 'unknown')}")
            logger.info(f"🛤️ Feldolgozási útvonal: {result.get('processing_branch', 'unknown')}")
            
            logger.info("📄 Generált fájlok:")
            for output_name, output_path in result.get("output_paths", {}).items():
                if isinstance(output_path, str) and os.path.exists(output_path):
                    file_size = os.path.getsize(output_path) / 1024  # KB
                    logger.info(f"  - {output_name}: {output_path} ({file_size:.1f} KB)")
            
            return True
        else:
            logger.error(f"❌ Elemzés sikertelen: {result.get('error', 'Ismeretlen hiba')}")
            
            if "error_details" in result:
                logger.error(f"⚠️ Részletes hiba: {result['error_details']}")
            
            if "partial_results" in result:
                logger.info("⚠️ Részleges eredmények elérhetők")
                for output_name, output_path in result.get("partial_results", {}).items():
                    if isinstance(output_path, str) and os.path.exists(output_path):
                        logger.info(f"  - {output_name}: {output_path}")
            
            return False
    except Exception as e:
        logger.error(f"❌ Kritikus hiba az elemzés során: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False

async def main():
    parser = argparse.ArgumentParser(description="Web Content Analyzer Runner")
    parser.add_argument("--url", required=True, help="Az elemzendő weboldal URL-je")
    parser.add_argument("--analysis-type", default="comprehensive", choices=["basic", "comprehensive", "technical"], 
                        help="Az elemzés típusa: basic, comprehensive vagy technical")
    args = parser.parse_args()
    
    success = await run_web_content_analyzer(args.url, args.analysis_type)
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    asyncio.run(main())
