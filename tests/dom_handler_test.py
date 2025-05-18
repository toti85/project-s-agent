"""
AI Interface DOM Handler Test Script
-----------------------------------
Ez a script a különböző AI interfészek (ChatGPT, Claude) DOM-kezelését teszteli.
Lehetővé teszi parancsok észlelését és válaszok visszaküldését az interfészbe.

Használat:
1. Állítsd be a CHROME_PATH és CHROME_DRIVER_PATH változókat
2. Futtasd a scriptet
3. Kövesd a terminál utasításokat a teszteléshez
"""

import os
import time
import json
import logging
import asyncio
import threading
import subprocess
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service

# Konfiguráció
CHROME_PATH = r"С:\S\chatgpt_selenium_automation\chrome-win64\chrome.exe"
CHROME_DRIVER_PATH = r"C:\S\chatgpt_selenium_automation\chromedriver-win64\chromedriver.exe"
LOG_FILE = "dom_handler_test.log"

# Naplózás beállítása
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE, encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("DOM_Handler_Test")

class AIDOMHandler:
    """
    AI interfészek DOM-kezelésére szolgáló teszt osztály.
    """
    
    # Felismerhető parancs prefixek
    COMMAND_PREFIXES = ("CMD:", "CODE:", "INFO:", "FILE:", "TEST:")
    
    def __init__(self, chrome_path, chrome_driver_path):
        self.chrome_path = chrome_path
        self.chrome_driver_path = chrome_driver_path
        self.driver = None
        
        # Teljesítmény optimalizálás
        self.last_dom_scan = 0
        self.dom_scan_interval = 0.3  # másodperc
        
        # Parancs követés
        self.last_command = ""
        self.last_timestamp = 0
        self.command_cooldown = 3  # másodperc
        self.recent_commands = set()
        self.max_recent_commands = 5
        
        # Új: Aktív interfész típus követése
        self.active_interface = None  # 'chatgpt', 'claude', 'gemini', stb.
        
        # Új: Működési mód
        self.operation_mode = "manual"  # vagy "auto"
        
        # Initialize browser
        self._initialize_browser()
        
    def _initialize_browser(self):
        """Böngésző kapcsolat inicializálása"""
        try:
            logger.info("Böngésző kapcsolat inicializálása...")
            
            # Próbálunk kapcsolódni egy futó böngészőhöz
            chrome_options = webdriver.ChromeOptions()
            chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
            
            service = Service(executable_path=self.chrome_driver_path)
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            
            logger.info(f"Sikeresen kapcsolódtunk a böngészőhöz: {self.driver.title}")
            self._detect_active_interface()
            
        except Exception as e:
            # Ha a kapcsolódás nem sikerül, új böngészőt indítunk
            logger.warning(f"Nem sikerült kapcsolódni a böngészőhöz: {e}")
            self._launch_new_browser()
    
    def _launch_new_browser(self):
        """Új Chrome példány indítása távoli hibakereséssel"""
        try:
            logger.info("Új böngésző példány indítása...")
            url = "https://chat.openai.com"  # Alapértelmezett, később megváltoztatható
            port = 9222
            
            def open_chrome():
                subprocess.Popen([
                    self.chrome_path,
                    f'--remote-debugging-port={port}',
                    '--user-data-dir=remote-profile',
                    url
                ])
            
            threading.Thread(target=open_chrome).start()
            time.sleep(3)  # Várunk, amíg a böngésző elindul
            
            # Kapcsolódás az új böngészőhöz
            chrome_options = webdriver.ChromeOptions()
            chrome_options.add_experimental_option("debuggerAddress", f"127.0.0.1:{port}")
            
            service = Service(executable_path=self.chrome_driver_path)
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            
            logger.info("Böngésző elindítva. Várakozás a bejelentkezésre...")
            input("Nyomj Enter-t, ha már bejelentkeztél az AI interfészbe...")
            self._detect_active_interface()
            
        except Exception as e:
            logger.error(f"Nem sikerült elindítani a böngészőt: {e}")
            raise
    
    def _reconnect_browser(self):
        """Újracsatlakozás a böngészőhöz érvénytelen munkamenet esetén"""
        try:
            logger.info("Újracsatlakozási kísérlet a böngészőhöz...")
            
            # Régi driver bezárása, ha létezik
            try:
                if hasattr(self, 'driver'):
                    self.driver.quit()
            except:
                pass  # Ignoráljuk a bezárási hibákat
                
            # Várunk egy kicsit az újracsatlakozás előtt
            time.sleep(2)
            
            # Újracsatlakozási kísérlet
            chrome_options = webdriver.ChromeOptions()
            chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
            
            service = Service(executable_path=self.chrome_driver_path)
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            
            logger.info(f"Sikeresen újracsatlakoztunk a böngészőhöz: {self.driver.title}")
            self._detect_active_interface()
            
            # Oldal frissítése, ha szükséges
            try:
                self.driver.refresh()
                time.sleep(2)  # Várunk, amíg az oldal újratöltődik
                logger.info("Böngésző oldal frissítve")
            except:
                logger.warning("Nem sikerült frissíteni a böngésző oldalt")
                
        except Exception as e:
            logger.error(f"Újracsatlakozás sikertelen: {e}")
            # Ha az újracsatlakozás sikertelen, megpróbálunk új böngészőt indítani
            try:
                logger.info("Új böngésző példány indítási kísérlet...")
                self._launch_new_browser()
            except Exception as e2:
                logger.error(f"Nem sikerült új böngészőt indítani: {e2}")
                raise

    def _detect_active_interface(self):
        """Az aktív AI interfész típusának detektálása az URL alapján"""
        try:
            current_url = self.driver.current_url.lower()
            
            if "chat.openai.com" in current_url:
                self.active_interface = "chatgpt"
                logger.info("ChatGPT interfész detektálva")
            elif "claude.ai" in current_url:
                self.active_interface = "claude"
                logger.info("Claude interfész detektálva")
            elif "gemini" in current_url or "bard" in current_url:
                self.active_interface = "gemini"
                logger.info("Gemini interfész detektálva")
            elif "copilot" in current_url:
                self.active_interface = "copilot"
                logger.info("Copilot interfész detektálva")
            else:
                self.active_interface = "unknown"
                logger.warning(f"Ismeretlen AI interfész: {current_url}")
            
            return self.active_interface
        except Exception as e:
            logger.error(f"Hiba az aktív interfész detektálásakor: {e}")
            return "unknown"

    def navigate_to_interface(self, interface_type):
        """Navigálás a megadott AI interfészhez"""
        if not self.driver:
            logger.error("A böngésző nincs inicializálva")
            return False
            
        try:
            url = {
                "chatgpt": "https://chat.openai.com",
                "claude": "https://claude.ai",
                "gemini": "https://gemini.google.com",
                "copilot": "https://copilot.microsoft.com"
            }.get(interface_type.lower())
            
            if not url:
                logger.error(f"Ismeretlen interfész típus: {interface_type}")
                return False
                
            logger.info(f"Navigálás: {url}")
            self.driver.get(url)
            time.sleep(3)  # Várunk, amíg az oldal betöltődik
            
            # Ellenőrizzük, hogy a navigálás sikeres volt-e
            current_url = self.driver.current_url.lower()
            success = interface_type.lower() in current_url
            
            if success:
                self.active_interface = interface_type.lower()
                logger.info(f"Sikeres navigálás az interfészhez: {interface_type}")
            else:
                logger.warning(f"Navigálás sikertelen. Aktuális URL: {current_url}")
                
            return success
        except Exception as e:
            logger.error(f"Hiba a navigálás során: {e}")
            return False

    def detect_commands(self):
        """
        Parancsok felismerése a DOM-ban több stratégia használatával.
        Visszaadja a legutolsó érvényes parancsot, vagy üres stringet ha nincs ilyen.
        """
        command = ""
        now = time.time()
        
        try:
            # Ha túl gyakran hívjuk, akkor kihagyjuk ezt a detektálást
            if now - self.last_dom_scan < self.dom_scan_interval:
                return ""
                
            self.last_dom_scan = now
            
            # Aktív interfész típus frissítése (URL váltás esetére)
            self._detect_active_interface()
            
            last_detected_command = None
            
            # Stratégia 1: Az asszisztens szerepű üzenetek keresése (ChatGPT-ben működik)
            command = self._detect_from_assistant_role()
            if command:
                last_detected_command = command
                
            # Stratégia 2: A text-base osztály keresése (Copilot-ban működik)
            command = self._detect_from_text_base()
            if command:
                # Ha különböző parancsot találtunk, az lehet, hogy újabb
                if command != last_detected_command:
                    last_detected_command = command
                
            # Stratégia 3: Markdown tartalom keresése
            command = self._detect_from_markdown()
            if command:
                if command != last_detected_command:
                    last_detected_command = command
                
            # Stratégia 4: JavaScript közvetlen végrehajtása az összes tartalom átvizsgálásához
            command = self._detect_via_javascript()
            if command:
                if command != last_detected_command:
                    last_detected_command = command
                    
            # Stratégia 5: Claude-specifikus keresés
            if self.active_interface == "claude":
                command = self._detect_from_claude()
                if command and command != last_detected_command:
                    last_detected_command = command
            
            # Csak akkor dolgozzuk fel a parancsot, ha átmegy az érvényesítésen
            if last_detected_command and self._is_new_command(last_detected_command, now):
                return last_detected_command
            
        except Exception as e:
            if "Invalid session id" in str(e):
                logger.warning("Érvénytelen böngésző munkamenet, újracsatlakozási kísérlet...")
                self._reconnect_browser()
            else:
                logger.error(f"Hiba a parancsok észlelése során: {e}")
        
        return ""
    
    def _detect_from_assistant_role(self):
        """Parancsok észlelése az asszisztens szerepű elemekből (ChatGPT)"""
        try:
            elements = self.driver.find_elements(By.CSS_SELECTOR, "div[data-message-author-role='assistant'] div.markdown")
            for el in reversed(elements):  # A legújabbaktól kezdve
                text = el.text.strip()
                if text.startswith(self.COMMAND_PREFIXES):
                    return text
        except Exception as e:
            logger.debug(f"Hiba az asszisztens szerepű elemek detektálása során: {e}")
        return ""
    
    def _detect_from_text_base(self):
        """Parancsok észlelése a text-base osztályú elemekből (Copilot)"""
        try:
            elements = self.driver.find_elements(By.CSS_SELECTOR, "div.text-base")
            for el in reversed(elements):
                text = el.text.strip()
                if text.startswith(self.COMMAND_PREFIXES):
                    return text
        except Exception as e:
            logger.debug(f"Hiba a text-base elemek detektálása során: {e}")
        return ""
    
    def _detect_from_markdown(self):
        """Parancsok észlelése a markdown elemekből (általános)"""
        try:
            elements = self.driver.find_elements(By.CSS_SELECTOR, ".markdown, .prose")
            for el in reversed(elements):
                text = el.text.strip()
                if text.startswith(self.COMMAND_PREFIXES):
                    return text
        except Exception as e:
            logger.debug(f"Hiba a markdown elemek detektálása során: {e}")
        return ""
    
    def _detect_from_claude(self):
        """Claude-specifikus detektálás"""
        try:
            # Claude sajátos selectorok
            elements = self.driver.find_elements(By.CSS_SELECTOR, ".claude-message-content, .message-content")
            for el in reversed(elements):
                text = el.text.strip()
                if text.startswith(self.COMMAND_PREFIXES):
                    return text
                    
            # Alternatív módszer Claude-hoz
            elements = self.driver.find_elements(By.CSS_SELECTOR, ".message[data-message-author-type='ai']")
            for el in reversed(elements):
                text = el.text.strip()
                if text.startswith(self.COMMAND_PREFIXES):
                    return text
        except Exception as e:
            logger.debug(f"Hiba a Claude-specifikus detektálás során: {e}")
        return ""
    
    def _detect_via_javascript(self):
        """JavaScript használata a parancsok kereséséhez a DOM-ban"""
        try:
            script = """
            const prefixes = ["CMD:", "CODE:", "INFO:", "FILE:", "TEST:"];
            let allTextElements = document.querySelectorAll('div, p, span, pre');
            
            for (let i = allTextElements.length - 1; i >= 0; i--) {
                const text = allTextElements[i].textContent.trim();
                for (const prefix of prefixes) {
                    if (text.startsWith(prefix)) {
                        return text;
                    }
                }
            }
            return "";
            """
            
            return self.driver.execute_script(script)
        except Exception as e:
            logger.debug(f"Hiba a JavaScript detektálás során: {e}")
        return ""
    
    def _is_new_command(self, command, now):
        """Ellenőrzi, hogy egy parancs új-e és fel kell-e dolgozni"""
        if not command:
            return False
            
        # Ellenőrizzük, hogy a parancs érvényes prefixszel kezdődik-e
        if not command.startswith(self.COMMAND_PREFIXES):
            return False
            
        # Megszerezzük a megfelelő prefixet
        prefix = next((p for p in self.COMMAND_PREFIXES if command.startswith(p)), "")
        
        # Túl rövid parancsokat (csak prefix) ignoráljuk
        if len(command.strip()) <= len(prefix):
            return False
            
        # Kényszerített parancsok mindig lefutnak, ismétlődés esetén is
        if "FORCE:" in command[:15]:
            # Timestamp frissítése
            self.last_timestamp = now
            return True
            
        # Cooldown ellenőrzése minden parancsra
        if (now - self.last_timestamp) <= self.command_cooldown:
            return False
        
        # Ellenőrizzük, hogy a parancs nemrég volt-e feldolgozva
        if command in self.recent_commands:
            return False
        
        # Hozzáadjuk a nemrég feldolgozott parancsokhoz és frissítjük a timestamp-et
        self.recent_commands.add(command)
        if len(self.recent_commands) > self.max_recent_commands:
            self.recent_commands.pop()
            
        # Timestamp frissítése, ha ténylegesen feldolgozzuk a parancsot
        self.last_timestamp = now
        
        return True

    def send_response(self, message):
        """
        Válasz küldése az AI interfészbe a megfelelő módszerrel,
        az aktív interfész típusától függően.
        """
        if self.active_interface == "chatgpt":
            return self.send_response_to_chatgpt(message)
        elif self.active_interface == "claude":
            return self.send_response_to_claude_improved(message)
        elif self.active_interface == "gemini":
            return self.send_response_to_gemini(message)
        elif self.active_interface == "copilot":
            return self.send_response_to_copilot(message)
        else:
            # Alapértelmezett metódus, ha az interfész típusa ismeretlen
            return self.send_response_via_selenium(message)

    def send_response_to_chatgpt(self, message):
        """ChatGPT-specifikus válasz küldési metódus"""
        try:
            logger.info("Válasz küldése a ChatGPT interfészbe...")
            
            # Sanitizáljuk a szöveget
            message = self._sanitize_text(message)
            
            # Prefix hozzáadása a ChatGPT-nek
            prefix = "[DOM-Test] "
            message = prefix + message
            
            # Textarea keresése ChatGPT-specifikus selectorokkal
            textarea_selectors = [
                "#prompt-textarea",  # ChatGPT elsődleges selector
                "textarea[data-id='prompt-textarea']",
                "textarea.m-0",  # Új ChatGPT specifikus osztály
                "textarea[placeholder*='Send a message']",
                "textarea[tabindex='0']"
            ]
            
            textarea = self._find_element_with_selectors(textarea_selectors)
            if not textarea:
                raise Exception("Nem találtuk a ChatGPT textarea elemet")

            # Textarea láthatóvá tétele és szöveg beillesztése
            self._insert_text_with_fallbacks(textarea, message)
            
            # Küldés gomb keresése és kattintás
            button_selectors = [
                "button[data-testid='send-button']",
                "button.absolute.p-1",
                "button[class*='bottom-right']",
                "button[type='submit']"
            ]
            
            return self._click_button_with_fallbacks(button_selectors, textarea)
            
        except Exception as e:
            logger.error(f"Hiba a ChatGPT válasz küldése során: {e}")
            return False

    def send_response_to_claude(self, message):
        """Claude-specifikus válasz küldési metódus"""
        try:
            logger.info("Válasz küldése a Claude interfészbe...")
            
            # Sanitizáljuk a szöveget
            message = self._sanitize_text(message)
            
            # Prefix hozzáadása a Claude-nak
            prefix = "[DOM-Test] "
            message = prefix + message
            
            # Textarea keresése Claude-specifikus selectorokkal
            textarea_selectors = [
                "textarea[placeholder*='Message Claude']",
                "textarea.w-full",
                "textarea.resize-none",
                "textarea[placeholder*='Send a message']",
                "textarea.h-full"
            ]
            
            textarea = self._find_element_with_selectors(textarea_selectors)
            if not textarea:
                raise Exception("Nem találtuk a Claude textarea elemet")

            # Textarea láthatóvá tétele és szöveg beillesztése
            self._insert_text_with_fallbacks(textarea, message)
            
            # Küldés gomb keresése és kattintás
            button_selectors = [
                "button[aria-label='Send message']",
                "button.rounded-full",
                "button.absolute.right-",
                "button[type='submit']"
            ]
            
            return self._click_button_with_fallbacks(button_selectors, textarea)
            
        except Exception as e:
            logger.error(f"Hiba a Claude válasz küldése során: {e}")
            return False

    def send_response_to_claude_improved(self, message):
        """Továbbfejlesztett Claude-specifikus válasz küldési metódus"""
        # Improved Claude send: inject text via JS, then click via Selenium
        logger.info("Válasz küldése a Claude interfészbe JavaScript injektálással és Selenium fallbackkel...")
        # Sanitizáljuk a szöveget
        message = self._sanitize_text(message)
        # JS to set textarea content
        js_set = '''
        (function(msg) {
            let textarea = document.querySelector('textarea') || document.querySelector('[contenteditable="true"]');
            if (!textarea) return false;
            if (textarea.tagName === 'TEXTAREA') {
                textarea.value = msg;
            } else {
                textarea.textContent = msg;
            }
            textarea.dispatchEvent(new Event('input', { bubbles: true }));
            return true;
        })(arguments[0]);
        '''
        try:
            injected = self.driver.execute_script(js_set, message)
            logger.info(f"JS injection success: {injected}")
        except Exception as e:
            logger.error(f"JS injection failed: {e}")
        # wait a moment for DOM update
        time.sleep(0.5)
        # Claude-specific selectors
        textarea_selectors = [
            "textarea[placeholder*='Message Claude']",
            "textarea.w-full", "textarea.resize-none",
            "textarea[placeholder*='Send a message']", "textarea.h-full",
            "[contenteditable='true']"
        ]
        button_selectors = [
            "button[aria-label='Send message']",
            "button.rounded-full", "button.absolute.right-", "button[type='submit']"
        ]
        # find textarea and click send via Selenium
        textarea = self._find_element_with_selectors(textarea_selectors)
        if textarea:
            success = self._click_button_with_fallbacks(button_selectors, textarea)
            if success:
                logger.info("Selenium click success for Claude send")
                return True
        logger.error("Nem sikerült elküldeni a választ Claude-n")
        return False

    def send_response_to_gemini(self, message):
        """Gemini-specifikus válasz küldési metódus"""
        try:
            logger.info("Válasz küldése a Gemini interfészbe...")
            
            # Sanitizáljuk a szöveget
            message = self._sanitize_text(message)
            
            # Prefix hozzáadása a Gemini-nek
            prefix = "[DOM-Test] "
            message = prefix + message
            
            # Textarea keresése Gemini-specifikus selectorokkal
            textarea_selectors = [
                "textarea[placeholder*='Enter your question']",
                "textarea.input-area",
                "textarea.message-input",
                "textarea.gemini-input"
            ]
            
            textarea = self._find_element_with_selectors(textarea_selectors)
            if not textarea:
                raise Exception("Nem találtuk a Gemini textarea elemet")

            # Textarea láthatóvá tétele és szöveg beillesztése
            self._insert_text_with_fallbacks(textarea, message)
            
            # Küldés gomb keresése és kattintás
            button_selectors = [
                "button[aria-label='Submit']",
                "button.send-button",
                "button.mdc-icon-button",
                "button[type='submit']"
            ]
            
            return self._click_button_with_fallbacks(button_selectors, textarea)
            
        except Exception as e:
            logger.error(f"Hiba a Gemini válasz küldése során: {e}")
            return False

    def send_response_to_copilot(self, message):
        """Copilot-specifikus válasz küldési metódus"""
        try:
            logger.info("Válasz küldése a Copilot interfészbe...")
            
            # Sanitizáljuk a szöveget
            message = self._sanitize_text(message)
            
            # Prefix hozzáadása a Copilot-nak
            prefix = "[DOM-Test] "
            message = prefix + message
            
            # Textarea keresése Copilot-specifikus selectorokkal
            textarea_selectors = [
                "textarea.input-area",
                "textarea[placeholder*='Ask me anything']",
                "textarea.copilot-input",
                "textarea[aria-label='Ask Copilot']"
            ]
            
            textarea = self._find_element_with_selectors(textarea_selectors)
            if not textarea:
                raise Exception("Nem találtuk a Copilot textarea elemet")

            # Textarea láthatóvá tétele és szöveg beillesztése
            self._insert_text_with_fallbacks(textarea, message)
            
            # Küldés gomb keresése és kattintás
            button_selectors = [
                "button.send-button",
                "button[aria-label='Send']",
                "button.action-button",
                "button[type='submit']"
            ]
            
            return self._click_button_with_fallbacks(button_selectors, textarea)
            
        except Exception as e:
            logger.error(f"Hiba a Copilot válasz küldése során: {e}")
            return False

    def send_response_via_selenium(self, message):
        """
        Általános válasz küldési metódus Selenium segítségével.
        Több fallback stratégiát használ a megbízható válasz küldéshez.
        """
        max_retries = 3
        for attempt in range(max_retries):
            try:
                logger.info(f"Válasz küldése Selenium segítségével (kísérlet {attempt + 1}/{max_retries})...")
                
                # Szöveg sanitizálása az emojik és speciális karakterek kezelésére
                message = self._sanitize_text(message)
                
                # Rendszer azonosító prefix hozzáadása
                message = "[DOM-Test] " + message
                
                # Textarea keresése a legspecifikusabb selektorokkal először
                textarea_selectors = [
                    "#prompt-textarea",  # ChatGPT elsődleges selector
                    "textarea[data-id='prompt-textarea']",
                    "textarea.m-0",  # ChatGPT specifikus osztály
                    "textarea[placeholder*='Send a message']",  # Placeholder szöveg
                    "textarea[placeholder*='Message']",  # Claude
                    "textarea[tabindex='0']",  # Hozzáférhetőségi attribútum
                    "textarea"  # Általános fallback
                ]
                
                textarea = None
                for selector in textarea_selectors:
                    try:
                        textarea = WebDriverWait(self.driver, 5).until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                        )
                        if textarea:
                            logger.info(f"Textarea megtalálva a következő selectorral: {selector}")
                            break
                    except:
                        continue
                
                if not textarea:
                    raise Exception("Nem találtuk a textarea elemet")

                # Textarea láthatóvá tétele és szöveg beillesztés
                result = self._insert_text_with_fallbacks(textarea, message)
                if not result:
                    raise Exception("Nem sikerült beilleszteni a szöveget")
                
                # Küldés gomb keresése és kattintás
                button_selectors = [
                    "button[data-testid='send-button']",  # ChatGPT
                    "button[aria-label='Send message']",  # Claude
                    "button.absolute.p-1",
                    "button[class*='bottom-right']",
                    "button[type='submit']"
                ]
                
                result = self._click_button_with_fallbacks(button_selectors, textarea)
                if result:
                    return True
                else:
                    raise Exception("Nem sikerült a küldés gombra kattintani")

            except Exception as e:
                if "invalid session id" in str(e).lower():
                    logger.error("Érvénytelen session ID, újracsatlakozási kísérlet...")
                    try:
                        self._reconnect_browser()
                        if attempt < max_retries - 1:
                            logger.info("Böngésző újracsatlakoztatva, válasz újraküldése...")
                            continue
                    except Exception as re:
                        logger.error(f"Nem sikerült újracsatlakozni a böngészőhöz: {re}")
                
                logger.error(f"Hiba a válasz küldése során (kísérlet {attempt + 1}): {e}")
                if attempt < max_retries - 1:
                    logger.info(f"Újrapróbálkozás 1 másodperc múlva...")
                    time.sleep(1)
                    continue
                else:
                    logger.error("Minden próbálkozás sikertelen")
                    return False
        
        return False

    def _sanitize_text(self, text):
        """Szöveg sanitizálása az emojik és speciális karakterek kezelésére"""
        try:
            # Problémás emojik helyettesítése szöveges megfelelőikkel
            emoji_map = {
                '✔️': '[OK]',
                '🔍': '[SEARCH]',
                '⭐': '[STAR]',
                '🚀': '[ROCKET]',
                '📝': '[WRITE]',
                '⏳': '[TIMER]',
                '✅': '[CHECK]',
                '❌': '[X]',
                '⚠️': '[WARNING]',
                '💫': '[SPARKLE]',
                '🔥': '[FIRE]',
                '🌟': '[GLOW]',
                '🌍': '[EARTH]'
            }
            
            for emoji, replacement in emoji_map.items():
                text = text.replace(emoji, replacement)
            
            # Nem-BMP karakterek eltávolítása
            return ''.join(c for c in text if ord(c) < 0x10000)
        except:
            return text

    def _find_element_with_selectors(self, selectors):
        """Elem keresése több selector próbálásával"""
        for selector in selectors:
            try:
                element = WebDriverWait(self.driver, 5).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                )
                if element:
                    logger.info(f"Elem találat: {selector}")
                    return element
            except Exception as e:
                logger.debug(f"Nem találtuk az elemet a {selector} selectorral: {e}")
        return None

    def _insert_text_with_fallbacks(self, textarea, message):
        """Szöveg beillesztése több módszerrel, fallback-ekkel"""
        try:
            # Először biztosítjuk, hogy a textarea látható és elérhető
            self.driver.execute_script("""
                arguments[0].scrollIntoView({ behavior: 'smooth', block: 'center' });
            """, textarea)
            time.sleep(0.5)  # Várunk egy kicsit a görgetés után
            
            # Textarea törlése először
            try:
                textarea.clear()
                time.sleep(0.2)
            except Exception as e:
                logger.warning(f"Nem sikerült törölni a textarea tartalmát: {e}")
                try:
                    self.driver.execute_script("arguments[0].value = '';", textarea)
                except Exception as e2:
                    logger.error(f"Nem sikerült törölni a textarea tartalmát JavaScript-tel sem: {e2}")
            
            success = False
            
            # 1. Próba: közvetlen send_keys módszer (legmegbízhatóbb)
            try:
                textarea.send_keys(message)
                logger.info("Szöveg beillesztve a send_keys módszerrel")
                success = True
            except Exception as e:
                logger.warning(f"Nem sikerült a send_keys módszerrel beilleszteni a szöveget: {e}")
            
            # 2. Próba: JavaScript megközelítés
            if not success:
                try:
                    self.driver.execute_script("""
                        const textarea = arguments[0];
                        const message = arguments[1];
                        textarea.value = message;
                        textarea.dispatchEvent(new Event('input', { bubbles: true }));
                        textarea.dispatchEvent(new Event('change', { bubbles: true }));
                    """, textarea, message)
                    logger.info("Szöveg beillesztve JavaScript módszerrel")
                    success = True
                except Exception as e:
                    logger.warning(f"Nem sikerült JavaScript-tel beilleszteni a szöveget: {e}")
            
            # 3. Utolsó próbálkozás: vágólap használata
            if not success:
                try:
                    import pyperclip
                    pyperclip.copy(message)
                    textarea.send_keys(Keys.CONTROL, 'v')
                    time.sleep(0.2)
                    logger.info("Szöveg beillesztve vágólap módszerrel")
                    success = True
                except Exception as e:
                    logger.error(f"Nem sikerült a vágólapról beilleszteni: {e}")
            
            return success
        
        except Exception as e:
            logger.error(f"Hiba a szöveg beillesztése során: {e}")
            return False

    def _click_button_with_fallbacks(self, button_selectors, textarea=None):
        """Küldés gombra kattintás több módszerrel, fallback-ekkel"""
        try:
            # Gomb keresése
            send_button = None
            for selector in button_selectors:
                try:
                    send_button = WebDriverWait(self.driver, 5).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                    )
                    if send_button:
                        logger.info(f"Küldés gomb megtalálva a következő selectorral: {selector}")
                        break
                except:
                    continue
            
            if send_button:
                # 1. Próba: JavaScript kattintás
                try:
                    self.driver.execute_script("arguments[0].click();", send_button)
                    logger.info("Sikeresen kattintottunk a küldés gombra JavaScript-tel")
                    time.sleep(0.5)
                    return True
                except Exception as e:
                    logger.warning(f"JavaScript kattintás sikertelen, normál kattintás próbálása: {e}")
                    
                    # 2. Próba: Normál kattintás
                    try:
                        send_button.click()
                        logger.info("Sikeresen kattintottunk a küldés gombra normál kattintással")
                        time.sleep(0.5)
                        return True
                    except Exception as e2:
                        logger.warning(f"Normál kattintás sikertelen, ActionChains próbálása: {e2}")
                        
                        # 3. Próba: ActionChains
                        try:
                            from selenium.webdriver.common.action_chains import ActionChains
                            actions = ActionChains(self.driver)
                            actions.move_to_element(send_button).click().perform()
                            logger.info("Sikeresen kattintottunk a küldés gombra ActionChains-szel")
                            time.sleep(0.5)
                            return True
                        except Exception as e3:
                            logger.error(f"Minden kattintási módszer sikertelen: {e3}")
            
            # Ha egyik gomb kattintás sem működött, próbáljuk az Enter billentyűt
            if textarea:
                try:
                    textarea.send_keys(Keys.RETURN)
                    logger.info("Válasz elküldve Enter billentyűvel")
                    time.sleep(0.5)
                    return True
                except Exception as e:
                    logger.error(f"Enter billentyűvel sem sikerült küldeni: {e}")
            
            return False
            
        except Exception as e:
            logger.error(f"Hiba a gombra kattintás során: {e}")
            return False

    def run_test_mode(self):
        """
        Teszt mód futtatása - parancsok detektálása és válaszküldés tesztelése
        manuális irányítással
        """
        print("\n==== AI Interface DOM Handler Test Mode ====")
        print(f"Aktív interfész: {self.active_interface}")
        print("Parancsok:")
        print("  1: Detektálási teszt")
        print("  2: Válasz küldési teszt")
        print("  3: Interfész váltás")
        print("  4: Automatikus figyelés indítása")
        print("  0: Kilépés")
        
        while True:
            choice = input("\nVálassz műveletet (0-4): ")
            
            if choice == "0":
                print("Kilépés...")
                break
                
            elif choice == "1":
                print("\n--- Parancs detektálási teszt ---")
                print("Figyelés 30 másodpercig, vagy amíg parancsot nem találunk...")
                
                start_time = time.time()
                while time.time() - start_time < 30:
                    command = self.detect_commands()
                    if command:
                        print(f"\nParancs észlelve: {command}")
                        break
                    print(".", end="", flush=True)
                    time.sleep(0.5)
                else:
                    print("\nNem észleltünk parancsot 30 másodperc alatt.")
            
            elif choice == "2":
                print("\n--- Válasz küldési teszt ---")
                message = input("Írd be a küldendő üzenetet: ")
                if not message:
                    message = "Ez egy automatikus teszt üzenet."
                
                prefix = None
                if self.active_interface:
                    prefix = f"[DOM Test - {self.active_interface.upper()}]"
                
                if prefix:
                    message = f"{prefix} {message}"
                    
                success = self.send_response(message)
                if success:
                    print("Üzenet sikeresen elküldve!")
                else:
                    print("Nem sikerült elküldeni az üzenetet.")
            
            elif choice == "3":
                print("\n--- Interfész váltás ---")
                print("Elérhető interfészek:")
                print("  1: ChatGPT")
                print("  2: Claude")
                print("  3: Gemini")
                print("  4: Copilot")
                
                interface_choice = input("\nVálassz interfészt (1-4): ")
                interface_map = {
                    "1": "chatgpt",
                    "2": "claude",
                    "3": "gemini",
                    "4": "copilot"
                }
                
                if interface_choice in interface_map:
                    interface = interface_map[interface_choice]
                    success = self.navigate_to_interface(interface)
                    if success:
                        print(f"Sikeresen átváltottunk a következő interfészre: {interface}")
                    else:
                        print(f"Nem sikerült átváltani a következő interfészre: {interface}")
                else:
                    print("Érvénytelen választás.")
            
            elif choice == "4":
                print("\n--- Automatikus figyelés indítása ---")
                print("Figyelés 300 másodpercig (5 perc)...")
                print("Nyomj CTRL+C-t a megszakításhoz.")
                
                try:
                    start_time = time.time()
                    while time.time() - start_time < 300:
                        command = self.detect_commands()
                        if command:
                            print(f"\nParancs észlelve: {command}")
                            print("Válasz küldése...")
                            
                            response = f"Parancs feldolgozva: {command[:50]}..."
                            success = self.send_response(response)
                            
                            if success:
                                print("Válasz sikeresen elküldve!")
                            else:
                                print("Nem sikerült elküldeni a választ.")
                        
                        time.sleep(0.5)
                    print("\nAutomatikus figyelés befejezve.")
                except KeyboardInterrupt:
                    print("\nFigyelés megszakítva a felhasználó által.")
            
            else:
                print("Érvénytelen választás, próbáld újra.")

    async def run_async_monitor(self):
        """Aszinkron parancs monitor futtatása"""
        print("\n==== Aszinkron parancs monitor indítása ====")
        print(f"Aktív interfész: {self.active_interface}")
        print("A CTRL+C billentyűkombináció megszakítja a figyelést.")
        
        try:
            while True:
                # Parancs detektálás
                command = self.detect_commands()
                if command:
                    print(f"\nParancs észlelve: {command}")
                    
                    # Egyszerű echo válasz a parancsra
                    response = f"Parancs fogadva: {command[:50]}..."
                    success = self.send_response(response)
                    
                    if success:
                        print("Válasz elküldve.")
                    else:
                        print("Nem sikerült elküldeni a választ.")
                
                # Rövid várakozás a következő ellenőrzésig
                await asyncio.sleep(0.5)
                
        except KeyboardInterrupt:
            print("\nFigyelés megszakítva a felhasználó által.")
        except Exception as e:
            print(f"\nHiba a monitor futtatása közben: {e}")

    def close(self):
        """Erőforrások felszabadítása"""
        try:
            if self.driver:
                self.driver.quit()
                logger.info("Böngésző bezárva")
        except Exception as e:
            logger.error(f"Hiba a böngésző bezárása közben: {e}")


async def main():
    """Fő függvény a DOM handler teszteléséhez"""
    # Chrome útvonalak - pontosan a megadott útvonalakkal
    CHROME_PATH = r"С:\S\chatgpt_selenium_automation\chrome-win64\chrome.exe"
    CHROME_DRIVER_PATH = r"C:\S\chatgpt_selenium_automation\chromedriver-win64\chromedriver.exe"
    
    print(f"AI Interface DOM Handler Test Script v1.0")
    print("=========================================")
    
    # Konfigurálás
    print("\nBöngésző útvonalak ellenőrzése...")
    
    # Chrome létezésének ellenőrzése
    if not os.path.exists(CHROME_PATH):
        chrome_path = input(f"Chrome nem található itt: {CHROME_PATH}\nKérlek add meg a Chrome böngésző helyes útvonalát: ")
        if chrome_path:
            CHROME_PATH = chrome_path
    
    # ChromeDriver létezésének ellenőrzése
    if not os.path.exists(CHROME_DRIVER_PATH):
        driver_path = input(f"ChromeDriver nem található itt: {CHROME_DRIVER_PATH}\nKérlek add meg a ChromeDriver helyes útvonalát: ")
        if driver_path:
            CHROME_DRIVER_PATH = driver_path
    
    print(f"Chrome útvonal: {CHROME_PATH}")
    print(f"ChromeDriver útvonal: {CHROME_DRIVER_PATH}")
    
    # DOM handler inicializálása
    handler = None
    try:
        print("\nBöngésző inicializálása...")
        handler = AIDOMHandler(CHROME_PATH, CHROME_DRIVER_PATH)
        
        # Teszt mód futtatása
        handler.run_test_mode()
        
    except Exception as e:
        print(f"Hiba a DOM handler inicializálása vagy futtatása közben: {e}")
    finally:
        if handler:
            handler.close()
            print("\nDOM handler tesztelés befejezve.")


if __name__ == "__main__":
    # Aszinkron futtatás, hogy az async/await funkciók működjenek
    asyncio.run(main())