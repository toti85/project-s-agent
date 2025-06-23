#!/usr/bin/env python
"""
Web Content Analyzer - Test Script
----------------------------------
Ez a script teszteli a Web Content Analyzer intelligens workflow rendszert.
Egy adott URL-t elemez és bemutatja a munkafolyamat működését.
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

logger = logging.getLogger("web_analyzer_test")

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

async def test_web_content_analyzer(url: str, output_dir: str = None):
    """
    Teszteli a Web Content Analyzer-t egy adott URL-lel.
    
    Args:
        url (str): Az elemzendő URL
        output_dir (str, optional): Kimeneti könyvtár az eredményeknek
    """
    logger.info("=" * 70)
    logger.info(f"Web Content Analyzer Teszt - {datetime.now().isoformat()}")
    logger.info("=" * 70)
    
    if not output_dir:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_dir = os.path.join(project_root, "analysis_results", f"test_{timestamp}")
    
    logger.info(f"🔍 URL elemzése: {url}")
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
            
            if "errors" in result:
                logger.error("⚠️ Részletes hibák:")
                for error in result.get("errors", []):
                    logger.error(f"  - {error.get('step', 'unknown')}: {error.get('error', 'ismeretlen hiba')}")
            
            if "partial_results" in result:
                logger.info("⚠️ Részleges eredmények elérhetők")
                for output_name, output_path in result.get("partial_results", {}).items():
                    if isinstance(output_path, str) and os.path.exists(output_path):
                        logger.info(f"  - {output_name}: {output_path}")
            
            return False
            
    except Exception as e:
        logger.error(f"❌ Kivétel a teszt során: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        logger.info("=" * 70)
        logger.info("Web Content Analyzer Teszt befejezve")
        logger.info("=" * 70)

def open_results_folder(folder_path):
    """
    Megnyitja az eredmények mappáját a fájlkezelőben.
    """
    import platform
    import subprocess
    
    try:
        if platform.system() == "Windows":
            os.startfile(folder_path)
        elif platform.system() == "Darwin":  # macOS
            subprocess.run(["open", folder_path])
        else:  # Linux
            subprocess.run(["xdg-open", folder_path])
        
        logger.info(f"📂 Eredmények mappa megnyitva: {folder_path}")
    except Exception as e:
        logger.error(f"❌ Nem sikerült megnyitni a mappát: {e}")

async def main():
    """
    Fő belépési pont
    """
    parser = argparse.ArgumentParser(description="Web Content Analyzer Teszt")
    parser.add_argument("--url", type=str, 
                        default="https://docs.python.org/3/library/asyncio.html",
                        help="Az elemzendő URL")
    parser.add_argument("--output-dir", type=str, default=None,
                        help="Kimeneti könyvtár (opcionális)")
    parser.add_argument("--open", action="store_true",
                        help="Automatikusan megnyitja az eredmények mappáját a teszt után")
    
    args = parser.parse_args()
    
    # Teszt futtatása
    output_dir = args.output_dir
    if not output_dir:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_dir = os.path.join(project_root, "analysis_results", f"test_{timestamp}")
    
    success = await test_web_content_analyzer(args.url, output_dir)
    
    if success and args.open:
        open_results_folder(output_dir)
    
    # Exit code beállítása az eredmény alapján
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    asyncio.run(main())
