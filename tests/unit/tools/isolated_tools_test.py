"""
Project-S Tool System izolált tesztje
-----------------------------------
Ez a script a Project-S Tool rendszert teszteli teljesen függetlenül
a projekt többi részétől, hogy elkerüljük a cirkuláris importálási
problémákat.
"""

import asyncio
import logging
import os
import sys
from pathlib import Path
import json
import time
from datetime import datetime

# Hozzáadjuk a projekt gyökérkönyvtárát a keresési útvonalhoz
project_root = Path(__file__).parent
if str(project_root) not in sys.path:
    sys.path.append(str(project_root))

# Konfiguráljuk a naplózást
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger("isolated_tools_test")

# Csak a szükséges dolgokat importáljuk innen
from tools.tool_interface import BaseTool

# Saját eszköz példa a függőségek demonstrálására
class SimpleFileTool(BaseTool):
    """
    Egyszerű fájlkezelő eszköz demonstrációs célokra.
    
    Category: file
    Version: 1.0.0
    Requires permissions: Yes
    Safe: Yes
    """
    
    async def execute(self, path: str, content: str = None) -> dict:
        """
        Fájl olvasása vagy írása.
        
        Args:
            path: A fájl elérési útja
            content: Ha meg van adva, akkor írás, egyébként olvasás
            
        Returns:
            dict: Az eredmény
        """
        result = {}
        
        try:
            file_path = Path(path)
            
            if content is not None:
                # Írás
                file_path.parent.mkdir(parents=True, exist_ok=True)
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                    
                result = {
                    "success": True,
                    "operation": "write",
                    "path": str(file_path),
                    "size": len(content)
                }
            else:
                # Olvasás
                if not file_path.exists():
                    return {
                        "success": False,
                        "operation": "read",
                        "error": f"File not found: {path}"
                    }
                
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                result = {
                    "success": True,
                    "operation": "read",
                    "path": str(file_path),
                    "content": content,
                    "size": len(content)
                }
                
            return result
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }


class SimpleWebTool(BaseTool):
    """
    Egyszerű web eszköz demonstrációs célokra.
    
    Category: web
    Version: 1.0.0
    Requires permissions: Yes
    Safe: Yes
    """
    
    async def execute(self, url: str) -> dict:
        """
        URL információk megjelenítése (tényleges hálózati kapcsolat nélkül).
        
        Args:
            url: A weboldal URL-je
            
        Returns:
            dict: Az eredmény
        """
        try:
            # Ez csak szimuláció, nincs tényleges hálózati kapcsolat
            return {
                "success": True,
                "url": url,
                "simulated": True,
                "timestamp": datetime.now().isoformat()
            }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }


async def run_isolated_test():
    """
    A Project-S Tool rendszer izolált tesztje.
    """
    logger.info("Project-S Tool rendszer izolált tesztje indul...")
    
    try:
        # 1. SimpleFileTool teszt
        logger.info("1. Egyszerű fájl eszköz tesztelése...")
        file_tool = SimpleFileTool()
        
        # Fájl írása
        test_file_path = str(Path(__file__).parent / "temp" / "test_file.txt")
        test_content = f"Ez egy teszt fájl.\nIdőbélyeg: {datetime.now().isoformat()}\nVéletlen: {time.time()}"
        
        write_result = await file_tool.execute(test_file_path, test_content)
        
        if write_result["success"]:
            logger.info(f"Fájl sikeresen írva: {test_file_path}")
        else:
            logger.error(f"Hiba a fájl írása során: {write_result.get('error', 'Ismeretlen hiba')}")
            
        # Fájl olvasása
        read_result = await file_tool.execute(test_file_path)
        
        if read_result["success"]:
            content_matches = read_result.get("content") == test_content
            logger.info(f"Fájl sikeresen olvasva: {test_file_path}")
            logger.info(f"Tartalom egyezik: {'Igen' if content_matches else 'Nem'}")
        else:
            logger.error(f"Hiba a fájl olvasása során: {read_result.get('error', 'Ismeretlen hiba')}")
        
        # 2. SimpleWebTool teszt
        logger.info("\n2. Egyszerű web eszköz tesztelése...")
        web_tool = SimpleWebTool()
        
        web_result = await web_tool.execute("https://www.example.com")
        
        if web_result["success"]:
            logger.info(f"Web eszköz sikeresen végrehajtva")
            logger.info(f"URL: {web_result.get('url')}")
            logger.info(f"Időbélyeg: {web_result.get('timestamp')}")
        else:
            logger.error(f"Hiba a web eszköz végrehajtása során: {web_result.get('error', 'Ismeretlen hiba')}")
            
        # 3. Tool interfész ellenőrzése
        logger.info("\n3. Eszköz interfész ellenőrzése...")
        
        # Eszköz információk ellenőrzése
        file_tool_info = file_tool.get_info()
        logger.info(f"Fájl eszköz neve: {file_tool_info['name']}")
        logger.info(f"Fájl eszköz kategóriája: {file_tool_info['category']}")
        logger.info(f"Fájl eszköz paraméterei: {len(file_tool_info['parameters'])}")
        
        # Az eredmények összesítése
        successful_tests = 0
        if write_result["success"]: successful_tests += 1
        if read_result["success"] and read_result.get("content") == test_content: successful_tests += 1
        if web_result["success"]: successful_tests += 1
        
        logger.info(f"\nÖsszesítés: {successful_tests}/3 teszt sikeres")
        
        # Jelentés készítése
        report = {
            "timestamp": datetime.now().isoformat(),
            "tests": {
                "file_write": write_result["success"],
                "file_read": read_result["success"] and read_result.get("content") == test_content,
                "web_tool": web_result["success"]
            },
            "success_rate": f"{successful_tests}/3",
            "tools_tested": [
                file_tool_info,
                web_tool.get_info()
            ]
        }
        
        # Jelentés mentése
        report_path = str(Path(__file__).parent / "outputs" / "isolated_tools_report.json")
        report_dir = Path(report_path).parent
        report_dir.mkdir(parents=True, exist_ok=True)
        
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2)
            
        logger.info(f"Jelentés mentve: {report_path}")
        
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
    result = asyncio.run(run_isolated_test())
    
    print("\n=== Tool Rendszer Izolált Teszt Összegzése ===")
    
    if result["success"]:
        print("✅ A Project-S Tool interfész sikeresen működik!")
    else:
        print("❌ A Project-S Tool interfész tesztje sikertelen!")
        
    print(f"Végrehajtott tesztek: {result.get('tests_completed', 0)}")
    print(f"Sikeres tesztek: {result.get('tests_successful', 0)}")
    
    if "error" in result:
        print(f"\nHiba: {result['error']}")
    
    print("\nA részletes naplót lásd fentebb.")
    
    # Ha van jelentés, mutassuk az elérési útját
    report_path = Path(__file__).parent / "outputs" / "isolated_tools_report.json"
    if report_path.exists():
        print(f"\nA részletes jelentés itt található: {report_path}")
