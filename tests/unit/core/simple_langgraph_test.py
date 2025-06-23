#!/usr/bin/env python
"""
Egyszerű LangGraph teszt
------------------------
Ez egy önálló teszt, ami csak a LangGraph könyvtárat használja, 
és független a Project-S belső komponenseitől.
"""
import os
import sys
import asyncio
from typing import Dict, Any, TypedDict, List

try:
    from langgraph.graph import StateGraph
    LANGGRAPH_AVAILABLE = True
    print("LangGraph könyvtár elérhető")
except ImportError:
    LANGGRAPH_AVAILABLE = False
    print("LangGraph könyvtár NEM elérhető - telepítse a következő paranccsal: pip install langgraph")
    sys.exit(1)

class SimpleState(TypedDict):
    """Egyszerű állapot definíció"""
    count: int
    messages: List[str]

def add_one(state: SimpleState) -> SimpleState:
    """Növeli a számlálót eggyel"""
    print(f"Számláló növelése: {state['count']} -> {state['count'] + 1}")
    state["count"] += 1
    state["messages"].append(f"Számláló növelve: {state['count']}")
    return state

def check_done(state: SimpleState) -> str:
    """Ellenőrzi, hogy elértük-e már a célt"""
    if state["count"] >= 5:
        print("Kész: A számláló elérte vagy meghaladta az 5-öt")
        return "done"
    print("Folytatás: A számláló még nem érte el az 5-öt")
    return "continue"

async def main():
    """Fő teszt funkció"""
    print("LangGraph alapvető működési teszt indítása...")
    
    # Létrehozunk egy egyszerű StateGraph-ot
    graph = StateGraph(SimpleState)
    
    # Hozzáadjuk a node-okat
    graph.add_node("increment", add_one)
    graph.add_node("done", lambda x: x)  # Ez a node csak továbbadja az állapotot
    
    # Definiáljuk az éleket
    graph.add_conditional_edges(
        "increment",
        check_done,
        {
            "continue": "increment",
            "done": "done"
        }
    )
    
    # Beállítjuk a belépési pontot
    graph.set_entry_point("increment")
    
    # Létrehozzuk a futtatható gráfot
    runnable = graph.compile()
    
    # Kezdeti állapot
    initial_state = {"count": 0, "messages": []}
    
    # Teszteljük a gráfot
    print("\n=== Gráf futtatása ===")
    try:
        for i, state in enumerate(runnable.stream(initial_state)):
            print(f"Lépés {i+1}: {state}")
            
        print("\n=== Gráf futtatása sikeres! ===")
        return True
    except Exception as e:
        print(f"\n=== HIBA a gráf futtatása közben: {e} ===")
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
