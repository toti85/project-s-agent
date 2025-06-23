"""
Project-S Tools Integration Test
----------------------------
Ez a modul teszteli a Project-S eszközök integrált működését.
"""

import asyncio
import logging
import os
import sys
from pathlib import Path
import json
from datetime import datetime
from pprint import pprint

# Hozzáadjuk a projekt gyökérkönyvtárát a keresési útvonalhoz
project_root = Path(__file__).parent
if str(project_root) not in sys.path:
    sys.path.append(str(project_root))

# Eszközök importálása
from tools import tool_registry, register_all_tools
from tools.file_tools import FileSearchTool, FileReadTool, FileWriteTool
from tools.web_tools import WebPageFetchTool
from tools.system_tools import SystemCommandTool

# Naplózás beállítása
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger("tools_test")

async def run_test_case():
    """
    Teszteset végrehajtása: "Keresd meg a config fájlokat, olvass egy weboldalat, és írj egy összefoglaló jelentést"
    """
    logger.info("Project-S eszközök integrációs teszt indítása...")
    
    # Eszközök regisztrálása
    await register_all_tools()
    
    # 1. Konfig fájlok keresése
    logger.info("1. Konfiguráció fájlok keresése...")
    file_search_tool = FileSearchTool()
    
    config_search_result = await file_search_tool.execute(
        pattern="**/*.{yaml,json,ini,cfg,conf,xml}",
        base_dir=str(Path(__file__).parent),
        max_depth=3
    )
    
    if not config_search_result["success"]:
        logger.error(f"Hiba a konfig fájlok keresése során: {config_search_result['error']}")
        return
        
    config_files = config_search_result["matches"]
    logger.info(f"{len(config_files)} konfig fájl található")
    
    # 2. Weboldal olvasása
    logger.info("2. Weboldal olvasása...")
    web_tool = WebPageFetchTool()
    
    web_result = await web_tool.execute(
        url="https://www.python.org",
        extract_text=True
    )
    
    if not web_result["success"]:
        logger.error(f"Hiba a weboldal olvasása során: {web_result.get('error')}")
        return
        
    web_content = web_result["text"]
    logger.info(f"Weboldal tartalma letöltve ({len(web_content)} karakter)")
    
    # 3. Rendszerparancs végrehajtása
    logger.info("3. Rendszer információk lekérése...")
    
    system_cmd_tool = SystemCommandTool()
    if os.name == "nt":  # Windows
        cmd_result = await system_cmd_tool.execute(command="systeminfo")
    else:  # Linux/Unix
        cmd_result = await system_cmd_tool.execute(command="uname -a")
    
    if not cmd_result["success"]:
        logger.error(f"Hiba a rendszerparancs végrehajtása során: {cmd_result.get('error')}")
        system_info = "Nem sikerült lekérni"
    else:
        system_info = cmd_result["stdout"]
    
    # 4. Jelentés összeállítása és mentése
    logger.info("4. Összefoglaló jelentés írása...")
    
    # Jelentés összeállítása
    report = {
        "timestamp": datetime.now().isoformat(),
        "config_files": config_files,
        "config_files_count": len(config_files),
        "website": {
            "url": "https://www.python.org",
            "content_length": len(web_content),
            "extract": web_content[:500] + "..." if len(web_content) > 500 else web_content
        },
        "system_info": system_info[:1000] + "..." if len(system_info) > 1000 else system_info
    }
    
    # Jelentés mentése
    file_write_tool = FileWriteTool()
    report_path = str(Path(__file__).parent / "outputs" / "integration_report.json")
    
    write_result = await file_write_tool.execute(
        path=report_path,
        content=json.dumps(report, indent=2),
        create_dirs=True
    )
    
    if not write_result["success"]:
        logger.error(f"Hiba a jelentés írása során: {write_result.get('error')}")
        return
        
    logger.info(f"Jelentés sikeresen mentve: {report_path}")
    
    # Sikeres befejezés
    logger.info("Teszt sikeresen befejeződött!")
    return report

if __name__ == "__main__":
    report = asyncio.run(run_test_case())
    print("\n--- Jelentés összefoglaló ---")
    
    if report:
        print(f"Időbélyeg: {report['timestamp']}")
        print(f"Talált konfigurációs fájlok száma: {report['config_files_count']}")
        print("Példa fájlok:")
        for file in report['config_files'][:5]:
            print(f"  - {file}")
        if len(report['config_files']) > 5:
            print(f"  ...és még {len(report['config_files']) - 5} fájl")
            
        print("\nWeboldal kivonata:")
        print(f"  {report['website']['extract'][:200]}...")
        
        print("\nRendszer információ részlet:")
        print(f"  {report['system_info'][:200]}...")
        
        print("\nA teljes jelentés elérhető: " + str(Path(__file__).parent / "outputs" / "integration_report.json"))
    else:
        print("A teszt futtatása sikertelen volt. Ellenőrizze a naplófájlt további információkért.")
