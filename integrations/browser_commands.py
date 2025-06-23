"""
Browser Commands for Project-S
-----------------------------
Ez a modul magas szintű böngészőautomatizációs parancsokat biztosít,
amelyek felhasználhatók a LangGraph munkafolyamatokban. A parancsok
absztrakciós réteget biztosítanak a közvetlen Selenium műveletek fölött.
"""
import logging
import time
import asyncio
from typing import Dict, Any, List, Optional, Union, TypedDict
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

from integrations.browser_automation_tool import BrowserAutomationTool
from integrations.browser_state import BrowserAutomationState, BrowserStateManager
from integrations.tool_manager import tool_manager

from core.event_bus import event_bus

logger = logging.getLogger(__name__)


class BrowserCommands(BrowserAutomationTool):
    """
    Magas szintű böngésző műveletek végrehajtása
    
    Képességek:
    - Navigáció (URL betöltése, vissza/előre lépés)
    - Kattintások és űrlapkitöltés
    - Várakozás elemekre
    - Scrollozás és képernyőképek
    - DOM manipuláció
    """
    
    def __init__(self, state_manager: Optional[BrowserStateManager] = None):
        """Inicializálja a böngésző parancsok osztályt"""
        super().__init__(state_manager)
        
    @tool_manager.register(
        metadata={
            "name": "navigate_to_url",
            "description": "Navigálás a megadott URL-re",
            "category": "browser_navigation",
            "tags": ["navigation", "browser", "url"],
            "is_dangerous": False,
        }
    )
    async def navigate_to_url(self, state: BrowserAutomationState, 
                           url: str, wait_for_load: bool = True) -> BrowserAutomationState:
        """
        Navigálás a megadott URL-re.
        
        Args:
            state: Az aktuális böngészőautomatizációs állapot
            url: A betöltendő URL
            wait_for_load: Várakozás az oldal teljes betöltődésére
            
        Returns:
            Az aktualizált állapot
        """
        # Böngésző inicializálása, ha még nem történt meg
        if not self.driver:
            state = self.initialize_driver(state)
            
        # Művelet hozzáadása a szekvenciához
        state = self.state_manager.add_action_to_sequence(
            state, 
            "navigate", 
            {"url": url}
        )
        
        # Előző URL rögzítése
        current_url = state.get("current_url", "about:blank")
        if current_url != "about:blank":
            history = state.get("navigation_history", [])
            if current_url not in history:
                history.append(current_url)
                state = self.state_manager.update_state(state, {
                    "navigation_history": history
                })
        
        # Navigáció indítása
        try:
            state = self.state_manager.update_state(state, {
                "navigation_start_time": time.time()
            })
            
            self.driver.get(url)
            
            # Várakozás az oldal betöltésére
            if wait_for_load:
                WebDriverWait(self.driver, 30).until(
                    lambda d: d.execute_script("return document.readyState") == "complete"
                )
                
            # Állapot frissítése
            state = self.state_manager.update_state(state, {
                "navigation_end_time": time.time(),
                "current_url": self.driver.current_url,
                "page_title": self.driver.title,
                "page_content": self.driver.page_source,
                "error_state": False,
                "last_interaction_time": time.time()
            })
            
            event_bus.emit("browser.navigation_completed", {
                "url": self.driver.current_url,
                "title": self.driver.title,
                "status": "success"
            })
            
            return state
            
        except Exception as e:
            error_msg = f"Hiba az URL betöltése közben: {str(e)}"
            logger.error(error_msg)
            
            # Hiba állapot frissítése
            return self.state_manager.update_state(state, {
                "error_state": True,
                "error_details": error_msg,
                "error_timestamp": time.time(),
                "navigation_end_time": time.time()
            })
    
    @tool_manager.register(
        metadata={
            "name": "click_element",
            "description": "Kattintás egy webes elemen",
            "category": "browser_interaction",
            "tags": ["click", "interaction", "browser"],
            "is_dangerous": False,
        }
    )
    async def click_element(self, state: BrowserAutomationState,
                        selector: str, selector_type: str = "css",
                        wait_seconds: int = 10) -> BrowserAutomationState:
        """
        Kattintás egy webes elemen.
        
        Args:
            state: Az aktuális böngészőautomatizációs állapot
            selector: Az elem azonosítására szolgáló szelektor
            selector_type: A szelektor típusa ("css", "xpath", "id", "name")
            wait_seconds: Várakozási idő az elem megjelenésére
            
        Returns:
            Az aktualizált állapot
        """
        if not self.driver:
            return self.state_manager.update_state(state, {
                "error_state": True,
                "error_details": "Nincs inicializált WebDriver",
                "error_timestamp": time.time()
            })
        
        # Művelet hozzáadása a szekvenciához
        state = self.state_manager.add_action_to_sequence(
            state, 
            "click", 
            {"selector": selector, "selector_type": selector_type}
        )
        
        try:
            # Szelektor típus konvertálása Selenium By osztályra
            by_type = {
                "css": By.CSS_SELECTOR,
                "xpath": By.XPATH,
                "id": By.ID,
                "name": By.NAME,
                "class": By.CLASS_NAME,
                "tag": By.TAG_NAME,
                "link_text": By.LINK_TEXT,
                "partial_link_text": By.PARTIAL_LINK_TEXT
            }.get(selector_type.lower(), By.CSS_SELECTOR)
            
            # Várakozás az elem megjelenésére
            element = WebDriverWait(self.driver, wait_seconds).until(
                EC.element_to_be_clickable((by_type, selector))
            )
            
            # Elem adatainak rögzítése kattintás előtt
            element_data = {
                "tag_name": element.tag_name,
                "text": element.text,
                "location": element.location,
                "size": element.size,
                "attributes": {}
            }
            
            # Fontosabb attribútumok kinyerése
            for attr in ["id", "name", "class", "href", "src", "value", "type", "aria-label"]:
                try:
                    value = element.get_attribute(attr)
                    if value:
                        element_data["attributes"][attr] = value
                except:
                    pass
            
            # Kattintás végrehajtása és várakozás
            element.click()
            time.sleep(0.5)  # Rövid várakozás, hogy az oldal reagálhasson
            
            # Állapot frissítése
            state = self.state_manager.update_state(state, {
                "current_url": self.driver.current_url,
                "page_title": self.driver.title,
                "active_element_data": element_data,
                "error_state": False,
                "last_interaction_time": time.time()
            })
            
            event_bus.emit("browser.element_clicked", {
                "selector": selector,
                "selector_type": selector_type,
                "element_data": element_data
            })
            
            return state
            
        except Exception as e:
            error_msg = f"Hiba az elemre kattintás során: {str(e)}"
            logger.error(error_msg)
            
            # Hiba állapot frissítése
            return self.state_manager.update_state(state, {
                "error_state": True,
                "error_details": error_msg,
                "error_timestamp": time.time()
            })
            
    @tool_manager.register(
        metadata={
            "name": "fill_form_field",
            "description": "Űrlap mező kitöltése",
            "category": "browser_interaction",
            "tags": ["form", "input", "browser"],
            "is_dangerous": False,
        }
    )
    async def fill_form_field(self, state: BrowserAutomationState,
                           selector: str, value: str, selector_type: str = "css",
                           clear_first: bool = True) -> BrowserAutomationState:
        """
        Űrlap mező kitöltése.
        
        Args:
            state: Az aktuális böngészőautomatizációs állapot
            selector: Az űrlapmező azonosítására szolgáló szelektor
            value: A beírandó érték
            selector_type: A szelektor típusa ("css", "xpath", "id", "name")
            clear_first: A mező törlése kitöltés előtt
            
        Returns:
            Az aktualizált állapot
        """
        if not self.driver:
            return self.state_manager.update_state(state, {
                "error_state": True,
                "error_details": "Nincs inicializált WebDriver",
                "error_timestamp": time.time()
            })
        
        # Művelet hozzáadása a szekvenciához
        state = self.state_manager.add_action_to_sequence(
            state, 
            "fill_form", 
            {"selector": selector, "selector_type": selector_type, "value": value}
        )
        
        try:
            # Szelektor típus konvertálása Selenium By osztályra
            by_type = {
                "css": By.CSS_SELECTOR,
                "xpath": By.XPATH,
                "id": By.ID,
                "name": By.NAME,
                "class": By.CLASS_NAME,
                "tag": By.TAG_NAME
            }.get(selector_type.lower(), By.CSS_SELECTOR)
            
            # Várakozás az elem megjelenésére
            element = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((by_type, selector))
            )
            
            # Mező törlése ha szükséges
            if clear_first:
                element.clear()
            
            # Érték beírása
            element.send_keys(value)
            
            # Frissítsük a form adatokat az állapotban
            form_data = state.get("form_data", {})
            
            # Azonosítsuk az aktuális űrlapot
            try:
                form = element.find_element(By.XPATH, "ancestor::form")
                form_id = form.get_attribute("id") or form.get_attribute("name") or f"form_{len(form_data) + 1}"
                
                if form_id not in form_data:
                    form_data[form_id] = {}
                    
                # Mező azonosítása
                field_id = element.get_attribute("id") or element.get_attribute("name") or selector
                form_data[form_id][field_id] = value
                
            except NoSuchElementException:
                # Ha nincs form szülő, akkor egy általános formba vesszük fel
                if "general_form" not in form_data:
                    form_data["general_form"] = {}
                
                field_id = element.get_attribute("id") or element.get_attribute("name") or selector
                form_data["general_form"][field_id] = value
            
            # Állapot frissítése
            state = self.state_manager.update_state(state, {
                "form_data": form_data,
                "active_element_data": {
                    "tag_name": element.tag_name,
                    "value": value,
                    "selector": selector,
                    "selector_type": selector_type
                },
                "error_state": False,
                "last_interaction_time": time.time()
            })
            
            event_bus.emit("browser.form_field_filled", {
                "selector": selector,
                "value": value
            })
            
            return state
            
        except Exception as e:
            error_msg = f"Hiba az űrlapmező kitöltése során: {str(e)}"
            logger.error(error_msg)
            
            # Hiba állapot frissítése
            return self.state_manager.update_state(state, {
                "error_state": True,
                "error_details": error_msg,
                "error_timestamp": time.time()
            })
            
    @tool_manager.register(
        metadata={
            "name": "wait_for_element",
            "description": "Várakozás egy elem megjelenésére",
            "category": "browser_interaction",
            "tags": ["wait", "browser", "element"],
            "is_dangerous": False,
        }
    )
    async def wait_for_element(self, state: BrowserAutomationState,
                            selector: str, selector_type: str = "css",
                            timeout: int = 30,
                            condition: str = "presence") -> BrowserAutomationState:
        """
        Várakozás egy elem meghatározott állapotára.
        
        Args:
            state: Az aktuális böngészőautomatizációs állapot
            selector: Az elem azonosítására szolgáló szelektor
            selector_type: A szelektor típusa ("css", "xpath", "id", "name")
            timeout: Várakozási idő másodpercben
            condition: Feltétel típusa: "presence", "visibility", "clickable", "invisible"
            
        Returns:
            Az aktualizált állapot
        """
        if not self.driver:
            return self.state_manager.update_state(state, {
                "error_state": True,
                "error_details": "Nincs inicializált WebDriver",
                "error_timestamp": time.time()
            })
        
        # Művelet hozzáadása a szekvenciához
        state = self.state_manager.add_action_to_sequence(
            state, 
            "wait", 
            {"selector": selector, "selector_type": selector_type, 
             "timeout": timeout, "condition": condition}
        )
        
        try:
            # Szelektor típus konvertálása Selenium By osztályra
            by_type = {
                "css": By.CSS_SELECTOR,
                "xpath": By.XPATH,
                "id": By.ID,
                "name": By.NAME,
                "class": By.CLASS_NAME,
                "tag": By.TAG_NAME
            }.get(selector_type.lower(), By.CSS_SELECTOR)
            
            # Feltétel típus konvertálása expected_conditions-re
            wait_conditions = {
                "presence": EC.presence_of_element_located((by_type, selector)),
                "visibility": EC.visibility_of_element_located((by_type, selector)),
                "clickable": EC.element_to_be_clickable((by_type, selector)),
                "invisible": EC.invisibility_of_element_located((by_type, selector)),
                "text": lambda text: EC.text_to_be_present_in_element((by_type, selector), text),
            }
            
            wait_condition = wait_conditions.get(condition.lower(), wait_conditions["presence"])
            
            # Várakozás kezdeti idejének rögzítése
            wait_start_time = time.time()
            
            # Várakozás végrehajtása
            WebDriverWait(self.driver, timeout).until(wait_condition)
            
            wait_end_time = time.time()
            
            # Állapot frissítése
            state = self.state_manager.update_state(state, {
                "error_state": False,
                "last_interaction_time": wait_end_time,
                "extracted_data": {
                    **state.get("extracted_data", {}),
                    "wait_duration": wait_end_time - wait_start_time
                }
            })
            
            event_bus.emit("browser.element_wait_completed", {
                "selector": selector,
                "condition": condition,
                "duration": wait_end_time - wait_start_time
            })
            
            return state
            
        except Exception as e:
            error_msg = f"Hiba a várakozás során: {str(e)}"
            logger.error(error_msg)
            
            # Hiba állapot frissítése
            return self.state_manager.update_state(state, {
                "error_state": True,
                "error_details": error_msg,
                "error_timestamp": time.time()
            })


# Tool Manager regisztráció és elérhetővé tétel
browser_commands = BrowserCommands()
"""
