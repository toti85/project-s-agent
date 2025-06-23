"""
Project-S Fejlett LangGraph Többmodelles Workflow
----------------------------------------------
Ez a fájl a Project-S rendszer LangGraph integrációját valósítja meg, 
amely támogatja a többmodelles működést és komplex feladatokat.
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional, Union, Literal
from enum import Enum
from datetime import datetime

from integrations.simplified_model_manager import model_manager
from integrations.persistent_state_manager import persistent_state_manager

logger = logging.getLogger(__name__)

try:
    from langgraph.graph import StateGraph, END
    LANGGRAPH_AVAILABLE = True
except ImportError:
    logger.warning("LangGraph nem elérhető. Telepítsd: pip install langgraph")
    LANGGRAPH_AVAILABLE = False

# Állapot típus
State = Dict[str, Any]

# Feladat típusok
class TaskType(str, Enum):
    PLANNING = "tervezés"
    CODING = "kódolás"
    DOCUMENTATION = "dokumentáció"
    DATA_ANALYSIS = "adatelemzés"
    CREATIVE = "kreatív_írás"
    TRANSLATION = "fordítás"
    SUMMARY = "összefoglalás"
    QUICK_RESPONSE = "gyors_válasz"
    UNKNOWN = "ismeretlen"

class AdvancedLangGraphWorkflow:
    """
    Fejlett LangGraph munkafolyamat-kezelő, többmodelles és 
    többlépéses feladatok végrehajtásához.
    """
    
    def __init__(self):
        """Inicializálja a fejlett LangGraph munkafolyamat-kezelőt."""
        self.graph = None
        self.multi_step_graph = None
        self.multi_model_graph = None
        
        # Hozzáférés a perzisztens állapotkezelőhöz
        self.state_manager = persistent_state_manager
        
        if LANGGRAPH_AVAILABLE:
            self._setup_basic_graph()
            self._setup_multi_step_graph()
            self._setup_multi_model_graph()
            logger.info("Fejlett LangGraph workflow inicializálva")
        else:
            logger.warning("LangGraph nem érhető el, workflow inicializálás sikertelen")
    
    def _setup_basic_graph(self):
        """
        Beállítja az alapvető állapotgráfot egyszerű feladatokhoz.
        """
        # Állapotgráf létrehozása
        builder = StateGraph(State)
        
        # Csomópontok definíciói
        def parse_input(state: State) -> State:
            """Bemenet elemzése és feladat azonosítása."""
            input_text = state.get("input", "")
            
            return {
                **state, 
                "parsed_input": {
                    "original": input_text,
                    "tokens": input_text.split(),
                    "detected_type": model_manager.determine_task_type(input_text)
                }
            }
            
        def process_with_model(state: State) -> State:
            """A megfelelő modell kiválasztása és a feladat feldolgozása."""
            input_text = state.get("input", "")
            detected_type = state.get("parsed_input", {}).get("detected_type", "gyors_válasz")
            
            # Itt csak előkészítjük a modell kiválasztást - az aszinkron hívást később végezzük
            return {
                **state, 
                "model_selection": {
                    "suggested_model": model_manager.ai_client.suggest_model_for_task(detected_type),
                    "task_type": detected_type,
                    "ready_for_execution": True
                }
            }
            
        def prepare_response(state: State) -> State:
            """Válasz előkészítése és formázása."""
            # Ez a rész csak a válasz előkészítést végzi, a tényleges generálás később történik
            input_text = state.get("input", "")
            model_data = state.get("model_selection", {})
            
            return {
                **state,
                "prepared_response": {
                    "input": input_text,
                    "selected_model": model_data.get("suggested_model", "gpt-3.5-turbo"),
                    "task_type": model_data.get("task_type", "gyors_válasz"),
                    "ready": True
                }
            }
        
        # Csomópontok hozzáadása
        builder.add_node("parse_input", parse_input)
        builder.add_node("process_with_model", process_with_model)
        builder.add_node("prepare_response", prepare_response)
        
        # Élek hozzáadása
        builder.add_edge("parse_input", "process_with_model")
        builder.add_edge("process_with_model", "prepare_response")
        builder.add_edge("prepare_response", END)
        
        # Kezdő csomópont beállítása
        builder.set_entry_point("parse_input")
        
        # Gráf kompilálása
        self.graph = builder.compile()
        logger.debug("Alap LangGraph workflow létrehozva")
    
    def _setup_multi_step_graph(self):
        """
        Beállít egy összetett, többlépéses workflow-t komplex feladatokhoz.
        """
        # Állapotgráf létrehozása
        builder = StateGraph(State)
        
        # Csomópontok definíciói
        def analyze_task(state: State) -> State:
            """A feladat elemzése és felbontása."""
            input_text = state.get("input", "")
            
            # Itt azonosítjuk a feladat komplexitását és típusát
            task_complexity = "simple"  # Egyszerű alapértelmezés
            subtasks = []
            
            # Egyszerű heurisztikák a komplexitás becslésére
            if len(input_text.split()) > 50:
                task_complexity = "complex"
                subtasks = ["planning", "execution", "verification"]
            elif "," in input_text or "és " in input_text or "majd " in input_text:
                # Ha vesszővel vagy "és"/"majd" szóval elválasztott részek vannak, feltételezzük, hogy összetett
                task_complexity = "medium"
                subtasks = ["analysis", "execution"]
                
            return {
                **state, 
                "task_analysis": {
                    "complexity": task_complexity,
                    "subtasks": subtasks,
                    "current_step": 0
                }
            }
        
        def route_task(state: State) -> str:
            """Útvonalválasztó funkció a feladat komplexitásától függően."""
            complexity = state.get("task_analysis", {}).get("complexity", "simple")
            
            if complexity == "complex":
                return "complex_workflow"
            elif complexity == "medium":
                return "medium_workflow"
            else:
                return "simple_workflow"
            
        def simple_workflow(state: State) -> State:
            """Egyszerű feladat végrehajtása egy lépésben."""
            return {**state, "workflow": "simple", "ready": True}
            
        def medium_workflow_step1(state: State) -> State:
            """Közepes bonyolultságú feladat - első lépés."""
            return {**state, "workflow": "medium", "step": 1}
            
        def medium_workflow_step2(state: State) -> State:
            """Közepes bonyolultságú feladat - második lépés."""
            return {**state, "workflow": "medium", "step": 2, "ready": True}
            
        def complex_workflow_step1(state: State) -> State:
            """Komplex feladat - első lépés (tervezés)."""
            return {**state, "workflow": "complex", "step": 1}
            
        def complex_workflow_step2(state: State) -> State:
            """Komplex feladat - második lépés (végrehajtás)."""
            return {**state, "workflow": "complex", "step": 2}
            
        def complex_workflow_step3(state: State) -> State:
            """Komplex feladat - harmadik lépés (ellenőrzés)."""
            return {**state, "workflow": "complex", "step": 3, "ready": True}
            
        def prepare_final_response(state: State) -> State:
            """Végső válasz előkészítése."""
            workflow = state.get("workflow", "simple")
            
            response_template = {
                "simple": "Egyszerű feladat végrehajtva.",
                "medium": "Közepes bonyolultságú feladat végrehajtva 2 lépésben.",
                "complex": "Komplex feladat végrehajtva 3 lépésben."
            }
            
            return {**state, "final_response": response_template.get(workflow, "Feladat végrehajtva."), "complete": True}
        
        # Csomópontok hozzáadása
        builder.add_node("analyze_task", analyze_task)
        builder.add_node("simple_workflow", simple_workflow)
        builder.add_node("medium_workflow_step1", medium_workflow_step1)
        builder.add_node("medium_workflow_step2", medium_workflow_step2)
        builder.add_node("complex_workflow_step1", complex_workflow_step1)
        builder.add_node("complex_workflow_step2", complex_workflow_step2)
        builder.add_node("complex_workflow_step3", complex_workflow_step3)
        builder.add_node("prepare_final_response", prepare_final_response)
        
        # Útvonalválasztó csomópont hozzáadása
        builder.add_conditional_edges(
            "analyze_task",
            route_task,
            {
                "simple_workflow": "simple_workflow",
                "medium_workflow": "medium_workflow_step1",
                "complex_workflow": "complex_workflow_step1"
            }
        )
        
        # További élek
        builder.add_edge("simple_workflow", "prepare_final_response")
        builder.add_edge("medium_workflow_step1", "medium_workflow_step2")
        builder.add_edge("medium_workflow_step2", "prepare_final_response")
        builder.add_edge("complex_workflow_step1", "complex_workflow_step2")
        builder.add_edge("complex_workflow_step2", "complex_workflow_step3")
        builder.add_edge("complex_workflow_step3", "prepare_final_response")
        builder.add_edge("prepare_final_response", END)
        
        # Kezdő csomópont beállítása
        builder.set_entry_point("analyze_task")
        
        # Gráf kompilálása
        self.multi_step_graph = builder.compile()
        logger.debug("Többlépéses LangGraph workflow létrehozva")
    
    def _setup_multi_model_graph(self):
        """
        Beállít egy többmodelles workflow-t, amely képes
        különböző AI modelleket használni a feladat különböző 
        részeinek végrehajtására.
        """
        # Állapotgráf létrehozása
        builder = StateGraph(State)
        
        # Csomópontok definíciói
        def analyze_request(state: State) -> State:
            """Elemzi a kérést, és azonosítja a szükséges modelleket."""
            input_text = state.get("input", "")
            
            # Alapértelmezett modellek inicializálása
            planning_model = "gpt-4"  # Tervezési fázishoz
            execution_model = "claude-3-sonnet"  # Végrehajtáshoz
            verification_model = "gpt-3.5-turbo"  # Ellenőrzéshez
            
            # Egyszerű modell azonosítás a bemeneti szöveg alapján
            if "használj" in input_text.lower() and "modell" in input_text.lower():
                # Ha explicit modell meghatározás van a szövegben
                if "gpt-4" in input_text.lower():
                    planning_model = "gpt-4"
                if "claude" in input_text.lower():
                    execution_model = "claude-3-opus" if "opus" in input_text.lower() else "claude-3-sonnet"
                if "helyi" in input_text.lower() or "ollama" in input_text.lower():
                    verification_model = "llama3"
            
            return {
                **state, 
                "multi_model": {
                    "planning_model": planning_model,
                    "execution_model": execution_model,
                    "verification_model": verification_model,
                    "current_phase": "planning"
                }
            }
            
        def route_phase(state: State) -> str:
            """Útvonalválasztó a jelenlegi fázis alapján."""
            current_phase = state.get("multi_model", {}).get("current_phase", "planning")
            
            if current_phase == "planning":
                return "planning_phase"
            elif current_phase == "execution":
                return "execution_phase"
            elif current_phase == "verification":
                return "verification_phase"
            else:
                return "finalization"
                
        def planning_phase(state: State) -> State:
            """Tervezési fázis a megfelelő modellel."""
            planning_model = state.get("multi_model", {}).get("planning_model", "gpt-4")
            
            # Itt csak előkészítjük a tervezési fázist - a tényleges végrehajtás később történik
            return {
                **state, 
                "planning_result": {
                    "model": planning_model,
                    "status": "prepared",
                    "task": "Feladat tervezése"
                },
                "multi_model": {
                    **state.get("multi_model", {}),
                    "current_phase": "execution"
                }
            }
            
        def execution_phase(state: State) -> State:
            """Végrehajtási fázis a megfelelő modellel."""
            execution_model = state.get("multi_model", {}).get("execution_model", "claude-3-sonnet")
            
            # Itt csak előkészítjük a végrehajtási fázist
            return {
                **state, 
                "execution_result": {
                    "model": execution_model,
                    "status": "prepared",
                    "task": "Feladat végrehajtása",
                    "planning_input": state.get("planning_result", {})
                },
                "multi_model": {
                    **state.get("multi_model", {}),
                    "current_phase": "verification"
                }
            }
            
        def verification_phase(state: State) -> State:
            """Ellenőrzési fázis a megfelelő modellel."""
            verification_model = state.get("multi_model", {}).get("verification_model", "gpt-3.5-turbo")
            
            # Itt csak előkészítjük az ellenőrzési fázist
            return {
                **state, 
                "verification_result": {
                    "model": verification_model,
                    "status": "prepared",
                    "task": "Eredmény ellenőrzése",
                    "execution_input": state.get("execution_result", {})
                },
                "multi_model": {
                    **state.get("multi_model", {}),
                    "current_phase": "finalization"
                }
            }
            
        def finalization(state: State) -> State:
            """Eredmények összesítése."""
            # Összegezzük a különböző fázisok eredményeit
            return {
                **state,
                "final_result": {
                    "planning": state.get("planning_result", {}),
                    "execution": state.get("execution_result", {}),
                    "verification": state.get("verification_result", {}),
                    "status": "complete"
                }
            }
            
        # Csomópontok hozzáadása
        builder.add_node("analyze_request", analyze_request)
        builder.add_node("planning_phase", planning_phase)
        builder.add_node("execution_phase", execution_phase)
        builder.add_node("verification_phase", verification_phase)
        builder.add_node("finalization", finalization)
        
        # Útvonalválasztó és élek
        builder.add_conditional_edges(
            "analyze_request",
            route_phase,
            {
                "planning_phase": "planning_phase",
                "execution_phase": "execution_phase",
                "verification_phase": "verification_phase",
                "finalization": "finalization"
            }
        )
        
        builder.add_conditional_edges(
            "planning_phase",
            route_phase,
            {
                "planning_phase": "planning_phase",
                "execution_phase": "execution_phase",
                "verification_phase": "verification_phase",
                "finalization": "finalization"
            }
        )
        
        builder.add_conditional_edges(
            "execution_phase",
            route_phase,
            {
                "planning_phase": "planning_phase",
                "execution_phase": "execution_phase",
                "verification_phase": "verification_phase",
                "finalization": "finalization"
            }
        )
        
        builder.add_conditional_edges(
            "verification_phase",
            route_phase,
            {
                "planning_phase": "planning_phase",
                "execution_phase": "execution_phase",
                "verification_phase": "verification_phase",
                "finalization": "finalization"
            }
        )
        
        builder.add_edge("finalization", END)
        
        # Kezdő csomópont beállítása
        builder.set_entry_point("analyze_request")
        
        # Gráf kompilálása
        self.multi_model_graph = builder.compile()
        logger.debug("Többmodelles LangGraph workflow létrehozva")
    
    async def process_with_basic_graph(self, command: str) -> Dict[str, Any]:
        """
        Feldolgozza a parancsot az alapvető LangGraph workflow segítségével.
        
        Args:
            command: A feldolgozandó parancs
            
        Returns:
            Dict: A feldolgozás eredménye
        """
        if not LANGGRAPH_AVAILABLE or not self.graph:
            return {"error": "LangGraph nem elérhető"}
        
        try:
            # Kezdeti állapot létrehozása
            initial_state = {"input": command}
            
            # Futtatás az állapotgráfon
            logger.info(f"Parancs feldolgozása alapvető LangGraph workflow-val: '{command}'")
            final_state = self.graph.invoke(initial_state)
            
            # Most, hogy megkaptuk a javasolt modellt, valóban végrehajtjuk a feladatot
            task_type = final_state.get("parsed_input", {}).get("detected_type", "gyors_válasz")
            selected_model = final_state.get("prepared_response", {}).get("selected_model", "gpt-3.5-turbo")
            
            # A tényleges AI végrehajtás
            result = await model_manager.execute_task_with_model(
                query=command,
                system_message="Feldolgozd a felhasználó kérését a megadott modellel.",
                model=selected_model,
                task_type=task_type
            )
            
            # Összesítjük az eredményeket
            final_state["result"] = result
            
            return final_state
            
        except Exception as e:
            logger.error(f"Hiba a LangGraph workflow során: {e}")
            return {"error": str(e)}
    
    async def process_with_multi_step_graph(self, command: str) -> Dict[str, Any]:
        """
        Feldolgozza a parancsot a többlépéses LangGraph workflow segítségével.
        
        Args:
            command: A feldolgozandó parancs
            
        Returns:
            Dict: A feldolgozás eredménye
        """
        if not LANGGRAPH_AVAILABLE or not self.multi_step_graph:
            return {"error": "LangGraph többlépéses workflow nem elérhető"}
        
        try:
            # Kezdeti állapot létrehozása
            initial_state = {"input": command}
            
            # Futtatás az állapotgráfon
            logger.info(f"Parancs feldolgozása többlépéses LangGraph workflow-val: '{command}'")
            final_state = self.multi_step_graph.invoke(initial_state)
            
            workflow_type = final_state.get("workflow", "simple")
            final_response = final_state.get("final_response", "")
              # Csak az egyszerű végrehajtáshoz hívjuk meg az AI-t
            # Más workflow típusokhoz több lépésben, egyedi kezeléssel hívnánk meg
            if workflow_type == "simple":
                result = await model_manager.execute_task_with_tools(
                    query=command,
                    system_message="Egyszerű feladat végrehajtása. Használj megfelelő eszközöket a feladat teljesítéséhez."
                )
                
                final_state["ai_result"] = result
                
            return final_state
            
        except Exception as e:
            logger.error(f"Hiba a többlépéses LangGraph workflow során: {e}")
            return {"error": str(e)}
    
    async def process_with_multi_model_graph(self, command: str) -> Dict[str, Any]:
        """
        Feldolgozza a parancsot a többmodelles LangGraph workflow segítségével.
        
        Args:
            command: A feldolgozandó parancs
            
        Returns:
            Dict: A feldolgozás eredménye
        """
        if not LANGGRAPH_AVAILABLE or not self.multi_model_graph:
            return {"error": "LangGraph többmodelles workflow nem elérhető"}
        
        try:
            # Kezdeti állapot létrehozása
            initial_state = {"input": command}
            
            # Futtatás az állapotgráfon
            logger.info(f"Parancs feldolgozása többmodelles LangGraph workflow-val: '{command}'")
            final_state = self.multi_model_graph.invoke(initial_state)
            
            # Tényleges AI végrehajtás az egyes fázisokhoz            # 1. Tervezés
            planning_model = final_state.get("planning_result", {}).get("model", "gpt-4")
            planning_result = await model_manager.execute_task_with_tools(
                query=f"Tervezési fázis a következő feladathoz: {command}",
                system_message="Most a tervezési fázisban vagy. Készíts részletes tervet a feladat végrehajtásához. Ha szükséges, használj eszközöket a terv megvalósításához.",
                model=planning_model,
                task_type="tervezés"
            )
            
            # 2. Végrehajtás
            execution_model = final_state.get("execution_result", {}).get("model", "claude-3-sonnet")
            planning_content = planning_result.get("content", "")
            execution_result = await model_manager.execute_task_with_tools(
                query=f"Végrehajtási fázis. Terv: {planning_content}. Feladat: {command}",
                system_message="Most a végrehajtási fázisban vagy. Hajtsd végre a tervet a feladat megoldásához. Használj megfelelő eszközöket (fájlírás, parancsok futtatása, stb.) a feladat teljesítéséhez.",
                model=execution_model,
                task_type="kódolás"
            )
            
            # 3. Ellenőrzés
            verification_model = final_state.get("verification_result", {}).get("model", "gpt-3.5-turbo")
            execution_content = execution_result.get("content", "")
            verification_result = await model_manager.execute_task_with_tools(
                query=f"Ellenőrzési fázis. Végrehajtás eredménye: {execution_content}. Eredeti feladat: {command}",
                system_message="Most az ellenőrzési fázisban vagy. Értékeld a végrehajtás eredményét és ellenőrizd a létrehozott fájlokat vagy rendszerállapotot eszközök segítségével.",
                model=verification_model,
                task_type="összefoglalás"
            )
            
            # Eredmények összesítése
            final_state["planning_ai_result"] = planning_result
            final_state["execution_ai_result"] = execution_result
            final_state["verification_ai_result"] = verification_result
            
            # Az egyes fázisok eredményeinek összesítése
            final_state["combined_result"] = {
                "planning": planning_result.get("content", ""),
                "execution": execution_result.get("content", ""),
                "verification": verification_result.get("content", ""),
                "summary": f"A feladat több modell segítségével lett végrehajtva:\n"
                          f"1. Tervezés: {planning_model}\n"
                          f"2. Végrehajtás: {execution_model}\n"
                          f"3. Ellenőrzés: {verification_model}"
            }
            
            return final_state
            
        except Exception as e:
            logger.error(f"Hiba a többmodelles LangGraph workflow során: {e}")
            return {"error": str(e)}
    
    async def process_with_multi_model_graph_with_persistence(self, 
                                              command: str, 
                                              session_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Feldolgozza a parancsot a többmodelles gráffal, perzisztens állapotmegőrzéssel.
        
        Args:
            command: A feldolgozandó parancs
            session_id: Opcionális munkamenet azonosító. Ha nincs megadva, új jön létre.
            
        Returns:
            Dict[str, Any]: A feldolgozás eredménye
        """
        if not LANGGRAPH_AVAILABLE:
            return {"error": "LangGraph nem elérhető"}
            
        # Ellenőrizzük vagy létrehozzuk a munkamenetet
        if not session_id:
            session_id = await self.state_manager.create_session({
                "workflow_type": "multi_model"
            })
            
        # Konfiguráció ID a LangGraph-hoz
        config_id = "multi_model_workflow"
        
        # Ellenőrizzük, van-e korábban mentett állapot ehhez a munkamenethez
        saved_state = await self.state_manager.load_langgraph_checkpoint(session_id, config_id)
        
        initial_state = {}
        if saved_state:
            # Ha van mentett állapot, azt használjuk
            logger.info(f"Korábban mentett állapot betöltve a munkamenetből: {session_id}")
            initial_state = saved_state
            
            # Hozzáadjuk az új bemenetet a meglévő állapothoz
            initial_state["input"] = command
            initial_state["last_command_timestamp"] = datetime.now().isoformat()
        else:
            # Különben új kezdeti állapotot hozunk létre
            initial_state = {"input": command, "multi_model": {}}
          # Futtatjuk a gráfot a kezdeti állapottal
        events = []
        final_state = None
        
        try:
            # Use astream instead of stream for proper async iteration
            async for event in self.multi_model_graph.astream(initial_state):
                events.append(event)
                final_state = event  # The event contains the state
        except AttributeError:
            # Fallback: if astream is not available, use invoke
            try:
                final_state = await self.multi_model_graph.ainvoke(initial_state)
                events.append(final_state)
            except AttributeError:
                # Final fallback: synchronous invoke
                final_state = self.multi_model_graph.invoke(initial_state)
                events.append(final_state)
            
        if not final_state:
            return {"error": "A workflow nem adott vissza állapotot"}
        
        # Elmenti az állapotot későbbi folytatáshoz
        await self.state_manager.save_langgraph_checkpoint(session_id, config_id, final_state)
          # Feldolgozás befejezése - hasonló a process_with_multi_model_graph-hoz
        planning_model = final_state.get("planning_result", {}).get("model", "gpt-4")
        planning_result = await model_manager.execute_task_with_tools(
            query=f"Tervezési fázis a következő feladathoz: {command}",
            system_message="Most a tervezési fázisban vagy. Készíts részletes tervet a feladat végrehajtásához. Ha szükséges, használj eszközöket a terv megvalósításához.",
            model=planning_model,
            task_type="tervezés"
        )
        
        # 2. Végrehajtás
        execution_model = final_state.get("execution_result", {}).get("model", "claude-3-sonnet")
        planning_content = planning_result.get("content", "")
        execution_result = await model_manager.execute_task_with_tools(
            query=f"Végrehajtási fázis. Terv: {planning_content}. Feladat: {command}",
            system_message="Most a végrehajtási fázisban vagy. Hajtsd végre a tervet a feladat megoldásához. Használj megfelelő eszközöket (fájlírás, parancsok futtatása, stb.) a feladat teljesítéséhez.",
            model=execution_model,
            task_type="kódolás"
        )
        
        # 3. Ellenőrzés
        verification_model = final_state.get("verification_result", {}).get("model", "gpt-3.5-turbo")
        execution_content = execution_result.get("content", "")
        verification_result = await model_manager.execute_task_with_tools(
            query=f"Ellenőrzési fázis. A végrehajtás eredménye: {execution_content}. Eredeti feladat: {command}",
            system_message="Most az ellenőrzési fázisban vagy. Ellenőrizd, hogy a végrehajtás teljesítette-e a feladatot. Használj eszközöket a létrehozott fájlok vagy rendszerállapot ellenőrzéséhez.",
            model=verification_model,
            task_type="ellenőrzés"
        )
        
        # Visszaadjuk a munkamenet eredményét
        return {
            "result": verification_result.get("content", ""),
            "models_used": {
                "planning": planning_model,
                "execution": execution_model,
                "verification": verification_model
            },
            "session_id": session_id,
            "workflow_events": events
        }
