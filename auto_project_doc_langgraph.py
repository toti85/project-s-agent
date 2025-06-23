"""
Project-S Automatikus Projekt Dokumentáció Generáló - LangGraph Verzió
-------------------------------------------------------------------
Ez a modul a Project-S eszköz rendszerét használja egy komplex,
több AI-t használó dokumentáció generáló workflow létrehozására, LangGraph integrációval.

Az implementáció a már meglévő auto_project_doc_generator.py eszközre épít, de
a folyamatokat egy LangGraph munkafolyamatban szervezi, ami lehetővé teszi:
1. Az eszközök moduláris munkafolyamatba szervezését
2. A több AI modell kezelését a LangGraph által
3. A dokumentáció generálás részfeladatainak elkülönített kezelését
4. A robusztus hibakezelést és az állapot követését
"""

import asyncio
import logging
import os
import sys
from pathlib import Path
import json
from datetime import datetime
import re
import traceback
from typing import Dict, List, Any, Optional, Tuple, Set, TypedDict, cast

# Hozzáadjuk a projekt gyökérkönyvtárát a keresési útvonalhoz
project_root = Path(__file__).parent
if str(project_root) not in sys.path:
    sys.path.append(str(project_root))

# Konfiguráljuk a naplózást
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger("auto_doc_langgraph")

# Project-S importok
try:
    from tools import register_all_tools
    from tools.file_tools import FileSearchTool, FileReadTool, FileWriteTool, FileInfoTool
    from tools.web_tools import WebPageFetchTool
    from tools.code_tools import CodeExecutionTool, PythonModuleInfoTool
    from tools.langgraph_integration import tool_graph_integrator, ToolState
    logger.info("Project-S eszköz modulok sikeresen importálva")
except ImportError as e:
    logger.error(f"Hiba történt a Project-S modulok importálásakor: {e}")
    sys.exit(1)

# LangGraph importok
try:
    from langgraph.graph import StateGraph
    from langgraph.prebuilt import ToolNode
    from langgraph.graph.message import add_messages
    logger.info("LangGraph modulok sikeresen importálva")
except ImportError as e:
    logger.error(f"Hiba történt a LangGraph importálásakor: {e}")
    logger.error("Futtassa a 'pip install langgraph' parancsot a hiányzó könyvtár telepítéséhez.")
    sys.exit(1)

# Újrahasználjuk a komponenseket az eredeti fájlból
from auto_project_doc_generator import (
    AIModelIntegration, 
    ProjectStructureAnalyzer,
    DocumentationGenerator,
    update_status
)

# Használjuk a megosztott típusdefiníciókat a körkörös importálás elkerüléséhez
from tools.langgraph_types import DocGenState

# Munkafolyamat állapot inicializálása
def init_docgen_state(project_path: str) -> DocGenState:
    """
    Inicializálja a dokumentáció generáló munkafolyamat állapotát.
    """
    return cast(DocGenState, {
        "messages": [
            {
                "role": "system",
                "content": "Automatikus projekt dokumentáció generálás munkafolyamat indulása."
            }
        ],
        "tools": [],
        "tool_results": {},
        "tool_history": [],
        "tool_errors": [],
        
        "project_data": {
            "project_path": project_path,
            "python_files": [],
            "config_files": [],
            "doc_files": []
        },
        "file_analysis": {
            "analyzed_files_count": 0,
            "total_files_count": 0,
            "files": []
        },
        "ai_results": {},
        "output_paths": {
            "output_dir": os.path.join(project_path, "outputs"),
            "readme_path": "",
            "analysis_path": ""
        },
        "current_stage": "init"
    })

# LangGraph csomópontok a munkafolyamathoz
async def analyze_project_structure(state: DocGenState) -> DocGenState:
    """
    Elemzi a projekt struktúráját és frissíti az állapotot.
    """
    logger.info("🔍 Projekt struktúra elemzése...")
    try:
        analyzer = ProjectStructureAnalyzer()
        project_path = state["project_data"]["project_path"]
        project_data = await analyzer.get_project_structure(project_path)
        
        # Frissítjük az állapotot
        state["project_data"] = project_data
        state["current_stage"] = "project_structure_analyzed"
        
        # Hozzáadunk egy üzenetet a munkafolyamat naplózásához
        add_messages(state, [
            {
                "role": "system",
                "content": f"Projekt struktúra elemzése sikeres. Python fájlok száma: {len(project_data.get('python_files', []))}"
            }
        ])
    except Exception as e:
        error_msg = f"Hiba a projekt struktúra elemzésekor: {str(e)}"
        logger.error(error_msg)
        state["tool_errors"].append({
            "stage": "analyze_project_structure",
            "error": error_msg,
            "timestamp": datetime.now().isoformat()
        })
        state["current_stage"] = "error"
        add_messages(state, [
            {
                "role": "system",
                "content": error_msg
            }
        ])
    
    return state

async def analyze_python_files(state: DocGenState) -> DocGenState:
    """
    Elemzi a Python fájlok tartalmát és frissíti az állapotot.
    """
    logger.info("📄 Python fájlok részletes elemzése...")
    try:
        analyzer = ProjectStructureAnalyzer()
        python_files = state["project_data"].get("python_files", [])
        
        if not python_files:
            logger.warning("Nem találhatók Python fájlok a projektben.")
            add_messages(state, [
                {
                    "role": "system",
                    "content": "Figyelmeztetés: Nem találhatók Python fájlok a projektben."
                }
            ])
            state["current_stage"] = "files_analyzed"
            return state
        
        file_analysis = await analyzer.analyze_python_files(python_files)
        
        # Frissítjük az állapotot
        state["file_analysis"] = file_analysis
        state["current_stage"] = "files_analyzed"
        
        # Hozzáadunk egy üzenetet a munkafolyamat naplózásához
        add_messages(state, [
            {
                "role": "system",
                "content": f"Fájl elemzés sikeres. Elemzett fájlok száma: {file_analysis.get('analyzed_files_count', 0)}"
            }
        ])
    except Exception as e:
        error_msg = f"Hiba a Python fájlok elemzésekor: {str(e)}"
        logger.error(error_msg)
        state["tool_errors"].append({
            "stage": "analyze_python_files",
            "error": error_msg,
            "timestamp": datetime.now().isoformat()
        })
        state["current_stage"] = "error"
        add_messages(state, [
            {
                "role": "system",
                "content": error_msg
            }
        ])
    
    return state

async def perform_ai_analysis(state: DocGenState) -> DocGenState:
    """
    AI modellek használata a kód elemzéséhez.
    """
    logger.info("🧠 AI elemzés végrehajtása...")
    try:
        ai_integration = AIModelIntegration()
        project_data = state["project_data"]
        file_analysis = state["file_analysis"]
        context = {"project_data": project_data, "file_analysis": file_analysis}
        
        # GPT-4 használata architektúra elemzéshez
        logger.info("GPT-4 használata architektúra elemzéshez")
        architecture_result = await ai_integration.analyze_with_model(
            model="gpt-4", 
            prompt="Elemezd a projekt architektúráját és azonosítsd a fő design pattern-eket.",
            context=context
        )
        
        # GPT-4 használata kód struktúra elemzéshez
        logger.info("GPT-4 használata kód struktúra elemzéshez")
        code_structure_result = await ai_integration.analyze_with_model(
            model="gpt-4", 
            prompt="Elemezd a projekt kód struktúráját és fő komponenseit.",
            context=context
        )
        
        # Claude használata best practices elemzéshez
        logger.info("Claude használata best practices elemzéshez")
        best_practices_result = await ai_integration.analyze_with_model(
            model="claude-sonnet", 
            prompt="Értékeld a kód minőségét és ajánlj best practices technikákat.",
            context=context
        )
        
        # Claude használata biztonsági elemzéshez
        logger.info("Claude használata biztonsági elemzéshez")
        security_result = await ai_integration.analyze_with_model(
            model="claude-sonnet", 
            prompt="Értékeld a projekt biztonsági aspektusait, különösen a kód futtatás és rendszerparancs végrehajtás szempontjából.",
            context=context
        )
        
        # Frissítjük az állapotot
        state["ai_results"] = {
            "architecture": architecture_result,
            "code_structure": code_structure_result,
            "best_practices": best_practices_result,
            "security": security_result
        }
        state["current_stage"] = "ai_analysis_completed"
        
        # Hozzáadunk egy üzenetet a munkafolyamat naplózásához
        add_messages(state, [
            {
                "role": "system",
                "content": "AI elemzés sikeresen végrehajtva mindkét modellel (GPT-4 és Claude)"
            }
        ])
    except Exception as e:
        error_msg = f"Hiba az AI elemzés során: {str(e)}"
        logger.error(error_msg)
        state["tool_errors"].append({
            "stage": "perform_ai_analysis",
            "error": error_msg,
            "timestamp": datetime.now().isoformat()
        })
        state["current_stage"] = "error"
        add_messages(state, [
            {
                "role": "system",
                "content": error_msg
            }
        ])
    
    return state

async def generate_documentation(state: DocGenState) -> DocGenState:
    """
    Dokumentáció generálás az összegyűjtött adatok alapján.
    """
    logger.info("📝 Dokumentáció generálása...")
    try:
        output_dir = state["output_paths"]["output_dir"]
        os.makedirs(output_dir, exist_ok=True)
        
        doc_generator = DocumentationGenerator(output_dir)
        project_data = state["project_data"]
        file_analysis = state["file_analysis"]
        ai_results = state["ai_results"]
        
        # README.md generálása
        readme_path = await doc_generator.generate_readme(project_data, ai_results)
        
        # PROJECT_ANALYSIS.md generálása
        analysis_path = await doc_generator.generate_project_analysis(project_data, file_analysis, ai_results)
        
        # Frissítjük az állapotot
        state["output_paths"]["readme_path"] = readme_path
        state["output_paths"]["analysis_path"] = analysis_path
        state["current_stage"] = "documentation_generated"
        
        # Hozzáadunk egy üzenetet a munkafolyamat naplózásához
        add_messages(state, [
            {
                "role": "system",
                "content": f"Dokumentáció generálás sikeres. Létrehozott fájlok:\n- README.md: {readme_path}\n- PROJECT_ANALYSIS.md: {analysis_path}"
            }
        ])
    except Exception as e:
        error_msg = f"Hiba a dokumentáció generálása során: {str(e)}"
        logger.error(error_msg)
        state["tool_errors"].append({
            "stage": "generate_documentation",
            "error": error_msg,
            "timestamp": datetime.now().isoformat()
        })
        state["current_stage"] = "error"
        add_messages(state, [
            {
                "role": "system",
                "content": error_msg
            }
        ])
    
    return state

async def update_project_status(state: DocGenState) -> DocGenState:
    """
    Frissíti a PROJECT_STATUS.md fájlt a folyamat állapotával.
    """
    logger.info("📊 PROJECT_STATUS.md frissítése...")
    try:
        project_path = state["project_data"]["project_path"]
        status_path = os.path.join(project_path, "PROJECT_STATUS.md")
        
        # Állapot üzenet összeállítása a munkafolyamat eredménye alapján
        if state["current_stage"] == "documentation_generated":
            status = {
                "current_task": "Automatikus projekt dokumentáció generálás (LangGraph verzió)",
                "last_modification": "Dokumentáció generálás befejezve, README.md és PROJECT_ANALYSIS.md elkészült",
                "next_step": "A generált dokumentáció ellenőrzése és finomhangolása",
                "new_files": {
                    "auto_project_doc_langgraph.py": "✅ [Új]",
                    "outputs/README.md": "📝 [Generált]",
                    "outputs/PROJECT_ANALYSIS.md": "📝 [Generált]"
                }
            }
        else:
            # Hiba esetén
            errors = state["tool_errors"]
            last_error = errors[-1]["error"] if errors else "Ismeretlen hiba"
            status = {
                "current_task": "Automatikus projekt dokumentáció generálás (LangGraph verzió)",
                "last_modification": f"Dokumentáció generálás sikertelen: {last_error}",
                "next_step": "A hiba javítása és újrapróbálkozás",
                "new_files": {
                    "auto_project_doc_langgraph.py": "🔄 [Implementálás alatt]"
                }
            }
        
        # Frissítjük a státusz fájlt
        await update_status(status_path, status)
        
        # Frissítjük az állapotot
        state["current_stage"] = "status_updated" if state["current_stage"] == "documentation_generated" else "error_reported"
        
        # Hozzáadunk egy üzenetet a munkafolyamat naplózásához
        add_messages(state, [
            {
                "role": "system",
                "content": f"PROJECT_STATUS.md frissítve: {status['last_modification']}"
            }
        ])
    except Exception as e:
        error_msg = f"Hiba a PROJECT_STATUS.md frissítése során: {str(e)}"
        logger.error(error_msg)
        state["tool_errors"].append({
            "stage": "update_project_status",
            "error": error_msg,
            "timestamp": datetime.now().isoformat()
        })
        state["current_stage"] = "error"
        add_messages(state, [
            {
                "role": "system",
                "content": error_msg
            }
        ])
    
    return state

# Munkafolyamat kondícióinak definíciója
def should_continue_on_error(state: DocGenState) -> str:
    """
    Eldönti, hogy folytatható-e a munkafolyamat hiba esetén.
    """
    if state["current_stage"] == "error":
        return "stop"
    return "continue"

def get_next_step(state: DocGenState) -> str:
    """
    Meghatározza a következő lépést a munkafolyamatban.
    """
    current_stage = state["current_stage"]
    
    if current_stage == "project_structure_analyzed":
        return "analyze_files"
    elif current_stage == "files_analyzed":
        return "ai_analysis"
    elif current_stage == "ai_analysis_completed":
        return "generate_docs"
    elif current_stage == "documentation_generated":
        return "update_status"
    elif current_stage == "status_updated":
        # Ha befejeztük a munkát, újra kezdjük a folyamatot (de ez nem fog futni, mert a main() függvény kilép)
        return "analyze_project"
    else:
        # Alapértelmezett érték, csak hogy mindig legyen valid visszatérési érték
        return "analyze_project"

# LangGraph munkafolyamat létrehozása
async def create_docgen_workflow(project_path: str) -> StateGraph:
    """
    Létrehozza a dokumentáció generáló LangGraph munkafolyamatot.
    """
    # Az eszközök regisztrálása
    await register_all_tools()
    
    # Létrehozzuk a munkafolyamat gráfot
    workflow = StateGraph(DocGenState)
    
    # Csomópontok hozzáadása a munkafolyamathoz
    workflow.add_node("analyze_project", analyze_project_structure)
    workflow.add_node("analyze_files", analyze_python_files)
    workflow.add_node("ai_analysis", perform_ai_analysis)
    workflow.add_node("generate_docs", generate_documentation)
    workflow.add_node("update_status", update_project_status)
    
    # Élek meghatározása a csomópontok között
    workflow.add_edge("analyze_project", "analyze_files")
    workflow.add_edge("analyze_files", "ai_analysis")
    workflow.add_edge("ai_analysis", "generate_docs")
    workflow.add_edge("generate_docs", "update_status")
      # Dinamikus elágazások kezelése
    workflow.add_conditional_edges(
        "update_status",
        get_next_step,
        {
            "update_status": "update_status",  # Ha még nem fejeződött be
            "end": "analyze_project"  # Helyett egy létező csomópontot használunk
        }
    )
      # Hibakezelés minden csomópontban
    workflow.add_conditional_edges(
        "analyze_project",
        should_continue_on_error,
        {
            "continue": "analyze_files",
            "stop": "update_status"  # Hiba esetén frissítsük a státuszt
        }
    )
    
    workflow.add_conditional_edges(
        "analyze_files",
        should_continue_on_error,
        {
            "continue": "ai_analysis",
            "stop": "update_status"  # Hiba esetén frissítsük a státuszt
        }
    )
    
    workflow.add_conditional_edges(
        "ai_analysis",
        should_continue_on_error,
        {
            "continue": "generate_docs",
            "stop": "update_status"  # Hiba esetén frissítsük a státuszt
        }
    )
    
    workflow.add_conditional_edges(
        "generate_docs",
        should_continue_on_error,
        {
            "continue": "update_status",
            "stop": "update_status"  # Hiba esetén is frissítsük a státuszt
        }
    )
    
    # Definiáljuk a kezdőcsomópontot
    workflow.set_entry_point("analyze_project")
    
    return workflow

# Fő futtatási függvény
async def main():
    """
    Fő belépési pont a LangGraph alapú dokumentáció generáló futtatásához.
    """
    logger.info("=== Project-S Automatikus Dokumentáció Generáló (LangGraph verzió) ===")
    
    # Projekt könyvtár beállítása
    project_path = str(Path(__file__).parent)
    
    try:
        # Frissítjük a PROJECT_STATUS.md-t az indulás jelzésére
        await update_status(
            os.path.join(project_path, "PROJECT_STATUS.md"),
            {
                "current_task": "Automatikus projekt dokumentáció generálás (LangGraph verzió)",
                "last_modification": "Dokumentáció generáló LangGraph workflow inicializálása",
                "next_step": "Workflow futtatása és dokumentáció generálása",
                "new_files": {
                    "auto_project_doc_langgraph.py": "✅ [Új]"
                }
            }
        )
        
        # Inicializáljuk az állapotot
        state = init_docgen_state(project_path)
        
        # Létrehozzuk a munkafolyamatot
        workflow = await create_docgen_workflow(project_path)
        
        # Egyszerű- nem LangGraph-kompatibilis - állapot használata a teszteléshez
        simple_state = {
            "project_path": project_path,
            "output_dir": os.path.join(project_path, "outputs")
        }
        
        # Közvetlenül futtatjuk a funkciókat tesztelés céljából
        logger.info("🚀 Munkafolyamat futtatása közvetlen módon (nem LangGraph-fal)...")
        
        # Projekt struktúra elemzése
        analyzer = ProjectStructureAnalyzer()
        project_data = await analyzer.get_project_structure(project_path)
        
        # Python fájlok részletes elemzése
        file_analysis = await analyzer.analyze_python_files(project_data["python_files"])
        
        # AI elemzések
        ai_integration = AIModelIntegration()
        context = {"project_data": project_data, "file_analysis": file_analysis}
        
        ai_results = {}
        
        # GPT-4 elemzés
        ai_results["architecture"] = await ai_integration.analyze_with_model(
            model="gpt-4", 
            prompt="Elemezd a projekt architektúráját és azonosítsd a fő design pattern-eket.",
            context=context
        )
        
        ai_results["code_structure"] = await ai_integration.analyze_with_model(
            model="gpt-4", 
            prompt="Elemezd a projekt kód struktúráját és fő komponenseit.",
            context=context
        )
        
        # Claude elemzés
        ai_results["best_practices"] = await ai_integration.analyze_with_model(
            model="claude-sonnet", 
            prompt="Értékeld a kód minőségét és ajánlj best practices technikákat.",
            context=context
        )
        
        ai_results["security"] = await ai_integration.analyze_with_model(
            model="claude-sonnet", 
            prompt="Értékeld a projekt biztonsági aspektusait.",
            context=context
        )
        
        # Dokumentáció generálása
        doc_generator = DocumentationGenerator(os.path.join(project_path, "outputs"))
        readme_path = await doc_generator.generate_readme(project_data, ai_results)
        analysis_path = await doc_generator.generate_project_analysis(project_data, file_analysis, ai_results)
        
        # Frissítsük a PROJECT_STATUS.md-t a befejezés jelzésére
        await update_status(
            os.path.join(project_path, "PROJECT_STATUS.md"),
            {
                "current_task": "Automatikus projekt dokumentáció generálás (LangGraph verzió)",
                "last_modification": "Dokumentáció generálás befejezve (közvetlen módban, LangGraph nélkül)",
                "next_step": "A generált dokumentáció ellenőrzése és LangGraph integráció debuggolása",
                "new_files": {
                    "auto_project_doc_langgraph.py": "🔄 [Hibaelhárítás alatt]",
                    "outputs/README.md": "📝 [Generált]",
                    "outputs/PROJECT_ANALYSIS.md": "📝 [Generált]"
                }
            }
        )
        
        logger.info("🎉 Dokumentáció generálás sikeres!")
        logger.info(f"📄 README.md: {readme_path}")
        logger.info(f"📄 PROJECT_ANALYSIS.md: {analysis_path}")
        
        return {
            "success": True,
            "readme_path": readme_path,
            "analysis_path": analysis_path,
            "note": "Futtatva közvetlen módban, nem LangGraph munkafolyamattal a kompatibilitási problémák miatt."
        }
        
        # Megjegyzés: A LangGraph workflow futtatása jelenleg deaktiválva van kompatibilitási problémák miatt
        # Az alábbi kód visszaállítható, ha a LangGraph integráció problémái megoldódnak
        """
        # Konfigurálható verzióban készítjük el a munkafolyamatot
        configurable_workflow = workflow.compile()
        
        # Futtatjuk a munkafolyamatot
        logger.info("🚀 Munkafolyamat futtatása...")
        final_state = await configurable_workflow.ainvoke(state)
        
        # Eredmény feldolgozása
        current_stage = final_state["current_stage"]
        tool_errors = final_state["tool_errors"]
        
        if current_stage == "status_updated":
            logger.info("🎉 Dokumentáció generálás sikeres!")
            logger.info(f"📄 README.md: {final_state['output_paths']['readme_path']}")
            logger.info(f"📄 PROJECT_ANALYSIS.md: {final_state['output_paths']['analysis_path']}")
            return {
                "success": True,
                "readme_path": final_state['output_paths']['readme_path'],
                "analysis_path": final_state['output_paths']['analysis_path']
            }
        else:
            logger.error(f"💥 Dokumentáció generálás sikertelen: {current_stage}")
            for error in tool_errors:
                logger.error(f"- Hiba a '{error['stage']}' lépésnél: {error['error']}")
            return {
                "success": False,
                "error": tool_errors[-1]["error"] if tool_errors else "Ismeretlen hiba"
            }
        """
        
    except Exception as e:
        logger.error(f"Hiba a dokumentáció generáló futtatása közben: {str(e)}")
        traceback.print_exc()
        
        # Frissítjük a PROJECT_STATUS.md-t a hiba jelzésére
        await update_status(
            os.path.join(project_path, "PROJECT_STATUS.md"),
            {
                "current_task": "Automatikus projekt dokumentáció generálás",
                "last_modification": f"Hibaelhárítás: {str(e)}",
                "next_step": "A hiba javítása és újrapróbálkozás"
            }
        )
        
        return {
            "success": False,
            "error": str(e)
        }

if __name__ == "__main__":
    result = asyncio.run(main())
    
    print("\n=== Automatikus Dokumentáció Generáló (LangGraph) Eredmény ===")
    if result.get("success", False):
        print("✅ A dokumentáció generálás sikeresen befejezve!")
        print(f"📊 Létrehozott fájlok:")
        print(f"  - {result.get('readme_path')}")
        print(f"  - {result.get('analysis_path')}")
    else:
        print(f"❌ Hiba: {result.get('error', 'Ismeretlen hiba')}")
