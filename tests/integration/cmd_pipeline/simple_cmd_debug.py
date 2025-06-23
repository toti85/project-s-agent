#!/usr/bin/env python3
print("=== CMD TESZT DEBUG ===")
print("Ha ezt látod, a Python script működik!")

import sys
import os
print(f"Python verzió: {sys.version}")
print(f"Aktuális könyvtár: {os.getcwd()}")

try:
    print("Próbálom betölteni a CMD handlert...")
    from core.ai_command_handler import AICommandHandler
    print("✅ CMD handler betöltve!")
    
    # Egyszerű teszt
    ai_handler = AICommandHandler()
    print("✅ CMD handler példány létrehozva!")
    
    # Sync teszt parancs
    print("Tesztelés: dir parancs...")
    import subprocess
    result = subprocess.run("dir", shell=True, capture_output=True, text=True)
    print(f"Dir parancs eredmény: {result.returncode}")
    print(f"STDOUT: {result.stdout[:100]}...")
    
except Exception as e:
    print(f"❌ HIBA: {e}")
    import traceback
    traceback.print_exc()

print("=== TESZT VÉGE ===")
