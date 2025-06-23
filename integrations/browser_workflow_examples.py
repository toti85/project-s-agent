"""
Browser Automation Workflow Examples for Project-S
-----------------------------------------------
Ez a modul példa munkafolyamatokat biztosít a Project-S böngésző automatizáció
használatához LangGraph keretrendszerben.
"""
import logging
from typing import Dict, Any, List, Optional, Union, TypedDict
import time

from langgraph.graph import StateGraph
from langgraph.prebuilt import ToolNode

from integrations.browser_state import BrowserAutomationState, BrowserStateManager
from integrations.browser_automation_tool import BrowserAutomationTool
from integrations.browser_commands import BrowserCommands
from integrations.browser_search_tools import BrowserSearchTools
from integrations.tool_manager import tool_manager

logger = logging.getLogger(__name__)

# Inicializáljuk az eszközöket
state_manager = BrowserStateManager()
browser_tools = BrowserAutomationTool(state_manager)
browser_commands = BrowserCommands(state_manager)
browser_search_tools = BrowserSearchTools(state_manager)


def create_web_information_extraction_workflow(workflow_id: str) -> StateGraph:
    """
    Létrehoz egy LangGraph munkafolyamatot webes információgyűjtéshez.
    
    Ez a munkafolyamat a következő lépésekből áll:
    1. Böngésző inicializálása
    2. Navigálás a megadott URL-re
    3. Tartalom kinyerése
    4. Specifikus adatok kinyerése (pl. táblázatok)
    5. Böngésző bezárása
    
    Args:
        workflow_id: A munkafolyamat egyedi azonosítója
        
    Returns:
        StateGraph: A konfigurált LangGraph munkafolyamat
    """
    # Kezdeti állapot létrehozása
    initial_state = state_manager.create_initial_state(workflow_id, "chrome")
    
    # Tool Node-ok létrehozása a böngésző műveletekhez
    initialize_node = ToolNode("initialize_browser")
    navigate_node = ToolNode("navigate_to_url") 
    extract_text_node = ToolNode("extract_page_content")
    extract_tables_node = ToolNode("extract_page_content")
    close_node = ToolNode("close_browser")
    
    # Gráf létrehozása
    graph = StateGraph()
    
    # Csomópontok hozzáadása
    graph.add_node("initialize", initialize_node)
    graph.add_node("navigate", navigate_node)
    graph.add_node("extract_text", extract_text_node)
    graph.add_node("extract_tables", extract_tables_node)
    graph.add_node("close", close_node)
    
    # Élek definiálása
    graph.add_edge("initialize", "navigate")
    graph.add_edge("navigate", "extract_text")
    graph.add_edge("extract_text", "extract_tables")
    graph.add_edge("extract_tables", "close")
    
    # Belépési pont beállítása
    graph.set_entry_point("initialize")
    
    return graph


def create_google_search_workflow(workflow_id: str) -> StateGraph:
    """
    Létrehoz egy LangGraph munkafolyamatot Google kereséshez.
    
    Ez a munkafolyamat a következő lépésekből áll:
    1. Böngésző inicializálása
    2. Google keresés végrehajtása
    3. Keresési eredmények kinyerése
    4. Első eredményre navigálás
    5. Tartalom kinyerése
    6. Böngésző bezárása
    
    Args:
        workflow_id: A munkafolyamat egyedi azonosítója
        
    Returns:
        StateGraph: A konfigurált LangGraph munkafolyamat
    """
    # Kezdeti állapot létrehozása
    initial_state = state_manager.create_initial_state(workflow_id, "chrome")
    
    # Tool Node-ok létrehozása a böngésző műveletekhez
    initialize_node = ToolNode("initialize_browser")
    search_node = ToolNode("perform_google_search")
    click_result_node = ToolNode("click_element")
    extract_content_node = ToolNode("extract_page_content")
    close_node = ToolNode("close_browser")
    
    # Gráf létrehozása
    graph = StateGraph()
    
    # Csomópontok hozzáadása
    graph.add_node("initialize", initialize_node)
    graph.add_node("search", search_node)
    graph.add_node("click_result", click_result_node)
    graph.add_node("extract_content", extract_content_node)
    graph.add_node("close", close_node)
    
    # Élek definiálása
    graph.add_edge("initialize", "search")
    graph.add_edge("search", "click_result")
    graph.add_edge("click_result", "extract_content")
    graph.add_edge("extract_content", "close")
    
    # Belépési pont beállítása
    graph.set_entry_point("initialize")
    
    return graph


def create_form_fill_workflow(workflow_id: str) -> StateGraph:
    """
    Létrehoz egy LangGraph munkafolyamatot űrlap kitöltéshez.
    
    Ez a munkafolyamat a következő lépésekből áll:
    1. Böngésző inicializálása
    2. Navigálás az űrlapot tartalmazó oldalra
    3. Űrlapmezők kitöltése
    4. Űrlap elküldése
    5. Visszaigazoló oldal ellenőrzése
    6. Böngésző bezárása
    
    Args:
        workflow_id: A munkafolyamat egyedi azonosítója
        
    Returns:
        StateGraph: A konfigurált LangGraph munkafolyamat
    """
    # Kezdeti állapot létrehozása
    initial_state = state_manager.create_initial_state(workflow_id, "chrome")
    
    # Tool Node-ok létrehozása az űrlapkitöltéshez
    initialize_node = ToolNode("initialize_browser")
    navigate_node = ToolNode("navigate_to_url")
    fill_field1_node = ToolNode("fill_form_field")
    fill_field2_node = ToolNode("fill_form_field")  
    click_submit_node = ToolNode("click_element")
    verify_success_node = ToolNode("extract_page_content")
    close_node = ToolNode("close_browser")
    
    # Gráf létrehozása
    graph = StateGraph()
    
    # Csomópontok hozzáadása
    graph.add_node("initialize", initialize_node)
    graph.add_node("navigate", navigate_node)
    graph.add_node("fill_field1", fill_field1_node)
    graph.add_node("fill_field2", fill_field2_node)
    graph.add_node("click_submit", click_submit_node)
    graph.add_node("verify_success", verify_success_node)
    graph.add_node("close", close_node)
    
    # Élek definiálása (szekvenciális munkafolyamat)
    graph.add_edge("initialize", "navigate")
    graph.add_edge("navigate", "fill_field1")
    graph.add_edge("fill_field1", "fill_field2")
    graph.add_edge("fill_field2", "click_submit")
    graph.add_edge("click_submit", "verify_success")
    graph.add_edge("verify_success", "close")
    
    # Belépési pont beállítása
    graph.set_entry_point("initialize")
    
    return graph


def browser_workflow_with_error_handling(workflow_id: str) -> StateGraph:
    """
    Létrehoz egy fejlett hibakezeléssel ellátott LangGraph munkafolyamatot.
    
    A munkafolyamat dinamikus útvonalakkal rendelkezik, amelyek a műveletek 
    sikerességétől függően változnak.
    
    Args:
        workflow_id: A munkafolyamat egyedi azonosítója
        
    Returns:
        StateGraph: A konfigurált LangGraph munkafolyamat hibakezeléssel
    """
    # Kezdeti állapot létrehozása
    initial_state = state_manager.create_initial_state(workflow_id, "chrome")
    
    # Tool Node-ok létrehozása
    initialize_node = ToolNode("initialize_browser")
    navigate_node = ToolNode("navigate_to_url")
    extract_node = ToolNode("extract_page_content")
    retry_node = ToolNode("navigate_to_url")  # Újrapróbálkozási node
    close_node = ToolNode("close_browser")
    
    # Gráf létrehozása
    graph = StateGraph()
    
    # Csomópontok hozzáadása
    graph.add_node("initialize", initialize_node)
    graph.add_node("navigate", navigate_node)
    graph.add_node("extract", extract_node)
    graph.add_node("retry", retry_node)
    graph.add_node("close", close_node)
    
    # Feltételes elágazás definiálása - siker vagy hiba
    def route_after_navigate(state):
        # Ellenőrizzük a hibaállapotot
        if state.get("error_state", False):
            retry_count = state.get("retry_count", 0)
            if retry_count < 3:  # Maximum 3 újrapróbálkozás
                return "retry"
            else:
                return "close"  # Feladjuk és bezárjuk
        else:
            return "extract"  # Sikeres volt, folytatjuk
    
    # Élek definiálása feltételes átmenetekkel
    graph.add_edge("initialize", "navigate")
    graph.add_conditional_edges("navigate", route_after_navigate)
    graph.add_edge("extract", "close")
    graph.add_edge("retry", "navigate")
    
    # Belépési pont beállítása
    graph.set_entry_point("initialize")
    
    return graph


def execute_workflow_example():
    """
    Példa egy böngésző automatizációs munkafolyamat végrehajtására.
    """
    # Workflow ID generálása
    workflow_id = f"browser_workflow_{int(time.time())}"
    
    # Információkinyerési munkafolyamat létrehozása
    graph = create_web_information_extraction_workflow(workflow_id)
    
    # Munkafolyamat konfigurálása induláshoz
    config = {
        "initialize_browser": {
            "state": state_manager.create_initial_state(workflow_id)
        },
        "navigate_to_url": {
            "url": "https://www.wikipedia.org",
            "wait_for_load": True
        },
        "extract_page_content": [
            {"content_type": "text"},  # Az extract_text_node-hoz
            {"content_type": "tables"}  # Az extract_tables_node-hoz
        ]
    }
    
    # A munkafolyamat végrehajtása itt történne
    # Megjegyzés: A megfelelő LangGraph API felhasználásával kell meghívni a munkafolyamatot
    
    # Példa kimenet
    logger.info(f"Munkafolyamat létrehozva: {workflow_id}")
    logger.info("A munkafolyamat csomópontjai: initialize -> navigate -> extract_text -> extract_tables -> close")


# Munkafolyamat példák elérhetővé tétele
workflows = {
    "info_extraction": create_web_information_extraction_workflow,
    "google_search": create_google_search_workflow,
    "form_fill": create_form_fill_workflow,
    "error_handling": browser_workflow_with_error_handling
}
"""
