"""
BrowserAutomationState - LangGraph kompatibilis böngésző automatizációs állapotkezelő
-----------------------------------------------------------------------------------------
Ez a modul LangGraph-kompatibilis állapotobjektumot biztosít a böngésző automatizációhoz,
amely lehetővé teszi a böngésző állapotának tárolását és visszaállítását a LangGraph 
munkafolyamat különböző lépései között.

Funkcionalitás:
- Böngésző munkamenet adatainak tárolása
- Sikertelen műveletek esetén az állapot visszaállítása
- A böngésző interakció állapotának persistálása
- Támogatás a különböző böngésző interfészek kezeléséhez (ChromeDriver, EdgeDriver, stb.)
"""
import logging
from typing import Dict, Any, List, Optional, TypedDict, Union
import json
import os
import time
from datetime import datetime
import pickle
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement

logger = logging.getLogger(__name__)

class BrowserAutomationState(TypedDict, total=False):
    """
    TypedDict a böngésző automatizáció állapotának tárolására
    LangGraph munkafolyamatokban való használatra tervezve
    """
    # Alapvető állapot információk
    browser_active: bool  # A böngésző aktív-e
    current_url: str  # Az aktuális URL
    page_title: str  # Az aktuális oldal címe
    driver_type: str  # A használt WebDriver típusa (pl. "chrome", "edge")
    
    # Navigációs állapot
    navigation_history: List[str]  # Előző URL-ek listája
    navigation_start_time: float  # A navigáció kezdete (timestamp)
    navigation_end_time: float  # A navigáció befejezése (timestamp)
    last_interaction_time: float  # Az utolsó interakció ideje
    
    # Munkamenet információk
    cookies: List[Dict[str, Any]]  # A munkamenet sütijeinek állapota
    local_storage: Dict[str, Any]  # A localStorage tartalma
    session_storage: Dict[str, Any]  # A sessionStorage tartalma
    
    # Tartalom és elemek
    page_content: str  # Az oldal szöveges tartalma
    active_element_data: Optional[Dict[str, Any]]  # Az aktív elem adatai
    form_data: Dict[str, Any]  # Űrlapok adatai
    
    # Hibakezelési adatok
    error_state: bool  # Van-e hiba
    error_details: Optional[str]  # Hiba részletek
    error_timestamp: Optional[float]  # Hiba időpontja
    retry_count: int  # Újrapróbálkozások száma
    
    # Adatgyűjtés
    extracted_data: Dict[str, Any]  # Weboldalról kinyert adatok
    search_results: List[Dict[str, Any]]  # Keresési eredmények
    
    # META adatok
    workflow_id: str  # A munkafolyamat azonosítója
    action_sequence: List[Dict[str, Any]]  # Az elvégzett műveletek sorozata
    timestamp: float  # Az állapot utolsó frissítésének időpontja
    

class BrowserStateManager:
    """
    Böngésző állapot kezelő osztály a LangGraph böngésző automatizációhoz
    
    Ez az osztály kezeli a böngésző állapot perzisztenciáját, mentését és visszaállítását,
    valamint lehetővé teszi a böngésző állapotának számos aspektusának nyomon követését.
    """
    
    def __init__(self, storage_dir: str = "./browser_states"):
        """
        Inicializálja a BrowserStateManager osztályt
        
        Args:
            storage_dir: Könyvtár az állapotok mentéséhez
        """
        self.storage_dir = storage_dir
        
        # Biztosítsuk, hogy a tárolómappa létezik
        os.makedirs(storage_dir, exist_ok=True)
        
        # Aktív állapotok nyilvántartása (workflow_id -> state)
        self.active_states = {}
        
    def create_initial_state(self, workflow_id: str, driver_type: str = "chrome") -> BrowserAutomationState:
        """
        Létrehoz egy kezdeti böngésző állapotot
        
        Args:
            workflow_id: A munkafolyamat azonosítója
            driver_type: A használandó böngésző driver típusa
            
        Returns:
            Kezdeti böngésző állapot
        """
        current_time = time.time()
        initial_state: BrowserAutomationState = {
            "browser_active": False,
            "current_url": "about:blank",
            "page_title": "",
            "driver_type": driver_type,
            "navigation_history": [],
            "navigation_start_time": current_time,
            "navigation_end_time": current_time,
            "last_interaction_time": current_time,
            "cookies": [],
            "local_storage": {},
            "session_storage": {},
            "page_content": "",
            "active_element_data": None,
            "form_data": {},
            "error_state": False,
            "error_details": None,
            "error_timestamp": None,
            "retry_count": 0,
            "extracted_data": {},
            "search_results": [],
            "workflow_id": workflow_id,
            "action_sequence": [],
            "timestamp": current_time
        }
        
        # Tároljuk az aktív állapotot
        self.active_states[workflow_id] = initial_state
        
        return initial_state
        
    def update_state(self, state: BrowserAutomationState, updates: Dict[str, Any]) -> BrowserAutomationState:
        """
        Frissíti a böngésző állapotot az új adatokkal
        
        Args:
            state: Az aktuális állapot
            updates: Frissítendő mezők és értékeik
            
        Returns:
            A frissített állapot
        """
        # Készítsünk másolatot, hogy ne módosítsuk közvetlenül a bemeneti állapotot
        updated_state = state.copy()
        
        # Frissítsük a mezőket
        for key, value in updates.items():
            updated_state[key] = value
        
        # Frissítsük az időbélyeget
        updated_state["timestamp"] = time.time()
        
        # Frissítsük az aktív állapotot is
        workflow_id = updated_state["workflow_id"]
        if workflow_id in self.active_states:
            self.active_states[workflow_id] = updated_state
        
        return updated_state
    
    def add_action_to_sequence(self, state: BrowserAutomationState, 
                              action_type: str, 
                              action_data: Dict[str, Any]) -> BrowserAutomationState:
        """
        Hozzáad egy műveletet az állapot műveletsorozatához
        
        Args:
            state: Az aktuális állapot
            action_type: A művelet típusa (pl. "click", "navigate", "type")
            action_data: A művelet adatai
            
        Returns:
            A frissített állapot
        """
        # Készítsünk másolatot, hogy ne módosítsuk közvetlenül a bemeneti állapotot
        updated_state = state.copy()
        
        # Hozzáadjuk az új műveletet
        action = {
            "type": action_type,
            "data": action_data,
            "timestamp": time.time()
        }
        
        if "action_sequence" not in updated_state:
            updated_state["action_sequence"] = []
            
        updated_state["action_sequence"].append(action)
        
        # Frissítsük az időbélyeget
        updated_state["timestamp"] = time.time()
        updated_state["last_interaction_time"] = time.time()
        
        # Frissítsük az aktív állapotot is
        workflow_id = updated_state["workflow_id"]
        if workflow_id in self.active_states:
            self.active_states[workflow_id] = updated_state
        
        return updated_state
    
    def update_from_driver(self, state: BrowserAutomationState, driver: WebDriver) -> BrowserAutomationState:
        """
        Frissíti az állapotot az aktuális böngésző állapot alapján
        
        Args:
            state: Az aktuális állapot
            driver: WebDriver példány
            
        Returns:
            A frissített állapot
        """
        try:
            updates = {
                "browser_active": True,
                "current_url": driver.current_url,
                "page_title": driver.title,
                "page_content": driver.page_source,
                "timestamp": time.time(),
                "last_interaction_time": time.time()
            }
            
            # Próbáljuk meg lekérni a sütiket
            try:
                cookies = driver.get_cookies()
                updates["cookies"] = cookies
            except Exception as e:
                logger.warning(f"Nem sikerült lekérni a sütiket: {e}")
                
            # Próbáljuk meg lekérni a localStorage tartalmát
            try:
                local_storage = driver.execute_script("""
                    var storage = {};
                    for (var i = 0; i < localStorage.length; i++) {
                        var key = localStorage.key(i);
                        storage[key] = localStorage.getItem(key);
                    }
                    return storage;
                """)
                updates["local_storage"] = local_storage
            except Exception as e:
                logger.warning(f"Nem sikerült lekérni a localStorage tartalmát: {e}")
                
            # Próbáljuk meg lekérni a sessionStorage tartalmát
            try:
                session_storage = driver.execute_script("""
                    var storage = {};
                    for (var i = 0; i < sessionStorage.length; i++) {
                        var key = sessionStorage.key(i);
                        storage[key] = sessionStorage.getItem(key);
                    }
                    return storage;
                """)
                updates["session_storage"] = session_storage
            except Exception as e:
                logger.warning(f"Nem sikerült lekérni a sessionStorage tartalmát: {e}")
                
            # Frissítsük a navigációs előzményeket
            if "navigation_history" not in state:
                state["navigation_history"] = []
                
            if (driver.current_url != "about:blank" and 
                (not state["navigation_history"] or 
                 state["navigation_history"][-1] != driver.current_url)):
                updated_history = state["navigation_history"].copy()
                updated_history.append(driver.current_url)
                updates["navigation_history"] = updated_history
            
            # Frissítsük az állapotot
            return self.update_state(state, updates)
            
        except Exception as e:
            logger.error(f"Hiba történt a böngésző állapot frissítésekor: {str(e)}")
            
            # Jelezzük a hibát az állapotban, de tartsuk meg a többi adatot
            error_updates = {
                "error_state": True,
                "error_details": str(e),
                "error_timestamp": time.time()
            }
            
            return self.update_state(state, error_updates)
    
    def save_state(self, state: BrowserAutomationState) -> str:
        """
        Elmenti az állapotot a lemezre
        
        Args:
            state: A mentendő állapot
            
        Returns:
            A mentett fájl elérési útja
        """
        workflow_id = state["workflow_id"]
        timestamp = datetime.fromtimestamp(state["timestamp"]).strftime("%Y%m%d_%H%M%S")
        filename = f"{workflow_id}_{timestamp}.json"
        filepath = os.path.join(self.storage_dir, filename)
        
        # Az állapotot JSON-ként mentjük
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(state, f, ensure_ascii=False, indent=2)
            
        logger.info(f"Böngésző állapot elmentve: {filepath}")
        return filepath
        
    def load_state(self, filepath: str) -> BrowserAutomationState:
        """
        Betölt egy állapotot a lemezről
        
        Args:
            filepath: A betöltendő fájl elérési útja
            
        Returns:
            A betöltött állapot
        """
        with open(filepath, 'r', encoding='utf-8') as f:
            state = json.load(f)
            
        workflow_id = state["workflow_id"]
        self.active_states[workflow_id] = state
        
        logger.info(f"Böngésző állapot betöltve: {filepath}")
        return state
        
    def get_latest_state(self, workflow_id: str) -> Optional[BrowserAutomationState]:
        """
        Visszaadja a legfrissebb állapotot egy adott munkafolyamathoz
        
        Args:
            workflow_id: A munkafolyamat azonosítója
            
        Returns:
            A legfrissebb állapot vagy None, ha nincs
        """
        # Először ellenőrizzük az aktív állapotokat
        if workflow_id in self.active_states:
            return self.active_states[workflow_id]
            
        # Ha nincs az aktív állapotokban, keressük a fájlrendszerben
        files = [f for f in os.listdir(self.storage_dir) 
                if f.startswith(f"{workflow_id}_") and f.endswith(".json")]
        
        if not files:
            return None
            
        # Rendezzük időbélyeg szerint
        files.sort(reverse=True)
        latest_file = os.path.join(self.storage_dir, files[0])
        
        return self.load_state(latest_file)
        
    def record_error(self, state: BrowserAutomationState, error: Exception) -> BrowserAutomationState:
        """
        Rögzít egy hibát az állapotban
        
        Args:
            state: Az aktuális állapot
            error: A keletkezett hiba
            
        Returns:
            A frissített állapot
        """
        updates = {
            "error_state": True,
            "error_details": str(error),
            "error_timestamp": time.time(),
            "retry_count": state.get("retry_count", 0) + 1
        }
        
        return self.update_state(state, updates)
        
    def clear_error(self, state: BrowserAutomationState) -> BrowserAutomationState:
        """
        Törli a hibaállapotot
        
        Args:
            state: Az aktuális állapot
            
        Returns:
            A frissített állapot
        """
        updates = {
            "error_state": False,
            "error_details": None,
            "error_timestamp": None
        }
        
        return self.update_state(state, updates)
        
    def store_extracted_data(self, state: BrowserAutomationState, 
                           data_key: str, 
                           data_value: Any) -> BrowserAutomationState:
        """
        Eltárolja a kinyert adatokat az állapotban
        
        Args:
            state: Az aktuális állapot
            data_key: Az adat kulcsa
            data_value: Az adat értéke
            
        Returns:
            A frissített állapot
        """
        extracted_data = state.get("extracted_data", {}).copy()
        extracted_data[data_key] = data_value
        
        updates = {
            "extracted_data": extracted_data
        }
        
        return self.update_state(state, updates)
        
    def store_search_results(self, state: BrowserAutomationState, 
                           results: List[Dict[str, Any]]) -> BrowserAutomationState:
        """
        Eltárolja a keresési eredményeket az állapotban
        
        Args:
            state: Az aktuális állapot
            results: A keresési eredmények
            
        Returns:
            A frissített állapot
        """
        updates = {
            "search_results": results
        }
        
        return self.update_state(state, updates)
