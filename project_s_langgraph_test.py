"""
Project-S LangGraph integrációs teszt
------------------------------------
Ez a teszt kifejezetten a Project-S LangGraph integrációját vizsgálja.
Minimális függőségeket használ, hogy elkerülje a körkörös importálási problémákat.
"""
import os
import sys
import uuid
import asyncio
import logging
import traceback
from pathlib import Path
from typing import Dict, Any, List, TypedDict, Optional

# Naplózás beállítása
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    handlers=[
        logging.FileHandler("project_s_langgraph_test.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("ps_langgraph_test")

# Ellenőrizzük, hogy a LangGraph elérhető-e
try:
    from langgraph.graph import StateGraph
    LANGGRAPH_AVAILABLE = True
    logger.info("LangGraph könyvtár elérhető")
except ImportError:
    LANGGRAPH_AVAILABLE = False
    logger.error("LangGraph könyvtár NEM elérhető - telepítse a következő paranccsal: pip install langgraph")
    sys.exit(1)

# Project-S elérési út hozzáadása
sys.path.insert(0, str(Path(__file__).parent.resolve()))

# GraphState osztály másolata az eredeti fájlból
class GraphState(TypedDict):
    """
    Enhanced type definition for the state managed by LangGraph,
    harmonized with Project-S state model
    """
    # Core LangGraph fields
    messages: List[Dict[str, Any]]  # Chat messages in the conversation
    context: Dict[str, Any]  # Workflow context data
    command_history: List[Dict[str, Any]]  # History of executed commands
    status: str  # Current workflow status (created, running, completed, error, cancelled)
    current_task: Optional[Dict[str, Any]]  # Currently executing task
    error_info: Optional[Dict[str, Any]]  # Information about errors
    retry_count: int  # Number of command retries
    branch: Optional[str]  # Current execution branch if using branched workflows
    
    # Project-S integration fields
    conversation_id: Optional[str]  # Link to Project-S conversation
    session_data: Optional[Dict[str, Any]]  # Session-specific data
    memory_references: Optional[List[str]]  # References to Project-S memory items
    system_state: Optional[Dict[str, Any]]  # Global system state from Project-S
    persistence_metadata: Optional[Dict[str, Any]]  # Metadata for state persistence

# Egyszerűsített LangGraphIntegrator implementáció teszteléshez
class SimpleLangGraphIntegrator:
    """
    Egyszerűsített LangGraph integrátor a Project-S rendszerhez
    """
    
    def __init__(self):
        """Initialize the LangGraph integrator"""
        self.active_graphs = {}
        self.graph_states = {}
        self.max_retries = 3
        logger.info("SimpleLangGraphIntegrator inicializálva")
    
    def create_workflow(self, name: str, steps: List[Dict[str, Any]], 
                      context: Optional[Dict[str, Any]] = None,
                      branches: Optional[Dict[str, List[Dict[str, Any]]]] = None) -> str:
        """
        Új munkafolyamat létrehozása
        """
        # Egyedi azonosító a gráfhoz
        graph_id = f"graph_{uuid.uuid4().hex[:8]}"
        
        # Új StateGraph létrehozása
        graph = StateGraph(GraphState)
        
        # Gráf állapot inicializálása
        initial_state: GraphState = {
            "messages": [],
            "context": context or {},
            "command_history": [],
            "status": "created",
            "current_task": None,
            "error_info": None,
            "retry_count": 0,
            "branch": None
        }
        
        # Munkafolyamat metaadatainak hozzáadása a kontextushoz
        initial_state["context"]["workflow_steps"] = steps
        initial_state["context"]["workflow_name"] = name
        initial_state["context"]["graph_id"] = graph_id
        initial_state["context"]["created_at"] = 0  # egyszerűsített implementáció
        
        # Branch-ek hozzáadása, ha vannak
        if branches:
            initial_state["context"]["branches"] = branches
        
        # Gráf és állapot tárolása
        self.active_graphs[graph_id] = graph
        self.graph_states[graph_id] = initial_state
        
        logger.info(f"Munkafolyamat gráf létrehozva: {graph_id} ({len(steps)} lépéssel)")
        
        return graph_id
    
    def get_workflow_state(self, graph_id: str) -> Optional[GraphState]:
        """Lekérdezi egy munkafolyamat állapotát"""
        return self.graph_states.get(graph_id)
    
    def update_workflow_state(self, graph_id: str, updates: Dict[str, Any]) -> bool:
        """Frissíti egy munkafolyamat állapotát"""
        if graph_id not in self.graph_states:
            return False
        
        for key, value in updates.items():
            if key in self.graph_states[graph_id]:
                self.graph_states[graph_id][key] = value
        
        return True

async def test_langgraph_integrator():
    """
    Teszteli a LangGraph integrátor alapvető működését
    """
    logger.info("SimpleLangGraphIntegrator tesztelése...")
    
    # Integrátor létrehozása
    integrator = SimpleLangGraphIntegrator()
    
    # Teszt munkafolyamat létrehozása
    steps = [
        {"type": "command", "name": "Step 1", "command": "echo 'Hello World'"},
        {"type": "command", "name": "Step 2", "command": "echo 'Step 2'"},
        {"type": "command", "name": "Step 3", "command": "echo 'Final Step'"}
    ]
    
    context = {
        "description": "Test workflow",
        "created_by": "test_script"
    }
    
    branches = {
        "error_path": [
            {"type": "command", "name": "Error Handler", "command": "echo 'Error occurred'"}
        ]
    }
    
    # Munkafolyamat létrehozása
    graph_id = integrator.create_workflow(
        name="Test Workflow",
        steps=steps,
        context=context,
        branches=branches
    )
    
    # Ellenőrizzük, hogy megfelelően létrejött-e
    state = integrator.get_workflow_state(graph_id)
    
    # Teszteredmények összegyűjtése
    results = {
        "graph_created": graph_id is not None,
        "state_exists": state is not None,
        "correct_step_count": len(state["context"]["workflow_steps"]) == 3 if state else False,
        "has_branches": "branches" in state["context"] if state else False
    }
    
    # Állapot frissítés tesztelése
    update_success = integrator.update_workflow_state(graph_id, {
        "status": "running",
        "current_task": steps[0]
    })
    
    results["update_success"] = update_success
    
    # Frissítés ellenőrzése
    updated_state = integrator.get_workflow_state(graph_id)
    results["status_updated"] = updated_state["status"] == "running" if updated_state else False
    
    # Eredmények összesítése
    all_passed = all(results.values())
    
    # Eredmények kiírása
    logger.info("Teszt eredmények:")
    for test_name, result in results.items():
        status = "✅ SIKERES" if result else "❌ SIKERTELEN"
        logger.info(f"{status}: {test_name}")
    
    logger.info(f"Végeredmény: {'✅ MINDEN TESZT SIKERES' if all_passed else '❌ VANNAK SIKERTELEN TESZTEK'}")
    
    # Gráf állapot kiírása
    logger.info("Végső gráf állapot:")
    logger.info(f"ID: {graph_id}")
    logger.info(f"Status: {updated_state['status']}")
    logger.info(f"Steps: {len(updated_state['context']['workflow_steps'])}")
    logger.info(f"Current task: {updated_state['current_task']['name'] if updated_state['current_task'] else 'None'}")
    
    return all_passed

async def test_langgraph_integration():
    """Teszteli a tényleges Project-S LangGraph integrációt"""
    logger.info("Project-S LangGraph integráció tesztelése...")
    
    # Megpróbáljuk importálni az eredeti LangGraphIntegrator osztályt
    try:
        from integrations.langgraph_integration import LangGraphIntegrator
        
        # Létrehozzuk az integrátort
        integrator = LangGraphIntegrator()
        
        logger.info("LangGraphIntegrator sikeresen betöltve")
        logger.info(f"Active graphs: {len(integrator.active_graphs)}")
        
        return True
    except Exception as e:
        logger.error(f"Hiba a LangGraphIntegrator betöltésekor: {e}")
        traceback.print_exc()
        return False

async def main():
    """Fő teszt funkció"""
    logger.info("Project-S LangGraph integrációs teszt indítása...")
    
    results = {}
    
    # Alapvető integrátor működés tesztelése
    try:
        results["basic_integrator"] = await test_langgraph_integrator()
    except Exception as e:
        logger.error(f"Hiba az alap integrátor tesztelése során: {e}")
        results["basic_integrator"] = False
    
    # Project-S integráció tesztelése ha lehetséges
    try:
        results["project_s_integration"] = await test_langgraph_integration()
    except Exception as e:
        logger.error(f"Hiba a Project-S integráció tesztelése során: {e}")
        results["project_s_integration"] = False
    
    # Eredmények összesítése
    all_passed = all(results.values())
    
    # Végeredmény kiírása
    print("\n=== Teszteredmények összefoglalása ===")
    for test_name, result in results.items():
        status = "PASS" if result else "FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\nÖsszesített eredmény: {'SIKERES' if all_passed else 'SIKERTELEN'}")
    
    return all_passed

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
