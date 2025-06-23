"""
Browser Automation Test for Project-S
------------------------------------
Ez a modul a Project-S böngésző automatizációs eszközeinek tesztelésére szolgál.
Teszteli a böngésző automatizáció alapvető funkcióit a LangGraph integrációval együtt.
"""
import asyncio
import pytest
import logging
import time
import os
from typing import Dict, Any, List

from integrations.browser_state import BrowserAutomationState, BrowserStateManager
from integrations.browser_automation_tool import BrowserAutomationTool
from integrations.browser_commands import BrowserCommands
from integrations.browser_search_tools import BrowserSearchTools
from integrations.browser_workflow_examples import (
    create_web_information_extraction_workflow,
    create_google_search_workflow
)

# Logging beállítása
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@pytest.fixture
def state_manager():
    """Állapotkezelő fixture"""
    return BrowserStateManager("./test_browser_states")


@pytest.fixture
def workflow_id():
    """Teszt munkafolyamat ID generálása"""
    return f"test_workflow_{int(time.time())}"


@pytest.fixture
def initial_state(state_manager, workflow_id):
    """Kezdeti böngésző állapot"""
    return state_manager.create_initial_state(workflow_id)


@pytest.mark.asyncio
async def test_browser_initialization(state_manager, initial_state):
    """Böngésző inicializálás teszt"""
    browser_tool = BrowserAutomationTool(state_manager)
    
    # Inicializáljuk a böngészőt
    updated_state = browser_tool.initialize_driver(initial_state)
    
    # Ellenőrizzük az állapot frissülését
    assert updated_state["browser_active"] == True
    assert browser_tool.driver is not None
    
    # Zárjuk be a böngészőt
    browser_tool.close_driver(updated_state)


@pytest.mark.asyncio
async def test_browser_navigation(state_manager, initial_state):
    """Böngésző navigáció teszt"""
    browser_commands = BrowserCommands(state_manager)
    
    # Inicializáljuk a böngészőt
    state = browser_commands.initialize_driver(initial_state)
    
    # Navigáljunk egy tesztoldalra
    test_url = "https://www.example.com"
    state = await browser_commands.navigate_to_url(state, test_url)
    
    # Ellenőrizzük az állapot frissülését
    assert state["current_url"] == test_url
    assert "Example Domain" in state["page_title"]
    assert not state["error_state"]
    
    # Zárjuk be a böngészőt
    browser_commands.close_driver(state)


@pytest.mark.asyncio
async def test_form_interaction(state_manager, initial_state):
    """Űrlap interakció teszt"""
    browser_commands = BrowserCommands(state_manager)
    
    # Inicializáljuk a böngészőt
    state = browser_commands.initialize_driver(initial_state)
    
    # Navigáljunk egy tesztoldalra űrlappal
    test_url = "https://httpbin.org/forms/post"
    state = await browser_commands.navigate_to_url(state, test_url)
    
    # Töltsük ki az űrlapot
    state = await browser_commands.fill_form_field(state, "input[name='custname']", "Test User")
    state = await browser_commands.fill_form_field(state, "input[value='pizza']", "", selector_type="css")
    
    # Ellenőrizzük az űrlap adatokat az állapotban
    assert "Test User" in str(state["form_data"])
    
    # Küldjük el az űrlapot
    state = await browser_commands.click_element(state, "button[type='submit']")
    
    # Ellenőrizzük, hogy az oldal megváltozott
    assert "httpbin.org/post" in state["current_url"]
    
    # Zárjuk be a böngészőt
    browser_commands.close_driver(state)


@pytest.mark.asyncio
async def test_content_extraction(state_manager, initial_state):
    """Tartalom kinyerés teszt"""
    browser_search = BrowserSearchTools(state_manager)
    
    # Inicializáljuk a böngészőt
    state = browser_search.initialize_driver(initial_state)
    
    # Navigáljunk egy tesztoldalra
    test_url = "https://www.wikipedia.org"
    state = await browser_search.browser_commands.navigate_to_url(state, test_url)
    
    # Nyerjünk ki szöveges tartalmat
    state = await browser_search.extract_page_content(state, content_type="text")
    
    # Ellenőrizzük a kinyert adatokat
    assert "text" in state["extracted_data"]
    assert len(state["extracted_data"]["text"]) > 0
    assert "Wikipedia" in state["extracted_data"]["text"]
    
    # Nyerjük ki a linkeket
    state = await browser_search.extract_page_content(state, content_type="links")
    
    # Ellenőrizzük a linkeket
    assert "links" in state["extracted_data"]
    assert len(state["extracted_data"]["links"]) > 0
    
    # Zárjuk be a böngészőt
    browser_search.close_driver(state)


@pytest.mark.asyncio
async def test_google_search(state_manager, initial_state):
    """Google keresés teszt"""
    browser_search = BrowserSearchTools(state_manager)
    
    # Inicializáljuk a böngészőt
    state = browser_search.initialize_driver(initial_state)
    
    # Végezzünk Google keresést
    search_query = "LangGraph Python framework"
    state = await browser_search.perform_google_search(state, search_query, 3)
    
    # Ellenőrizzük a keresési eredményeket
    assert not state["error_state"]
    assert len(state["search_results"]) > 0
    assert "google.com" in state["current_url"]
    
    # Zárjuk be a böngészőt
    browser_search.close_driver(state)


@pytest.mark.asyncio
async def test_state_persistence(state_manager, workflow_id):
    """Állapot perzisztencia teszt"""
    # Hozzunk létre egy kezdeti állapotot
    initial_state = state_manager.create_initial_state(workflow_id)
    
    # Frissítsük az állapotot néhány adattal
    test_data = {
        "current_url": "https://test.com",
        "page_title": "Test Page",
        "extracted_data": {"test_key": "test_value"},
    }
    
    updated_state = state_manager.update_state(initial_state, test_data)
    
    # Mentsük az állapotot
    state_manager.save_state(updated_state)
    
    # Töltsük be az állapotot
    loaded_state = state_manager.load_state(workflow_id)
    
    # Ellenőrizzük, hogy az adatok megmaradtak
    assert loaded_state["current_url"] == "https://test.com"
    assert loaded_state["page_title"] == "Test Page"
    assert loaded_state["extracted_data"]["test_key"] == "test_value"


@pytest.mark.asyncio
async def test_error_handling(state_manager, initial_state):
    """Hibakezelés teszt"""
    browser_commands = BrowserCommands(state_manager)
    
    # Inicializáljuk a böngészőt
    state = browser_commands.initialize_driver(initial_state)
    
    # Navigáljunk egy valós oldalra
    state = await browser_commands.navigate_to_url(state, "https://www.example.com")
    
    # Próbáljunk egy nem létező elemre kattintani
    state = await browser_commands.click_element(state, "#non_existent_element", wait_seconds=2)
    
    # Ellenőrizzük a hibaállapotot
    assert state["error_state"] == True
    assert "Hiba az elemre kattintás során" in state["error_details"]
    assert state["error_timestamp"] is not None
    
    # Zárjuk be a böngészőt
    browser_commands.close_driver(state)


def test_workflow_creation(workflow_id):
    """Munkafolyamat létrehozás teszt"""
    # Információ kinyerési munkafolyamat
    info_workflow = create_web_information_extraction_workflow(workflow_id)
    
    # Keresési munkafolyamat
    search_workflow = create_google_search_workflow(workflow_id)
    
    # Ellenőrizzük a munkafolyamatok létrehozását
    assert info_workflow is not None
    assert search_workflow is not None
    assert hasattr(info_workflow, "add_node")
    assert hasattr(search_workflow, "add_node")


if __name__ == "__main__":
    # Tesztfájl közvetlen futtatása esetén
    asyncio.run(test_browser_navigation(BrowserStateManager(), BrowserStateManager().create_initial_state("manual_test")))
"""
