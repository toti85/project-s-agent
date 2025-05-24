"""
Project-S Minimális Verzió
--------------------------
Ez a fájl a Project-S rendszer minimális verzióját indítja el,
amely csak az alapvető eseménykezelést és parancsok feldolgozását tartalmazza.
"""

import asyncio
import logging
import os
from pathlib import Path
import sys

# Configure logging with UTF-8 encoding for Windows
import io
import sys

# Set UTF-8 encoding for stdout/stderr on Windows
if sys.platform.startswith('win'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(levelname)s] %(name)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('logs/minimal_system.log', mode='w', encoding='utf-8')
    ]
)

logger = logging.getLogger(__name__)

# Biztosítsuk, hogy a logs könyvtár létezik
os.makedirs('logs', exist_ok=True)

# Elérési utak beállítása
project_root = Path(__file__).parent.absolute()
sys.path.append(str(project_root))

# Core komponensek importálása
from core.event_bus import event_bus
from core.error_handler import ErrorHandler

# Inicializáljuk az error handlert
error_handler = ErrorHandler()

async def process_simple_command(command: str) -> str:
    """
    Egyszerű parancsfeldolgozás LangGraph integráció nélkül.
    Ez csak egy teszt implementáció.
    """
    logger.info(f"Processing command: {command}")
    
    # Küldjük az eseményt az eseménybusznak
    await event_bus.publish("command.received", {"command": command})
    
    # Egyszerű válasz generálása
    return f"Command received: {command}"

async def main():
    """A minimális rendszer fő belépési pontja."""
    print("\n" + "="*50)
    print("Project-S Minimális Verzió")
    print("="*50 + "\n")
    
    try:
        # Az eseménybusz inicializálása
        event_bus.register_default_handlers()
        logger.info("Event bus initialized")
        
        # Teszt parancs feldolgozása
        test_command = "Hello World!"
        result = await process_simple_command(test_command)
        print(f"\nTeszt eredmény: {result}\n")
        
        # Tartsuk életben a programot
        print("A minimális rendszer fut. Nyomj Ctrl+C a kilépéshez.")
        while True:
            await asyncio.sleep(1)
            
    except KeyboardInterrupt:
        logger.info("Kilépési kérelem fogadva, leállítás...")
        print("\nA Project-S minimális verzió leáll...")
        
    except Exception as e:
        await error_handler.handle_error(e, {"component": "main", "operation": "startup"})
        print(f"Hiba történt: {str(e)}")
    
    print("\n" + "="*50)
    print("Project-S Minimális Verzió - Leállítva")
    print("="*50 + "\n")

if __name__ == "__main__":
    asyncio.run(main())
