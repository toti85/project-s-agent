"""
Project-S Minimális Verzió LangGraph Integrációval
-------------------------------------------------
Ez a fájl a Project-S rendszer minimális verzióját indítja el,
LangGraph integrációval.
"""

import asyncio
import logging
import os
from pathlib import Path
import sys

# Konfiguráljuk a naplózást
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(levelname)s] %(name)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('logs/minimal_system.log', mode='w')
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
from integrations.langgraph_minimal import langgraph_minimal

# Inicializáljuk az error handlert
error_handler = ErrorHandler()

async def main():
    """A minimális rendszer fő belépési pontja LangGraph integrációval."""
    print("\n" + "="*50)
    print("Project-S Minimális Verzió LangGraph Integrációval")
    print("="*50 + "\n")
    
    try:
        # Az eseménybusz inicializálása
        event_bus.register_default_handlers()
        logger.info("Eseménybusz inicializálva")
        
        # Teszt üzenetek LangGraph-al
        test_commands = [
            "Hello World!",
            "Mi a Project-S rendszer?",
        ]
        
        print("LangGraph teszt végrehajtása...\n")
        for cmd in test_commands:
            print(f"Parancs: {cmd}")
            # Küldjük az eseményt az eseménybusznak
            await event_bus.publish("command.received", {"command": cmd})
            
            # Feldolgozzuk a LangGraph-al
            result = await langgraph_minimal.process_with_graph(cmd)
            print(f"Eredmény: {result}\n")
        
        # Tartsuk életben a programot
        print("A rendszer fut. Nyomj Ctrl+C a kilépéshez.")
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
