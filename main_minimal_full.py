"""
Project-S Teljes Minimális Verzió
--------------------------------
Ez a fájl a Project-S minimális, de teljes verzióját indítja,
amely tartalmazza a LangGraph és AI integrációt is.
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
        logging.FileHandler('logs/minimal_full_system.log', mode='w')
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
from integrations.simple_ai import ai_client

# Inicializáljuk az error handlert
error_handler = ErrorHandler()

class AIBasedLangGraphIntegration:
    """
    Összekötő osztály a LangGraph és az AI között.
    Ez az osztály lehetővé teszi, hogy az AI feldolgozza a munkafolyamaton áthaladó állapotot.
    """
    
    def __init__(self):
        """Inicializálja az integráció osztályt."""
        self.system_prompt = """
        Te egy segítőkész asszisztens vagy a Project-S rendszerben.
        A parancsokat professzionálisan és pontosan dolgozod fel.
        Válaszaid informatívak és hasznosak.
        """
        logger.info("AI-LangGraph integráció inicializálva")
    
    async def process_command_with_ai(self, command: str) -> str:
        """
        Parancs feldolgozása LangGraph és AI segítségével.
        
        Args:
            command: A feldolgozandó parancs
            
        Returns:
            str: A generált válasz
        """
        try:
            # 1. LangGraph előfeldolgozás
            logger.info(f"LangGraph előfeldolgozás: '{command}'")
            langgraph_result = await langgraph_minimal.process_with_graph(command)
            
            # 2. AI válasz generálás
            prompt = f"""
            Parancs: {command}
            
            LangGraph előfeldolgozás eredménye: {langgraph_result}
            
            Kérlek, generálj egy informatív és hasznos választ.
            """
            
            logger.info("AI válasz generálása...")
            ai_response = await ai_client.generate_response(prompt, self.system_prompt)
            
            return ai_response
            
        except Exception as e:
            logger.error(f"Hiba a parancs feldolgozása során: {e}")
            return f"Hiba történt a feldolgozás során: {str(e)}"

# Integráció példány létrehozása
integration = AIBasedLangGraphIntegration()

async def main():
    """A teljes minimális rendszer belépési pontja."""
    print("\n" + "="*50)
    print("Project-S Teljes Minimális Verzió")
    print("="*50 + "\n")
    
    try:
        # Az eseménybusz inicializálása
        event_bus.register_default_handlers()
        logger.info("Eseménybusz inicializálva")
        
        # Ellenőrizzük, hogy van-e API kulcs
        if not os.environ.get("OPENAI_API_KEY") and not os.environ.get("OPENROUTER_API_KEY"):
            print("\n⚠️ FIGYELEM: Nincs beállítva AI API kulcs!")
            print("Állítsd be az OPENAI_API_KEY vagy OPENROUTER_API_KEY környezeti változót.")
            print("A rendszer korlátozott funkcionalitással fut.\n")
        
        # Interaktív mód
        print("Project-S interaktív mód. Írj parancsokat, vagy 'exit' a kilépéshez.\n")
        
        while True:
            user_input = input("> ")
            
            if user_input.lower() in ['exit', 'quit', 'kilep']:
                print("Kilépés...")
                break
            
            # Parancs feldolgozása
            await event_bus.publish("command.received", {"command": user_input})
            
            # Válasz generálása
            print("Feldolgozás...")
            try:
                response = await integration.process_command_with_ai(user_input)
                print(f"\nVÁLASZ:\n{response}\n")
            except Exception as e:
                print(f"\nHiba történt: {str(e)}\n")
            
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
