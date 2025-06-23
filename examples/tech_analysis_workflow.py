"""
Technology Analysis Workflow for Project-S
----------------------------------------
Ez a modul egy összetett technológiai elemzési munkafolyamatot implementál,
amely a rendszerszintű műveletek komponenseit használja.

A munkafolyamat:
1. Információgyűjtést végez az interneten (web access)
2. A begyűjtött információkat helyi fájlba menti
3. Feldolgozza és elemzi az adatokat
4. Összefoglaló dokumentumot készít
5. Opcionálisan továbbítja az eredményt (email vagy más rendszer)
"""
import os
import sys
import logging
import asyncio
import json
from typing import Dict, List, Any, TypedDict
from datetime import datetime
from pathlib import Path

# LangGraph importok
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode

# Project-S komponensek importja
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.web_access import web_access
from core.model_selector import model_selector
from core.event_bus import event_bus
from core.error_handler import error_handler
from integrations.system_operations_manager import system_operations_manager
from integrations.system_operations import SystemOperationState
from integrations.file_system_operations import file_system_operations
from integrations.config_operations import config_operations

# Logging beállítása
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Munkakönyvtár beállítása
WORKSPACE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "workspace")
if not os.path.exists(WORKSPACE_DIR):
    os.makedirs(WORKSPACE_DIR)

# Kimeneti fájl útvonalak
RESEARCH_DATA_PATH = os.path.join(WORKSPACE_DIR, "research_data.json")
ANALYSIS_RESULT_PATH = os.path.join(WORKSPACE_DIR, "analysis_result.md")


class TechAnalysisState(TypedDict, total=False):
    """
    A technológiai elemzési munkafolyamat állapotát tároló osztály.
    """
    # Keresési paraméterek
    search_query: str
    technology_name: str
    
    # Gyűjtött adatok
    web_search_results: List[Dict[str, Any]]
    research_data: Dict[str, Any]
    
    # Elemzési eredmények
    advantages: List[str]
    disadvantages: List[str]
    use_cases: List[Dict[str, Any]]
    
    # Rendszerműveletek állapota
    system_state: SystemOperationState
    
    # Folyamatkezelés
    current_step: str
    error_state: bool
    error_message: Optional[str]
    retry_count: int
    
    # Kimeneti adatok
    summary_document_path: str
    summary_content: str
    
    # Metaadatok
    timestamp: str
    execution_id: str


# Lépések definiálása egyszerű függvényekként
async def initialize_state(state: Dict[str, Any]) -> Dict[str, Any]:
    """Inicializálja a munkafolyamat állapotát a kezdeti adatokkal."""
    technology = state.get("technology_name", "Kubernetes")
    
    # Alapértelmezett értékek beállítása
    return {
        "technology_name": technology,
        "search_query": f"{technology} technology advantages disadvantages use cases",
        "web_search_results": [],
        "research_data": {},
        "advantages": [],
        "disadvantages": [],
        "use_cases": [],
        "system_state": {
            "error_state": False,
            "permissions": {
                "file_read": True,
                "file_write": True,
                "process_execute": True,
                "config_write": True
            }
        },
        "current_step": "initialize",
        "error_state": False,
        "retry_count": 0,
        "timestamp": datetime.now().isoformat(),
        "execution_id": f"analysis_{int(datetime.now().timestamp())}"
    }


async def search_web_information(state: Dict[str, Any]) -> Dict[str, Any]:
    """Webes keresés a technológiával kapcsolatos információkért."""
    try:
        query = state.get("search_query")
        technology = state.get("technology_name")
        
        logger.info(f"Webes keresés indítása: {query}")
        
        # Webes keresés végrehajtása
        search_results = await web_access.search(query, max_results=10)
        
        # Az eredmények lementése a fájlrendszerbe
        research_data = {
            "technology": technology,
            "search_query": query,
            "timestamp": datetime.now().isoformat(),
            "search_results": search_results
        }
        
        # Fájl létrehozása
        await file_system_operations.write_file(
            file_path=RESEARCH_DATA_PATH,
            content=json.dumps(research_data, indent=2)
        )
        
        # Állapot frissítése
        return {
            **state,
            "web_search_results": search_results,
            "research_data": research_data,
            "current_step": "web_search_completed"
        }
    
    except Exception as e:
        error_msg = f"Hiba a webes keresés során: {str(e)}"
        logger.error(error_msg)
        return {
            **state,
            "error_state": True,
            "error_message": error_msg,
            "current_step": "web_search_error"
        }


async def analyze_information(state: Dict[str, Any]) -> Dict[str, Any]:
    """A begyűjtött információk elemzése a kognitív modellekkel."""
    try:
        research_data = state.get("research_data", {})
        technology = state.get("technology_name")
        
        # A megfelelő modell kiválasztása
        model = model_selector.get_model_by_task("reasoning")
        
        # Az elemzési prompt létrehozása
        analysis_prompt = f"""
        Elemezd a következő technológiát: {technology}
        
        A rendelkezésre álló információk alapján válaszolj a következő kérdésekre:
        1. Mik a technológia fő előnyei?
        2. Mik a technológia hátrányai vagy korlátai?
        3. Milyen fő használati esetek vannak a technológiára?
        4. Milyen szervezetek vagy iparágak számára lehet különösen előnyös?
        
        Strukturált válaszokat adj, amelyeket könnyű feldolgozni.
        """
        
        # A modell meghívása
        analysis_result = await model.generate(analysis_prompt, params={"temperature": 0.1})
        
        # Az elemzési eredmények feldolgozása (egyszerűsített példa)
        # Valós implementációban itt egy strukturáltabb feldolgozás lenne
        advantages = []
        disadvantages = []
        use_cases = []
        
        # Egyszerűsített elemzés a példa kedvéért
        for line in analysis_result.strip().split("\n"):
            if "előny" in line.lower():
                advantages.append(line.strip())
            elif "hátrány" in line.lower() or "korlát" in line.lower():
                disadvantages.append(line.strip())
            elif "használat" in line.lower() or "eset" in line.lower():
                use_cases.append({"case": line.strip()})
        
        # Állapot frissítése
        return {
            **state,
            "advantages": advantages,
            "disadvantages": disadvantages,
            "use_cases": use_cases,
            "current_step": "analysis_completed"
        }
    
    except Exception as e:
        error_msg = f"Hiba az információ elemzése során: {str(e)}"
        logger.error(error_msg)
        return {
            **state,
            "error_state": True,
            "error_message": error_msg,
            "current_step": "analysis_error"
        }


async def create_summary_document(state: Dict[str, Any]) -> Dict[str, Any]:
    """Összefoglaló dokumentum létrehozása az elemzés eredményeiből."""
    try:
        technology = state.get("technology_name")
        advantages = state.get("advantages", [])
        disadvantages = state.get("disadvantages", [])
        use_cases = state.get("use_cases", [])
        
        # A dokumentum tartalmának létrehozása
        summary_content = f"""# {technology} Technológia Elemzés

## Áttekintés

Ez a dokumentum a {technology} technológia elemzését tartalmazza, beleértve annak előnyeit,
hátrányait és fő használati eseteit.

## Előnyök

{"- Nincs elérhető előny" if not advantages else ""}
{"".join([f"- {adv}\n" for adv in advantages])}

## Hátrányok és Korlátok

{"- Nincs ismert hátrány" if not disadvantages else ""}
{"".join([f"- {dis}\n" for dis in disadvantages])}

## Használati Esetek

{"- Nincs meghatározott használati eset" if not use_cases else ""}
{"".join([f"- {uc.get('case', '')}\n" for uc in use_cases])}

## Következtetések

A {technology} egy {len(advantages) > len(disadvantages) and "előnyös" or "kihívásokkal teli"} technológia, 
amely megfelelő lehet {len(use_cases) > 0 and "a fenti használati esetekhez" or "bizonyos speciális esetekben"}.

---
Generálva: {datetime.now().strftime("%Y-%m-%d %H:%M")}
Project-S Technológiai Elemző Rendszer
"""
        
        # A dokumentum mentése a fájlrendszerbe
        await file_system_operations.write_file(
            file_path=ANALYSIS_RESULT_PATH,
            content=summary_content
        )
        
        # Állapot frissítése
        return {
            **state,
            "summary_document_path": ANALYSIS_RESULT_PATH,
            "summary_content": summary_content,
            "current_step": "document_created"
        }
    
    except Exception as e:
        error_msg = f"Hiba az összefoglaló dokumentum létrehozása során: {str(e)}"
        logger.error(error_msg)
        return {
            **state,
            "error_state": True,
            "error_message": error_msg,
            "current_step": "document_creation_error"
        }


async def error_recovery(state: Dict[str, Any]) -> Dict[str, Any]:
    """Hibakezelés és helyreállítási kísérlet."""
    current_step = state.get("current_step", "")
    retry_count = state.get("retry_count", 0) + 1
    
    logger.warning(f"Helyreállítási kísérlet ({retry_count}/3) a következő lépésnél: {current_step}")
    
    # Maximum 3 próbálkozás
    if retry_count >= 3:
        return {
            **state,
            "error_state": True,
            "error_message": f"Maximális újrapróbálkozási kísérletek elérve: {current_step}",
            "current_step": "max_retries_reached"
        }
    
    # Állapot frissítése és visszatérés az előző lépéshez
    return {
        **state,
        "error_state": False,
        "retry_count": retry_count,
        "current_step": current_step.replace("_error", "").replace("_completed", "")
    }


async def finalize_workflow(state: Dict[str, Any]) -> Dict[str, Any]:
    """A munkafolyamat befejezése és eredmények összesítése."""
    summary_path = state.get("summary_document_path", "")
    
    # Esemény küldése a sikeres befejezésről
    event_bus.emit("workflow.completed", {
        "workflow_type": "tech_analysis",
        "technology": state.get("technology_name"),
        "output_path": summary_path,
        "timestamp": datetime.now().isoformat()
    })
    
    logger.info(f"Munkafolyamat sikeresen befejezve. Eredmény elérhetősége: {summary_path}")
    
    # Állapot frissítése és véglegesítése
    return {
        **state,
        "current_step": "workflow_completed",
        "error_state": False
    }


# Állapotvezérlő függvények
def route_by_step(state: Dict[str, Any]) -> str:
    """Routing függvény a munkafolyamat lépései között."""
    # Hibakezelés: ha hiba lépett fel, irányítás a hibajavító lépéshez
    if state.get("error_state", False):
        return "error_recovery"
    
    # Lépés alapú irányítás
    current_step = state.get("current_step", "")
    
    if current_step == "initialize":
        return "search_web"
    elif current_step == "web_search_completed":
        return "analyze_info"
    elif current_step == "analysis_completed":
        return "create_document"
    elif current_step == "document_created":
        return "finalize"
    elif current_step == "workflow_completed" or current_step == "max_retries_reached":
        return END
    
    # Ha nem ismerjük fel a lépést, alapértelmezetten az inicializáláshoz
    return "initialize"


def should_retry(state: Dict[str, Any]) -> str:
    """Eldönti, hogy újra kell-e próbálni egy hibás lépést."""
    if state.get("retry_count", 0) < 3:
        # A hiba után visszatérünk a megfelelő lépéshez
        current_step = state.get("current_step", "")
        if "web_search" in current_step:
            return "search_web"
        elif "analysis" in current_step:
            return "analyze_info"
        elif "document" in current_step:
            return "create_document"
    
    # Ha túl sokszor próbálkoztunk már, befejezzük a munkafolyamatot
    return "finalize"


class TechAnalysisWorkflow:
    """Technológiai elemzési munkafolyamatot kezelő osztály."""
    
    def __init__(self, workflow_id: str = None):
        """
        Inicializálja a munkafolyamatot.
        
        Args:
            workflow_id: A munkafolyamat egyedi azonosítója (opcionális)
        """
        self.workflow_id = workflow_id or f"tech_analysis_{int(datetime.now().timestamp())}"
        self.graph = self._create_workflow_graph()
        
    def _create_workflow_graph(self) -> StateGraph:
        """
        Létrehozza a munkafolyamat gráfját.
        
        Returns:
            StateGraph: A létrehozott LangGraph munkafolyamat
        """
        # Gráf létrehozása
        graph = StateGraph()
        
        # Csomópontok hozzáadása
        graph.add_node("initialize", initialize_state)
        graph.add_node("search_web", search_web_information)
        graph.add_node("analyze_info", analyze_information)
        graph.add_node("create_document", create_summary_document)
        graph.add_node("error_recovery", error_recovery)
        graph.add_node("finalize", finalize_workflow)
        
        # Rendszerműveletek hozzáadása
        system_tools = system_operations_manager.get_all_tool_nodes()
        for name, tool_node in system_tools.items():
            graph.add_node(f"system_{name}", tool_node)
        
        # Alapvető élek definiálása - lineáris folyamat
        graph.add_edge("initialize", "search_web")
        graph.add_edge("search_web", "analyze_info")
        graph.add_edge("analyze_info", "create_document")
        graph.add_edge("create_document", "finalize")
        
        # Feltételes élek a hibakezeléshez és állapotkezeléshez
        graph.add_conditional_edges("initialize", route_by_step)
        graph.add_conditional_edges("search_web", route_by_step)
        graph.add_conditional_edges("analyze_info", route_by_step)
        graph.add_conditional_edges("create_document", route_by_step)
        graph.add_conditional_edges("error_recovery", should_retry)
        graph.add_conditional_edges("finalize", route_by_step)
        
        # Belépési pont beállítása
        graph.set_entry_point("initialize")
        
        return graph
        
    async def execute(self, technology: str = "Kubernetes") -> Dict[str, Any]:
        """
        Végrehajtja a technológiai elemzési munkafolyamatot.
        
        Args:
            technology: Az elemzendő technológia neve
            
        Returns:
            Dict: A végrehajtás eredménye és a végállapot
        """
        # Kezdeti állapot létrehozása
        initial_state = {
            "technology_name": technology,
            "workflow_id": self.workflow_id
        }
        
        logger.info(f"Munkafolyamat indítása: {self.workflow_id} - Technológia: {technology}")
        
        try:
            # Munkafolyamat végrehajtása
            # Valós környezetben itt integrálnánk a LangGraph executor hívást
            result = await self._execute_graph(initial_state)
            
            return {
                "success": not result.get("error_state", False),
                "output_path": result.get("summary_document_path", ""),
                "technology": technology,
                "workflow_id": self.workflow_id,
                "final_state": result
            }
            
        except Exception as e:
            error_msg = f"Hiba a munkafolyamat végrehajtása során: {str(e)}"
            logger.error(error_msg)
            error_handler.handle_error(
                error_type="WorkflowExecutionError",
                source=self.__class__.__name__,
                details={"workflow_id": self.workflow_id, "error": str(e)}
            )
            
            return {
                "success": False,
                "error": error_msg,
                "workflow_id": self.workflow_id
            }
    
    async def _execute_graph(self, initial_state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Végrehajtja a LangGraph munkafolyamatot (szimulált implementáció).
        Valós környezetben itt használnánk a LangGraph executor API-t.
        
        Args:
            initial_state: A kezdeti állapot
            
        Returns:
            Dict: A végső állapot
        """
        # MEGJEGYZÉS: Ez egy szimulált végrehajtás a példa kedvéért
        # Valós implementációban itt a LangGraph executor-t használnánk
        
        # Inicializálás
        state = await initialize_state(initial_state)
        
        # Web keresés
        state = await search_web_information(state)
        
        # Ha hiba történt, próbáljuk helyreállítani
        if state.get("error_state", False):
            state = await error_recovery(state)
            if state.get("error_state", False):
                return state
            state = await search_web_information(state)
        
        # Információ elemzés
        state = await analyze_information(state)
        
        # Ha hiba történt, próbáljuk helyreállítani
        if state.get("error_state", False):
            state = await error_recovery(state)
            if state.get("error_state", False):
                return state
            state = await analyze_information(state)
        
        # Dokumentum létrehozása
        state = await create_summary_document(state)
        
        # Ha hiba történt, próbáljuk helyreállítani
        if state.get("error_state", False):
            state = await error_recovery(state)
            if state.get("error_state", False):
                return state
            state = await create_summary_document(state)
        
        # Befejezés
        state = await finalize_workflow(state)
        
        return state


# Példa a munkafolyamat használatára
async def run_example():
    """Futtat egy példa technológiai elemzési munkafolyamatot."""
    # Konfiguráció betöltése
    config = await config_operations.load_config(
        os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                     "config", "multi_model_config.json")
    )
    
    if not config.get("success", False):
        logger.error("Nem sikerült betölteni a konfigurációt")
        return
    
    # Munkafolyamat létrehozása
    workflow = TechAnalysisWorkflow()
    
    # Végrehajtás
    technology = "Kubernetes"
    result = await workflow.execute(technology=technology)
    
    # Eredmény megjelenítése
    if result.get("success", False):
        logger.info(f"Munkafolyamat sikeresen befejeződött!")
        logger.info(f"Eredmény elérhetősége: {result['output_path']}")
        
        # Az eredmény megjelenítése a konzolon
        if os.path.exists(result['output_path']):
            summary_content = await file_system_operations.read_file(result['output_path'])
            if summary_content.get("success", False):
                print("\n" + "-" * 80)
                print(summary_content["content"])
                print("-" * 80 + "\n")
    else:
        logger.error(f"Munkafolyamat végrehajtása sikertelen: {result.get('error', 'Ismeretlen hiba')}")


# Fő függvény
if __name__ == "__main__":
    asyncio.run(run_example())
