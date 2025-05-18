"""
DOMListener for Project-S
Integrates robust DOM-based command detection and response sending for AI interfaces (ChatGPT, Claude, Gemini, Copilot).
Adapted from tested logic in dom_handler_test.py.
"""
import time
import logging
import asyncio
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium import webdriver
import os
import subprocess
import threading
import sys

# --- Unicode logging fix for Windows terminals ---
if os.name == 'nt':
    try:
        import ctypes
        # Set Windows console to UTF-8
        ctypes.windll.kernel32.SetConsoleOutputCP(65001)
        # Set PYTHONIOENCODING for subprocesses
        os.environ['PYTHONIOENCODING'] = 'utf-8'
        # Reconfigure sys.stdout and sys.stderr to use utf-8
        if hasattr(sys.stdout, 'reconfigure'):
            sys.stdout.reconfigure(encoding='utf-8')
            sys.stderr.reconfigure(encoding='utf-8')
    except Exception as e:
        pass

# Ensure logger uses UTF-8 encoding for StreamHandler
for handler in logging.root.handlers:
    if hasattr(handler, 'stream') and hasattr(handler.stream, 'reconfigure'):
        try:
            handler.stream.reconfigure(encoding='utf-8')
        except Exception:
            pass

# If no handlers, add a StreamHandler with utf-8 encoding
if not logging.root.handlers:
    handler = logging.StreamHandler(sys.stdout)
    try:
        handler.stream.reconfigure(encoding='utf-8')
    except Exception:
        pass
    logging.root.addHandler(handler)

logger = logging.getLogger("DOM_Listener")

class DOMListener:
    COMMAND_PREFIXES = ("CMD:", "CODE:", "INFO:", "FILE:", "TEST:", "COMMAND:", "S_CMD:", "EXECUTE:", "TASK:")

    def __init__(self, driver):
        self.driver = driver
        self.active_interface = None
        self.last_dom_scan = 0
        self.dom_scan_interval = 0.3
        self.last_command = ""
        self.last_timestamp = 0
        self.command_cooldown = 3
        self.recent_commands = set()
        self.max_recent_commands = 5
        # DOM command listener task
        self._listener_task = None
        # The attribute main.py is looking for
        self.dom_command_listener = None
        # Detect active interface
        self._detect_active_interface()

    def _detect_active_interface(self):
        try:
            if not self.driver:
                logger.warning("No driver available, cannot detect interface")
                self.active_interface = "unknown"
                return

            current_url = self.driver.current_url.lower()
            if "chat.openai.com" in current_url:
                self.active_interface = "chatgpt"
            elif "claude.ai" in current_url:
                self.active_interface = "claude"
            elif "gemini" in current_url or "bard" in current_url:
                self.active_interface = "gemini"
            elif "copilot" in current_url:
                self.active_interface = "copilot"
            else:
                self.active_interface = "unknown"
            logger.info(f"Detected interface: {self.active_interface}")
        except Exception as e:
            logger.error(f"Error detecting interface: {e}")
            self.active_interface = "unknown"

    def detect_commands(self):
        """
        Detect commands in the DOM using multiple strategies.
        
        Supported formats:
        1. [S_COMMAND]{...}[/S_COMMAND] blocks
        2. PREFIX: content format commands (CMD:, CODE:, etc.)
        
        Returns:
            str: The detected command text, or empty string if none found
        """
        now = time.time()
        if now - self.last_dom_scan < self.dom_scan_interval:
            return ""
        
        self.last_dom_scan = now
        try:
            self._detect_active_interface()
        
            last_detected_command = None
            
            # Interface-specific detection strategies
            if self.active_interface == "chatgpt":
                # First look for S_COMMAND blocks
                command = self._detect_s_command_blocks()
                if command:
                    last_detected_command = command
                
                # If no S_COMMAND block, look for other command formats
                if not last_detected_command:
                    for strategy in [self._detect_from_assistant_role, self._detect_from_markdown]:
                        command = strategy()
                        if command:
                            last_detected_command = command
                            break
            
            elif self.active_interface == "claude":
                # Claude-specific detection
                command = self._detect_s_command_blocks()
                if command:
                    last_detected_command = command
                else:
                    command = self._detect_from_claude()
                    if command:
                        last_detected_command = command
            
            elif self.active_interface in ["gemini", "copilot"]:
                # Gemini/Copilot-specific detection
                command = self._detect_s_command_blocks()
                if command:
                    last_detected_command = command
                else:
                    command = self._detect_from_text_base()
                    if command:
                        last_detected_command = command
            
            else:
                # General strategies for all other interfaces
                for strategy in [
                    self._detect_s_command_blocks,
                    self._detect_from_assistant_role, 
                    self._detect_from_text_base, 
                    self._detect_from_markdown, 
                    self._detect_via_javascript
                ]:
                    command = strategy()
                    if command:
                        last_detected_command = command
                        break
            
            # Check if it's a new command
            if last_detected_command and self._is_new_command(last_detected_command, now):
                logger.info(f"New command detected: {last_detected_command[:30]}...")
                return last_detected_command
        except Exception as e:
            logger.error(f"Error in detect_commands: {e}")
        
        return ""

    def _detect_s_command_blocks(self):
        """
        Look for all [S_COMMAND] blocks in the DOM and return the most recent valid one.
        Only blocks with valid JSON and required fields are considered.
        """
        try:
            if not self.driver:
                return ""

            # JavaScript to collect all [S_COMMAND]...[/S_COMMAND] blocks in DOM order
            script = """
            function findAllSCommandBlocks() {
                let blocks = [];
                let elements = document.querySelectorAll('div, p, span, pre, code');
                for (let el of elements) {
                    const content = el.textContent || '';
                    let start = 0;
                    while (true) {
                        let sIdx = content.indexOf('[S_COMMAND]', start);
                        if (sIdx === -1) break;
                        let eIdx = content.indexOf('[/S_COMMAND]', sIdx);
                        if (eIdx === -1) break;
                        let block = content.substring(sIdx, eIdx + 12);
                        blocks.push(block);
                        start = eIdx + 12;
                    }
                }
                // Fallback: search full body text if no blocks found
                if (blocks.length === 0) {
                    const fullText = document.body.textContent || '';
                    let start = 0;
                    while (true) {
                        let sIdx = fullText.indexOf('[S_COMMAND]', start);
                        if (sIdx === -1) break;
                        let eIdx = fullText.indexOf('[/S_COMMAND]', sIdx);
                        if (eIdx === -1) break;
                        let block = fullText.substring(sIdx, eIdx + 12);
                        blocks.push(block);
                        start = eIdx + 12;
                    }
                }
                return blocks;
            }
            return findAllSCommandBlocks();
            """
            results = self.driver.execute_script(script)
            if not results or not isinstance(results, list):
                return ""

            import json, re
            # Validate each block, return the most recent valid one
            for block in reversed(results):
                if '[S_COMMAND]' in block and '[/S_COMMAND]' in block:
                    content = block
                    start_idx = content.find('[S_COMMAND]') + len('[S_COMMAND]')
                    end_idx = content.find('[/S_COMMAND]')
                    if start_idx > 0 and end_idx > start_idx:
                        command_content = content[start_idx:end_idx].strip()
                        # Try normal JSON parse first
                        try:
                            cmd_data = json.loads(command_content)
                        except json.JSONDecodeError:
                            # Try to fix common issues: single quotes, trailing commas, missing braces
                            fixed = command_content
                            fixed = re.sub(r"'", '"', fixed)
                            fixed = re.sub(r',([\s\n]*[}}\]])', r'\1', fixed)
                            if fixed.count('{') > fixed.count('}'):
                                fixed += '}'
                            try:
                                cmd_data = json.loads(fixed)
                            except Exception:
                                continue  # skip invalid block
                        cmd_type = str(cmd_data.get("type", "")).upper()
                        # Only accept CMD or ASK with required fields
                        if cmd_type == "CMD":
                            cmd_val = (
                                cmd_data.get("cmd")
                                or cmd_data.get("command")
                                or cmd_data.get("query")
                                or cmd_data.get("content")
                            )
                            if cmd_val:
                                return block
                        elif cmd_type == "ASK":
                            if cmd_data.get("query") or cmd_data.get("content"):
                                return block
            return ""
        except Exception as e:
            logger.debug(f"Error searching for S_COMMAND blocks: {e}")
            return ""

    def _detect_from_assistant_role(self):
        try:
            if not self.driver:
                return ""
                
            elements = self.driver.find_elements(By.CSS_SELECTOR, "div[data-message-author-role='assistant'] div.markdown")
            for el in reversed(elements):
                text = el.text.strip()
                if text.startswith(self.COMMAND_PREFIXES):
                    return text
        except Exception:
            pass
        return ""

    def _detect_from_text_base(self):
        try:
            if not self.driver:
                return ""
                
            elements = self.driver.find_elements(By.CSS_SELECTOR, "div.text-base")
            for el in reversed(elements):
                text = el.text.strip()
                if text.startswith(self.COMMAND_PREFIXES):
                    return text
        except Exception:
            pass
        return ""

    def _detect_from_markdown(self):
        try:
            if not self.driver:
                return ""
                
            elements = self.driver.find_elements(By.CSS_SELECTOR, ".markdown, .prose")
            for el in reversed(elements):
                text = el.text.strip()
                if text.startswith(self.COMMAND_PREFIXES):
                    return text
        except Exception:
            pass
        return ""

    def _detect_from_claude(self):
        try:
            if not self.driver:
                return ""
                
            elements = self.driver.find_elements(By.CSS_SELECTOR, ".claude-message-content, .message-content")
            for el in reversed(elements):
                text = el.text.strip()
                if text.startswith(self.COMMAND_PREFIXES):
                    return text
            elements = self.driver.find_elements(By.CSS_SELECTOR, ".message[data-message-author-type='ai']")
            for el in reversed(elements):
                text = el.text.strip()
                if text.startswith(self.COMMAND_PREFIXES):
                    return text
        except Exception:
            pass
        return ""

    def _detect_via_javascript(self):
        try:
            if not self.driver:
                return ""
                
            prefixes = list(self.COMMAND_PREFIXES)
            script = f'''
            const prefixes = {str(prefixes)};
            let allTextElements = document.querySelectorAll('div, p, span, pre');
            for (let i = allTextElements.length - 1; i >= 0; i--) {{
                const text = allTextElements[i].textContent.trim();
                for (const prefix of prefixes) {{
                    if (text.startsWith(prefix)) {{
                        return text;
                    }}
                }}
            }}
            return "";
            '''
            return self.driver.execute_script(script)
        except Exception:
            return ""

    def _is_new_command(self, command, now):
        if not command:
            return False
        # Only allow [S_COMMAND] blocks, ignore all prefix-based commands
        if "[S_COMMAND]" not in command:
            return False
        # Forced commands always run even if duplicate
        if "FORCE:" in command[:15]:
            self.last_timestamp = now
            return True
        # --- RESTORE: Only skip if command is exactly the same as last_command ---
        if hasattr(self, 'last_command') and command == self.last_command:
            return False
        self.last_timestamp = now
        return True

    def send_response(self, message):
        """
        Send a response to the AI interface using the appropriate method
        based on the detected interface type.
        Ensures Unicode output is always UTF-8 and replaces problematic characters.
        
        Args:
            message (str): Message text to send
            
        Returns:
            bool: True if successful, False otherwise
        """
        # If no active interface or unknown, try to redetect
        if not self.active_interface or self.active_interface == "unknown":
            self._detect_active_interface()
        
        # Configurable prefix to mark project responses
        response_prefix = "[Project-S] "
        
        # --- Unicode fix: replace problematic characters ---
        try:
            message = message.encode('utf-8', errors='replace').decode('utf-8', errors='replace')
        except Exception:
            pass
        # Optionally, replace common mojibake (GГјlГ¶, etc.) with '?'
        import re
        message = re.sub(r'[\uFFFD\uFFFD]+', '?', message)
        
        # Interface-specific response methods in priority order
        send_methods = []
        
        if self.active_interface == "chatgpt":
            send_methods = [
                self._send_response_to_chatgpt,
                self._send_response_via_selenium,  # Fallback method
            ]
        elif self.active_interface == "claude":
            send_methods = [
                self._send_response_to_claude,
                self._send_response_via_selenium,  # Fallback method
            ]
        elif self.active_interface == "gemini":
            send_methods = [
                self._send_response_to_gemini,
                self._send_response_via_selenium,  # Fallback method
            ]
        elif self.active_interface == "copilot":
            send_methods = [
                self._send_response_to_copilot,
                self._send_response_via_selenium,  # Fallback method
            ]
        else:
            send_methods = [self._send_response_via_selenium]
        
        # Try all methods until one succeeds
        message_with_prefix = response_prefix + message
        
        for send_method in send_methods:
            try:
                success = send_method(message_with_prefix)
                if success:
                    logger.info(f"Response successfully sent to {self.active_interface} interface")
                    return True
            except Exception as e:
                logger.warning(f"Error using {send_method.__name__}: {e}")
                continue
        
        logger.error(f"None of the response methods worked for {self.active_interface} interface")
        return False

    def _send_response_to_chatgpt(self, message):
        return self._send_response_generic(message, [
            "#prompt-textarea", "textarea[data-id='prompt-textarea']", "textarea.m-0", "textarea[placeholder*='Send a message']", "textarea[tabindex='0']"
        ], [
            "button[data-testid='send-button']", "button.absolute.p-1", "button[class*='bottom-right']", "button[type='submit']"
        ])

    def _send_response_to_claude(self, message):
        return self._send_response_generic(message, [
            "textarea[placeholder*='Message Claude']", "textarea.w-full", "textarea.resize-none", "textarea[placeholder*='Send a message']", "textarea.h-full", "[contenteditable='true']"
        ], [
            "button[aria-label='Send message']", "button.rounded-full", "button.absolute.right-", "button[type='submit']"
        ])

    def _send_response_to_gemini(self, message):
        return self._send_response_generic(message, [
            "textarea[placeholder*='Enter your question']", "textarea.input-area", "textarea.message-input", "textarea.gemini-input"
        ], [
            "button[aria-label='Submit']", "button.send-button", "button.mdc-icon-button", "button[type='submit']"
        ])

    def _send_response_to_copilot(self, message):
        return self._send_response_generic(message, [
            "textarea.input-area", "textarea[placeholder*='Ask me anything']", "textarea.copilot-input", "textarea[aria-label='Ask Copilot']"
        ], [
            "button.send-button", "button[aria-label='Send']", "button.action-button", "button[type='submit']"
        ])

    def _send_response_via_selenium(self, message):
        return self._send_response_generic(message, [
            "#prompt-textarea", "textarea[data-id='prompt-textarea']", "textarea.m-0", "textarea[placeholder*='Send a message']", "textarea[placeholder*='Message']", "textarea[tabindex='0']", "textarea"
        ], [
            "button[data-testid='send-button']", "button[aria-label='Send message']", "button.absolute.p-1", "button[class*='bottom-right']", "button[type='submit']"
        ])

    def _send_response_generic(self, message, textarea_selectors, button_selectors):
        if not self.driver:
            logger.error("No driver available for sending response")
            return False
            
        message = self._sanitize_text(message)
        
        textarea = self._find_element_with_selectors(textarea_selectors)
        if not textarea:
            logger.error("Textarea not found for response send")
            return False
        
        if not self._insert_text_with_fallbacks(textarea, message):
            logger.error("Failed to insert text into textarea")
            return False
            
        if not self._click_button_with_fallbacks(button_selectors, textarea):
            logger.error("Failed to click send button")
            return False
            
        return True

    def _sanitize_text(self, text):
        emoji_map = {'✔️': '[OK]', '🔍': '[SEARCH]', '⭐': '[STAR]', '🚀': '[WRITE]', '⏳': '[TIMER]', '✅': '[CHECK]', '❌': '[X]', '⚠️': '[WARNING]', '💫': '[SPARKLE]', '🔥': '[FIRE]', '🌟': '[GLOW]', '🌍': '[EARTH]'}
        for emoji, replacement in emoji_map.items():
            text = text.replace(emoji, replacement)
        return ''.join(c for c in text if ord(c) < 0x10000)

    def _find_element_with_selectors(self, selectors):
        if not self.driver:
            return None
            
        for selector in selectors:
            try:
                element = WebDriverWait(self.driver, 5).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                )
                if element:
                    return element
            except Exception:
                continue
        return None

    def _insert_text_with_fallbacks(self, textarea, message):
        if not self.driver:
            return False
            
        try:
            self.driver.execute_script("arguments[0].scrollIntoView({ behavior: 'smooth', block: 'center' });", textarea)
            time.sleep(0.5)
            try:
                textarea.clear()
                time.sleep(0.2)
            except Exception:
                try:
                    self.driver.execute_script("arguments[0].value = '';", textarea)
                except Exception:
                    pass
            success = False
            try:
                textarea.send_keys(message)
                success = True
            except Exception:
                pass
            if not success:
                try:
                    self.driver.execute_script("""
                        const textarea = arguments[0];
                        const message = arguments[1];
                        textarea.value = message;
                        textarea.dispatchEvent(new Event('input', { bubbles: true }));
                        textarea.dispatchEvent(new Event('change', { bubbles: true }));
                    """, textarea, message)
                    success = True
                except Exception:
                    pass
            if not success:
                try:
                    import pyperclip
                    pyperclip.copy(message)
                    textarea.send_keys(Keys.CONTROL, 'v')
                    time.sleep(0.2)
                    success = True
                except Exception:
                    pass
            return success
        except Exception:
            return False

    def _click_button_with_fallbacks(self, button_selectors, textarea=None):
        if not self.driver:
            return False
            
        try:
            send_button = None
            for selector in button_selectors:
                try:
                    send_button = WebDriverWait(self.driver, 5).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                    )
                    if send_button:
                        break
                except:
                    continue
            if send_button:
                try:
                    self.driver.execute_script("arguments[0].click();", send_button)
                    time.sleep(0.5)
                    return True
                except Exception:
                    try:
                        send_button.click()
                        time.sleep(0.5)
                        return True
                    except Exception:
                        try:
                            from selenium.webdriver.common.action_chains import ActionChains
                            actions = ActionChains(self.driver)
                            actions.move_to_element(send_button).click().perform()
                            time.sleep(0.5)
                            return True
                        except Exception:
                            pass
            if textarea:
                try:
                    textarea.send_keys(Keys.RETURN)
                    time.sleep(0.5)
                    return True
                except Exception:
                    pass
            return False
        except Exception:
            return False

    def _reconnect_browser(self):
        """
        Reconnect to the browser if the connection is lost or invalid.
        """
        try:
            logger.info("Attempting to reconnect to browser...")
            
            # Close old driver if it exists
            try:
                if hasattr(self, 'driver') and self.driver:
                    self.driver.quit()
            except Exception as e:
                logger.debug(f"Error closing driver: {e}")
                
            # Wait a bit before reconnecting
            time.sleep(2)
            
            # Initialize new driver
            self.driver = get_default_driver()
            
            if self.driver:
                # Detect interface
                self._detect_active_interface()
                logger.info(f"Successfully reconnected to browser, interface: {self.active_interface}")
                return True
            else:
                logger.error("Failed to reconnect to browser")
                return False
                
        except Exception as e:
            logger.error(f"Reconnection error: {e}")
            return False
    
    def _safely_execute_browser_operation(self, operation_func, *args, **kwargs):
        """
        Safely execute a browser operation and automatically reconnect on failure.
        
        Args:
            operation_func: The function to execute
            *args, **kwargs: Arguments to pass to the function
            
        Returns:
            The function's return value, or None on error
        """
        max_retries = 2
        
        for attempt in range(max_retries):
            try:
                # Check if browser is still valid
                if self.driver:
                    try:
                        # Simple check: query the URL
                        current_url = self.driver.current_url
                    except Exception as e:
                        # If error, driver is probably invalid
                        if "invalid session id" in str(e).lower():
                            logger.warning("Invalid browser session, reconnecting...")
                            self._reconnect_browser()
                        else:
                            logger.error(f"Browser operation error: {e}")
                
                # Execute operation
                return operation_func(*args, **kwargs)
                
            except Exception as e:
                if "invalid session id" in str(e).lower() and attempt < max_retries - 1:
                    logger.warning(f"Invalid browser session, reconnecting ({attempt+1}/{max_retries})...")
                    self._reconnect_browser()
                else:
                    logger.error(f"Browser operation error: {e}")
                    if attempt >= max_retries - 1:
                        return None
        
        return None

    # --- API for main.py compatibility ---
    async def start(self):
        """
        Start the DOMListener and initialize DOM command monitoring
        """
        logger.info("Starting DOMListener...")

        if self._listener_task is not None:
            logger.warning("DOMListener already running, restarting...")
            await self.stop()

        # Initialize DOM command listener
        try:
            # Define the dom_command_listener method
            async def dom_command_listener_task():
                logger.info("DOM command monitor started.")
                while True:
                    try:
                        # Search for commands using detection strategies
                        command = self.detect_commands()
                        # --- RESTORE: Only skip if command is None or same as last_command ---
                        if command and command != self.last_command:
                            logger.info(f"DOM command detected: {command[:50]}...")
                            result = await self.process_dom_command(command)
                            self.last_command = command  # Frissítjük az utolsó végrehajtott parancsot
                            # If there's a response, send it back to the interface
                            if result and isinstance(result, dict):
                                response_text = f"[Project-S Response]\n{str(result)}"
                                success = self.send_response(response_text)
                                if success:
                                    logger.info("DOM response successfully sent")
                                else:
                                    logger.error("Failed to send DOM response")
                    except Exception as e:
                        logger.error(f"Error during DOM command monitoring: {str(e)}")
                    # Wait a short time until next check
                    await asyncio.sleep(1)

            # Start periodic command monitor task
            self.dom_command_listener = dom_command_listener_task
            self._listener_task = asyncio.create_task(dom_command_listener_task())

            logger.info("DOMListener successfully started")
            return True

        except Exception as e:
            logger.error(f"Error starting DOMListener: {str(e)}")
            return False

    async def stop(self):
        """
        Stop the DOMListener and terminate running processes
        """
        logger.info("Stopping DOMListener...")
        
        try:
            # Stop listener task if running
            if self._listener_task and not self._listener_task.done():
                self._listener_task.cancel()
                logger.info("DOM monitor task stopped")
            
            # Close WebDriver if needed
            if hasattr(self, 'driver') and self.driver:
                try:
                    # Just disconnect, don't close browser
                    # driver.quit() would close the browser, which may not be desired
                    pass
                except Exception as e:
                    logger.warning(f"Error closing WebDriver: {str(e)}")
            
            logger.info("DOMListener successfully stopped")
            return True
            
        except Exception as e:
            logger.error(f"Error stopping DOMListener: {str(e)}")
            return False

    async def process_dom_command(self, dom_command):
        """
        Process a DOM command - extract command data,
        validate format, and execute the appropriate action.
        Only [S_COMMAND] blocks are accepted as commands.
        """
        logger.info(f"Processing DOM command: {dom_command[:50]}...")
        import json
        import re
        try:
            # --- Only process [S_COMMAND] blocks ---
            if "[S_COMMAND]" in dom_command and "[/S_COMMAND]" in dom_command:
                start_idx = dom_command.find("[S_COMMAND]") + len("[S_COMMAND]")
                end_idx = dom_command.find("[/S_COMMAND]")
                if start_idx > 0 and end_idx > start_idx:
                    command_content = dom_command[start_idx:end_idx].strip()
                    # Try normal JSON parse first
                    try:
                        cmd_data = json.loads(command_content)
                    except json.JSONDecodeError as e:
                        # Try to fix common issues: single quotes, trailing commas, missing braces
                        fixed = command_content
                        fixed = re.sub(r"'", '"', fixed)
                        fixed = re.sub(r',([\s\n]*[}}\]])', r'\1', fixed)
                        if fixed.count('{') > fixed.count('}'):
                            fixed += '}'
                        try:
                            cmd_data = json.loads(fixed)
                            logger.warning(f"JSON parse fixed: {e}")
                        except Exception as e2:
                            logger.error(f"JSON parse failed after fix: {e2}")
                            return {"error": f"Érvénytelen JSON parancs: {e2}", "raw": command_content}
                    cmd_type = str(cmd_data.get("type", "")).upper()
                    schemas = {
                        "CMD": {"required": ["cmd"], "optional": ["type", "query", "content", "options"]},
                        "ASK": {"required": ["query"], "optional": ["type", "options"]},
                    }
                    schema = schemas.get(cmd_type, {"required": [], "optional": []})
                    command = {"type": cmd_type}
                    for key in schema["required"] + schema["optional"]:
                        if key in cmd_data:
                            command[key] = cmd_data[key]
                    if cmd_type == "CMD" and "cmd" not in command:
                        command["cmd"] = (
                            cmd_data.get("cmd")
                            or cmd_data.get("command")
                            or cmd_data.get("query")
                            or cmd_data.get("content")
                        )
                    if cmd_type == "ASK" and "query" not in command:
                        command["query"] = cmd_data.get("content")
                    for k, v in command.items():
                        if isinstance(v, (int, float)):
                            command[k] = str(v)
                    missing = [k for k in schema["required"] if not command.get(k)]
                    if missing:
                        return {"error": f"Hiányzó kötelező mezők: {missing}", "raw": command_content}
                    from core.command_router import router
                    return await router.route_command(command)
            # If not an [S_COMMAND] block, ignore
            logger.warning("Ignored non-[S_COMMAND] command.")
            return None
        except Exception as e:
            logger.error(f"Error processing DOM command: {str(e)}")
            return {"status": "error", "message": f"Processing error: {str(e)}"}


def get_default_driver():
    """
    Initialize Selenium WebDriver with appropriate settings.
    Connect to an existing browser if possible, otherwise start a new one.
    """
    try:
        # First try to connect to a running browser
        options = webdriver.ChromeOptions()
        options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
        
        try:
            # Chrome path from environment variable or default
            if os.environ.get("CHROME_DRIVER_PATH"):
                chrome_driver_path = os.environ.get("CHROME_DRIVER_PATH")
                service = webdriver.chrome.service.Service(executable_path=chrome_driver_path)
                driver = webdriver.Chrome(service=service, options=options)
            else:
                # If no path specified, auto-detect
                driver = webdriver.Chrome(options=options)
                
            logger.info("Successfully connected to running Chrome browser")
            return driver
            
        except Exception as e:
            logger.warning(f"Couldn't connect to running browser: {e}")
            
            # If connection failed, start a new browser
            def start_chrome_process():
                chrome_path = os.environ.get("CHROME_PATH", "chrome")
                cmd = [
                    chrome_path,
                    "--remote-debugging-port=9222",
                    "--user-data-dir=./chrome-profile",
                    "--no-first-run",
                    "--no-default-browser-check"
                ]
                subprocess.Popen(cmd)
            
            # Start browser in separate thread to not block main thread
            thread = threading.Thread(target=start_chrome_process)
            thread.daemon = True  # Thread will terminate when main program exits
            thread.start()
            
            # Wait for browser to start
            time.sleep(3)
            
            # Try to connect again
            options = webdriver.ChromeOptions()
            options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
            driver = webdriver.Chrome(options=options)
            
            logger.info("New Chrome browser started and connected")
            return driver
            
    except Exception as e:
        # If all else fails, try running a headless browser
        logger.error(f"Error initializing WebDriver: {e}")
        logger.info("Trying headless Chrome browser...")
        
        try:
            options = webdriver.ChromeOptions()
            options.add_argument("--headless=new")  # Chrome 109+ required for new headless mode
            options.add_argument("--disable-gpu")
            options.add_argument("--window-size=1920,1080")
            driver = webdriver.Chrome(options=options)
            logger.info("Headless Chrome browser successfully initialized")
            return driver
        except Exception as e2:
            logger.error(f"Couldn't initialize headless browser either: {e2}")
            return None

# Singleton instance for main.py compatibility
try:
    # If environment variable is set, skip driver creation
    if os.environ.get("DOM_LISTENER_DISABLE") == "1":
        logger.warning("DOMListener creation skipped (DOM_LISTENER_DISABLE=1)")
        dom_listener = None
    else:
        driver = get_default_driver()
        if driver:
            dom_listener = DOMListener(driver)
            logger.info("DOMListener singleton successfully created")
        else:
            # If driver creation failed, initialize with None
            logger.warning("Failed to initialize WebDriver, DOMListener with limited functionality")
            dom_listener = DOMListener(None)
except Exception as e:
    dom_listener = None
    logger.error(f"Failed to create DOMListener singleton: {e}")
