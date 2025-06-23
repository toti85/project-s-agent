"""
Project-S Minimális Rendszer Ellenőrzés
--------------------------------------
Ez a szkript ellenőrzi a minimális rendszer összetevőit és függőségeit.
Futtatás előtt ellenőrizhetjük, hogy minden rendben van-e.
"""

import sys
import os
import importlib
import subprocess
from pathlib import Path

def print_header(title):
    """Formázott fejléc kiírása"""
    print("\n" + "=" * 60)
    print(f" {title}")
    print("=" * 60)

def check_python_version():
    """Python verzió ellenőrzése"""
    print_header("Python Verzió Ellenőrzés")
    ver = sys.version_info
    print(f"Python verzió: {ver.major}.{ver.minor}.{ver.micro}")
    
    if ver.major < 3 or (ver.major == 3 and ver.minor < 8):
        print("❌ HIBA: Python 3.8 vagy újabb verzió szükséges!")
        return False
    else:
        print("✅ Python verzió megfelelő")
        return True

def check_dependencies():
    """Függőségek ellenőrzése"""
    print_header("Függőségek Ellenőrzése")
    
    required_packages = {
        "asyncio": "Aszinkron műveletek",
        "httpx": "HTTP kérések küldése",
        "yaml": "YAML fájlok kezelése",
        "langgraph": "LangGraph integráció",
    }
    
    all_ok = True
    
    for package, description in required_packages.items():
        try:
            importlib.import_module(package)
            print(f"✅ {package}: Telepítve ({description})")
        except ImportError:
            print(f"❌ {package}: Hiányzik! ({description})")
            all_ok = False
    
    if not all_ok:
        print("\nHiányzó csomagok telepítése:")
        print("pip install -r requirements_minimal.txt")
    
    return all_ok

def check_api_keys():
    """API kulcsok ellenőrzése"""
    print_header("API Kulcsok Ellenőrzése")
    
    openai_key = os.environ.get("OPENAI_API_KEY", "")
    openrouter_key = os.environ.get("OPENROUTER_API_KEY", "")
    
    if openai_key:
        print(f"✅ OpenAI API kulcs: Beállítva ({openai_key[:5]}...{openai_key[-4:] if len(openai_key) > 8 else ''})")
    else:
        print("❓ OpenAI API kulcs: Nincs beállítva")
    
    if openrouter_key:
        print(f"✅ OpenRouter API kulcs: Beállítva ({openrouter_key[:5]}...{openrouter_key[-4:] if len(openrouter_key) > 8 else ''})")
    else:
        print("❓ OpenRouter API kulcs: Nincs beállítva")
    
    if not openai_key and not openrouter_key:
        print("\n⚠️ Figyelem: Egyik API kulcs sincs beállítva!")
        print("Az AI integráció nem fog működni. Állíts be legalább egy API kulcsot:")
        print("  - Windows: set OPENAI_API_KEY=your_key_here")
        print("  - Linux/Mac: export OPENAI_API_KEY=your_key_here")
        print("  - Vagy használd a start_minimal.bat/sh fájlokat és add meg ott a kulcsokat")
        return False
    
    return True

def check_file_structure():
    """Fájlszerkezet ellenőrzése"""
    print_header("Fájlszerkezet Ellenőrzése")
    
    required_files = [
        ("main_minimal.py", "Alapvető minimális verzió"),
        ("main_minimal_langgraph.py", "LangGraph integrációs verzió"),
        ("main_minimal_full.py", "Teljes minimális verzió"),
        ("requirements_minimal.txt", "Minimális függőségek"),
        ("integrations/simple_ai.py", "Egyszerű AI integráció"),
        ("integrations/langgraph_minimal.py", "Minimális LangGraph integráció"),
        ("core/event_bus.py", "Eseménykezelő rendszer"),
        ("core/error_handler.py", "Hibakezelő rendszer"),
    ]
    
    all_ok = True
    
    for file_path, description in required_files:
        if os.path.exists(file_path):
            print(f"✅ {file_path}: Megtalálva ({description})")
        else:
            print(f"❌ {file_path}: Hiányzik! ({description})")
            all_ok = False
    
    if not os.path.exists("logs"):
        os.makedirs("logs", exist_ok=True)
        print("📁 Létrehozva: logs mappa")
    
    return all_ok

def run_simple_test():
    """Egyszerű teszt végrehajtása"""
    print_header("Egyszerű Teszt Végrehajtása")
    
    try:
        # Importáljuk az eseménykezelőt
        sys.path.append(os.getcwd())
        from core.event_bus import event_bus
        
        # Regisztráljuk a tesztkezelőt
        async def test_handler(event_data):
            print(f"✅ Esemény sikeresen fogadva: {event_data}")
        
        event_bus.subscribe("test.event", test_handler)
        
        print("✅ Eseménykezelő sikeresen importálva és tesztkezelő regisztrálva")
        print("✅ Egyszerű teszt sikeres - a rendszer indulásra kész")
        return True
        
    except Exception as e:
        print(f"❌ Hiba a teszt során: {str(e)}")
        return False

def main():
    """Fő függvény"""
    print("\n" + "=" * 60)
    print(" PROJECT-S MINIMÁLIS RENDSZER ELLENŐRZÉS")
    print("=" * 60 + "\n")
    
    checks = {
        "Python verzió": check_python_version(),
        "Függőségek": check_dependencies(),
        "API kulcsok": check_api_keys(),
        "Fájlszerkezet": check_file_structure(),
        "Egyszerű teszt": run_simple_test(),
    }
    
    print_header("Ellenőrzés Összesítés")
    
    all_ok = True
    for check_name, result in checks.items():
        status = "✅ OK" if result else "❌ HIBA"
        print(f"{check_name}: {status}")
        if not result:
            all_ok = False
    
    print("\n" + "=" * 60)
    if all_ok:
        print("✅ MINDEN ELLENŐRZÉS SIKERES - A rendszer indulásra kész!")
        print("\nIndítás:")
        print("  - Windows: start_minimal.bat")
        print("  - Linux/Mac: ./start_minimal.sh")
    else:
        print("⚠️ FIGYELEM - Néhány ellenőrzés hibát jelzett!")
        print("Javítsd a fenti hibákat a rendszer indítása előtt.")
    print("=" * 60 + "\n")

if __name__ == "__main__":
    main()
