"""
Example Runner for Technology Analysis Workflow
--------------------------------------------
Ez a script bemutatja a technológiai elemzési munkafolyamat használatát
"""
import os
import sys
import asyncio
import logging
from pathlib import Path

# Project-S könyvtár hozzáadása a sys.path-hoz
sys.path.append(str(Path(__file__).parent.parent))

from examples.tech_analysis_workflow import TechAnalysisWorkflow

# Logging beállítása
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def run_workflow(technology):
    """
    Futtatja a technológiai elemzési munkafolyamatot.
    
    Args:
        technology: Az elemzendő technológia neve
    """
    logger.info(f"Technológiai elemzés indítása: {technology}")
    
    try:
        # Munkafolyamat létrehozása
        workflow = TechAnalysisWorkflow()
        
        # Végrehajtás
        result = await workflow.execute(technology=technology)
        
        # Eredmény ellenőrzése
        if result.get("success", False):
            logger.info(f"Elemzés sikeresen elkészült!")
            logger.info(f"Eredmény elérhetősége: {result.get('output_path', 'N/A')}")
            return result
        else:
            logger.error(f"Hiba történt az elemzés során: {result.get('error', 'Ismeretlen hiba')}")
            return None
    
    except Exception as e:
        logger.exception(f"Váratlan hiba történt a munkafolyamat futtatása közben: {str(e)}")
        return None


def select_technology():
    """
    Bekéri az elemzendő technológiát a felhasználótól.
    
    Returns:
        str: A kiválasztott technológia neve
    """
    print("\n" + "=" * 60)
    print("Project-S Technológiai Elemző Rendszer".center(60))
    print("=" * 60 + "\n")
    
    print("Elemzésre elérhető technológia területek:")
    techs = [
        "Kubernetes", 
        "Docker", 
        "Microservices", 
        "GraphQL", 
        "WebAssembly",
        "Quantum Computing",
        "Machine Learning",
        "Blockchain",
        "5G Networks",
        "Edge Computing"
    ]
    
    for i, tech in enumerate(techs, 1):
        print(f"{i}. {tech}")
    
    print("\nVálaszthat előre definiált technológiát, vagy írjon be egy tetszőleges technológia nevet.")
    
    choice = input("\nKérem, válasszon (1-10) vagy írjon be egy technológia nevet: ")
    
    try:
        choice_num = int(choice)
        if 1 <= choice_num <= len(techs):
            return techs[choice_num - 1]
    except ValueError:
        # Ha nem számot adott meg, akkor feltételezzük, hogy egy technológia nevét írta be
        pass
    
    return choice


async def main():
    """Fő függvény a technológiai elemzési munkafolyamat példák futtatásához."""
    try:
        # Technológia kiválasztása
        technology = select_technology()
        
        # Munkafolyamat futtatása
        result = await run_workflow(technology)
        
        if result:
            print("\n" + "=" * 60)
            print(f"Elemzés eredménye: {technology}")
            print("=" * 60)
            print(f"Az eredmény fájl elérhetősége: {result.get('output_path', 'N/A')}")
            print(f"A folyamat állapota: {result.get('final_state', {}).get('current_step', 'N/A')}")
            print("=" * 60 + "\n")
        
    except KeyboardInterrupt:
        print("\nFolyamat megszakítva a felhasználó által.")
    except Exception as e:
        print(f"\nVáratlan hiba történt: {str(e)}")
    
    print("\nA program befejeződött.")


if __name__ == "__main__":
    asyncio.run(main())
