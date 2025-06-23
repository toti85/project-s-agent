"""
Project-S LangGraph Minimális Integráció
---------------------------------------
Ez a fájl egy egyszerűsített LangGraph integrációt valósít meg
a Project-S rendszer minimális verziójához.
"""

import asyncio
import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

try:
    from langgraph.graph import StateGraph, END
    LANGGRAPH_AVAILABLE = True
except ImportError:
    logger.warning("LangGraph nem elérhető. Telepítsd: pip install langgraph")
    LANGGRAPH_AVAILABLE = False

# Egyszerű állapot típus
State = Dict[str, Any]

class MinimalLangGraphIntegration:
    """
    A LangGraph minimális integrációja a Project-S rendszerbe.
    """
    
    def __init__(self):
        """Inicializálja a minimális LangGraph integrációt."""
        self.graph = None
        if LANGGRAPH_AVAILABLE:
            self._setup_graph()
            logger.info("LangGraph minimális integráció inicializálva")
        else:
            logger.warning("LangGraph integráció nem elérhető")
    
    def _setup_graph(self):
        """
        Beállítja az egyszerű LangGraph munkafolyamatot.
        """
        # Állapotgráf létrehozása
        builder = StateGraph(State)
        
        # Synchronous functions for LangGraph 0.4.5
        def parse_input_sync(state: State) -> State:
            command = state.get("input", "")
            parsed_input = {
                "original_command": command,
                "tokens": command.split(),
                "command_type": "simple_command"
            }
            return {"input": state["input"], "parsed_input": parsed_input}
            
        def process_command_sync(state: State) -> State:
            parsed = state.get("parsed_input", {})
            command_type = parsed.get("command_type", "unknown")
            result = {
                "status": "processed",
                "command_type": command_type,
                "context": {"source": "minimal_langgraph"}
            }
            return {**state, "processed_result": result}
            
        def generate_response_sync(state: State) -> State:
            original_command = state.get("input", "")
            response = f"Feldolgozott parancs: '{original_command}' - Sikeres folyamatfeldolgozás a LangGraph-on keresztül."
            return {**state, "response": response}
        
        # Csomópontok hozzáadása (synchronous functions)
        builder.add_node("parse_input", parse_input_sync)
        builder.add_node("process_command", process_command_sync)
        builder.add_node("generate_response", generate_response_sync)
        
        # Élek hozzáadása
        builder.add_edge("parse_input", "process_command")
        builder.add_edge("process_command", "generate_response")
        builder.add_edge("generate_response", END)
        
        # Kezdő csomópont beállítása
        builder.set_entry_point("parse_input")
        
        # Gráf kompilálása
        self.graph = builder.compile()
        logger.debug("LangGraph munkafolyamat létrehozva")
    
    async def process_with_graph(self, command: str) -> str:
        """
        Egy parancs feldolgozása a LangGraph munkafolyamaton keresztül.
        
        Args:
            command: A feldolgozandó parancs
            
        Returns:
            str: A generált válasz
        """
        if not LANGGRAPH_AVAILABLE or not self.graph:
            return f"LangGraph nem elérhető. Parancs: {command}"
        
        try:
            # Kezdeti állapot létrehozása
            initial_state = {"input": command}
            
            # Futtatás az állapotgráfon - synchronous invoke használata
            # LangGraph 0.4.5 kompatibilis módon
            logger.info(f"LangGraph parancs feldolgozása: '{command}'")
            final_state = self.graph.invoke(initial_state)
            
            # Eredmény visszaadása
            return final_state.get("response", "Nincs válasz")
            
        except Exception as e:
            logger.error(f"Hiba a LangGraph folyamat során: {e}")
            return f"Hiba történt: {str(e)}"

# Singleton példány létrehozása
langgraph_minimal = MinimalLangGraphIntegration()
