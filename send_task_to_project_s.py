"""
Auto Task Sender for Project-S
-----------------------------
Automatikusan elküldi a Downloads elemzési feladatot a futó Project-S rendszernek.
"""

import subprocess
import time
import sys

def send_task_to_project_s():
    """Send the Downloads analysis task to Project-S."""
    
    # A magyar nyelvű feladat
    task = "S, elemezd a Downloads mappámat: 1. Kategorizálj minden fájlt típus szerint 2. Azonosítsd a duplikátumokat 3. Javasolj szervezési struktúrát 4. Készíts cleanup action plan-t"
    
    print("📤 Project-S feladat küldése...")
    print(f"Feladat: {task}")
    print()
    
    try:
        # PowerShell parancs a feladat elküldéséhez
        powershell_cmd = f'''
        Add-Type -AssemblyName System.Windows.Forms
        Start-Sleep -Milliseconds 500
        [System.Windows.Forms.SendKeys]::SendWait("{task}")
        Start-Sleep -Milliseconds 200
        [System.Windows.Forms.SendKeys]::SendWait("{{ENTER}}")
        '''
        
        # Futtassuk a PowerShell parancsot
        result = subprocess.run(
            ["powershell", "-Command", powershell_cmd],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print("✅ Feladat sikeresen elküldve a Project-S-nek!")
            print("🔄 A rendszer dolgozik a feladaton...")
            print("📋 Nézd meg a Project-S terminal outputját az eredményért!")
        else:
            print(f"❌ Hiba történt: {result.stderr}")
            
    except Exception as e:
        print(f"❌ Hiba a feladat küldésekor: {e}")

if __name__ == "__main__":
    print("🤖 Project-S Multi-Model AI Task Sender")
    print("=" * 50)
    send_task_to_project_s()
