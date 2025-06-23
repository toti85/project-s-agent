"""
Project-S + LangGraph Hibrid Rendszer - Alapvető teszt szkript
-----------------------------------------------------------
Ez a szkript az alap funkcionalitást teszteli a Project-S + LangGraph rendszerben.
"""
import os
import sys
import asyncio
import json
import logging
from typing import Dict, Any, List
import time

# Naplózás beállítása
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("basic_test")

async def run_basic_tests():
    """Alapvető tesztfuttatás"""
    try:
        # Import Project-S kliens
        from project_s_client import ProjectSClient
        
        # Kliens létrehozása
        client = ProjectSClient()
        logger.info("Project-S kliens sikeresen inicializálva")
        
        # 1. Alapvető parancs végrehajtása
        print("\n=== 1. Alapvető működési teszt ===")
        print("Parancs: 'Írj egy Hello World programot Python-ban és mentsd el hello.py fájlba'")
        
        start_time = time.time()
        
        response = await client.execute_command(
            "Írj egy Hello World programot Python-ban és mentsd el hello.py fájlba"
        )
        
        duration = time.time() - start_time
        
        print(f"Válasz: {json.dumps(response, indent=2)}")
        print(f"Végrehajtási idő: {duration:.2f} másodperc")
        
        # Ellenőrizzük, hogy létrejött-e a fájl
        if os.path.exists("hello.py"):
            print("✓ A hello.py fájl sikeresen létrejött!")
            with open("hello.py", "r") as f:
                content = f.read()
                print(f"Fájl tartalma:\n{content}")
        else:
            print("✗ A hello.py fájl nem jött létre!")
        
        # 2. Állapotkezelés ellenőrzése
        print("\n=== 2. Állapotkezelés teszt ===")
        print("Parancs: 'Mi volt az előző feladat, amit megoldottál?'")
        
        response2 = await client.execute_command(
            "Mi volt az előző feladat, amit megoldottál?"
        )
        
        print(f"Válasz: {json.dumps(response2, indent=2)}")
        
        # Ellenőrizzük, hogy a válasz tartalmazza-e a "Hello World" és "Python" szavakat
        contains_hello = "hello" in response2.get("response", "").lower()
        contains_python = "python" in response2.get("response", "").lower()
        if contains_hello and contains_python:
            print("✓ Az állapotkezelés megfelelően működik, a rendszer emlékszik az előző feladatra!")
        else:
            print("✗ Az állapotkezelés nem működik megfelelően!")
        
        # 3. LangGraph komponens teszt
        print("\n=== 3. LangGraph komponens teszt ===")
        print("Parancs: 'Készíts egy munkafolyamatot a következő lépésekkel: 1) Készíts egy listát 5 gyümölccsel, 2) Rendezd őket abc-sorrendbe, 3) Írd ki egy fruits.txt fájlba'")
        
        response3 = await client.execute_command(
            "Készíts egy munkafolyamatot a következő lépésekkel: 1) Készíts egy listát 5 gyümölccsel, 2) Rendezd őket abc-sorrendbe, 3) Írd ki egy fruits.txt fájlba"
        )
        
        print(f"Válasz: {json.dumps(response3, indent=2)}")
        
        # Ellenőrizzük, hogy létrejött-e a fájl
        if os.path.exists("fruits.txt"):
            print("✓ A fruits.txt fájl sikeresen létrejött!")
            with open("fruits.txt", "r") as f:
                content = f.read()
                print(f"Fájl tartalma:\n{content}")
                
            # Ellenőrizzük, hogy a tartalom rendezett-e
            lines = [line.strip() for line in content.split("\n") if line.strip()]
            sorted_lines = sorted(lines)
            if lines == sorted_lines:
                print("✓ A gyümölcsök megfelelően rendezve vannak!")
            else:
                print("✗ A gyümölcsök nincsenek megfelelően rendezve!")
        else:
            print("✗ A fruits.txt fájl nem jött létre!")
            
        # 4. Eszköz használat teszt
        print("\n=== 4. Eszköz használat teszt ===")
        print("Parancs: 'Listázd a jelenlegi könyvtár tartalmát'")
        
        response4 = await client.execute_command("Listázd a jelenlegi könyvtár tartalmát")
        print(f"Válasz: {json.dumps(response4, indent=2)}")
        
        # Ellenőrizzük, hogy a válaszban szerepelnek-e a korábban létrehozott fájlok
        contains_hello_py = "hello.py" in response4.get("response", "").lower()
        contains_fruits_txt = "fruits.txt" in response4.get("response", "").lower()
        if contains_hello_py and contains_fruits_txt:
            print("✓ Az eszköz használat megfelelően működik, a fájllistázás sikeres!")
        else:
            print("✗ Az eszköz használat nem működik megfelelően!")
        
        # 5. Hibakezelés teszt
        print("\n=== 5. Hibakezelés teszt ===")
        print("Parancs: 'Olvasd be a nem_letezik.txt fájl tartalmát'")
        
        response5 = await client.execute_command("Olvasd be a nem_letezik.txt fájl tartalmát")
        print(f"Válasz: {json.dumps(response5, indent=2)}")
        
        # Ellenőrizzük, hogy a rendszer helyesen kezeli-e a hibát
        if "not found" in response5.get("response", "").lower() or "nem található" in response5.get("response", "").lower() or "nem létezik" in response5.get("response", "").lower():
            print("✓ A hibakezelés megfelelően működik!")
        else:
            print("✗ A hibakezelés nem működik megfelelően!")
        
        print("\n=== Összegzés ===")
        print("Az alap tesztek végrehajtása befejeződött.")
        
        # Kliens bezárása, ha szükséges
        if hasattr(client, 'close') and callable(client.close):
            await client.close()
        
        return True
    
    except Exception as e:
        logger.error(f"Hiba a teszt végrehajtása közben: {e}", exc_info=True)
        return False

async def run_async_tests():
    """Run the basic tests asynchronously"""
    return await run_basic_tests()

def run_tests():
    """Synchronous wrapper for run_basic_tests"""
    return asyncio.run(run_basic_tests())

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
