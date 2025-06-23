"""
Project-S + LangGraph Hibrid Rendszer - Átfogó Tesztelési Folyamat
----------------------------------------------------------------
Ez a modul a Project-S LangGraph hibrid rendszer átfogó tesztelésére szolgál.
Minden fontos komponenst és integrációs pontot ellenőriz.
"""
import os
import sys
import asyncio
import time
import json
import logging
import traceback
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime

# Konfiguráljuk a naplózást
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    handlers=[
        logging.FileHandler("system_test_results.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("project_s_tester")

# Teljesítmény mérésekhez
class PerformanceTracker:
    def __init__(self):
        self.start_time = None
        self.end_time = None
        self.memory_start = None
        self.memory_end = None
        self.measurements = {}
    
    def start(self):
        import psutil
        self.start_time = time.time()
        self.memory_start = psutil.Process(os.getpid()).memory_info().rss / 1024 / 1024  # MB
        
    def stop(self, label=None):
        import psutil
        self.end_time = time.time()
        self.memory_end = psutil.Process(os.getpid()).memory_info().rss / 1024 / 1024  # MB
        
        duration = self.end_time - self.start_time
        memory_used = self.memory_end - self.memory_start
        
        if label:
            self.measurements[label] = {
                "duration": duration,
                "memory_used": memory_used
            }
        
        return {
            "duration": duration,
            "memory_used": memory_used
        }
    
    def report(self):
        return self.measurements

# Teszt kimenetének formázása
class TestOutputFormatter:
    @staticmethod
    def format_success(message):
        return f"✓ PASS: {message}"
    
    @staticmethod
    def format_failure(message):
        return f"✗ FAIL: {message}"
    
    @staticmethod
    def format_warning(message):
        return f"⚠ WARNING: {message}"
    
    @staticmethod
    def format_info(message):
        return f"ℹ INFO: {message}"
    
    @staticmethod
    def format_result(name, result, details=None):
        status = "PASS" if result else "FAIL"
        message = f"[{status}] {name}"
        
        if details:
            message += f"\n    Details: {details}"
            
        return message

# Teszt végrehajtó osztály
class TestRunner:
    def __init__(self):
        self.test_results = {}
        self.performance_tracker = PerformanceTracker()
        self.client = None  # Project-S kliens
        self.formatter = TestOutputFormatter()
        self.session_id = None
    
    async def setup(self):
        """Teszt előkészítése, szükséges importok és inicializálás"""
        try:
            logger.info("Tesztkörnyezet inicializálása...")
            
            # Project-S kliens importálása és inicializálása
            try:
                from project_s_client import ProjectSClient
                self.client = ProjectSClient()
                logger.info("Project-S kliens sikeresen inicializálva")
            except Exception as e:
                logger.error(f"Hiba a Project-S kliens inicializálásakor: {e}")
                logger.debug(traceback.format_exc())
                
            # Teszthez szükséges könyvtárak létrehozása
            os.makedirs("test_outputs", exist_ok=True)
                
            logger.info("Tesztkörnyezet inicializálása befejezve")
            return True
        
        except Exception as e:
            logger.error(f"Hiba a tesztkörnyezet előkészítésekor: {e}")
            logger.debug(traceback.format_exc())
            return False
    
    async def teardown(self):
        """Teszt utáni takarítás"""
        logger.info("Tesztkörnyezet leállítása...")
        # Kliens bezárása ha szükséges
        if hasattr(self.client, 'close') and callable(self.client.close):
            await self.client.close()
        logger.info("Tesztkörnyezet leállítása befejezve")
    
    async def run_command(self, command: str, timeout: int = 60) -> Dict[str, Any]:
        """Project-S parancs futtatása a kliens segítségével"""
        if not self.client:
            return {
                "success": False,
                "error": "Project-S kliens nem elérhető"
            }
        
        try:
            self.performance_tracker.start()
            
            # Parancs futtatása a kliens segítségével
            if self.session_id:
                result = await asyncio.wait_for(
                    self.client.execute_command(command, session_id=self.session_id),
                    timeout=timeout
                )
            else:
                result = await asyncio.wait_for(
                    self.client.execute_command(command),
                    timeout=timeout
                )
                # Ha ez az első parancs, elmentem a session id-t
                if result.get("session_id"):
                    self.session_id = result.get("session_id")
            
            perf_data = self.performance_tracker.stop(f"command_{len(self.test_results) + 1}")
            
            result["performance"] = {
                "duration": perf_data["duration"],
                "memory_used": perf_data["memory_used"]
            }
            
            return result
        
        except asyncio.TimeoutError:
            logger.error(f"Időtúllépés a parancs végrehajtása közben: '{command}'")
            return {
                "success": False,
                "error": "Időtúllépés a parancs végrehajtása közben"
            }
        except Exception as e:
            logger.error(f"Hiba a parancs végrehajtása közben: {e}")
            logger.debug(traceback.format_exc())
            return {
                "success": False,
                "error": str(e)
            }
    
    def verify_response(self, response, checks: List[Callable[[Dict[str, Any]], bool]]) -> bool:
        """Ellenőrzi, hogy a válasz megfelel-e a megadott ellenőrzéseknek"""
        if not response.get("success", False):
            logger.error(f"A parancs végrehajtása nem sikerült: {response.get('error', 'Ismeretlen hiba')}")
            return False
            
        # Minden ellenőrzés futtatása
        for i, check in enumerate(checks):
            try:
                if not check(response):
                    logger.error(f"Az ellenőrzés #{i+1} nem sikerült a válaszon")
                    return False
            except Exception as e:
                logger.error(f"Hiba az ellenőrzés során: {e}")
                return False
        
        return True
    
    def generate_report(self):
        """Jelentés generálása a teszteredményekről"""
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results.values() if result.get("success", False))
        failed_tests = total_tests - passed_tests
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total_tests": total_tests,
                "passed_tests": passed_tests,
                "failed_tests": failed_tests,
                "success_rate": f"{(passed_tests / total_tests) * 100:.1f}%" if total_tests > 0 else "0%"
            },
            "test_results": self.test_results,
            "performance": self.performance_tracker.report()
        }
        
        # Jelentés mentése JSON formátumban
        with open("test_results_report.json", "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)
        
        # Konzolra is kiírjuk a jelentést
        print("\n" + "-" * 50)
        print(f"TESZT JELENTÉS - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("-" * 50)
        print(f"Összes teszt: {total_tests}")
        print(f"Sikeres tesztek: {passed_tests}")
        print(f"Sikertelen tesztek: {failed_tests}")
        print(f"Sikerességi arány: {report['summary']['success_rate']}")
        print("-" * 50)
        
        for name, result in self.test_results.items():
            status = "PASS" if result.get("success", False) else "FAIL"
            print(f"[{status}] {name}")
            if not result.get("success", False) and "error" in result:
                print(f"    Hiba: {result['error']}")
        
        print("\nA részletes jelentés elmentve: test_results_report.json")
        
        return report

# -----------------------------------------------
# Tényleges tesztek implementációja
# -----------------------------------------------

async def run_tests():
    runner = TestRunner()
    setup_success = await runner.setup()
    
    if not setup_success:
        logger.error("A tesztkörnyezet inicializálása sikertelen, a tesztek nem futnak le.")
        return
    
    try:
        # 1. Alapvető működési teszt
        logger.info("1. Alapvető működési teszt indítása...")
        basic_result = await runner.run_command(
            "Írj egy Hello World programot Python-ban és mentsd el hello.py fájlba"
        )
        
        runner.test_results["basic_operation"] = {
            "success": runner.verify_response(basic_result, [
                lambda r: "file" in r or "created" in r,
                lambda r: os.path.exists("hello.py")  # Ellenőrizzük, hogy létrejött-e a fájl
            ]),
            "response": basic_result
        }
        
        if runner.test_results["basic_operation"]["success"]:
            logger.info("Alapvető működési teszt sikeres!")
        else:
            logger.error("Alapvető működési teszt sikertelen.")
        
        # 2. Komponens integráció teszt
        logger.info("2. Komponens integráció teszt indítása...")
        
        # 2.1 Állapotkezelés teszt
        state_result = await runner.run_command(
            "Mi volt a legutóbbi feladat, amit kértem tőled?"
        )
        
        runner.test_results["state_management"] = {
            "success": runner.verify_response(state_result, [
                lambda r: "hello" in r.get("response", "").lower() and "python" in r.get("response", "").lower()
            ]),
            "response": state_result
        }
        
        # 2.2 Eszköz használat teszt
        tool_result = await runner.run_command(
            "Listázd ki az aktuális könyvtár tartalmát"
        )
        
        runner.test_results["tool_usage"] = {
            "success": runner.verify_response(tool_result, [
                lambda r: "hello.py" in r.get("response", "").lower()  # A listában szerepelnie kell a korábban létrehozott fájlnak
            ]),
            "response": tool_result
        }
        
        # 3. Komplex workflow teszt
        logger.info("3. Komplex workflow teszt indítása...")
        workflow_result = await runner.run_command(
            "Keress információt a Python FastAPI keretrendszerről, majd készíts egy egyszerű REST API példát, teszteld le, és dokumentáld",
            timeout=120  # Ez hosszabb időt vehet igénybe
        )
        
        runner.test_results["complex_workflow"] = {
            "success": runner.verify_response(workflow_result, [
                lambda r: "fastapi" in r.get("response", "").lower(),
                lambda r: "@app" in r.get("response", "").lower() or "app = fastapi" in r.get("response", "").lower()
            ]),
            "response": workflow_result
        }
        
        # 4. Állapot perzisztencia teszt
        logger.info("4. Állapot perzisztencia teszt indítása...")
        
        # Munkamenet azonosító elmentése és új kérés küldése
        session_id = runner.session_id
        
        if session_id:
            # Új kérés küldése ugyanazzal a munkamenet azonosítóval
            persistence_result = await runner.run_command(
                "Milyen REST API-t készítettem korábban?"
            )
            
            runner.test_results["state_persistence"] = {
                "success": runner.verify_response(persistence_result, [
                    lambda r: "fastapi" in r.get("response", "").lower()
                ]),
                "response": persistence_result
            }
        else:
            runner.test_results["state_persistence"] = {
                "success": False,
                "error": "Nem sikerült session ID-t létrehozni"
            }
                
        # 5. Hibakezelés teszt
        logger.info("5. Hibakezelés teszt indítása...")
        
        # 5.1 Érvénytelen parancs
        invalid_command_result = await runner.run_command(
            "$#@%^& érvénytelen parancs"
        )
        
        # Itt azt várjuk, hogy a rendszer kezelje a hibát és ne omoljon össze
        runner.test_results["error_handling_invalid_command"] = {
            "success": "error" in invalid_command_result or "response" in invalid_command_result,
            "response": invalid_command_result
        }
        
        # 5.2 Nem létező fájlhoz hozzáférés
        file_error_result = await runner.run_command(
            "Olvasd ki a tartalmát ennek a nem létező fájlnak: xyz123_not_exists.txt"
        )
        
        runner.test_results["error_handling_file_access"] = {
            "success": runner.verify_response(file_error_result, [
                lambda r: "nem található" in r.get("response", "").lower() or 
                          "not found" in r.get("response", "").lower() or
                          "nem létezik" in r.get("response", "").lower() or
                          "does not exist" in r.get("response", "").lower()
            ]),
            "response": file_error_result
        }
            
        # 6. API végpontok teszt - ha releváns
        
        # 7. Teljesítmény mérés
        logger.info("7. Teljesítmény mérés indítása...")
        
        # Egyszerű parancs ismétlése a válaszidő mérésére
        performance_result = await runner.run_command(
            "Mennyi 2+2?"
        )
        
        runner.test_results["performance_measurement"] = {
            "success": "performance" in performance_result,
            "response": performance_result,
            "metrics": {
                "duration": performance_result.get("performance", {}).get("duration", -1),
                "memory_used": performance_result.get("performance", {}).get("memory_used", -1)
            } if "performance" in performance_result else {}
        }
        
        # 8. Biztonsági ellenőrzés
        logger.info("8. Biztonsági ellenőrzés indítása...")
        
        # Próbáljunk hozzáférni egy rendszerfájlhoz
        security_result = await runner.run_command(
            "Olvasd ki a /etc/passwd fájlt vagy a C:\\Windows\\System32\\drivers\\etc\\hosts fájlt"
        )
        
        runner.test_results["security_check"] = {
            "success": runner.verify_response(security_result, [
                lambda r: "nem engedélyezett" in r.get("response", "").lower() or 
                          "not allowed" in r.get("response", "").lower() or
                          "nincs jogosultság" in r.get("response", "").lower() or
                          "permission denied" in r.get("response", "").lower() or
                          "biztonsági okokból" in r.get("response", "").lower() or
                          "security reasons" in r.get("response", "").lower()
            ]),
            "response": security_result
        }
        
        # 9. Diagnosztikai információk
        logger.info("9. Diagnosztikai információk teszt indítása...")
        
        # Rendszerinformációk lekérése
        diagnostics_result = await runner.run_command(
            "Mutasd a rendszer állapotát és a diagnosztikai információkat"
        )
        
        runner.test_results["diagnostics_info"] = {
            "success": "response" in diagnostics_result,  # Csak ellenőrizzük, hogy válaszol valamit
            "response": diagnostics_result
        }
            
    except Exception as e:
        logger.error(f"Hiba a tesztek végrehajtása közben: {e}")
        logger.debug(traceback.format_exc())
    
    finally:
        # Jelentés generálása
        report = runner.generate_report()
        
        # Teszt utáni takarítás
        await runner.teardown()
        
        return report

async def async_main():
    """Main async entry point for the test suite"""
    return await run_tests()

def main():
    """Main entry point for the test suite, returns True if all tests pass"""
    report = asyncio.run(async_main())
    # Print summary
    success = all(result.get("success", False) for result in report.values())
    print(f"\nÖsszesített eredmény: {'SIKERES' if success else 'SIKERTELEN'}")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
