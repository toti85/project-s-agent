"""
Project-S Intelligent Workflow System
------------------------------------
A komplex, többlépcsős AI-vezérelt workflow-k kezelésére szolgáló rendszer.
Támogatja az intelligens eszközválasztást, döntéshozatalt és állapotkövetést.

Ez a modul a Project-S eszközrendszerre épül, és a LangGraph-ot használja
a workflow-k strukturálására és végrehajtására.

Főbb komponensek:
- SmartToolOrchestrator: Eszközök intelligens kiválasztása és láncolása
- WorkflowDecisionEngine: Köztes eredmények elemzése és következő lépések meghatározása 
- WorkflowContextManager: Állapotkövetés és kontextus kezelés
- EnhancedLangGraphIntegration: LangGraph munkafolyamatok kiterjesztett integrációja
"""

import asyncio
import logging
import os
import sys
import json
import time
import uuid
import traceback
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Union, Callable, Tuple, TypedDict, cast

# Naplózás beállítása
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger("intelligent_workflow")

# Adjuk hozzá a projekt gyökérkönyvtárát a keresési útvonalhoz
project_root = Path(__file__).parent
if str(project_root) not in sys.path:
    sys.path.append(str(project_root))

# Project-S importálások
try:
    from tools import register_all_tools
    from tools.file_tools import FileWriteTool, FileReadTool
    from tools.web_tools import WebPageFetchTool
    from tools.tool_interface import BaseTool
    from tools.tool_registry import tool_registry
    logger.info("✅ Project-S eszközök importálása sikeres")
except ImportError as e:
    logger.error(f"❌ Hiba a Project-S eszközök importálásakor: {e}")
    sys.exit(1)

# LangGraph importálások
try:
    from langgraph.graph import StateGraph
    from langgraph.prebuilt import ToolNode
    from langgraph.graph.message import add_messages
    logger.info("✅ LangGraph importálása sikeres")
except ImportError as e:
    logger.error(f"❌ Hiba a LangGraph importálásakor: {e}")
    logger.error("Futtassa a 'pip install langgraph' parancsot a hiányzó könyvtár telepítéséhez.")
    sys.exit(1)

class WorkflowState(TypedDict, total=False):
    """
    Workflow állapot a munkafolyamatok követéséhez.
    """
    messages: List[Dict[str, Any]]
    tool_results: Dict[str, Any]
    errors: List[Dict[str, Any]]
    
    # Workflow-specifikus mezők
    workflow_id: str
    start_time: str
    current_step: str
    completed_steps: List[str]
    input_data: Dict[str, Any]
    intermediate_results: Dict[str, Any]
    output_data: Dict[str, Any]
    metadata: Dict[str, Any]

class SmartToolOrchestrator:
    """
    Intelligens eszközkezelő az optimális eszközök kiválasztásához és
    végrehajtási láncok létrehozásához.
    """
    
    def __init__(self):
        """
        Inicializálja az intelligens eszközkészletet.
        """
        self.available_tools: Dict[str, BaseTool] = {}
        self.tool_capabilities: Dict[str, Dict[str, Any]] = {}
        self.execution_history: List[Dict[str, Any]] = []
    
    async def register_available_tools(self):
        """
        Regisztrálja az elérhető eszközöket a rendszerből.
        """
        logger.info("🔍 Elérhető eszközök regisztrálása...")
        
        # Az összes eszköz regisztrálása a registry-ből
        try:
            await register_all_tools()
            
            # Az elérhető eszközök lekérése - közvetlen hozzáférés a tools dictionary-hez
            self.available_tools = tool_registry.tools
            
            # Eszköz képességeinek feltérképezése
            for name, tool in self.available_tools.items():
                self.tool_capabilities[name] = {
                    "name": name,
                    "description": tool.__doc__ or "",
                    "parameters": getattr(tool, "parameters", {}),
                    "category": self._determine_tool_category(tool),
                    "async": asyncio.iscoroutinefunction(tool.execute)
                }
                
            logger.info(f"✅ {len(self.available_tools)} eszköz sikeresen regisztrálva")
            
        except Exception as e:
            logger.error(f"❌ Hiba az eszközök regisztrációjakor: {str(e)}")
            raise
    
    def _determine_tool_category(self, tool: BaseTool) -> str:
        """
        Meghatározza egy eszköz kategóriáját a neve és funkciói alapján.
        """
        name = tool.__class__.__name__.lower()
        
        if "file" in name:
            return "file_operation"
        elif "web" in name:
            return "web_operation"
        elif "code" in name:
            return "code_operation"
        elif "system" in name:
            return "system_operation"
        else:
            return "general"
    
    async def select_best_tool(self, task_description: str, context: Dict[str, Any]) -> Tuple[str, BaseTool]:
        """
        Kiválasztja a legjobb eszközt egy feladat végrehajtásához.
        """
        logger.info(f"🔍 Eszköz kiválasztása a feladathoz: {task_description}")
        
        # Egyszerű eszközválasztási logika - később AI-alapú lehet
        task_lower = task_description.lower()
        
        # Web művelet felismerése
        if any(kw in task_lower for kw in ["web", "url", "http", "fetch", "download"]):
            tool_name = next(
                (name for name, cap in self.tool_capabilities.items() 
                if cap["category"] == "web_operation"),
                None
            )
            if tool_name:
                logger.info(f"✅ Kiválasztott eszköz: {tool_name} (web operation)")
                return tool_name, self.available_tools[tool_name]
        
        # Fájlműveletek felismerése
        if any(kw in task_lower for kw in ["file", "save", "write", "read", "load"]):
            # Különböztessünk meg olvasási és írási műveleteket
            if any(kw in task_lower for kw in ["save", "write", "create"]):
                tool_candidates = [
                    name for name, cap in self.tool_capabilities.items()
                    if cap["category"] == "file_operation" and "write" in name.lower()
                ]
            else:
                tool_candidates = [
                    name for name, cap in self.tool_capabilities.items()
                    if cap["category"] == "file_operation" and "read" in name.lower()
                ]
                
            if tool_candidates:
                tool_name = tool_candidates[0]
                logger.info(f"✅ Kiválasztott eszköz: {tool_name} (file operation)")
                return tool_name, self.available_tools[tool_name]
        
        # Alapértelmezett eszköz vagy hiba
        if not self.available_tools:
            raise ValueError("Nincsenek elérhető eszközök a rendszerben")
        
        # Válasszuk ki az első elérhető eszközt
        default_tool_name = next(iter(self.available_tools.keys()))
        default_tool = self.available_tools[default_tool_name]
        logger.warning(f"⚠️ Nem sikerült specifikus eszközt találni. Alapértelmezett eszköz használata: {default_tool_name}")
        
        return default_tool_name, default_tool
    
    async def execute_tool_chain(self, tool_sequence: List[Tuple[str, Dict[str, Any]]], 
                              initial_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Végrehajt egy eszközláncot, ahol az előző eszköz kimenete a következő bemenete lesz.
        """
        logger.info(f"🔄 Eszközlánc végrehajtása ({len(tool_sequence)} lépés)...")
        
        current_data = initial_data.copy()
        results = {}
        
        for i, (tool_name, params) in enumerate(tool_sequence):
            try:
                # Ellenőrizzük, hogy az eszköz létezik-e
                if tool_name not in self.available_tools:
                    raise ValueError(f"Az eszköz nem létezik: {tool_name}")
                
                tool = self.available_tools[tool_name]
                
                logger.info(f"⚙️ Végrehajtás: {tool_name} (lépés {i+1}/{len(tool_sequence)})")
                
                # Paraméterek előkészítése a kontextus alapján
                prepared_params = self._prepare_parameters(tool, params, current_data)
                
                # Eszköz végrehajtása
                start_time = time.time()
                result = await tool.execute(**prepared_params)
                execution_time = time.time() - start_time
                
                # Eredmény mentése
                results[tool_name] = result
                
                # Állapot frissítése a következő eszköznek
                current_data.update(self._extract_relevant_output(tool_name, result))
                
                # Végrehajtási napló
                self.execution_history.append({
                    "tool": tool_name,
                    "params": params,
                    "execution_time": execution_time,
                    "success": True,
                    "timestamp": datetime.now().isoformat()
                })
                
                logger.info(f"✅ {tool_name} sikeresen végrehajtva ({execution_time:.2f}s)")
                
            except Exception as e:
                logger.error(f"❌ Hiba a(z) {tool_name} eszköz végrehajtásakor: {str(e)}")
                
                # Hibanapló
                self.execution_history.append({
                    "tool": tool_name,
                    "params": params,
                    "error": str(e),
                    "success": False,
                    "timestamp": datetime.now().isoformat()
                })
                
                # Próbáljuk meg a hibát kezelni
                handled = await self.handle_tool_failures(tool_name, e, current_data)
                if not handled:
                    raise
        
        return {
            "final_result": current_data,
            "individual_results": results,
            "execution_history": self.execution_history
        }
    
    def _prepare_parameters(self, tool: BaseTool, params: Dict[str, Any], 
                          context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Előkészíti a paramétereket egy eszköz számára, figyelembe véve a kontextust.
        """
        prepared_params = params.copy()
        
        # Itt lehet implementálni speciális paraméterkezelést
        # Például: paraméterek automatikus kitöltése a kontextusból
        
        return prepared_params
    
    def _extract_relevant_output(self, tool_name: str, result: Any) -> Dict[str, Any]:
        """
        Kinyeri a releváns információkat egy eszköz kimenetéből.
        """
        output = {}
        
        # Alapértelmezett feldolgozás
        if isinstance(result, dict):
            # Ha az eredmény szótár, akkor minden kulcsot átveszünk egy prefixszel
            prefix = f"{tool_name.lower()}_"
            output = {f"{prefix}{key}": value for key, value in result.items()}
        else:
            # Egyéb esetben az eredményt közvetlenül tároljuk
            output[tool_name.lower() + "_result"] = result
            
        return output
    
    async def handle_tool_failures(self, failed_tool: str, error: Exception, 
                               context: Dict[str, Any]) -> bool:
        """
        Kezeli az eszközhibákat, és megpróbál alternatívákat találni.
        """
        logger.warning(f"⚠️ Hibakezelés a következő eszközhöz: {failed_tool}")
        
        # Egyszerű hibakezelési logika
        tool_category = next(
            (cap["category"] for name, cap in self.tool_capabilities.items() if name == failed_tool),
            None
        )
        
        if not tool_category:
            logger.error(f"❌ Nem ismert eszközkategória: {failed_tool}")
            return False
        
        # Alternatív eszközök keresése ugyanabban a kategóriában
        alternatives = [
            name for name, cap in self.tool_capabilities.items()
            if cap["category"] == tool_category and name != failed_tool
        ]
        
        if alternatives:
            alternative = alternatives[0]
            logger.info(f"🔄 Alternatív eszköz használata: {alternative}")
            
            # Itt lehetne implementálni az alternatív eszköz végrehajtását
            # Ez most egyszerűsítve van, csak jelezzük, hogy találtunk alternatívát
            
            return True
        
        logger.error(f"❌ Nem található alternatív eszköz a következő kategóriában: {tool_category}")
        return False

class WorkflowDecisionEngine:
    """
    Döntési motor az intelligens workflow vezérléshez.
    Elemzi a köztes eredményeket és meghatározza a következő lépéseket.
    """
    
    def __init__(self):
        """
        Inicializálja a döntési motort.
        """
        self.decision_history = []
    
    async def analyze_intermediate_results(self, step_output: Dict[str, Any]) -> Dict[str, Any]:
        """
        Elemzi a munkafolyamat köztes eredményeit.
        """
        logger.info("🔍 Köztes eredmények elemzése...")
        
        analysis = {
            "has_error": self._check_for_errors(step_output),
            "data_quality": self._assess_data_quality(step_output),
            "content_type": self._determine_content_type(step_output),
            "analysis_timestamp": datetime.now().isoformat()
        }
        
        return analysis
    
    async def decide_next_action(self, current_state: Dict[str, Any], available_tools: List[str]) -> str:
        """
        Eldönti a következő műveletet az aktuális állapot alapján.
        """
        logger.info("🤔 Következő művelet meghatározása...")
        
        # Állapot elemzése
        has_error = current_state.get("has_error", False)
        current_step = current_state.get("current_step", "")
        content_type = current_state.get("content_type", "unknown")
        
        # Döntési logika
        next_action = "default"
        
        if has_error:
            next_action = "error_handling"
        elif content_type == "technical":
            next_action = "deep_analysis"
        elif content_type == "general":
            next_action = "summary_only"
        
        # Döntés naplózása
        self.decision_history.append({
            "current_state": current_state,
            "decision": next_action,
            "timestamp": datetime.now().isoformat()
        })
        
        logger.info(f"✅ Döntés: {next_action}")
        return next_action
    
    async def evaluate_success_criteria(self, workflow_results: Dict[str, Any]) -> bool:
        """
        Értékeli, hogy a munkafolyamat eredménye megfelel-e a sikerkritériumoknak.
        """
        logger.info("🧐 Sikerkritériumok értékelése...")
        
        # Alapvető ellenőrzések
        required_files = ["raw_content.txt", "analysis_data.json", "executive_summary.md"]
        file_results = workflow_results.get("file_results", {})
        
        # Ellenőrizzük, hogy a szükséges fájlok létrejöttek-e
        files_created = [
            filename for filename, result in file_results.items()
            if result.get("success", False)
        ]
        
        missing_files = [f for f in required_files if not any(f in filename for filename in files_created)]
        
        if missing_files:
            logger.warning(f"⚠️ Hiányzó fájlok: {', '.join(missing_files)}")
            return False
            
        logger.info("✅ A munkafolyamat sikeresen teljesítette a kritériumokat")
        return True
    
    def _check_for_errors(self, data: Dict[str, Any]) -> bool:
        """
        Ellenőrzi, hogy vannak-e hibák az adatokban.
        """
        # Keressünk hibákat a kimenetben
        if isinstance(data, dict):
            error_keys = ["error", "exception", "failure"]
            for key in error_keys:
                if key in data:
                    return True
            
            # Rekurzívan ellenőrizzük a beágyazott szótárakat
            for value in data.values():
                if isinstance(value, dict) and self._check_for_errors(value):
                    return True
        
        return False
    
    def _assess_data_quality(self, data: Dict[str, Any]) -> str:
        """
        Értékeli az adatok minőségét.
        """
        # Egyszerű adatminőség-ellenőrzés
        if not data:
            return "empty"
        
        content_fields = ["content", "text", "body", "html"]
        has_content = any(field in data for field in content_fields)
        
        if not has_content:
            return "low"
        
        # Ellenőrizzük a tartalom méretét (ha elérhető)
        for field in content_fields:
            if field in data and isinstance(data[field], str):
                content = data[field]
                if len(content) < 100:
                    return "low"
                elif len(content) < 1000:
                    return "medium"
                else:
                    return "high"
        
        return "medium"
    
    def _determine_content_type(self, data: Dict[str, Any]) -> str:
        """
        Meghatározza a tartalom típusát.
        """
        # Tartalom kinyerése
        content = ""
        content_fields = ["content", "text", "body", "html"]
        
        for field in content_fields:
            if field in data and isinstance(data[field], str):
                content = data[field]
                break
        
        if not content:
            return "unknown"
        
        # Egyszerű heurisztika a tartalom típusának meghatározásához
        technical_keywords = ["code", "algorithm", "function", "class", "api", 
                            "implementation", "framework", "language", "programming"]
                            
        news_keywords = ["news", "article", "report", "journalist", "published", 
                       "today", "yesterday", "week", "month"]
        
        academic_keywords = ["research", "study", "paper", "academic", "university", 
                           "professor", "journal", "experiment"]
        
        # Egyszerű kulcsszó alapú osztályozás
        technical_count = sum(1 for kw in technical_keywords if kw.lower() in content.lower())
        news_count = sum(1 for kw in news_keywords if kw.lower() in content.lower())
        academic_count = sum(1 for kw in academic_keywords if kw.lower() in content.lower())
        
        # A legtöbb találat alapján döntünk
        counts = {
            "technical": technical_count,
            "news": news_count,
            "academic": academic_count
        }
        
        max_type = max(counts, key=counts.get)
        max_count = counts[max_type]
        
        # Ha túl kevés találat van, akkor általános típus
        if max_count < 3:
            return "general"
            
        return max_type

class WorkflowContextManager:
    """
    Workflow-k állapotkezelése, kontextus tárolása és megosztása
    a különböző komponensek között.
    """
    
    def __init__(self, max_context_size: int = 1024*1024):
        """
        Inicializálja a kontextuskezelőt egy maximális kontextusmérettel (alapértelmezetten 1MB).
        """
        self.contexts = {}
        self.max_context_size = max_context_size
    
    def create_workflow_context(self, workflow_id: str = None) -> str:
        """
        Létrehoz egy új munkafolyamat-kontextust.
        """
        if not workflow_id:
            workflow_id = str(uuid.uuid4())
            
        self.contexts[workflow_id] = {
            "workflow_id": workflow_id,
            "start_time": datetime.now().isoformat(),
            "current_step": "init",
            "completed_steps": [],
            "input_data": {},
            "intermediate_results": {},
            "output_data": {},
            "metadata": {
                "context_size": 0,
                "last_updated": datetime.now().isoformat()
            }
        }
        
        logger.info(f"✅ Új workflow kontextus létrehozva: {workflow_id}")
        return workflow_id
    
    def maintain_workflow_state(self, workflow_id: str, step_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Karbantartja a munkafolyamat állapotát a lépés eredményeinek hozzáadásával.
        """
        if workflow_id not in self.contexts:
            raise ValueError(f"Nem létező workflow ID: {workflow_id}")
        
        context = self.contexts[workflow_id]
        
        # Lépés eredményeinek feldolgozása
        step_name = step_results.get("step_name", "unknown_step")
        context["current_step"] = step_name
        context["completed_steps"].append(step_name)
        context["intermediate_results"][step_name] = step_results.get("result", {})
        
        # Kontextusméret ellenőrzése és kezelése
        self._update_context_size(workflow_id)
        if context["metadata"]["context_size"] > self.max_context_size:
            context = self.compress_large_context(workflow_id)
        
        context["metadata"]["last_updated"] = datetime.now().isoformat()
        self.contexts[workflow_id] = context
        
        return context
    
    def compress_large_context(self, workflow_id: str) -> Dict[str, Any]:
        """
        Tömöríti a kontextust, ha az túl nagy lett.
        """
        if workflow_id not in self.contexts:
            raise ValueError(f"Nem létező workflow ID: {workflow_id}")
            
        logger.info(f"🗜️ Nagy kontextus tömörítése: {workflow_id}")
        
        context = self.contexts[workflow_id]
        
        # Stratégia a nagy kontextusok kezelésére:
        # 1. Részletes köztes eredmények összegzése
        # 2. Korábbi lépések részleteinek eltávolítása
        
        # Az utolsó N lépés kivételével a többit összegezzük
        steps_to_keep_detailed = 2
        completed_steps = context["completed_steps"]
        
        if len(completed_steps) > steps_to_keep_detailed:
            steps_to_summarize = completed_steps[:-steps_to_keep_detailed]
            
            # Összesítés létrehozása és a részletek eltávolítása
            summary = {
                "steps_summarized": steps_to_summarize,
                "timestamp": datetime.now().isoformat()
            }
            
            for step in steps_to_summarize:
                if step in context["intermediate_results"]:
                    # Táruljuk el a lényeges információkat
                    step_result = context["intermediate_results"][step]
                    if isinstance(step_result, dict):
                        # Csak a legfontosabb mezők megtartása
                        summary[f"{step}_status"] = "completed"
                        summary[f"{step}_success"] = not self._check_for_errors(step_result)
                        
                        # Mentsük el a fájlelérési utakat vagy más fontos eredményeket
                        if "file_path" in step_result:
                            summary[f"{step}_file"] = step_result["file_path"]
                        if "url" in step_result:
                            summary[f"{step}_url"] = step_result["url"]
                    
                    # Töröljük az eredeti részletes eredményt
                    del context["intermediate_results"][step]
            
            # A tömörített összefoglalás hozzáadása a kontextushoz
            context["intermediate_results"]["summarized_steps"] = summary
        
        # Kontextus méret frissítése
        self._update_context_size(workflow_id)
        logger.info(f"✅ Kontextus tömörítve: {workflow_id} (új méret: {context['metadata']['context_size']} byte)")
        
        return context
    
    def provide_context_to_tools(self, workflow_id: str, tool_name: str) -> Dict[str, Any]:
        """
        Előkészíti és biztosítja a megfelelő kontextust egy eszköz számára.
        """
        if workflow_id not in self.contexts:
            raise ValueError(f"Nem létező workflow ID: {workflow_id}")
            
        context = self.contexts[workflow_id]
        
        # Alapértelmezett és eszközspecifikus kontextus összeállítása
        tool_context = {
            "workflow_id": workflow_id,
            "current_step": context["current_step"],
            "input_data": context["input_data"]
        }
        
        # Eszközspecifikus kontextus kiegészítések
        # WebPageFetchTool esetén
        if "WebPageFetchTool" in tool_name:
            # Csak az URL és kapcsolódó információk
            tool_context["url"] = context["input_data"].get("url", "")
            
        # FileWriteTool esetén
        elif "FileWriteTool" in tool_name:
            # Biztosítsuk a mentési helyet
            tool_context["output_dir"] = context["input_data"].get("output_dir", "outputs")
            
            # Ha az előző eszköz egy weboldal letöltése volt, adjuk hozzá a webtartalmat
            if context["current_step"] == "web_fetch" and "web_content" in context["intermediate_results"].get("web_fetch", {}):
                tool_context["content"] = context["intermediate_results"]["web_fetch"]["web_content"]
        
        return tool_context
    
    def _update_context_size(self, workflow_id: str) -> None:
        """
        Frissíti a kontextus méretét.
        """
        if workflow_id not in self.contexts:
            return
            
        context = self.contexts[workflow_id]
        
        # JSON méret becslése
        try:
            context_json = json.dumps(context)
            context_size = len(context_json)
            context["metadata"]["context_size"] = context_size
        except Exception as e:
            logger.warning(f"⚠️ Nem sikerült frissíteni a kontextus méretét: {e}")
    
    def _check_for_errors(self, data: Dict[str, Any]) -> bool:
        """
        Ellenőrzi, hogy vannak-e hibák az adatokban.
        """
        if isinstance(data, dict):
            error_keys = ["error", "exception", "failure"]
            return any(key in data for key in error_keys)
        return False

class WebContentAnalyzer:
    """
    Web Content Analyzer - Intelligens munkafolyamat a webtartalom elemzésére
    többlépcsős feldolgozással és kontextustudatos döntésekkel.
    
    A munkafolyamat LangGraph integrációt használ az intelligens döntéshozatal 
    és feltételes elágazások megvalósítására.
    """
    
    def __init__(self, output_dir: str = None):
        """
        Inicializálja a Web Content Analyzer munkafolyamatot.
        """
        self.output_dir = output_dir or os.path.join(os.getcwd(), "analysis_results")
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Komponensek inicializálása
        self.orchestrator = SmartToolOrchestrator()
        self.decision_engine = WorkflowDecisionEngine()
        self.context_manager = WorkflowContextManager()
        
        # Munkafolyamat állapota
        self.workflow_id = None
        self.graph = None
    
    async def initialize(self):
        """
        Inicializálja a szükséges komponenseket és eszközöket, 
        valamint létrehozza a LangGraph munkafolyamatot.
        """
        try:
            await self.orchestrator.register_available_tools()
            self.workflow_id = self.context_manager.create_workflow_context()
            
            # LangGraph munkafolyamat létrehozása
            await self._create_workflow_graph()
            
            logger.info("✅ Web Content Analyzer inicializálva")
            return True
        except Exception as e:
            logger.error(f"❌ Hiba a Web Content Analyzer inicializálásakor: {e}")
            return False
    
    async def _create_workflow_graph(self):
        """
        Létrehozza a Web Content Analysis munkafolyamat LangGraph állapotgráfját.
        """
        # Munkafolyamat állapotának definiálása
        class WebAnalysisState(WorkflowState):
            """Web Content Analysis állapot"""
            url: Optional[str]
            content: Optional[str]
            content_type: Optional[str]
            analysis_results: Optional[Dict[str, Any]]
            keywords: Optional[List[str]]
            branch: Optional[str]
            
        # Gráf létrehozása a definiált állapottípussal
        builder = StateGraph(WebAnalysisState)
        
        # Csomópontok definiálása
        
        # 1. Inicializáló csomópont
        async def initialize_node(state: Dict[str, Any]) -> Dict[str, Any]:
            """A munkafolyamat kezdeti beállítása"""
            logger.info("🚀 Web Content Analyzer munkafolyamat inicializálása")
            
            new_state = state.copy()
            new_state["workflow_id"] = self.workflow_id
            new_state["start_time"] = datetime.now().isoformat()
            new_state["metadata"] = {"created_by": "WebContentAnalyzer", "version": "0.3.0"}
            
            # Küldünk eseményt a diagnosztikai rendszernek
            try:
                from core.event_bus import event_bus
                await event_bus.publish("workflow.start", {
                    "graph_id": self.workflow_id,
                    "state": new_state
                })
            except ImportError:
                logger.warning("⚠️ Event bus nem elérhető, nem küldhető workflow.start esemény")
                
            return new_state
        
        # 2. Web tartalom letöltése
        async def fetch_web_content(state: Dict[str, Any]) -> Dict[str, Any]:
            """Weboldal tartalmának letöltése"""
            logger.info("🌐 Weboldal tartalom letöltése")
            
            new_state = state.copy()
            try:
                url = state.get("url", "")
                if not url:
                    raise ValueError("Hiányzó URL a weblap letöltéséhez")
                    
                web_tool_name, web_tool = await self.orchestrator.select_best_tool(
                    "web page fetch", {"url": url}
                )
                
                web_result = await web_tool.execute(url=url)
                
                # Hibakezelés
                if "error" in web_result:
                    raise ValueError(f"Nem sikerült letölteni a weboldalt: {web_result['error']}")
                
                content = web_result.get("content", "")
                raw_content_path = os.path.join(self.output_dir, "raw_content.txt")
                
                # Tartalom mentése fájlba
                file_tool_name, file_tool = await self.orchestrator.select_best_tool(
                    "write file", {"output_dir": self.output_dir}
                )
                
                await file_tool.execute(path=raw_content_path, content=content)
                
                # Állapot frissítése
                new_state["content"] = content
                new_state["raw_content_path"] = raw_content_path
                new_state["current_step"] = "web_fetch"
                
                logger.info("✅ Weboldal tartalom sikeresen letöltve")
            except Exception as e:
                logger.error(f"❌ Hiba a weboldal letöltése közben: {e}")
                new_state["errors"] = new_state.get("errors", []) + [{
                    "step": "web_fetch",
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                }]
            
            return new_state
            
        # 3. Tartalom elemzése
        async def analyze_content(state: Dict[str, Any]) -> Dict[str, Any]:
            logger.info("🔍 Tartalom elemzése (DEBUG)")
            logger.debug(f"[DEBUG] analyze_content state: {state}")
            new_state = state.copy()
            try:
                content = state.get("content", "")
                if not content:
                    raise ValueError("Nincs tartalom az elemzéshez")
                    
                # Alapszintű elemzés
                analysis = {
                    "word_count": len(content.split()),
                    "content_length": len(content),
                    "has_code": "```" in content or "<code>" in content,
                    "analyzed_at": datetime.now().isoformat()
                }
                
                # Tartalomtípus meghatározása
                content_type = self.decision_engine._determine_content_type({"content": content})
                
                # Állapot frissítése
                new_state["analysis_results"] = analysis
                new_state["content_type"] = content_type
                new_state["current_step"] = "content_analysis"
                
                # Eredmények mentése fájlba
                file_tool_name, file_tool = await self.orchestrator.select_best_tool(
                    "write file", {"output_dir": self.output_dir}
                )
                
                analysis_data = {
                    "source_url": state.get("url", ""),
                    "analysis_timestamp": datetime.now().isoformat(),
                    "content_type": content_type,
                    "content_stats": analysis
                }
                
                analysis_json_path = os.path.join(self.output_dir, "analysis_data.json")
                await file_tool.execute(
                    path=analysis_json_path, 
                    content=json.dumps(analysis_data, indent=2)
                )
                
                new_state["analysis_json_path"] = analysis_json_path
                logger.info(f"✅ Tartalom elemzés kész. Típus: {content_type}")
                
            except Exception as e:
                logger.error(f"❌ Hiba a tartalom elemzése közben: {e}")
                logger.debug(f"[DEBUG] analyze_content exception: {e}")
                new_state["errors"] = new_state.get("errors", []) + [{
                    "step": "content_analysis",
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                }]
            logger.debug(f"[DEBUG] analyze_content new_state: {new_state}")
            return new_state
        
        # 4. Kulcsszavak kinyerése
        async def extract_keywords(state: Dict[str, Any]) -> Dict[str, Any]:
            logger.info("🔑 Kulcsszavak kinyerése (DEBUG)")
            logger.debug(f"[DEBUG] extract_keywords state: {state}")
            new_state = state.copy()
            try:
                content = state.get("content", "")
                if not content:
                    raise ValueError("Nincs tartalom a kulcsszavak kinyeréséhez")
                
                # Kulcsszavak kinyerése
                keywords = self._extract_keywords(content)
                
                # Eredmények mentése fájlba
                file_tool_name, file_tool = await self.orchestrator.select_best_tool(
                    "write file", {"output_dir": self.output_dir}
                )
                
                keywords_json = json.dumps({
                    "keywords": keywords,
                    "extracted_at": datetime.now().isoformat(),
                    "content_type": state.get("content_type", "unknown")
                }, indent=2)
                
                keywords_path = os.path.join(self.output_dir, "keywords_extracted.json")
                await file_tool.execute(path=keywords_path, content=keywords_json)
                
                # Állapot frissítése
                new_state["keywords"] = keywords
                new_state["keywords_path"] = keywords_path
                new_state["current_step"] = "keywords_extraction"
                
                logger.info(f"✅ Kulcsszavak sikeresen kinyerve: {', '.join(keywords[:5])}")
                
            except Exception as e:
                logger.error(f"❌ Hiba a kulcsszavak kinyerése közben: {e}")
                logger.debug(f"[DEBUG] extract_keywords exception: {e}")
                new_state["errors"] = new_state.get("errors", []) + [{
                    "step": "keywords_extraction",
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                }]
            logger.debug(f"[DEBUG] extract_keywords new_state: {new_state}")
            return new_state
        
        # 5. Tartalom típus alapján elágazás meghatározása
        async def decide_branch(state: Dict[str, Any]) -> Dict[str, Any]:
            logger.info("🔀 Feldolgozási útvonal meghatározása (DEBUG)")
            logger.debug(f"[DEBUG] decide_branch state: {state}")
            new_state = state.copy()
            content_type = state.get("content_type", "unknown")
            
            # Döntés a tartalom típusa alapján
            if content_type == "technical":
                branch = "technical_branch"
                logger.info("✅ Technikai tartalom feldolgozási útvonal kiválasztva")
            elif content_type == "academic":
                branch = "academic_branch"
                logger.info("✅ Akadémiai tartalom feldolgozási útvonal kiválasztva")
            else:
                branch = "general_branch"
                logger.info("✅ Általános tartalom feldolgozási útvonal kiválasztva")
            
            # Állapot frissítése a kiválasztott ággal
            new_state["branch"] = branch
            new_state["current_step"] = "branch_decision"
            
            logger.debug(f"[DEBUG] decide_branch new_state: {new_state}")
            return new_state
            
        # 6. Technical branch: Executive summary generálás technikai tartalomhoz
        async def technical_summary(state: Dict[str, Any]) -> Dict[str, Any]:
            """Technikai tartalomhoz optimalizált összefoglaló generálása"""
            logger.info("📘 Technikai tartalomhoz összefoglaló generálása")
            
            new_state = state.copy()
            try:
                # Optimalizált technikai összefoglaló generálás
                url = state.get("url", "")
                content = state.get("content", "")
                analysis_data = {
                    "content_type": "technical",
                    "keywords": state.get("keywords", [])
                }
                
                summary = self._generate_executive_summary(url, content, analysis_data)
                
                # Technikai részeket kiemelő kiegészítés
                if analysis_data["keywords"]:
                    tech_keywords = [k for k in analysis_data["keywords"] 
                                    if k in ["code", "api", "framework", "library", "function", "class", "method"]]
                    if tech_keywords:
                        tech_section = "\n## Technical Details\n\n"
                        tech_section += "This content includes details about:\n"
                        for kw in tech_keywords[:5]:
                            tech_section += f"- {kw.capitalize()}\n"
                        summary += tech_section
                
                # Összefoglaló mentése fájlba
                file_tool_name, file_tool = await self.orchestrator.select_best_tool(
                    "write file", {"output_dir": self.output_dir}
                )
                
                summary_path = os.path.join(self.output_dir, "executive_summary_technical.md")
                await file_tool.execute(path=summary_path, content=summary)
                
                # Állapot frissítése
                new_state["summary_path"] = summary_path
                new_state["current_step"] = "technical_summary"
                
                logger.info("✅ Technikai összefoglaló sikeresen generálva")
                
            except Exception as e:
                logger.error(f"❌ Hiba a technikai összefoglaló generálása közben: {e}")
                new_state["error"] = {
                    "step": "technical_summary",
                    "message": str(e),
                    "timestamp": datetime.now().isoformat()
                }
            
            return new_state
            
        # 7. Academic branch: Executive summary generálás akadémiai tartalomhoz
        async def academic_summary(state: Dict[str, Any]) -> Dict[str, Any]:
            """Akadémiai tartalomhoz optimalizált összefoglaló generálása"""
            logger.info("📚 Akadémiai tartalomhoz összefoglaló generálása")
            
            new_state = state.copy()
            try:
                # Optimalizált akadémiai összefoglaló generálás
                url = state.get("url", "")
                content = state.get("content", "")
                analysis_data = {
                    "content_type": "academic",
                    "keywords": state.get("keywords", [])
                }
                
                summary = self._generate_executive_summary(url, content, analysis_data)
                
                # Akadémiai-specifikus kiegészítés
                academic_section = "\n## Research Implications\n\n"
                academic_section += "This research has implications for:\n"
                for kw in analysis_data["keywords"][:3]:
                    academic_section += f"- Further studies in {kw}\n"
                academic_section += "- Development of new methodologies in this field\n"
                academic_section += "- Practical applications of the research findings\n"
                summary += academic_section
                
                # Összefoglaló mentése fájlba
                file_tool_name, file_tool = await self.orchestrator.select_best_tool(
                    "write file", {"output_dir": self.output_dir}
                )
                
                summary_path = os.path.join(self.output_dir, "executive_summary_academic.md")
                await file_tool.execute(path=summary_path, content=summary)
                
                # Állapot frissítése
                new_state["summary_path"] = summary_path
                new_state["current_step"] = "academic_summary"
                  logger.info("✅ Akadémiai összefoglaló sikeresen generálva")
                
            except Exception as e:
                logger.error(f"❌ Hiba az akadémiai összefoglaló generálása közben: {e}")
                new_state["error"] = {
                    "step": "academic_summary",
                    "message": str(e),
                    "timestamp": datetime.now().isoformat()
                }
            
            return new_state
            
        # 8. General branch: Executive summary generálás általános tartalomhoz
        async def general_summary(state: Dict[str, Any]) -> Dict[str, Any]:
            """Általános tartalomhoz összefoglaló generálása"""
            logger.info("📄 Általános tartalomhoz összefoglaló generálása")
            
            new_state = state.copy()
            try:
                # Általános összefoglaló generálás
                url = state.get("url", "")
                content = state.get("content", "")
                analysis_data = {
                    "content_type": "general",
                    "keywords": state.get("keywords", [])
                }
                
                summary = self._generate_executive_summary(url, content, analysis_data)
                
                # Összefoglaló mentése fájlba
                file_tool_name, file_tool = await self.orchestrator.select_best_tool(
                    "write file", {"output_dir": self.output_dir}
                )
                
                summary_path = os.path.join(self.output_dir, "executive_summary.md")
                await file_tool.execute(path=summary_path, content=summary)
                
                # Állapot frissítése
                new_state["summary_path"] = summary_path
                new_state["current_step"] = "general_summary"
                  logger.info("✅ Általános összefoglaló sikeresen generálva")
                
            except Exception as e:
                logger.error(f"❌ Hiba az általános összefoglaló generálása közben: {e}")
                new_state["error"] = {
                    "step": "general_summary",
                    "message": str(e),
                    "timestamp": datetime.now().isoformat()
                }
            
            return new_state
            
        # 9. Javaslatok generálása
        async def generate_recommendations(state: Dict[str, Any]) -> Dict[str, Any]:
            """Javaslatok generálása a elemzés eredményei alapján"""
            logger.info("💡 Javaslatok generálása")
            
            new_state = state.copy()
            try:
                content_type = state.get("content_type", "general")
                keywords = state.get("keywords", [])
                
                # Javaslatok generálása
                recommendations = self._generate_recommendations(content_type, keywords)
                
                # Javaslatok mentése fájlba
                file_tool_name, file_tool = await self.orchestrator.select_best_tool(
                    "write file", {"output_dir": self.output_dir}
                )
                
                recommendations_path = os.path.join(self.output_dir, "recommended_actions.md")
                await file_tool.execute(path=recommendations_path, content=recommendations)
                
                # Állapot frissítése
                new_state["recommendations_path"] = recommendations_path
                new_state["current_step"] = "recommendations"
                
                logger.info("✅ Javaslatok sikeresen generálva")
                  except Exception as e:
                logger.error(f"❌ Hiba a javaslatok generálása közben: {e}")
                new_state["error"] = {
                    "step": "recommendations",
                    "message": str(e),
                    "timestamp": datetime.now().isoformat()
                }
            
            return new_state
            
        # 10. Összegzés és munkafolyamat befejezése
        async def finalize_workflow(state: Dict[str, Any]) -> Dict[str, Any]:
            """Munkafolyamat befejezése és eredmények összegzése"""
            logger.info("🏁 Munkafolyamat összegzése és befejezése")
            
            new_state = state.copy()
            
            # Végeredmény összegzése
            output_data = {
                "workflow_id": state.get("workflow_id", ""),
                "url": state.get("url", ""),
                "raw_content_path": state.get("raw_content_path", ""),
                "analysis_json_path": state.get("analysis_json_path", ""),
                "keywords_path": state.get("keywords_path", ""),
                "summary_path": state.get("summary_path", ""),
                "recommendations_path": state.get("recommendations_path", ""),
                "content_type": state.get("content_type", "unknown"),
                "completed_at": datetime.now().isoformat(),
                "branch": state.get("branch", "unknown")
            }
            
            # Indexfájl generálása az eredményekről
            try:
                file_tool_name, file_tool = await self.orchestrator.select_best_tool(
                    "write file", {"output_dir": self.output_dir}
                )
                
                index_content = "# Web Content Analysis Results\n\n"
                index_content += f"Analysis of: {state.get('url', '')}\n"
                index_content += f"Content Type: {state.get('content_type', 'unknown')}\n"
                index_content += f"Completed: {datetime.now().isoformat()}\n\n"
                
                index_content += "## Generated Files\n\n"
                for name, path in output_data.items():
                    if name.endswith("_path") and path:
                        file_name = os.path.basename(path)
                        index_content += f"- {name.replace('_path', '')}: [{file_name}]({file_name})\n"
                
                index_path = os.path.join(self.output_dir, "analysis_index.md")
                await file_tool.execute(path=index_path, content=index_content)
                output_data["index_path"] = index_path
                
            except Exception as e:
                logger.warning(f"⚠️ Hiba az index generálása közben: {e}")
            
            # Állapot frissítése
            new_state["output_data"] = output_data
            new_state["current_step"] = "completed"
            new_state["end_time"] = datetime.now().isoformat()
            
            # Esemény küldése a diagnosztikai rendszernek
            try:
                from core.event_bus import event_bus
                await event_bus.publish("workflow.complete", {
                    "graph_id": self.workflow_id,
                    "state": new_state
                })
            except ImportError:
                logger.warning("⚠️ Event bus nem elérhető, nem küldhető workflow.complete esemény")
                
            logger.info("✅ Munkafolyamat sikeresen befejezve")
            return new_state
          # Hibakezelő csomópont
        async def handle_errors(state: Dict[str, Any]) -> Dict[str, Any]:
            """Hibakezelés a munkafolyamat során"""
            logger.error("❌ Hibakezelési csomópont aktiválva")
            
            new_state = state.copy()
            error = new_state.get("error", {})
            
            # Hiba részletek naplózása
            if error:
                logger.error(f"  - {error.get('step', 'unknown')}: {error.get('message', 'ismeretlen hiba')}")
            
            # Hiba jelentés generálása
            try:
                file_tool_name, file_tool = await self.orchestrator.select_best_tool(
                    "write file", {"output_dir": self.output_dir}
                )
                
                error_report = "# Web Content Analysis Error Report\n\n"
                error_report += f"Analysis of: {state.get('url', '')}\n"
                error_report += f"Generated: {datetime.now().isoformat()}\n\n"
                
                error_report += "## Error Encountered\n\n"
                if error:
                    error_report += f"### Step: {error.get('step', 'unknown')}\n"
                    error_report += f"Error: {error.get('message', 'unknown error')}\n"
                    error_report += f"Time: {error.get('timestamp', '')}\n\n"
                  error_report += "\n## Diagnostic Information\n\n"
                error_report += f"- Workflow ID: {state.get('workflow_id', 'unknown')}\n"
                error_report += f"- Current step when error occurred: {state.get('current_step', 'unknown')}\n"
                
                error_path = os.path.join(self.output_dir, "error_report.md")
                await file_tool.execute(path=error_path, content=error_report)
                
                new_state["error_report_path"] = error_path
                
            except Exception as e:
                logger.error(f"❌ Hiba a hibajelentés mentése közben: {str(e)}")
            
            # Esemény küldése a diagnosztikai rendszernek
            try:
                from core.event_bus import event_bus
                await event_bus.publish("workflow.error", {
                    "graph_id": self.workflow_id,
                    "error": f"Error encountered: {error.get('message', 'Unknown error')}",
                    "state": new_state
                })
            except ImportError:
                logger.warning("⚠️ Event bus nem elérhető, nem küldhető workflow.error esemény")
            
            return new_state
        
        # Csomópontok hozzáadása a gráfhoz
        builder.add_node("initialize", initialize_node)
        builder.add_node("fetch_content", fetch_web_content)
        builder.add_node("analyze_content", analyze_content)
        builder.add_node("extract_keywords", extract_keywords)
        builder.add_node("decide_branch", decide_branch)
        builder.add_node("technical_summary", technical_summary)
        builder.add_node("academic_summary", academic_summary)
        builder.add_node("general_summary", general_summary)
        builder.add_node("generate_recommendations", generate_recommendations)
        builder.add_node("finalize", finalize_workflow)
        builder.add_node("handle_errors", handle_errors)
          # Csak az első él marad itt, a többit a conditional edges kezelik
        builder.add_edge("initialize", "fetch_content")
        
        # Feltételes elágazások a tartalom típusa alapján
        builder.add_conditional_edges(
            "decide_branch",
            lambda state: state.get("branch"),
            {
                "technical_branch": "technical_summary",
                "academic_branch": "academic_summary",
                "general_branch": "general_summary",
            }
        )
        
        # Összefutó élek - mindegyik összefoglaló után javaslatok generálása
        builder.add_edge("technical_summary", "generate_recommendations")
        builder.add_edge("academic_summary", "generate_recommendations")
        builder.add_edge("general_summary", "generate_recommendations")
        
        # Befejező él
        # Alapvető munkafolyamat útvonal visszaállítása
        builder.add_edge("fetch_content", "analyze_content")
        builder.add_edge("analyze_content", "extract_keywords")
        builder.add_edge("extract_keywords", "decide_branch")
          # Hiba ellenőrző függvény
        def has_errors(state):
            return "error" in state and state.get("error") is not None
        
        # Hibakezelés feltételes élek hozzáadása minden lépéshez
        for node in ["fetch_content", "analyze_content", "extract_keywords"]:
            builder.add_conditional_edges(
                node,
                has_errors,
                {
                    True: "handle_errors"
                    # Ha False, a már definiált élek alapján folytatja
                }
            )
            
        # Összefoglaló típusú csomópontok egyedi hibakezelése
        for node in ["technical_summary", "academic_summary", "general_summary"]:
            builder.add_conditional_edges(
                node,
                has_errors,
                {
                    True: "handle_errors",
                    # Ha False, akkor a recommendations node-ra megy, ami már definiálva van
                }
            )
            
        # Javaslatok generálása után vagy a befejezésre vagy a hibakezelésre megy
        builder.add_conditional_edges(
            "generate_recommendations",
            has_errors,
            {
                True: "handle_errors",
                False: "finalize"
            }
        )
        
        # A hibakezelő után befejezés
        builder.add_edge("handle_errors", "finalize")
        
        # Entrypoint beállítása
        builder.set_entry_point("initialize")
        
        # Gráf létrehozása és beállítása
        self.graph = builder.compile()
        
        logger.info("✅ Web Content Analysis munkafolyamat gráf sikeresen létrehozva")
    
    async def analyze_url(self, url: str) -> Dict[str, Any]:
        """
        Teljes webtartalom-elemző munkafolyamat végrehajtása egy URL-en,
        LangGraph alapú intelligens feldolgozással és hibakezeléssel.
        """
        logger.info(f"🚀 Web Content Analyzer indítása az URL-re: {url}")
        
        if not self.workflow_id or not self.graph:
            logger.error("❌ A munkafolyamat nincs inicializálva")
            return {"success": False, "error": "A munkafolyamat nincs inicializálva"}
        
        try:
            # Kezdeti állapot létrehozása
            initial_state = {
                "url": url,
                "output_dir": self.output_dir,
                "workflow_id": self.workflow_id,
                "errors": []
            }            # Munkafolyamat végrehajtása
            logger.info("⚡ LangGraph munkafolyamat indítása...")
            try:
                # Próbáljuk először az async módszert
                if hasattr(self.graph, 'ainvoke'):
                    result_state = await self.graph.ainvoke(initial_state)
                elif hasattr(self.graph, 'invoke'):
                    logger.info("⚡ Szinkron végrehajtás használata...")
                    result_state = self.graph.invoke(initial_state)
                else:
                    raise RuntimeError('LangGraph StateGraph does not support ainvoke/invoke/arun/run methods!')
            except Exception as e:
                logger.error(f"❌ Hiba a munkafolyamat végrehajtása közben: {str(e)}")
                raise
                
            # Eredmények ellenőrzése és visszaadása
            if "errors" in result_state and result_state["errors"]:
                logger.error("❌ A munkafolyamat hibákkal fejeződött be")
                return {
                    "success": False, 
                    "error": "A munkafolyamat hibákkal fejeződött be",
                    "errors": result_state["errors"],
                    "partial_results": result_state.get("output_data", {})
                }
            
            # Sikeres befejezés
            logger.info("✅ Web Content Analysis munkafolyamat sikeresen befejezve!")
            
            return {
                "success": True,
                "workflow_id": self.workflow_id,
                "output_paths": result_state.get("output_data", {}),
                "content_type": result_state.get("content_type", "unknown"),
                "processing_branch": result_state.get("branch", "unknown")
            }
            
        except Exception as e:
            logger.error(f"❌ Kritikus hiba a webtartalom elemzése során: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _extract_keywords(self, content: str) -> List[str]:
        """
        Egyszerű kulcsszókinyerés a tartalomból.
        """
        # Valódi implementációban itt NLP-t használnánk
        # Most csak egy egyszerű implementáció
        import re
        from collections import Counter
        
        # Tisztítsuk meg a HTML-től
        content_clean = re.sub(r'<[^>]+>', ' ', content)
        
        # Tokenizálás egyszerű szavakra
        words = re.findall(r'\b[a-zA-Z]{4,}\b', content_clean.lower())
        
        # Stopszavak (gyakori szavak, amelyeket ki akarunk szűrni)
        stopwords = set([
            "this", "that", "these", "those", "the", "and", "but", "for", "with",
            "about", "from", "when", "where", "what", "which", "who", "whom", "whose"
        ])
        
        # Stopszavak eltávolítása
        filtered_words = [word for word in words if word not in stopwords]
        
        # Leggyakoribb szavak megtalálása
        counter = Counter(filtered_words)
        top_keywords = [word for word, count in counter.most_common(15)]
        
        return top_keywords
    
    def _generate_executive_summary(self, url: str, content: str, analysis_data: Dict[str, Any]) -> str:
        """
        Executive summary generálás a tartalomból.
        """
        # Valódi implementációban itt AI-t használnánk
        keywords = ", ".join(analysis_data.get("keywords", [])[:5])
        word_count = analysis_data.get("content_stats", {}).get("word_count", 0)
        content_type = analysis_data.get("content_type", "unknown")
        
        return f"""# Executive Summary

## Content Overview

Source: {url}
Content Type: {content_type.capitalize()}
Length: {word_count} words
Primary Keywords: {keywords}

## Key Insights

This {content_type} content explores topics related to {keywords}. 
The material provides information about various aspects of these subjects and their relationships.

## Summary

The content from {url} discusses {content_type} topics with a focus on {keywords}.
It's structured in a way that presents the information in a coherent manner.

## Relevance

Based on the keywords and content, this material would be relevant for audiences interested in 
{content_type} content, particularly those focused on {keywords}.

## Recommendations

Further analysis is recommended to extract more specific insights and potential applications.

*Generated by Web Content Analyzer at {datetime.now().isoformat()}*
"""
    
    def _generate_recommendations(self, content_type: str, keywords: List[str]) -> str:
        """
        Generálja a javasolt következő lépéseket a tartalom típusa alapján.
        """
        # Kulcsszavak listájából véletlenszerűen válasszunk ki párat
        import random
        selected_keywords = random.sample(keywords, min(3, len(keywords)))
        keywords_str = ", ".join(selected_keywords)
        
        recommendations = f"""# Recommended Follow-up Actions

Based on the analysis of the content, the following actions are recommended:

"""
        
        # Tartalomtípus-specifikus javaslatok
        if content_type == "technical":
            recommendations += f"""## Technical Content Recommendations

1. **Research Related Technical Documentation**
   - Look for official documentation related to {keywords_str}
   - Search for code samples and implementation guides

2. **Code Implementation**
   - Create a proof-of-concept using the described techniques
   - Test the implementation with various scenarios

3. **Expert Consultation**
   - Connect with subject matter experts in {selected_keywords[0] if selected_keywords else "this field"}
   - Join relevant technical communities and forums

4. **Technical Comparison**
   - Compare with alternative approaches or technologies
   - Evaluate performance and scalability considerations
"""
        elif content_type == "academic":
            recommendations += f"""## Academic Content Recommendations

1. **Literature Review**
   - Search for related papers in academic databases
   - Review cited references and bibliography

2. **Methodology Evaluation**
   - Analyze the research methodology for validity
   - Consider replication studies or extensions

3. **Cross-disciplinary Connections**
   - Explore how this research connects to other fields
   - Identify potential applications in related domains

4. **Research Collaboration**
   - Identify institutions working on {keywords_str}
   - Connect with researchers in this field
"""
        else:
            recommendations += f"""## General Content Recommendations

1. **Further Information Gathering**
   - Search for additional sources on {keywords_str}
   - Explore different perspectives on the topic

2. **Content Validation**
   - Cross-reference with reputable sources
   - Verify factual claims and data

3. **Broader Context**
   - Understand how this topic relates to wider trends
   - Consider historical development and future directions

4. **Practical Applications**
   - Identify how this information can be applied
   - Develop actionable insights based on the content
"""
        
        recommendations += f"""
## Priority Actions

1. **High Priority**: Research more about {selected_keywords[0] if selected_keywords else "the main topic"}
2. **Medium Priority**: Connect with communities focused on {keywords_str}
3. **Ongoing**: Monitor for updates and new developments in this area

*Generated by Web Content Analyzer at {datetime.now().isoformat()}*
"""
        
        return recommendations

async def main():
    """
    Fő belépési pont a Web Content Analyzer futtatásához.
    """
    logger.info("=" * 50)
    logger.info("Web Content Analyzer - Intelligens Workflow Demo")
    logger.info("=" * 50)
    
    import argparse
    parser = argparse.ArgumentParser(description="Web Content Analyzer")
    parser.add_argument("--url", type=str, default="https://openai.com/research/gpt-4", 
                     help="Az elemzendő URL")
    args = parser.parse_args()
    
    try:
        # Analyzer inicializálása
        analyzer = WebContentAnalyzer()
        await analyzer.initialize()
        
        # URL elemzése
        logger.info(f"🌐 URL elemzése: {args.url}")
        result = await analyzer.analyze_url(args.url)
        
        # Eredmények kiírása
        if result["success"]:
            logger.info("✅ Elemzés sikeresen befejezve!")
            logger.info("📁 Eredmények:")
            for output_name, output_path in result.get("output_paths", {}).items():
                logger.info(f"  - {output_name}: {output_path}")
        else:
            logger.error(f"❌ Elemzés sikertelen: {result.get('error', 'Ismeretlen hiba')}")
            
    except Exception as e:
        logger.error(f"❌ Hiba a program futása közben: {str(e)}")
        traceback.print_exc()
    
    logger.info("=" * 50)
    logger.info("Web Content Analyzer - Futtatás befejezve")
    logger.info("=" * 50)

if __name__ == "__main__":
    asyncio.run(main())
