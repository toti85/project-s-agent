"""
Egyszerű Project-S tool rendszer teszt
---------------------------------------
Ez a modul egy egyszerű, önálló futtatható példát ad a Project-S eszközök
használatára, LangGraph nélkül.
"""

import asyncio
import logging
import os
import sys
from pathlib import Path
import json
from datetime import datetime
import traceback

# Hozzáadjuk a projekt gyökérkönyvtárát a keresési útvonalhoz
project_root = Path(__file__).parent
if str(project_root) not in sys.path:
    sys.path.append(str(project_root))

# Konfiguráljuk a naplózást
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger("basic_tool_runner")

# Project-S importok
try:
    from tools import register_all_tools
    from tools.file_tools import FileSearchTool, FileReadTool, FileWriteTool
    from tools.web_tools import WebPageFetchTool
    logger.info("Project-S eszköz modulok sikeresen importálva")
except ImportError as e:
    logger.error(f"Hiba történt a Project-S modulok importálásakor: {e}")
    sys.exit(1)

async def run_tools_sequence():
    """
    Egy egyszerű eszközsorozat futtatása, amely bemutatja a Project-S eszközöket.
    """
    logger.info("Project-S eszköz sorozat indítása...")
    
    try:
        # 1. Eszközök regisztrálása
        await register_all_tools()
        logger.info("✅ Eszközök sikeresen regisztrálva")
          # 2. Fájlok keresése
        file_search_tool = FileSearchTool()
        search_result = await file_search_tool.execute(
            pattern="**/*.{json,yaml,md}",
            root_dir=str(project_root),
            recursive=True
        )
        
        if search_result.get("success", False):
            files_found = search_result.get("files", [])
            logger.info(f"✅ Fájl keresés sikeres, {len(files_found)} fájl találat")
            
            # A találatok egy részének kijelzése
            for i, file_path in enumerate(files_found[:5]):
                logger.info(f"   - {file_path}")
                
            if len(files_found) > 5:
                logger.info(f"   ... és még {len(files_found) - 5} további fájl")
        else:
            logger.error(f"❌ Fájl keresés sikertelen: {search_result.get('error')}")
        
        # 3. Weboldal letöltése
        web_tool = WebPageFetchTool()
        web_result = await web_tool.execute(
            url="https://python.org",
            extract_text=True
        )
        
        if web_result.get("success", False):
            text_content = web_result.get("text", "")
            logger.info(f"✅ Weboldal letöltve, {len(text_content)} karakter")
            logger.info(f"   Első 100 karakter: {text_content[:100]}...")
        else:
            logger.error(f"❌ Weboldal letöltés sikertelen: {web_result.get('error')}")
        
        # 4. Jelentés készítése és mentése
        report_data = {
            "timestamp": datetime.now().isoformat(),
            "test_name": "Project-S Tool Runner Test",
            "results": [
                {
                    "tool": "FileSearchTool",
                    "success": search_result.get("success", False),
                    "files_found": len(search_result.get("files", [])) if search_result.get("success", False) else 0
                },
                {
                    "tool": "WebPageFetchTool",
                    "success": web_result.get("success", False),
                    "content_length": len(web_result.get("text", "")) if web_result.get("success", False) else 0
                }
            ]
        }
        
        # Készítsük el az outputs könyvtárat, ha nem létezik
        outputs_dir = project_root / "outputs"
        outputs_dir.mkdir(exist_ok=True)
        
        # Elmentsük a jelentést
        report_path = outputs_dir / "basic_tool_runner_report.json"
        
        file_write_tool = FileWriteTool()
        write_result = await file_write_tool.execute(
            path=str(report_path),
            content=json.dumps(report_data, indent=2),
            create_dirs=True
        )
        
        if write_result.get("success", False):
            logger.info(f"✅ Jelentés sikeresen mentve: {report_path}")
        else:
            logger.error(f"❌ Jelentés mentése sikertelen: {write_result.get('error')}")
        
        return {
            "success": True,
            "report_path": str(report_path) if write_result.get("success", False) else None,
            "tools_executed": ["FileSearchTool", "WebPageFetchTool", "FileWriteTool"]
        }
        
    except Exception as e:
        logger.error(f"❌ Hiba történt az eszközök futtatása közben: {str(e)}")
        traceback.print_exc()
        return {
            "success": False,
            "error": str(e)
        }

async def main():
    """
    Fő belépési pont az eszközök futtatásához.
    """
    logger.info("=== Project-S Tool Runner Példa ===")
    
    result = await run_tools_sequence()
    
    if result.get("success", False):
        logger.info("🎉 Az eszközök sikeresen végrehajtva!")
        if result.get("report_path"):
            logger.info(f"📄 A jelentés elérhető: {result['report_path']}")
    else:
        logger.error(f"💥 Az eszközök futtatása sikertelen: {result.get('error')}")
    
    return result

if __name__ == "__main__":
    result = asyncio.run(main())
    
    print("\n=== Tool Runner Eredmény ===")
    if result.get("success", False):
        print("✅ A Project-S eszközök sikeresen futottak!")
        print(f"📊 Végrehajtott eszközök: {', '.join(result.get('tools_executed', []))}")
        if result.get("report_path"):
            print(f"📄 Jelentés: {result['report_path']}")
    else:
        print(f"❌ Hiba: {result.get('error', 'Ismeretlen hiba')}")
