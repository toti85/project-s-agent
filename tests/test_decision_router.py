"""
Döntéshozatali Logika Tesztek
-----------------------------
Ez a modul a hibrid rendszer döntéshozatali logikáját teszteli LangGraph használatával.
"""
import pytest
import asyncio
from typing import Dict, Any, List
import os
import json
import time
import uuid

from langgraph.graph import StateGraph

from core.event_bus import event_bus
from core.error_handler import error_handler
from integrations.langgraph_types import GraphState
from integrations.langgraph_integration import langgraph_integrator
from integrations.decision_router import decision_router
from integrations.advanced_decision_router import (
    advanced_decision_router,
    check_context_contains,
    route_by_model_capabilities,
    route_by_confidence
)
from integrations.cognitive_decision_integration import cognitive_decision_integration

# Teszt eseménykezelők
test_events = []

async def on_event_handler(event_data):
    """Általános eseménykezelő a tesztekhez."""
    test_events.append({
        "type": "event",
        "data": event_data,
        "timestamp": time.time()
    })

# Alapvető csomópont funkciók a teszteléshez
async def start_node(state: GraphState) -> GraphState:
    """Kezdő csomópont a munkafolyamathoz."""
    state["context"]["started_at"] = time.time()
    state["context"]["status"] = "running"
    return state

async def process_text_node(state: GraphState) -> GraphState:
    """Szövegfeldolgozó csomópont."""
    text = state["context"].get("input_data", "")
    state["context"]["processed_data"] = {
        "type": "text",
        "word_count": len(text.split()),
        "processed_text": text.upper()
    }
    return state

async def process_code_node(state: GraphState) -> GraphState:
    """Kódfeldolgozó csomópont."""
    code = state["context"].get("input_data", "")
    state["context"]["processed_data"] = {
        "type": "code",
        "line_count": len(code.splitlines()),
        "language": "python" if "def " in code else "unknown"
    }
    return state

async def quality_check_node(state: GraphState) -> GraphState:
    """Minőségellenőrző csomópont."""
    processed_data = state["context"].get("processed_data", {})
    data_type = processed_data.get("type", "unknown")
    
    # Minőségi pontszám számítása
    if data_type == "text":
        word_count = processed_data.get("word_count", 0)
        quality_score = min(100, word_count * 5)
    elif data_type == "code":
        line_count = processed_data.get("line_count", 0)
        quality_score = min(100, line_count * 10)
    else:
        quality_score = 0
    
    state["context"]["quality_check"] = {
        "score": quality_score,
        "passed": quality_score >= 50,
        "timestamp": time.time()
    }
    
    state["context"]["quality_passed"] = quality_score >= 50
    return state

async def enhance_content_node(state: GraphState) -> GraphState:
    """Tartalom javítási csomópont."""
    processed_data = state["context"].get("processed_data", {})
    data_type = processed_data.get("type", "unknown")
    
    if data_type == "text":
        processed_text = processed_data.get("processed_text", "")
        enhanced_text = processed_text + " [ENHANCED]"
        state["context"]["processed_data"]["processed_text"] = enhanced_text
        state["context"]["processed_data"]["enhanced"] = True
    elif data_type == "code":
        state["context"]["processed_data"]["enhanced"] = True
        state["context"]["processed_data"]["comments_added"] = 5
    
    state["context"]["quality_check"]["score"] += 30
    state["context"]["quality_check"]["passed"] = True
    state["context"]["quality_passed"] = True
    
    return state

async def final_node(state: GraphState) -> GraphState:
    """Befejező csomópont."""
    start_time = state["context"].get("started_at", 0)
    processing_time = time.time() - start_time
    
    state["context"]["final_result"] = {
        "input_type": state["context"].get("input_type"),
        "processed_data": state["context"].get("processed_data"),
        "quality_check": state["context"].get("quality_check"),
        "processing_time_seconds": processing_time,
        "workflow_id": state["context"].get("graph_id")
    }
    
    state["context"]["status"] = "completed"
    return state

# Döntési kritériumok
def input_type_router(state: GraphState) -> str:
    """Irányítás a bemenet típusa alapján."""
    input_type = state["context"].get("input_type", "").lower()
    
    if input_type == "code":
        return "code"
    else:
        return "text"

def quality_check_router(state: GraphState) -> str:
    """Irányítás a minőségellenőrzés eredménye alapján."""
    quality_passed = state["context"].get("quality_passed", False)
    return "passed" if quality_passed else "failed"


@pytest.mark.asyncio
class TestDecisionRouter:
    """Döntéshozatali router tesztek."""
    
    async def setup_method(self):
        """Tesztmódszer előkészítése."""
        global test_events
        test_events = []
        
        # Eseménykezelők regisztrálása
        event_bus.subscribe("workflow.started", on_event_handler)
        event_bus.subscribe("workflow.node.entered", on_event_handler)
        event_bus.subscribe("workflow.decision.made", on_event_handler)
        event_bus.subscribe("workflow.completed", on_event_handler)

    async def teardown_method(self):
        """Tisztítás a teszt után."""
        # Eseménykezelők eltávolítása
        event_bus.unsubscribe("workflow.started", on_event_handler)
        event_bus.unsubscribe("workflow.node.entered", on_event_handler)
        event_bus.unsubscribe("workflow.decision.made", on_event_handler)
        event_bus.unsubscribe("workflow.completed", on_event_handler)
    
    async def create_test_workflow(self):
        """Teszt munkafolyamat létrehozása döntési routinggal."""
        # Új munkafolyamat gráf létrehozása
        graph = StateGraph(GraphState)
        
        # Csomópontok hozzáadása
        graph.add_node("start", start_node)
        graph.add_node("process_text", process_text_node)
        graph.add_node("process_code", process_code_node)
        graph.add_node("quality_check", quality_check_node)
        graph.add_node("enhance_content", enhance_content_node)
        graph.add_node("finalize", final_node)
        
        # Döntési csomópontok hozzáadása a decision router segítségével
        decision_router.add_decision_node(
            graph=graph,
            node_name="content_type_decision",
            criteria_func=input_type_router,
            destinations={
                "text": "process_text",
                "code": "process_code"
            },
            default="process_text"
        )
        
        decision_router.add_decision_node(
            graph=graph,
            node_name="quality_decision",
            criteria_func=quality_check_router,
            destinations={
                "passed": "finalize",
                "failed": "enhance_content"
            },
            default="enhance_content"
        )
        
        # Élek hozzáadása
        graph.add_edge("start", "content_type_decision")
        graph.add_edge("process_text", "quality_check")
        graph.add_edge("process_code", "quality_check")
        graph.add_edge("quality_check", "quality_decision")
        graph.add_edge("enhance_content", "finalize")
        
        # Belépési pont beállítása
        graph.set_entry_point("start")
        
        # Gráf fordítása
        compiled_graph = graph.compile()
        
        return compiled_graph
    
    async def create_advanced_test_workflow(self):
        """Fejlett teszt munkafolyamat létrehozása adaptív döntési routinggal."""
        # Új munkafolyamat gráf létrehozása
        graph = StateGraph(GraphState)
        
        # Alap csomópontok hozzáadása
        graph.add_node("start", start_node)
        graph.add_node("process_text", process_text_node)
        graph.add_node("process_code", process_code_node)
        graph.add_node("quality_check", quality_check_node)
        graph.add_node("enhance_content", enhance_content_node)
        graph.add_node("finalize", final_node)
        
        # Kritériumok regisztrálása
        advanced_decision_router.register_decision_criteria(
            "input_type_check", input_type_router
        )
        
        advanced_decision_router.register_decision_criteria(
            "quality_check", quality_check_router
        )
        
        # Adaptív döntési csomópont hozzáadása
        advanced_decision_router.add_adaptive_decision_node(
            graph=graph,
            node_name="content_type_decision",
            criteria_sources=[
                {"type": "function", "name": "input_type_check"},
                {"type": "path", "path": "context.input_type"}
            ],
            destinations={
                "text": "process_text",
                "code": "process_code"
            },
            fallback="process_text"
        )
        
        # Egyszerű döntési csomópont hozzáadása
        decision_router.add_decision_node(
            graph=graph,
            node_name="quality_decision",
            criteria_func=quality_check_router,
            destinations={
                "passed": "finalize",
                "failed": "enhance_content"
            },
            default="enhance_content"
        )
        
        # Élek hozzáadása
        graph.add_edge("start", "content_type_decision")
        graph.add_edge("process_text", "quality_check")
        graph.add_edge("process_code", "quality_check")
        graph.add_edge("quality_check", "quality_decision")
        graph.add_edge("enhance_content", "finalize")
        
        # Belépési pont beállítása
        graph.set_entry_point("start")
        
        # Gráf fordítása
        compiled_graph = graph.compile()
        
        return compiled_graph
    
    async def create_cognitive_test_workflow(self):
        """Teszt munkafolyamat létrehozása kognitív döntéshozatallal."""
        # Új munkafolyamat gráf létrehozása
        graph = StateGraph(GraphState)
        
        # Csomópontok hozzáadása
        graph.add_node("start", start_node)
        graph.add_node("process_text", process_text_node)
        graph.add_node("process_code", process_code_node)
        graph.add_node("quality_check", quality_check_node)
        graph.add_node("enhance_content", enhance_content_node)
        graph.add_node("finalize", final_node)
        
        # Kognitív döntési csomópont hozzáadása
        cognitive_decision_integration.add_cognitive_decision_node(
            graph=graph,
            node_name="content_type_decision",
            question="A bemeneti típus alapján milyen feldolgozást végezzünk? (text vagy code)",
            options={
                "text": "process_text",
                "code": "process_code"
            },
            context_keys=["input_type", "input_data"]
        )
        
        # Hibrid döntési csomópont hozzáadása
        cognitive_decision_integration.combine_with_advanced_router(
            graph=graph,
            node_name="quality_decision",
            question="A minőségellenőrzés alapján szükség van-e javításra?",
            decision_criteria=quality_check_router,
            options={
                "passed": "finalize",
                "failed": "enhance_content"
            },
            default_option="failed"
        )
        
        # Élek hozzáadása
        graph.add_edge("start", "content_type_decision")
        graph.add_edge("process_text", "quality_check")
        graph.add_edge("process_code", "quality_check")
        graph.add_edge("quality_check", "quality_decision")
        graph.add_edge("enhance_content", "finalize")
        
        # Belépési pont beállítása
        graph.set_entry_point("start")
        
        # Gráf fordítása
        compiled_graph = graph.compile()
        
        return compiled_graph
    
    async def run_workflow_with_input(self, workflow, input_type, input_data):
        """Munkafolyamat futtatása adott bemenettel."""
        # Kezdeti állapot létrehozása
        initial_state = {
            "messages": [],
            "context": {
                "input_type": input_type,
                "input_data": input_data,
                "graph_id": f"test_workflow_{int(time.time())}",
                "workflow_name": "Test Decision Routing Workflow"
            },
            "command_history": [],
            "status": "created",
            "current_task": None,
            "error_info": None,
            "retry_count": 0,
            "branch": None
        }
        
        # Workflow indítási esemény küldése
        await event_bus.publish("workflow.started", {
            "graph_id": initial_state["context"]["graph_id"],
            "workflow_name": initial_state["context"]["workflow_name"],
            "context": initial_state["context"]
        })
        
        # Munkafolyamat futtatása
        result = await workflow.ainvoke(initial_state)
        
        # Workflow befejezési esemény küldése
        await event_bus.publish("workflow.completed", {
            "graph_id": initial_state["context"]["graph_id"],
            "workflow_name": initial_state["context"]["workflow_name"],
            "completion_status": "completed",
            "final_context": result.get("context", {})
        })
        
        return result
    
    async def test_basic_decision_router(self):
        """Alap döntési router tesztelése."""
        # Munkafolyamat létrehozása
        workflow = await self.create_test_workflow()
        
        # Futtatás szöveges bemenettel
        text_result = await self.run_workflow_with_input(
            workflow, 
            input_type="text", 
            input_data="Ez egy tesztszöveg a döntési logika teszteléséhez."
        )
        
        # Ellenőrzés
        assert text_result["context"]["processed_data"]["type"] == "text"
        assert text_result["context"]["status"] == "completed"
        assert "workflow.decision.made" in [e["type"] for e in test_events]
        
        # Futtatás kód bemenettel
        code_result = await self.run_workflow_with_input(
            workflow, 
            input_type="code", 
            input_data="def test_func():\n    print('Hello')"
        )
        
        # Ellenőrzés
        assert code_result["context"]["processed_data"]["type"] == "code"
        assert code_result["context"]["status"] == "completed"
        
        # Döntéstörténet elemzése
        decision_history = decision_router.get_decision_history(
            code_result["context"]["graph_id"]
        )
        assert len(decision_history) > 0
    
    async def test_advanced_decision_router(self):
        """Fejlett döntési router tesztelése."""
        # Munkafolyamat létrehozása
        workflow = await self.create_advanced_test_workflow()
        
        # Futtatás szöveges bemenettel
        text_result = await self.run_workflow_with_input(
            workflow, 
            input_type="text", 
            input_data="Ez egy tesztszöveg a fejlett döntési logika teszteléséhez."
        )
        
        # Ellenőrzés
        assert text_result["context"]["processed_data"]["type"] == "text"
        assert text_result["context"]["status"] == "completed"
        
        # Futtatás rövid szöveges bemenettel, ami minőségi ellenőrzésen megbukik
        short_text_result = await self.run_workflow_with_input(
            workflow, 
            input_type="text", 
            input_data="Rövid szöveg"
        )
        
        # Ellenőrzés - javításnak kellett történnie
        assert short_text_result["context"]["processed_data"]["enhanced"] == True
        assert short_text_result["context"]["status"] == "completed"
        
        # Döntési minták elemzése
        patterns = advanced_decision_router.detect_decision_patterns(
            short_text_result["context"]["graph_id"]
        )
        assert "status" in patterns
    
    async def test_cognitive_decision_integration(self):
        """Kognitív döntési integráció tesztelése."""
        # Munkafolyamat létrehozása
        workflow = await self.create_cognitive_test_workflow()
        
        # Futtatás szöveges bemenettel
        text_result = await self.run_workflow_with_input(
            workflow, 
            input_type="text", 
            input_data="Ez egy tesztszöveg a kognitív döntési logika teszteléséhez."
        )
        
        # Ellenőrzés
        assert text_result["context"]["status"] == "completed"
        
        # Globális döntési trendek elemzése
        trends = advanced_decision_router.analyze_global_decision_trends()
        assert "total_decisions" in trends
        
        # Eseménynapló ellenőrzése
        decision_events = [e for e in test_events 
                        if e["type"] == "event" and "workflow.decision.made" in str(e["data"])]
        assert len(decision_events) > 0


if __name__ == "__main__":
    pytest.main(["-xvs", __file__])
