"""
BrowserAutomationTool - LangGraph-kompatibilis böngésző automatizációs eszköz
-------------------------------------------------------------------------------
Ez a modul olyan eszközosztályokat biztosít, amelyek lehetővé teszik a böngésző
automatizációt LangGraph munkafolyamatokban. Selenium WebDrivert használ a böngésző
irányításához, és integrálódik a Project-S eseménykezelő rendszerével.

Funkciók:
- Böngésző inicializálás és irányítás
- Weboldal navigáció és interakció
- Hibakezelés és újrapróbálkozás
- DOM elérés és manipuláció
- Állapot kezelés
- Adatkinyerés weboldalakról
"""
import logging
import time
import os
import json
import asyncio
import traceback
from typing import Dict, Any, List, Optional, Union, Callable, Type, TypedDict
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    WebDriverException, TimeoutException, NoSuchElementException,
    ElementNotInteractableException, ElementClickInterceptedException, StaleElementReferenceException
)
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement

from langgraph.prebuilt import ToolNode
from langgraph.graph import StateGraph

from integrations.browser_state import BrowserAutomationState, BrowserStateManager

from core.event_bus import event_bus
from core.error_handler import error_handler

logger = logging.getLogger(__name__)

# Alapértelmezett beállítások
DEFAULT_TIMEOUT = 30  # másodpercek
DEFAULT_RETRY_COUNT = 3
DEFAULT_RETRY_DELAY = 2  # másodpercek


class BrowserAutomationTool:
    """
    LangGraph-kompatibilis böngésző automatizációs alaposztály.
    
    Ez az osztály:
    1. Kezeli a WebDriver életciklusát (inicializálás, megszüntetés)
    2. Biztonságosan hajt végre műveleteket újrapróbálkozással
    3. Állapotkezelést biztosít LangGraph munkafolyamatokhoz
    4. Eseményeket küld a Project-S eseménykezelő rendszerébe
    """
    
    def __init__(self, state_manager: Optional[BrowserStateManager] = None):
        """
        Inicializálja a böngésző automatizációs eszközt.
        
        Args:
            state_manager: Opcionális állapotkezelő. Ha None, akkor új példányt hoz létre.
        """
        self.driver = None
        self.state_manager = state_manager if state_manager else BrowserStateManager()
        self.default_timeout = DEFAULT_TIMEOUT
        self.default_retry_count = DEFAULT_RETRY_COUNT
        self.default_retry_delay = DEFAULT_RETRY_DELAY
        
    def initialize_driver(self, state: BrowserAutomationState) -> BrowserAutomationState:
        """
        Inicializálja a megfelelő WebDrivert az állapot alapján.
        
        Args:
            state: A munkafolyamat állapota
            
        Returns:
            Frissített állapot
            
        Raises:
            WebDriverException: Ha a WebDriver inicializálása sikertelen
        """
        driver_type = state.get("driver_type", "chrome")
        
        try:
            driver = None
            
            if driver_type.lower() == "chrome":
                options = ChromeOptions()
                options.add_argument("--start-maximized")
                options.add_argument("--disable-infobars")
                options.add_argument("--disable-extensions")
                options.add_experimental_option("excludeSwitches", ["enable-logging"])
                options.add_argument("--disable-gpu")
                # Detektálási védelmek - production környezetben használandó
                # options.add_argument("--disable-blink-features=AutomationControlled")
                # options.add_experimental_option("excludeSwitches", ["enable-automation"])
                # options.add_experimental_option("useAutomationExtension", False)
                
                driver = webdriver.Chrome(options=options)
                
            elif driver_type.lower() == "edge":
                options = EdgeOptions()
                options.add_argument("--start-maximized")
                options.add_argument("--disable-infobars")
                options.add_argument("--disable-extensions")
                
                driver = webdriver.Edge(options=options)
                
            elif driver_type.lower() == "firefox":
                options = FirefoxOptions()
                options.add_argument("--start-maximized")
                
                driver = webdriver.Firefox(options=options)
            
            else:
                raise ValueError(f"Nem támogatott böngészőtípus: {driver_type}")
            
            # Beállítjuk a várakozási időt
            driver.implicitly_wait(self.default_timeout)
            
            # Frissítjük az osztály driver attribútumát
            self.driver = driver
            
            # Frissítjük az állapotot
            updated_state = self.state_manager.update_state(state, {
                "browser_active": True,
                "error_state": False,
                "error_details": None
            })
            
            # Esemény küldése
            event_bus.emit("browser.initialized", {
                "workflow_id": state.get("workflow_id"),
                "driver_type": driver_type,
                "success": True
            })
            
            logger.info(f"{driver_type} böngésző sikeresen inicializálva.")
            return updated_state
            
        except Exception as e:
            error_msg = f"Böngésző inicializálási hiba: {str(e)}"
            logger.error(error_msg)
            
            # Frissítjük az állapotot
            updated_state = self.state_manager.update_state(state, {
                "browser_active": False,
                "error_state": True,
                "error_details": error_msg,
                "error_timestamp": time.time()
            })
            
            # Esemény küldése
            event_bus.emit("browser.error", {
                "workflow_id": state.get("workflow_id"),
                "error": error_msg,
                "error_type": "initialization"
            })
            
            # Hiba továbbítása a hibaincidensek kezelőjének
            error_handler.handle_error("browser_initialization", e, {
                "driver_type": driver_type,
                "workflow_id": state.get("workflow_id")
            })
            
            # Kivétel tovább dobása
            raise WebDriverException(error_msg) from e
    
    def close_driver(self, state: BrowserAutomationState) -> BrowserAutomationState:
        """
        Bezárja a WebDrivert és frissíti az állapotot.
        
        Args:
            state: A munkafolyamat állapota
            
        Returns:
            Frissített állapot
        """
        workflow_id = state.get("workflow_id")
        
        try:
            if self.driver:
                self.driver.quit()
                self.driver = None
                
                logger.info(f"WebDriver sikeresen bezárva (workflow_id: {workflow_id})")
                
            # Frissítjük az állapotot
            updated_state = self.state_manager.update_state(state, {
                "browser_active": False
            })
            
            # Esemény küldése
            event_bus.emit("browser.closed", {
                "workflow_id": workflow_id,
                "success": True
            })
            
            return updated_state
            
        except Exception as e:
            error_msg = f"WebDriver bezárási hiba: {str(e)}"
            logger.error(error_msg)
            
            # Frissítjük az állapotot
            updated_state = self.state_manager.update_state(state, {
                "browser_active": False,
                "error_state": True,
                "error_details": error_msg,
                "error_timestamp": time.time()
            })
            
            # Esemény küldése
            event_bus.emit("browser.error", {
                "workflow_id": workflow_id,
                "error": error_msg,
                "error_type": "driver_close"
            })
            
            return updated_state
    
    def safe_operation(self, 
                      state: BrowserAutomationState, 
                      operation_func: Callable,
                      operation_name: str,
                      max_retries: Optional[int] = None,
                      retry_delay: Optional[int] = None,
                      **kwargs) -> tuple[BrowserAutomationState, Any]:
        """
        Biztonságosan hajt végre egy böngésző műveletet újrapróbálkozással.
        
        Args:
            state: A munkafolyamat állapota
            operation_func: A végrehajtandó művelet függvénye
            operation_name: A művelet neve (naplózáshoz)
            max_retries: Maximális újrapróbálkozások száma
            retry_delay: Várakozási idő újrapróbálkozások között
            **kwargs: A művelet függvény argumentumai
            
        Returns:
            A frissített állapot és a művelet eredménye
        """
        if max_retries is None:
            max_retries = self.default_retry_count
            
        if retry_delay is None:
            retry_delay = self.default_retry_delay
            
        retry_count = 0
        workflow_id = state.get("workflow_id")
        last_exception = None
        
        # Ha még nincs inicializálva a driver, inicializáljuk
        if not self.driver or not state.get("browser_active", False):
            try:
                state = self.initialize_driver(state)
            except Exception as e:
                logger.error(f"Nem sikerült inicializálni a böngészőt a művelethez: {operation_name}")
                updated_state = self.state_manager.record_error(state, e)
                raise e
        
        logger.info(f"Művelet végrehajtása: {operation_name} (workflow_id: {workflow_id})")
        
        while retry_count <= max_retries:
            try:
                # Végrehajtjuk a műveletet
                result = operation_func(self.driver, **kwargs)
                
                # Frissítjük az állapotot a driver alapján
                updated_state = self.state_manager.update_from_driver(state, self.driver)
                
                # Frissítjük a műveletsorozatot
                updated_state = self.state_manager.add_action_to_sequence(
                    updated_state,
                    operation_name,
                    kwargs
                )
                
                # Ha nem volt hiba, töröljük a hibaállapotot
                if updated_state.get("error_state", False):
                    updated_state = self.state_manager.clear_error(updated_state)
                    
                # Esemény küldése
                event_bus.emit("browser.operation.success", {
                    "workflow_id": workflow_id,
                    "operation": operation_name
                })
                
                return updated_state, result
                
            except (NoSuchElementException, 
                   ElementNotInteractableException, 
                   ElementClickInterceptedException,
                   StaleElementReferenceException) as e:
                # Ezek olyan kivételek, amik újrapróbálkozással megoldhatók
                retry_count += 1
                last_exception = e
                
                logger.warning(f"Elem hiba a műveletnél: {operation_name}, újrapróbálkozás {retry_count}/{max_retries}")
                
                if retry_count <= max_retries:
                    time.sleep(retry_delay)
                    continue
                    
            except TimeoutException as e:
                # Időtúllépés esetén növeljük a várakozási időt és újrapróbálkozunk
                retry_count += 1
                last_exception = e
                
                logger.warning(f"Időtúllépés a műveletnél: {operation_name}, újrapróbálkozás {retry_count}/{max_retries}")
                
                if retry_count <= max_retries:
                    time.sleep(retry_delay * retry_count)  # Növekvő várakozási idő
                    continue
                    
            except WebDriverException as e:
                # Súlyosabb hiba a driverrel
                retry_count += 1
                last_exception = e
                
                logger.error(f"WebDriver hiba a műveletnél: {operation_name}, újrapróbálkozás {retry_count}/{max_retries}")
                
                if retry_count <= max_retries:
                    try:
                        # Próbáljuk újracsatlakoztatni a drivert
                        self.close_driver(state)
                        state = self.initialize_driver(state)
                        time.sleep(retry_delay * retry_count)  # Növekvő várakozási idő
                        continue
                    except Exception as reinit_error:
                        logger.error(f"Nem sikerült újracsatlakoztatni a drivert: {reinit_error}")
                        break
                        
            except Exception as e:
                # Egyéb hiba esetén nincs újrapróbálkozás
                last_exception = e
                logger.error(f"Váratlan hiba a műveletnél: {operation_name}: {e}")
                break
                
        # Ha idáig jutottunk, akkor nem sikerült végrehajtani a műveletet
        error_msg = f"A művelet végrehajtása sikertelen {max_retries} próbálkozás után: {operation_name}"
        if last_exception:
            error_msg += f", hiba: {str(last_exception)}"
            
        logger.error(error_msg)
        
        # Frissítjük az állapotot
        updated_state = self.state_manager.record_error(state, last_exception or Exception(error_msg))
        
        # Esemény küldése
        event_bus.emit("browser.operation.error", {
            "workflow_id": workflow_id,
            "operation": operation_name,
            "error": error_msg,
            "retry_count": retry_count
        })
        
        # Hiba továbbítása a hibaincidensek kezelőjének
        error_handler.handle_error("browser_operation", last_exception or Exception(error_msg), {
            "workflow_id": workflow_id,
            "operation": operation_name,
            "retry_count": retry_count,
            "operation_args": kwargs
        })
        
        raise WebDriverException(error_msg) from last_exception


def create_browser_tool_node() -> ToolNode:
    """
    Létrehoz egy LangGraph ToolNode-ot a böngésző műveletek végrehajtásához.
    
    Ez az eszköz LangGraph munkafolyamatokban használható a böngésző irányításához,
    az állapot automatikus kezelésével.
    
    Returns:
        LangGraph ToolNode a böngésző automatizációhoz
    """
    browser_tool = BrowserAutomationTool()
    state_manager = browser_tool.state_manager
    
    def _handle_browser_operation(state: Dict[str, Any], operation_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Kezeli a böngésző műveleteket a LangGraph eszközben.
        
        Args:
            state: A LangGraph állapot
            operation_data: A böngésző művelethez szükséges adatok
            
        Returns:
            A frissített állapot
        """
        # Ellenőrizzük, hogy van-e browser_state a state-ben
        browser_state = state.get("browser_state", None)
        workflow_id = state.get("id") or str(time.time())
        operation = operation_data.get("operation", "unknown")
        
        if not browser_state:
            # Inicializáljunk egy új browser_state-t
            browser_state = state_manager.create_initial_state(workflow_id)
            
        try:
            # A művelet típusa alapján végezzük el a megfelelő műveletet
            if operation == "initialize":
                browser_type = operation_data.get("browser_type", "chrome")
                browser_state["driver_type"] = browser_type
                updated_state, _ = browser_tool.safe_operation(
                    browser_state,
                    lambda driver, **kwargs: driver,  # Csak inicializáljuk a drivert
                    "initialize_browser",
                )
                
            elif operation == "navigate":
                url = operation_data.get("url")
                if not url:
                    raise ValueError("URL nincs megadva a navigációs művelethez")
                    
                updated_state, _ = browser_tool.safe_operation(
                    browser_state,
                    lambda driver, url: driver.get(url),
                    "navigate_to_url",
                    url=url
                )
                
            elif operation == "close":
                updated_state = browser_tool.close_driver(browser_state)
                
            else:
                raise ValueError(f"Nem támogatott művelet: {operation}")
                
            # Frissítsük az állapotot a state dictionary-ben is
            state["browser_state"] = updated_state
            
            # Ha van kimeneti JSON mező, akkor azt is frissítsük
            state["output"] = json.dumps({
                "success": True,
                "operation": operation,
                "current_url": updated_state.get("current_url"),
                "page_title": updated_state.get("page_title"),
            })
            
            return state
            
        except Exception as e:
            logger.error(f"Hiba a böngésző művelet végrehajtása közben: {str(e)}")
            
            # Frissítsük a hibaállapotot
            if browser_state:
                updated_state = state_manager.record_error(browser_state, e)
                state["browser_state"] = updated_state
            
            # Állítsuk be a kimeneti JSON-t a hibával
            state["output"] = json.dumps({
                "success": False,
                "operation": operation,
                "error": str(e),
                "error_type": type(e).__name__
            })
            
            return state
    
    # Hozzuk létre a ToolNode-ot
    return ToolNode(name="browser_automation", fn=_handle_browser_operation)
