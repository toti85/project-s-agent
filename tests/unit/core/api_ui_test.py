"""
Project-S - API és Felhasználói Felület Teszt
--------------------------------------------
Ez a modul a Project-S API végpontjait és felhasználói felületét teszteli.
"""
import asyncio
import json
import logging
import aiohttp
import webbrowser
import os
from typing import Dict, Any, List, Optional

# Naplózás beállítása
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("api_ui_test")

class APITester:
    """API végpontok tesztelésére szolgáló osztály"""
    
    def __init__(self, base_url = "http://localhost:3000/api"):
        self.base_url = base_url
        self.session = None
    
    async def setup(self):
        """API tesztkörnyezet felállítása"""
        self.session = aiohttp.ClientSession()
        logger.info(f"API tesztelés kezdése, alap URL: {self.base_url}")
    
    async def teardown(self):
        """API tesztkörnyezet lezárása"""
        if self.session:
            await self.session.close()
        logger.info("API tesztelés lezárva")
    
    async def test_health_endpoint(self) -> Dict[str, Any]:
        """Egészség ellenőrző végpont tesztelése"""
        try:
            endpoint = f"{self.base_url}/health"
            logger.info(f"Egészség végpont tesztelése: {endpoint}")
            
            async with self.session.get(endpoint) as response:
                status = response.status
                result = await response.json()
                
                return {
                    "success": status == 200,
                    "status": status,
                    "response": result
                }
        except Exception as e:
            logger.error(f"Hiba az egészség végpont tesztelésekor: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def test_command_endpoint(self, command: str) -> Dict[str, Any]:
        """Parancs végpont tesztelése"""
        try:
            endpoint = f"{self.base_url}/command"
            logger.info(f"Parancs végpont tesztelése: {endpoint}")
            
            payload = {
                "command": command,
                "session_id": "test-session"
            }
            
            async with self.session.post(endpoint, json=payload) as response:
                status = response.status
                result = await response.json()
                
                return {
                    "success": status == 200,
                    "status": status,
                    "response": result
                }
        except Exception as e:
            logger.error(f"Hiba a parancs végpont tesztelésekor: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def test_session_endpoint(self) -> Dict[str, Any]:
        """Munkamenet végpont tesztelése"""
        try:
            # Új munkamenet létrehozása
            create_endpoint = f"{self.base_url}/session"
            logger.info(f"Munkamenet létrehozási végpont tesztelése: {create_endpoint}")
            
            async with self.session.post(create_endpoint) as create_response:
                create_status = create_response.status
                create_result = await create_response.json()
                
                if create_status != 200 or not create_result.get("session_id"):
                    return {
                        "success": False,
                        "status": create_status,
                        "response": create_result,
                        "error": "Nem sikerült munkamenetet létrehozni"
                    }
                
                session_id = create_result.get("session_id")
                
                # Munkamenet lekérdezése
                get_endpoint = f"{self.base_url}/session/{session_id}"
                logger.info(f"Munkamenet lekérdezési végpont tesztelése: {get_endpoint}")
                
                async with self.session.get(get_endpoint) as get_response:
                    get_status = get_response.status
                    get_result = await get_response.json()
                    
                    return {
                        "success": get_status == 200,
                        "status": get_status,
                        "response": get_result,
                        "session_id": session_id
                    }
        except Exception as e:
            logger.error(f"Hiba a munkamenet végpont tesztelésekor: {e}")
            return {
                "success": False,
                "error": str(e)
            }

class UITester:
    """Felhasználói felület tesztelésére szolgáló osztály"""
    
    def __init__(self, ui_url = "http://localhost:3000"):
        self.ui_url = ui_url
    
    def open_in_browser(self) -> bool:
        """Megnyitja a felhasználói felületet a böngészőben"""
        try:
            logger.info(f"Felhasználói felület megnyitása a böngészőben: {self.ui_url}")
            webbrowser.open(self.ui_url)
            return True
        except Exception as e:
            logger.error(f"Hiba a UI böngészőben való megnyitásakor: {e}")
            return False
    
    def create_ui_test_guide(self) -> str:
        """Létrehoz egy útmutatót a felhasználói felület manuális teszteléséhez"""
        guide = """
        # Project-S Felhasználói Felület Tesztelési Útmutató
        
        Ez az útmutató segít a Project-S felhasználói felületének manuális tesztelésében.
        
        ## Alapvető funkciók tesztelése
        
        1. **Parancs bevitel**
           - Nyisd meg a felhasználói felületet
           - Írj be egy egyszerű parancsot a beviteli mezőbe: "Írj egy 'Hello, Project-S!' üzenetet"
           - Ellenőrizd, hogy a válasz megfelelően jelenik meg
        
        2. **Korábbi parancsok megjelenítése**
           - Ellenőrizd, hogy a korábban beírt parancsok láthatóak-e
           - Próbáld meg újra elküldeni valamelyik korábbi parancsot
        
        3. **Munkafolyamat állapotának megjelenítése**
           - Készíts egy többlépéses munkafolyamatot: "Hozz létre egy listát 3 országról, add meg a fővárosaikat, majd mentsd el egy countries.txt fájlba"
           - Ellenőrizd, hogy a munkafolyamat állapota megfelelően jelenik-e meg
        
        4. **Eszközök használata**
           - Teszteld az elérhető eszközöket: "Mutasd meg, milyen eszközöket tudsz használni"
           - Próbálj ki egy konkrét eszközt, pl. "Listázd a jelenlegi könyvtár tartalmát"
        
        5. **Hosszú válaszok megjelenítése**
           - Kérj egy hosszabb választ: "Írj egy 500 szavas esszét a mesterséges intelligenciáról"
           - Ellenőrizd, hogy a hosszú válasz megfelelően jelenik-e meg (görgetés, formázás)
        
        6. **Munkamenetek kezelése**
           - Próbálj új munkamenetet létrehozni
           - Váltogass a munkamenetek között
           - Ellenőrizd, hogy a munkamenetek között megmarad-e a kontextus
           
        ## Hibaesetek tesztelése
        
        1. **Hálózati hiba**
           - Kapcsold ki ideiglenesen az internetkapcsolatot
           - Küldj egy parancsot
           - Ellenőrizd, hogy a rendszer megfelelően kezeli-e a hálózati hibát
        
        2. **Hosszú feldolgozási idő**
           - Küldj egy bonyolult parancsot, ami várhatóan hosszabb feldolgozási időt igényel
           - Ellenőrizd, hogy van-e folyamatjelző vagy visszajelzés
        
        ## Teljesítmény tesztelése
        
        1. **Válaszidők**
           - Mérd meg, mennyi ideig tart egy egyszerű parancs feldolgozása
           - Mérd meg egy összetettebb parancs feldolgozási idejét
        
        2. **Böngészőterhelés**
           - Figyeld meg a CPU és memóriahasználatot hosszú interakciók során
           
        ## Mobilkompatibilitás (ha releváns)
        
        1. **Reszponzív megjelenés**
           - Nyisd meg a felületet különböző képernyőméreteken (mobil, tablet, desktop)
           - Ellenőrizd, hogy minden funkció elérhető és használható-e
        """
        
        # Mentsük el az útmutatót egy fájlba
        guide_path = "ui_test_guide.md"
        try:
            with open(guide_path, "w", encoding="utf-8") as f:
                f.write(guide)
            logger.info(f"UI tesztelési útmutató létrehozva: {guide_path}")
        except Exception as e:
            logger.error(f"Hiba az UI tesztelési útmutató létrehozásakor: {e}")
        
        return guide_path

async def test_api_and_ui():
    """API és UI tesztelés végrehajtása"""
    try:
        results = {
            "api_tests": {},
            "ui_tests": {},
            "overall_success": False
        }
        
        # API tesztek
        print("\n=== API tesztek végrehajtása ===")
        
        api_tester = APITester()
        await api_tester.setup()
        
        try:
            # 1. Egészség végpont teszt
            print("\n1. Egészség végpont teszt")
            health_result = await api_tester.test_health_endpoint()
            
            results["api_tests"]["health_endpoint"] = health_result["success"]
            
            if health_result["success"]:
                print("✓ Az egészség végpont megfelelően válaszol")
                print(f"Válasz: {json.dumps(health_result.get('response', {}), indent=2)}")
            else:
                print("✗ Az egészség végpont nem válaszol megfelelően")
                if "error" in health_result:
                    print(f"Hiba: {health_result['error']}")
            
            # Ha az egészség végpont működik, folytassuk a többi tesztet
            if health_result["success"]:
                # 2. Parancs végpont teszt
                print("\n2. Parancs végpont teszt")
                command_result = await api_tester.test_command_endpoint("Echo test message")
                
                results["api_tests"]["command_endpoint"] = command_result["success"]
                
                if command_result["success"]:
                    print("✓ A parancs végpont megfelelően válaszol")
                    print(f"Válasz: {json.dumps(command_result.get('response', {}), indent=2)}")
                else:
                    print("✗ A parancs végpont nem válaszol megfelelően")
                    if "error" in command_result:
                        print(f"Hiba: {command_result['error']}")
                
                # 3. Munkamenet végpont teszt
                print("\n3. Munkamenet végpont teszt")
                session_result = await api_tester.test_session_endpoint()
                
                results["api_tests"]["session_endpoint"] = session_result["success"]
                
                if session_result["success"]:
                    print("✓ A munkamenet végpont megfelelően válaszol")
                    print(f"Létrehozott munkamenet azonosító: {session_result.get('session_id', 'N/A')}")
                    print(f"Válasz: {json.dumps(session_result.get('response', {}), indent=2)}")
                else:
                    print("✗ A munkamenet végpont nem válaszol megfelelően")
                    if "error" in session_result:
                        print(f"Hiba: {session_result['error']}")
            
        finally:
            await api_tester.teardown()
        
        # UI tesztek
        print("\n=== UI tesztelés ===")
        
        ui_tester = UITester()
        
        # Útmutató létrehozása
        guide_path = ui_tester.create_ui_test_guide()
        results["ui_tests"]["created_guide"] = os.path.exists(guide_path)
        
        if results["ui_tests"]["created_guide"]:
            print(f"✓ UI tesztelési útmutató sikeresen létrehozva: {guide_path}")
        else:
            print("✗ Az UI tesztelési útmutató létrehozása nem sikerült")
        
        # Böngésző megnyitása - opcionális
        browser_choice = input("\nSzeretnéd megnyitni a felhasználói felületet a böngészőben? (i/n): ")
        if browser_choice.lower() in ["i", "igen", "y", "yes"]:
            browser_result = ui_tester.open_in_browser()
            results["ui_tests"]["browser_open"] = browser_result
            
            if browser_result:
                print("✓ A felhasználói felület megnyílt a böngészőben")
                
                print("\nKérlek, kövesd a létrehozott UI tesztelési útmutatót a manuális teszteléshez.")
                print(f"Az útmutató itt található: {guide_path}")
                
                ui_test_feedback = input("\nA manuális tesztelés után értékeld a felhasználói felületet (1-5 skálán): ")
                try:
                    ui_rating = int(ui_test_feedback)
                    results["ui_tests"]["manual_rating"] = ui_rating
                    print(f"A megadott értékelés: {ui_rating}/5")
                except ValueError:
                    print("Érvénytelen értékelés, kihagyás...")
            else:
                print("✗ Nem sikerült megnyitni a felhasználói felületet a böngészőben")
        
        # Összesítés
        print("\n=== Összegzés ===")
        
        # API tesztek értékelése
        api_test_count = len(results["api_tests"])
        api_success_count = sum(1 for success in results["api_tests"].values() if success)
        
        if api_test_count > 0:
            api_success_rate = api_success_count / api_test_count * 100
            print(f"API tesztek sikerességi aránya: {api_success_rate:.1f}% ({api_success_count}/{api_test_count})")
        else:
            api_success_rate = 0
            print("Nem futottak le API tesztek")
        
        # UI tesztek értékelése
        ui_test_count = len(results["ui_tests"])
        ui_success_count = sum(1 for success in results["ui_tests"].values() if success)
        
        if ui_test_count > 0:
            ui_success_rate = ui_success_count / ui_test_count * 100
            print(f"UI tesztek sikerességi aránya: {ui_success_rate:.1f}% ({ui_success_count}/{ui_test_count})")
        else:
            ui_success_rate = 0
            print("Nem futottak le UI tesztek")
        
        # Végső értékelés
        if api_success_rate >= 50 and ui_success_rate >= 50:
            results["overall_success"] = True
            print("\n✅ Az API és UI tesztek SIKERESEK! A rendszer megfelelően működik.")
        else:
            results["overall_success"] = False
            print("\n❌ Az API vagy UI tesztek SIKERTELENEK! További fejlesztésekre van szükség.")
        
        return results
        
    except Exception as e:
        logger.error(f"Hiba az API és UI teszt végrehajtása közben: {e}", exc_info=True)
        return {"overall_success": False, "error": str(e)}

async def run_async_tests():
    """Run the API and UI tests asynchronously"""
    results = await test_api_and_ui()
    return results["overall_success"]

def run_tests():
    """Synchronous wrapper for API and UI tests"""
    return asyncio.run(run_async_tests())

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
