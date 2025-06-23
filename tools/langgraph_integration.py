"""
Project-S LangGraph Tool Integration
----------------------------------
Ez a modul biztosítja az eszközök (tool-ok) integrációját a LangGraph munkafolyamatokba.
Lehetővé teszi, hogy a Project-S eszközök natív módon használhatók legyenek
a LangGraph alapú AI ágens munkafolyamatokban.
"""

import logging
import asyncio
from typing import Dict, List, Any, Optional, Set, Callable, Union, TypedDict
import inspect
from pathlib import Path
import json
import uuid

# LangGraph importok
from langgraph.graph import StateGraph
from langgraph.prebuilt import ToolNode
try:
    from langgraph.graph.message import add_messages
except ImportError:
    add_messages = None

# Project-S importok
from tools.tool_interface import BaseTool
from tools.tool_registry import tool_registry
from core.event_bus import event_bus

# Használjuk a megosztott típusdefiníciókat a körkörös importálás elkerüléséhez
from tools.langgraph_types import GraphState, ToolState

logger = logging.getLogger(__name__)

# ToolState már importálva a langgraph_types.py fájlból
# A ToolState osztály dokumentációja:
# """
# A LangGraph állapot kiterjesztése eszköz-specifikus adatokkal.
# """
# Tartalmazza a következő mezőket:
# - messages: List[Dict[str, Any]]
# - tools: List[Dict[str, Any]]
# - tool_results: Dict[str, Any]]
# - tool_history: List[Dict[str, Any]]
# - tool_errors: List[Dict[str, Any]]

class ToolGraphIntegrator:
    """
    Az eszközök (tool-ok) integrációja LangGraph munkafolyamatokba.
    Biztosítja, hogy a Project-S eszközök használhatók legyenek
    a LangGraph alapú ágens munkafolyamatokban.
    """
    
    def __init__(self):
        """
        Inicializálja az integrátor objektumot.
        """
        self.registered_tools: Dict[str, BaseTool] = {}
        self.tool_instances: Dict[str, BaseTool] = {}
        self.tool_nodes: Dict[str, ToolNode] = {}
        
        # Események regisztrálása
        event_bus.subscribe("tool.executed", self._on_tool_executed)
        event_bus.subscribe("workflow.started", self._on_workflow_started)
        
        logger.info("LangGraph Tool Integrator inicializálva")
        
    async def load_tools(self) -> int:
        """
        Betölti az elérhető eszközöket a tool_registry-ből.
        
        Returns:
            int: A betöltött eszközök száma
        """
        # Eszközök betöltése a registry-ből
        try:
            # Előbb betöltjük az eszközöket a registry-be
            await tool_registry.load_tools()
            
            # Kategória szerint lekérjük az összes elérhető eszközt
            all_tools = tool_registry.list_tools()
            
            for tool_info in all_tools:
                tool_name = tool_info["name"]
                
                # Lekérjük az eszköz példányát
                tool = tool_registry.get_tool(tool_name)
                if tool:
                    self.registered_tools[tool_name] = tool
                    
            logger.info(f"Összesen {len(self.registered_tools)} eszköz betöltve a LangGraph integrációba")
            return len(self.registered_tools)
            
        except Exception as e:
            logger.error(f"Hiba történt az eszközök betöltése közben: {str(e)}")
            return 0
    
    def create_tool_node(self, tool_name: str) -> Optional[ToolNode]:
        """
        Létrehozza egy eszköz LangGraph csomópontját.
        
        Args:
            tool_name: Az eszköz neve
            
        Returns:
            Optional[ToolNode]: A létrehozott csomópont, vagy None hiba esetén
        """
        if tool_name not in self.registered_tools:
            logger.error(f"Az eszköz nem található: {tool_name}")
            return None
            
        tool = self.registered_tools[tool_name]
        
        # Eszköz információk kinyerése a dokumentációból és metaadatokból
        tool_info = tool.get_info()
        parameters = tool_info["parameters"]
        
        # Előkészítjük az eszköz hívásfüggvényét
        async def tool_execute_wrapper(state: Dict[str, Any], **kwargs) -> Dict[str, Any]:
            """
            Az eszközt hívó wrapper függvény a LangGraph számára.
            """
            try:
                # Az eszköz végrehajtása
                tool_instance = self.registered_tools[tool_name]
                result = await tool_registry.execute_tool(tool_name, **kwargs)
                
                # Az eredmény hozzáadása az állapothoz
                new_state = state.copy()
                
                # Tool eredmények tárolása
                if "tool_results" not in new_state:
                    new_state["tool_results"] = {}
                    
                # Az eredmény mentése
                new_state["tool_results"][tool_name] = result
                
                # Tool történet bővítése
                if "tool_history" not in new_state:
                    new_state["tool_history"] = []
                    
                # Hozzáadjuk a történethez
                new_state["tool_history"].append({
                    "tool": tool_name,
                    "params": kwargs,
                    "timestamp": asyncio.get_event_loop().time(),
                    "success": result.get("success", False)
                })
                
                # Ha van add_messages függvény, akkor a tool eredmény hozzáadása az üzenetekhez
                if add_messages and "messages" in new_state:
                    add_messages(
                        new_state,
                        [
                            {
                                "role": "tool",
                                "name": tool_name,
                                "content": json.dumps(result)
                            }
                        ]
                    )
                
                return new_state
                
            except Exception as e:
                logger.error(f"Hiba a tool_node végrehajtása közben ({tool_name}): {str(e)}")
                
                # Hibaállapot létrehozása
                new_state = state.copy()
                
                # Tool hibák tárolása
                if "tool_errors" not in new_state:
                    new_state["tool_errors"] = []
                    
                # A hiba hozzáadása
                new_state["tool_errors"].append({
                    "tool": tool_name,
                    "error": str(e),
                    "params": kwargs,
                    "timestamp": asyncio.get_event_loop().time()
                })
                
                # Ha van add_messages függvény, akkor a hiba hozzáadása az üzenetekhez
                if add_messages and "messages" in new_state:
                    add_messages(
                        new_state,
                        [
                            {
                                "role": "tool",
                                "name": tool_name,
                                "content": f"Hiba történt a végrehajtás során: {str(e)}"
                            }
                        ]
                    )
                
                return new_state
        
        # LangGraph ToolNode létrehozása
        try:
            # ToolNode létrehozása az eszköz adatai alapján
            tool_node = ToolNode(
                tool_execute_wrapper,
                name=tool_name, 
                description=tool_info["description"],
                # További adatok hozzáadása
                metadata={
                    "category": tool_info["category"],
                    "version": tool_info["version"],
                    "requires_permissions": tool_info["requires_permissions"],
                }
            )
            
            # Elmenetjük a létrehozott csomópontot
            self.tool_nodes[tool_name] = tool_node
            
            logger.debug(f"Tool node létrehozva: {tool_name}")
            return tool_node
            
        except Exception as e:
            logger.error(f"Hiba történt a Tool node létrehozása közben ({tool_name}): {str(e)}")
            return None
    
    def add_tools_to_graph(self, graph: StateGraph, tools: List[str]) -> bool:
        """
        Hozzáadja a megadott eszközöket egy LangGraph munkafolyamathoz.
        
        Args:
            graph: A LangGraph StateGraph objektum
            tools: Az eszközök listája, amiket hozzá kell adni
            
        Returns:
            bool: True, ha sikeres volt a hozzáadás
        """
        try:
            for tool_name in tools:
                # Ha még nem létezik a csomópont, akkor létrehozzuk
                if tool_name not in self.tool_nodes:
                    tool_node = self.create_tool_node(tool_name)
                    if not tool_node:
                        logger.error(f"Nem sikerült létrehozni a Tool node-ot: {tool_name}")
                        continue
                else:
                    tool_node = self.tool_nodes[tool_name]
                
                # Hozzáadjuk a csomópontot a munkafolyamathoz
                try:
                    # A csomópont nevére hivatkozunk, nem magára az objektumra
                    graph.add_node(tool_name, tool_node)
                    
                    # Hozzáadjuk az alapértelmezett éleket is
                    graph.add_conditional_edges(
                        "agent", # Feltételezzük, hogy létezik egy "agent" csomópont
                        # Ha az agent úgy dönt, hogy ezt az eszközt hívja meg
                        lambda state, tool=tool_name: state.get("next_tool") == tool,
                        {tool_name: "agent"} # Az eszköz után visszatérünk az agenthez
                    )
                    
                    logger.info(f"Tool node hozzáadva a munkafolyamathoz: {tool_name}")
                    
                except Exception as e:
                    logger.error(f"Hiba a csomópont hozzáadása közben a munkafolyamathoz ({tool_name}): {str(e)}")
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Hiba történt az eszközök hozzáadása közben a munkafolyamathoz: {str(e)}")
            return False
    
    def get_tools_as_langchain_format(self) -> List[Dict[str, Any]]:
        """
        Visszaadja az eszközök leírását a LangChain/LangGraph formátumban,
        ami közvetlenül használható az AI ágens számára.
        
        Returns:
            List[Dict[str, Any]]: Az eszközök listája LangChain formátumban
        """
        tools_list = []
        
        for tool_name, tool in self.registered_tools.items():
            tool_info = tool.get_info()
            
            # Paraméterek átalakítása LangChain formátummá
            parameters = {}
            properties = {}
            required = []
            
            for param_name, param_info in tool_info["parameters"].items():
                properties[param_name] = {
                    "type": param_info["type"],
                    "description": f"Parameter: {param_name}" 
                }
                
                # Alapértelmezett érték hozzáadása ha van
                if "default" in param_info:
                    properties[param_name]["default"] = param_info["default"]
                
                # Kötelező paraméterek kezelése
                if param_info["required"]:
                    required.append(param_name)
            
            # Paraméter séma összeállítása
            parameters = {
                "type": "object",
                "properties": properties,
                "required": required
            }
            
            # Eszköz információ összeállítása
            langchain_tool = {
                "name": tool_name,
                "description": tool_info["description"],
                "parameters": parameters
            }
            
            tools_list.append(langchain_tool)
        
        return tools_list
    
    async def _on_tool_executed(self, data: Dict[str, Any]) -> None:
        """
        Eszköz végrehajtás esemény kezelése.
        """
        tool_name = data.get("tool", "unknown")
        success = data.get("success", False)
        
        # Itt tovább integrálhatunk a LangGraph állapotkezeléssel
        
    async def _on_workflow_started(self, data: Dict[str, Any]) -> None:
        """
        Munkafolyamat indítás esemény kezelése.
        """
        workflow_id = data.get("workflow_id", "")
        
        # Itt inicializálhatjuk a szükséges eszközöket

# Singleton példány létrehozása
tool_graph_integrator = ToolGraphIntegrator()