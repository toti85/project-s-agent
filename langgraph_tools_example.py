"""
Project-S LangGraph Tool Integrációs Példa
---------------------------------------
Ez a modul bemutatja, hogyan lehet a Project-S eszközöket integrálni
a LangGraph munkafolyamatokba egy egyszerű példán keresztül.
"""

import asyncio
import logging
import os
import sys
from pathlib import Path
import json
from datetime import datetime

# Hozzáadjuk a projekt gyökérkönyvtárát a keresési útvonalhoz
project_root = Path(__file__).parent
if str(project_root) not in sys.path:
    sys.path.append(str(project_root))

# LangGraph importok
from langgraph.graph import StateGraph
from langgraph.prebuilt import ToolNode
from langgraph.graph.message import add_messages

# Project-S importok
from tools import tool_registry, register_all_tools
from tools.file_tools import FileSearchTool, FileReadTool, FileWriteTool
from tools.web_tools import WebPageFetchTool

# Definíáljuk a saját állapotunkat az integráció helyett
class ToolState(dict):
    """
    Egyszerű állapot a példához, hogy elkerüljük a körkörös importálást.
    """
    pass

# Konfiguráljuk a naplózást
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger("langgraph_tools_example")

class SimpleAIAgent:
    """Egyszerű AI ágens szimulációja a példához."""
    
    async def __call__(self, state):
        """
        Szimulálja az AI ágens viselkedését, amely kiválasztja a következő eszközt.
        Egyszerű példa célokra.
        
        Args:
            state: Az aktuális állapot
            
        Returns:
            Dict: Az új állapot
        """
        logger.info("AI ágens gondolkodik...")
        
        # Az aktuális lépés alapján válasszuk ki a következő eszközt
        step = state.get("current_step", 0)
        tasks = state.get("tasks", [])
        
        # Új állapot létrehozása
        new_state = state.copy()
        
        # Első lépés: konfig fájlok keresése
        if step == 0:
            new_state["next_tool"] = "FileSearchTool"
            new_state["tool_input"] = {
                "pattern": "**/*.{json,yaml,ini,conf}",
                "base_dir": str(Path(__file__).parent),
                "max_depth": 3
            }
            new_state["current_step"] = 1
            
            if "messages" in new_state:
                add_messages(
                    new_state,
                    [
                        {
                            "role": "assistant",
                            "content": "Most keresek konfigurációs fájlokat a projektben."
                        }
                    ]
                )
                
        # Második lépés: weboldal letöltése
        elif step == 1:
            # Elmentsük az előző eredményt a feladatokhoz
            if "tool_results" in state and "FileSearchTool" in state["tool_results"]:
                tasks.append({
                    "name": "Konfigurációs fájlok keresése",
                    "result": state["tool_results"]["FileSearchTool"]
                })
            
            new_state["next_tool"] = "WebPageFetchTool"
            new_state["tool_input"] = {
                "url": "https://python.org",
                "extract_text": True
            }
            new_state["current_step"] = 2
            new_state["tasks"] = tasks
            
            if "messages" in new_state:
                add_messages(
                    new_state,
                    [
                        {
                            "role": "assistant",
                            "content": "Most letöltöm a python.org weboldalt elemzésre."
                        }
                    ]
                )
                
        # Harmadik lépés: jelentés írása
        elif step == 2:
            # Elmentsük az előző eredményt a feladatokhoz
            if "tool_results" in state and "WebPageFetchTool" in state["tool_results"]:
                tasks.append({
                    "name": "Weboldal letöltése",
                    "result": {
                        "url": "https://python.org",
                        "content_length": len(state["tool_results"]["WebPageFetchTool"].get("text", ""))
                    }
                })
                
            # Jelentés készítése
            report_content = {
                "timestamp": datetime.now().isoformat(),
                "tasks_completed": tasks,
                "summary": "A munkafolyamat sikeresen végrehajtva"
            }
            
            new_state["next_tool"] = "FileWriteTool"
            new_state["tool_input"] = {
                "path": str(Path(__file__).parent / "outputs" / "langgraph_tool_report.json"),
                "content": json.dumps(report_content, indent=2),
                "create_dirs": True
            }
            new_state["current_step"] = 3
            new_state["tasks"] = tasks
            
            if "messages" in new_state:
                add_messages(
                    new_state,
                    [
                        {
                            "role": "assistant",
                            "content": "Most készítek egy jelentést az eredményekről."
                        }
                    ]
                )
                
        # Befejezés
        else:
            if "tool_results" in state and "FileWriteTool" in state["tool_results"]:
                tasks.append({
                    "name": "Jelentés írása",
                    "result": state["tool_results"]["FileWriteTool"]
                })
                
            new_state["tasks"] = tasks
            new_state["next_tool"] = "END"
            
            if "messages" in new_state:
                add_messages(
                    new_state,
                    [
                        {
                            "role": "assistant",
                            "content": "A munkafolyamat sikeresen végrehajtva. A jelentés elkészült."
                        }
                    ]
                )
        
        return new_state


async def run_example_workflow():
    """
    Létrehoz és futtat egy példa munkafolyamatot, amely bemutatja
    a Project-S eszközök és LangGraph integrációját.
    """
    logger.info("LangGraph - Project-S Tool integrációs példa indítása...")
    
    # Eszközök regisztrálása
    await register_all_tools()
    
    # LangGraph eszközintegrátor inicializálása
    await tool_graph_integrator.load_tools()
    
    # LangGraph munkafolyamat létrehozása
    workflow = StateGraph()
    
    # Ágens csomópont hozzáadása
    agent = SimpleAIAgent()
    workflow.add_node("agent", agent)
    
    # Eszközök hozzáadása a munkafolyamathoz
    tools_to_add = ["FileSearchTool", "FileReadTool", "FileWriteTool", "WebPageFetchTool"]
    tool_graph_integrator.add_tools_to_graph(workflow, tools_to_add)
    
    # Kezdeti és befejező élek hozzáadása
    workflow.set_entry_point("agent")
    workflow.add_edge("agent", "END", condition=lambda state: state.get("next_tool") == "END")
    
    # Munkafolyamat véglegesítése
    compiled_workflow = workflow.compile()
    
    # Kezdeti állapot létrehozása
    initial_state = {
        "messages": [
            {
                "role": "system",
                "content": "Te egy ágens vagy, amely különböző eszközöket használ feladatok végrehajtásához."
            },
            {
                "role": "user",
                "content": "Keress konfigurációs fájlokat, tölts le egy weboldalt, és készíts jelentést."
            }
        ],
        "current_step": 0,
        "tasks": [],
        "tool_results": {},
        "tool_history": []
    }
    
    # Munkafolyamat futtatása
    logger.info("Munkafolyamat futtatása...")
    result = await compiled_workflow.ainvoke(initial_state)
    
    # Eredmény kiértékelése
    logger.info("Munkafolyamat végrehajtva!")
    logger.info(f"Végrehajtott feladatok: {len(result.get('tasks', []))}")
    
    # Jelentés elérési útja
    report_path = Path(__file__).parent / "outputs" / "langgraph_tool_report.json"
    if report_path.exists():
        logger.info(f"A jelentés elkészült: {report_path}")
        
    return result


if __name__ == "__main__":
    result = asyncio.run(run_example_workflow())
    print("\n--- Munkafolyamat eredménye ---")
    
    if "tasks" in result:
        for i, task in enumerate(result["tasks"]):
            print(f"Feladat {i+1}: {task['name']}")
            print(f"  Eredmény: {'Sikeres' if task['result'].get('success', False) else 'Sikertelen'}")
        
        if "next_tool" in result and result["next_tool"] == "END":
            print("\nA munkafolyamat sikeresen befejeződött!")
            print(f"A jelentés elérhető: {Path(__file__).parent / 'outputs' / 'langgraph_tool_report.json'}")
        else:
            print("\nA munkafolyamat nem fejeződött be teljesen.")
            
    else:
        print("A munkafolyamat végrehajtása sikertelen volt.")
