"""
Project-S - LangGraph Integráció Teszt
--------------------------------------
Ez a teszt a LangGraph integrációt vizsgálja a Project-S rendszerben.
Ellenőrzi az állapotkezelést, a komponensek közötti adatáramlást és a munkafolyamatok kezelését.
"""
import asyncio
import json
import logging
import time
import os
from typing import Dict, Any, List, Optional

# Naplózás beállítása
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("langgraph_test")

async def test_langgraph_integration():
    """LangGraph integráció tesztelése"""
    try:
        # Importáljuk a LangGraph interfészt közvetlenül - ez opcionális, ha elérhető
        direct_access = False
        try:
            from integrations.langgraph_integration import LangGraphIntegrator
            from core.event_bus import event_bus
            direct_access = True
            logger.info("Közvetlen hozzáférés a LangGraph integrációs komponensekhez")
        except ImportError:
            logger.info("Nincs közvetlen hozzáférés a LangGraph komponensekhez, a klienst használjuk")
        
        # Importáljuk a Project-S klienst
        from project_s_client import ProjectSClient
        client = ProjectSClient()
        logger.info("Project-S kliens sikeresen inicializálva")
        
        results = {
            "tests": {},
            "overall_success": False
        }
        
        # 1. Ellenőrizzük, hogy a rendszer támogatja-e a LangGraph workflowkat
        print("\n=== 1. LangGraph workflow támogatás ellenőrzése ===")
        
        response = await client.execute_command(
            "Támogatod a LangGraph workflow-kat? Ha igen, készíts egy egyszerű példát, amely bemutatja, hogyan működik a munkafolyamat-kezelés a rendszerben."
        )
        
        print(f"Válasz: {json.dumps(response.get('response', ''), indent=2)}")
        
        # Ellenőrizzük a választ
        supports_langgraph = (
            "langgraph" in response.get("response", "").lower() or 
            "workflow" in response.get("response", "").lower() or
            "munkafolyamat" in response.get("response", "").lower()
        )
        
        results["tests"]["langgraph_support"] = supports_langgraph
        
        if supports_langgraph:
            print("✓ A rendszer támogatja a LangGraph workflowkat!")
        else:
            print("✗ A rendszer nem támogatja a LangGraph workflowkat!")
        
        # 2. Teszteljük a többlépéses munkafolyamatot
        print("\n=== 2. Többlépéses munkafolyamat teszt ===")
        print("Egy komplex, többlépéses feladat végrehajtásával teszteljük a munkafolyamat-kezelést")
        
        workflow_command = """
        Kérlek, hajtsd végre a következő lépéseket sorban:
        1. Készíts egy new_project nevű mappát
        2. A mappában hozz létre egy main.py fájlt, ami egy egyszerű "Hello, LangGraph!" üzenetet ír ki
        3. Készíts egy requirements.txt fájlt is, ami tartalmazza a langgraph csomagot
        4. Futtasd le a Python szkriptet, és add vissza az eredményt
        5. A végén készíts egy rövid összefoglalót a lépésekről
        """
        
        print(f"Parancs: {workflow_command}")
        
        start_time = time.time()
        workflow_response = await client.execute_command(workflow_command)
        duration = time.time() - start_time
        
        print(f"Válasz: {json.dumps(workflow_response.get('response', ''), indent=2)}")
        print(f"Végrehajtási idő: {duration:.2f} másodperc")
        
        # Ellenőrizzük, hogy minden létrejött-e
        directory_exists = os.path.exists("new_project")
        main_exists = os.path.exists(os.path.join("new_project", "main.py"))
        requirements_exists = os.path.exists(os.path.join("new_project", "requirements.txt"))
        
        workflow_success = directory_exists and main_exists and requirements_exists
        results["tests"]["multi_step_workflow"] = workflow_success
        
        if workflow_success:
            print("✓ A többlépéses munkafolyamat sikeresen végrehajtódott!")
            
            # Kiírjuk a létrehozott fájlok tartalmát
            if main_exists:
                with open(os.path.join("new_project", "main.py"), "r") as f:
                    print(f"\nmain.py tartalma:\n{f.read()}")
            
            if requirements_exists:
                with open(os.path.join("new_project", "requirements.txt"), "r") as f:
                    print(f"\nrequirements.txt tartalma:\n{f.read()}")
        else:
            print("✗ A többlépéses munkafolyamat nem teljesült teljesen!")
            if not directory_exists:
                print("  - A new_project mappa nem jött létre")
            if not main_exists:
                print("  - A main.py fájl nem jött létre")
            if not requirements_exists:
                print("  - A requirements.txt fájl nem jött létre")
        
        # 3. Állapotkezelés tesztelése
        print("\n=== 3. Állapotkezelés teszt ===")
        print("Ellenőrizzük, hogy a rendszer megtartja-e a munkafolyamat állapotát")
        
        state_response = await client.execute_command(
            "Mi volt az utolsó feladat, amit végrehajtottál? Sorold fel a lépéseket, amelyeket végrehajtottál."
        )
        
        print(f"Válasz: {json.dumps(state_response.get('response', ''), indent=2)}")
        
        # Ellenőrizzük, hogy a válasz tartalmazza-e a munkafolyamat lépéseit
        state_keywords = ["mappa", "new_project", "main.py", "requirements.txt", "python"]
        state_matches = sum(1 for keyword in state_keywords if keyword.lower() in state_response.get("response", "").lower())
        state_success = state_matches >= 3  # Legalább 3 kulcsszónak egyeznie kell
        
        results["tests"]["state_management"] = state_success
        
        if state_success:
            print("✓ Az állapotkezelés megfelelően működik, a rendszer emlékszik a munkafolyamat lépéseire!")
        else:
            print("✗ Az állapotkezelés nem működik megfelelően!")
        
        # 4. Döntési elágazások tesztelése (ha közvetlen hozzáférésünk van a LangGraph integrációhoz)
        if direct_access:
            print("\n=== 4. Döntési elágazások teszt ===")
            
            integrator = LangGraphIntegrator()
            
            # Létrehozunk egy elágazásos munkafolyamatot
            workflow_id = integrator.create_workflow(
                name="branch_test",
                steps=[{"type": "echo", "message": "Alap lépés végrehajtása"}],
                branches={
                    "branch_a": [{"type": "echo", "message": "A ág végrehajtása"}],
                    "branch_b": [{"type": "echo", "message": "B ág végrehajtása"}]
                }
            )
            
            print(f"Létrehozott workflow azonosító: {workflow_id}")
            
            # Ellenőrzés
            has_workflow = workflow_id in integrator.active_graphs
            has_state = workflow_id in integrator.graph_states
            branches_defined = False
            
            if has_state:
                branches = integrator.graph_states[workflow_id]["context"].get("branches", {})
                branches_defined = len(branches) >= 2
            
            branching_success = has_workflow and has_state and branches_defined
            results["tests"]["branching_workflow"] = branching_success
            
            if branching_success:
                print("✓ A döntési elágazásos munkafolyamat sikeresen létrejött!")
            else:
                print("✗ A döntési elágazásos munkafolyamat létrehozása nem sikerült!")
        
        # 5. Komplex eseménykezelés tesztelése
        print("\n=== 5. Komplex eseménykezelés teszt ===")
        print("Teszteljük az események kezelését és az aszinkron végrehajtást")
        
        # Ez egy olyan feladat, ami valószínűleg aszinkron műveleteket indít
        event_command = """
        Hajts végre egy összetett feladatot párhuzamos lépésekkel:
        1. Hozz létre egy 'data.txt' fájlt, ami tartalmaz 10 véletlen számot
        2. Miközben létrehozod a számokat, készíts egy másik fájlt 'info.txt' néven, amibe írd bele a mai dátumot
        3. Végül olvasd be mindkét fájlt és add vissza a tartalmukat
        """
        
        print(f"Parancs: {event_command}")
        
        event_response = await client.execute_command(event_command)
        print(f"Válasz: {json.dumps(event_response.get('response', ''), indent=2)}")
        
        # Ellenőrizzük, hogy mindkét fájl létrejött-e
        data_exists = os.path.exists("data.txt")
        info_exists = os.path.exists("info.txt")
        
        event_success = data_exists and info_exists
        results["tests"]["complex_event_handling"] = event_success
        
        if event_success:
            print("✓ A komplex eseménykezelés sikeresen végrehajtódott!")
            
            # Fájlok tartalmának ellenőrzése
            if data_exists:
                with open("data.txt", "r") as f:
                    data_content = f.read()
                    print(f"\ndata.txt tartalma:\n{data_content}")
                    
                    # Ellenőrizzük, hogy számokat tartalmaz-e
                    has_numbers = any(c.isdigit() for c in data_content)
                    if has_numbers:
                        print("✓ A data.txt fájl tartalmaz számokat!")
                    else:
                        print("✗ A data.txt fájl nem tartalmaz számokat!")
            
            if info_exists:
                with open("info.txt", "r") as f:
                    info_content = f.read()
                    print(f"\ninfo.txt tartalma:\n{info_content}")
                    
                    # Ellenőrizzük, hogy dátumot tartalmaz-e
                    import re
                    date_pattern = re.compile(r'\d{4}[-/\.]\d{1,2}[-/\.]\d{1,2}|\d{1,2}[-/\.]\d{1,2}[-/\.]\d{2,4}')
                    has_date = bool(date_pattern.search(info_content))
                    
                    if has_date:
                        print("✓ Az info.txt fájl tartalmaz dátumot!")
                    else:
                        print("✗ Az info.txt fájl nem tartalmaz dátumot!")
        else:
            print("✗ A komplex eseménykezelés nem sikerült!")
            if not data_exists:
                print("  - A data.txt fájl nem jött létre")
            if not info_exists:
                print("  - Az info.txt fájl nem jött létre")
        
        # Összesítés
        print("\n=== Összegzés ===")
        
        # Az összes teszt eredményét kiértékeljük
        total_tests = len(results["tests"])
        successful_tests = sum(1 for success in results["tests"].values() if success)
        
        print(f"Összes teszt: {total_tests}")
        print(f"Sikeres tesztek: {successful_tests}")
        print(f"Sikerességi arány: {successful_tests / total_tests * 100:.1f}%")
        
        results["overall_success"] = successful_tests / total_tests >= 0.7  # Legalább 70% sikerességi arány
        
        if results["overall_success"]:
            print("\n✅ A LangGraph integráció teszt SIKERES! A rendszer megfelelően működik.")
        else:
            print("\n❌ A LangGraph integráció teszt SIKERTELEN! További fejlesztésekre van szükség.")
        
        # Kliens bezárása, ha szükséges
        if hasattr(client, 'close') and callable(client.close):
            await client.close()
            
        return results
    
    except Exception as e:
        logger.error(f"Hiba a LangGraph teszt végrehajtása közben: {e}", exc_info=True)
        return {"overall_success": False, "error": str(e)}

async def run_async_tests():
    """Run the LangGraph integration tests asynchronously"""
    results = await test_langgraph_integration()
    return results["overall_success"]

def run_tests():
    """Synchronous wrapper for LangGraph integration tests"""
    return asyncio.run(run_async_tests())

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
