"""
Project-S Tool System alapvető tesztje
-----------------------------------
Ez a script csak a Project-S Tool rendszer működését teszteli anélkül,
hogy a komplex LangGraph integrációt használná. Ezt a fájlt kell futtatni
a cirkuláris importálási problémák elkerülésére.
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

# Konfiguráljuk a naplózást
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger("simple_tools_test")

async def run_simple_test():
    """
    Egyszerű teszt a Project-S Tool rendszer működésének ellenőrzésére.
    """
    logger.info("Project-S Tool rendszer egyszerű tesztje indul...")
    
    try:
        # Eszközök importálása
        from tools.tool_interface import BaseTool
        from tools.tool_registry import tool_registry
        from tools import register_all_tools
        
        # Eszközök regisztrálása
        logger.info("Eszközök regisztrálása...")
        await register_all_tools()
        
        # Elérhető eszközök listázása
        tools = tool_registry.list_tools()
        logger.info(f"Elérhető eszközök száma: {len(tools)}")
        
        # Néhány alapvető eszköz importálása
        from tools.file_tools import FileSearchTool, FileReadTool, FileWriteTool
        from tools.web_tools import WebPageFetchTool
        
        # 1. Fájl keresés végrehajtása
        logger.info("1. Konfiguráció fájlok keresése...")
        config_search_result = await tool_registry.execute_tool(
            "FileSearchTool",
            pattern="**/*.{json,yaml,ini,conf,xml}",
            base_dir=str(Path(__file__).parent),
            max_depth=3
        )
        
        if config_search_result["success"]:
            files_found = len(config_search_result.get("matches", []))
            logger.info(f"{files_found} konfigurációs fájl található")
            # Az első 5 találat kiírása
            for i, file in enumerate(config_search_result.get("matches", [])[:5]):
                logger.info(f"  - {file}")
            if files_found > 5:
                logger.info(f"  ... és még {files_found - 5} fájl")
        else:
            logger.error(f"Hiba a fájl keresés során: {config_search_result.get('error', 'Ismeretlen hiba')}")
            
        # 2. Weboldal letöltése
        logger.info("2. Weboldal tartalom lekérése...")
        web_result = await tool_registry.execute_tool(
            "WebPageFetchTool",
            url="https://www.python.org",
            extract_text=True
        )
        
        if web_result["success"]:
            content_length = len(web_result.get("text", ""))
            logger.info(f"Weboldal tartalom letöltve ({content_length} karakter)")
            logger.info(f"Első 100 karakter: {web_result.get('text', '')[:100]}...")
        else:
            logger.error(f"Hiba a weboldal letöltés során: {web_result.get('error', 'Ismeretlen hiba')}")
            
        # 3. Jelentés írása
        logger.info("3. Jelentés írása...")
        
        report_data = {
            "timestamp": datetime.now().isoformat(),
            "config_files": {
                "count": len(config_search_result.get("matches", [])),
                "samples": config_search_result.get("matches", [])[:5]
            },
            "web_content": {
                "url": "https://www.python.org",
                "content_length": len(web_result.get("text", "")),
                "excerpt": web_result.get("text", "")[:200]
            }
        }
        
        report_path = str(Path(__file__).parent / "outputs" / "simple_tools_report.json")
        
        write_result = await tool_registry.execute_tool(
            "FileWriteTool",
            path=report_path,
            content=json.dumps(report_data, indent=2),
            create_dirs=True
        )
        
        if write_result["success"]:
            logger.info(f"Jelentés sikeresen mentve: {report_path}")
        else:
            logger.error(f"Hiba a jelentés írása során: {write_result.get('error', 'Ismeretlen hiba')}")
            
        # 4. Kód végrehajtás tesztelése (ha elérhető CodeExecutionTool)
        try:
            from tools.code_tools import CodeExecutionTool
            
            logger.info("4. Python kód végrehajtás tesztelése...")
            
            test_code = """
import math
from datetime import datetime

# Egyszerű számítás
result = 0
for i in range(10):
    result += i * math.sqrt(i + 1)
    
# Aktuális dátum
current_date = datetime.now()

# Eredmény
print(f"Számítási eredmény: {result}")
print(f"Aktuális dátum: {current_date}")

# Utolsó értékként adjuk vissza
result
"""
            
            code_result = await tool_registry.execute_tool(
                "CodeExecutionTool",
                code=test_code
            )
            
            if code_result["success"]:
                logger.info(f"Kód végrehajtás sikeres!")
                logger.info(f"Kimenet: {code_result.get('output')}")
                logger.info(f"Visszatérési érték: {code_result.get('result')}")
            else:
                logger.error(f"Hiba a kód végrehajtása során: {code_result.get('error', 'Ismeretlen hiba')}")
                
        except ImportError:
            logger.warning("CodeExecutionTool nem elérhető, kód végrehajtási teszt kihagyva")
            
        # Az eredmények összesítése
        successful_tests = 0
        if config_search_result["success"]: successful_tests += 1
        if web_result["success"]: successful_tests += 1
        if write_result["success"]: successful_tests += 1
        
        logger.info(f"\nÖsszesítés: {successful_tests}/3 teszt sikeres")
        return {
            "success": successful_tests == 3,
            "tests_completed": 3,
            "tests_successful": successful_tests
        }
        
    except Exception as e:
        logger.error(f"Hiba történt a teszt futtatása közben: {str(e)}", exc_info=True)
        return {
            "success": False,
            "error": str(e)
        }


if __name__ == "__main__":
    result = asyncio.run(run_simple_test())
    
    print("\n=== Tool Rendszer Teszt Összegzése ===")
    
    if result["success"]:
        print("✅ A Project-S Tool rendszer sikeresen működik!")
    else:
        print("❌ A Project-S Tool rendszer tesztje sikertelen!")
        
    print(f"Végrehajtott tesztek: {result.get('tests_completed', 0)}")
    print(f"Sikeres tesztek: {result.get('tests_successful', 0)}")
    
    if "error" in result:
        print(f"\nHiba: {result['error']}")
    
    print("\nA részletes naplót lásd fentebb.")
    
    # Ha van jelentés, mutassuk az elérési útját
    report_path = Path(__file__).parent / "outputs" / "simple_tools_report.json"
    if report_path.exists():
        print(f"\nA részletes jelentés itt található: {report_path}")
