"""
Browser Search Tools for Project-S
---------------------------------
Ez a modul a böngészőautomatizációs rendszer keresési és információkinyerési funkcióit biztosítja.
LangGraph-kompatibilis eszközök webes kereséshez, tartalom kinyeréséhez és elemzéséhez.
"""
import logging
import time
import json
import re
from typing import Dict, Any, List, Optional, Union, TypedDict
from bs4 import BeautifulSoup
import requests
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse

from integrations.browser_automation_tool import BrowserAutomationTool
from integrations.browser_state import BrowserAutomationState, BrowserStateManager
from integrations.tool_manager import tool_manager

from core.event_bus import event_bus

logger = logging.getLogger(__name__)


class BrowserSearchTools(BrowserAutomationTool):
    """
    Böngésző alapú keresési és információkinyerési eszközök.
    
    Képességek:
    - Webes keresés különböző keresőmotorokkal
    - Információkinyerés weboldalakról
    - Keresési eredmények elemzése és strukturálása
    - Automatikus navigáció a keresési eredmények között
    """
    
    def __init__(self, state_manager: Optional[BrowserStateManager] = None):
        """Inicializálja a keresési eszközosztályt"""
        super().__init__(state_manager)
        
    @tool_manager.register(
        metadata={
            "name": "perform_google_search",
            "description": "Keresés a Google keresőmotorban és eredmények kinyerése",
            "category": "web_search",
            "tags": ["search", "web", "google"],
            "is_dangerous": False,
        }
    )
    async def perform_google_search(self, state: BrowserAutomationState, query: str, 
                                  result_limit: int = 5) -> BrowserAutomationState:
        """
        Keresés végrehajtása a Google keresőben és az eredmények kinyerése.
        
        Args:
            state: Az aktuális böngészőautomatizációs állapot
            query: A keresési kulcsszó vagy kifejezés
            result_limit: Kinyerendő találatok maximális száma
            
        Returns:
            Az aktualizált állapot a keresési eredményekkel
        """
        # Böngésző inicializálása, ha még nem történt meg
        if not self.driver:
            state = self.initialize_driver(state)
            
        # Google keresés végrehajtása
        search_url = f"https://www.google.com/search?q={query}"
        
        # Művelet hozzáadása a szekvenciához
        state = self.state_manager.add_action_to_sequence(
            state, 
            "web_search", 
            {"search_engine": "google", "query": query, "url": search_url}
        )
        
        # Navigálás a Google keresőoldalra
        try:
            self.driver.get(search_url)
            state = self.state_manager.update_state(state, {
                "current_url": self.driver.current_url,
                "page_title": self.driver.title
            })
            
            # Várakozás a keresési eredmények betöltésére
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div.g"))
            )
            
            # Keresési eredmények kinyerése
            results = []
            result_elements = self.driver.find_elements(By.CSS_SELECTOR, "div.g")
            
            for idx, element in enumerate(result_elements[:result_limit]):
                try:
                    # Cím és link kinyerése
                    title_element = element.find_element(By.CSS_SELECTOR, "h3")
                    title = title_element.text if title_element else "Nincs cím"
                    
                    link_element = element.find_element(By.CSS_SELECTOR, "a")
                    link = link_element.get_attribute("href") if link_element else ""
                    
                    # Leírás kinyerése
                    description_element = element.find_element(By.CSS_SELECTOR, "div.VwiC3b")
                    description = description_element.text if description_element else "Nincs leírás"
                    
                    results.append({
                        "title": title,
                        "url": link,
                        "description": description
                    })
                except Exception as e:
                    logger.warning(f"Hiba a keresési eredmény feldolgozása során: {str(e)}")
            
            # Eredmények tárolása az állapotban
            state = self.state_manager.update_state(state, {
                "search_results": results,
                "page_content": self.driver.page_source,
                "error_state": False,
                "extracted_data": {
                    "search_query": query,
                    "search_engine": "google",
                    "result_count": len(results)
                }
            })
            
            event_bus.emit("browser.search_completed", {
                "query": query,
                "results": results,
                "engine": "google"
            })
            
            return state
            
        except Exception as e:
            error_msg = f"Hiba a Google keresés során: {str(e)}"
            logger.error(error_msg)
            
            # Hiba állapot frissítése
            return self.state_manager.update_state(state, {
                "error_state": True,
                "error_details": error_msg,
                "error_timestamp": time.time()
            })
            
    @tool_manager.register(
        metadata={
            "name": "extract_page_content",
            "description": "Tartalom kinyerése az aktuális weboldalról",
            "category": "web_extract",
            "tags": ["extract", "content", "web"],
            "is_dangerous": False,
        }
    )
    async def extract_page_content(self, state: BrowserAutomationState, 
                                 content_type: str = "text",
                                 css_selector: Optional[str] = None) -> BrowserAutomationState:
        """
        Tartalom kinyerése az aktuális weboldalról.
        
        Args:
            state: Az aktuális böngészőautomatizációs állapot
            content_type: A kinyerendő tartalom típusa ('text', 'html', 'links', 'tables')
            css_selector: Opcionális CSS szelektor a tartalom szűkítéséhez
            
        Returns:
            Az aktualizált állapot a kinyert tartalommal
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
            "extract_content", 
            {"content_type": content_type, "css_selector": css_selector}
        )
        
        try:
            # Várakozás, hogy az oldal teljesen betöltődjön
            time.sleep(1)  # Rövid várakozás
            
            extracted_content = {}
            
            # A teljes oldalra vagy csak egy részére alkalmazzuk
            target_element = self.driver
            if css_selector:
                target_element = self.driver.find_element(By.CSS_SELECTOR, css_selector)
            
            # Tartalom kinyerése a kért típus alapján
            if content_type == "text":
                extracted_content["text"] = target_element.text
                
            elif content_type == "html":
                if css_selector:
                    extracted_content["html"] = target_element.get_attribute("outerHTML")
                else:
                    extracted_content["html"] = self.driver.page_source
                    
            elif content_type == "links":
                link_elements = target_element.find_elements(By.TAG_NAME, "a") if css_selector else self.driver.find_elements(By.TAG_NAME, "a")
                links = []
                for link in link_elements:
                    try:
                        href = link.get_attribute("href")
                        text = link.text
                        if href:
                            links.append({"url": href, "text": text})
                    except:
                        continue
                extracted_content["links"] = links
                
            elif content_type == "tables":
                table_elements = target_element.find_elements(By.TAG_NAME, "table") if css_selector else self.driver.find_elements(By.TAG_NAME, "table")
                tables = []
                
                for idx, table in enumerate(table_elements):
                    try:
                        # Táblázat fejléc
                        headers = []
                        header_cells = table.find_elements(By.TAG_NAME, "th")
                        for cell in header_cells:
                            headers.append(cell.text)
                            
                        # Táblázat sorai
                        rows = []
                        row_elements = table.find_elements(By.TAG_NAME, "tr")
                        for row in row_elements:
                            cells = []
                            cell_elements = row.find_elements(By.TAG_NAME, "td")
                            for cell in cell_elements:
                                cells.append(cell.text)
                            if cells:  # Csak a nem üres sorokat adjuk hozzá
                                rows.append(cells)
                                
                        tables.append({
                            "headers": headers,
                            "rows": rows
                        })
                    except:
                        continue
                        
                extracted_content["tables"] = tables
            
            # Frissítsük az állapotot a kinyert tartalommal
            current_extracted = state.get("extracted_data", {})
            current_extracted.update(extracted_content)
            
            state = self.state_manager.update_state(state, {
                "extracted_data": current_extracted,
                "error_state": False
            })
            
            event_bus.emit("browser.content_extracted", {
                "content_type": content_type,
                "url": self.driver.current_url,
                "title": self.driver.title
            })
            
            return state
            
        except Exception as e:
            error_msg = f"Hiba az oldal tartalmának kinyerése során: {str(e)}"
            logger.error(error_msg)
            
            # Hiba állapot frissítése
            return self.state_manager.update_state(state, {
                "error_state": True,
                "error_details": error_msg,
                "error_timestamp": time.time()
            })


# Tool Manager regisztráció és elérhetővé tétel
browser_search_tools = BrowserSearchTools()
"""
