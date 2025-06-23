"""
Project-S Modell Menedzser
-------------------------
Ez a modul kezeli az AI modell kiválasztását, váltást és a modellek teljesítményének nyomon követését.
"""

import os
import logging
import asyncio
import json
from typing import Dict, Any, List, Optional, Union, Tuple
import time
from datetime import datetime
from pathlib import Path

from integrations.multi_model_ai_client import multi_model_ai_client
from integrations.persistent_state_manager import persistent_state_manager
from integrations.core_execution_bridge import core_execution_bridge

# Tool integration for actual task execution
logger = logging.getLogger(__name__)

try:
    from tools.tool_registry import tool_registry
    TOOLS_AVAILABLE = True
    logger.info("Tool registry imported successfully - tools available for execution")
except ImportError as e:
    TOOLS_AVAILABLE = False
    logger.warning(f"Tool registry not available: {e}")

# Intelligent workflow integration
try:
    from integrations.intelligent_workflow_integration import (
        intelligent_workflow_orchestrator,
        process_with_intelligent_workflow
    )
    INTELLIGENT_WORKFLOWS_AVAILABLE = True
    logger.info("✅ Intelligent workflow integration imported successfully")
except ImportError as e:
    INTELLIGENT_WORKFLOWS_AVAILABLE = False
    logger.warning(f"⚠️ Intelligent workflow integration not available: {e}")

class ModelManager:
    """
    Modell menedzser osztály a modellek kezeléséhez és intelligens modellválasztáshoz.
    """
    
    def __init__(self):
        """Modell menedzser inicializálása."""
        self.ai_client = multi_model_ai_client
        
        # Modell metrikák
        self.model_metrics = {}
          # Alapértelmezett modell (config-ból betöltve)
        self.default_model = self._get_default_model_from_config()
        
        # Modell használat követése
        self.model_usage = {}
        
        # Utolsó modellváltás ideje
        self.last_model_switch_time = None
        
        # Modell teljesítmény cache
        self.performance_cache_path = Path(__file__).parent.parent / "memory" / "model_performance_cache.json"
        self.performance_cache = self._load_performance_cache()
        
        # Hozzáférés a perzisztens állapotkezelőhöz
        self.state_manager = persistent_state_manager
        
        logger.info("Modell menedzser inicializálva")
        
    def _load_performance_cache(self) -> Dict[str, Any]:
        """Betölti a modell teljesítmény cache-t, ha létezik."""
        try:
            if self.performance_cache_path.exists():
                with open(self.performance_cache_path, 'r', encoding='utf-8') as file:
                    return json.load(file)
            return {}
        except Exception as e:
            logger.error(f"Hiba a teljesítmény cache betöltése közben: {e}")
            return {}
    
    def _save_performance_cache(self) -> None:
        """Elmenti a modell teljesítmény cache-t."""
        try:
            # Biztosítjuk, hogy a könyvtár létezik
            self.performance_cache_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(self.performance_cache_path, 'w', encoding='utf-8') as file:
                json.dump(self.performance_cache, file, indent=2)
                
        except Exception as e:
            logger.error(f"Hiba a teljesítmény cache mentése közben: {e}")
    
    async def get_available_models(self) -> List[Dict[str, Any]]:
        """
        Visszaadja az elérhető modellek listáját.
        
        Returns:
            List[Dict]: Az elérhető modellek listája
        """
        return self.ai_client.list_available_models()
        
    def determine_task_type(self, query: str) -> str:
        """
        Meghatározza a bemeneti lekérdezés típusát.
        
        Args:
            query: A felhasználói lekérdezés
            
        Returns:
            str: A feladat típusa (pl. "tervezés", "kódolás", stb.)
        """
        # Itt később komplett feladat típus detektáló logikát lehet implementálni
          # Egyszerű kulcsszó alapú detektálás (magyar és angol támogatással)
        keywords = {
            "tervezés": ["tervezés", "tervezzünk", "tervezd meg", "építsd fel", "architektúra", "planning", "plan", "design", "architecture"],
            "kódolás": ["kód", "programozás", "implementáció", "fejlesztés", "scriptet", "code", "coding", "programming", "development", "script"],
            "dokumentáció": ["dokumentáció", "magyarázd el", "dokumentumd", "írj leírást", "documentation", "document", "explain", "describe"],
            "adatelemzés": ["elemezd", "adatelemzés", "adatfeldolgozás", "statisztika", "analysis", "analyze", "data analysis", "statistics"],
            "kreatív_írás": ["kreatív", "történet", "írj egy", "fogalmazás", "creative", "story", "writing", "compose"],
            "fordítás": ["fordítsd", "fordítás", "angolul", "magyarul", "translate", "translation"],
            "összefoglalás": ["összefoglalás", "összegzés", "röviden foglald", "tömöríts", "summary", "summarize", "brief"],
            "gyors_válasz": ["gyors", "rövid", "gyorsan", "quick", "fast", "short", "briefly"]
        }
        
        # Legjobb egyezés keresése
        task_matches = {}
        query_lower = query.lower()
        
        for task_type, task_keywords in keywords.items():
            matches = sum(1 for keyword in task_keywords if keyword.lower() in query_lower)
            if matches > 0:
                task_matches[task_type] = matches
                
        if task_matches:
            # Legtöbb egyezés kiválasztása
            best_task = max(task_matches.items(), key=lambda x: x[1])[0]
            logger.info(f"Feladat típus meghatározva: {best_task}")
            return best_task
            
        # Alapértelmezettként feltételezzük, hogy gyors válasz
        logger.info("Nem ismert fel specifikus feladat típust, 'gyors_válasz' használata")
        return "gyors_válasz"
    
    async def select_model_for_task(self, query: str, task_type: Optional[str] = None) -> str:
        """
        Kiválaszt egy megfelelő modellt a feladathoz.
        
        Args:
            query: A felhasználói lekérdezés
            task_type: Opcionális explicit feladat típus
            
        Returns:
            str: A kiválasztott modell azonosítója
        """
        # Ha nincs explicit feladat típus, detektáljuk
        if task_type is None:
            task_type = self.determine_task_type(query)
        # Fallback: ha nincs ilyen metódus, alapértelmezett modell
        if hasattr(self.ai_client, 'suggest_model_for_task'):
            suggested_model = self.ai_client.suggest_model_for_task(task_type)
        else:
            suggested_model = self.default_model
        logger.info(f"A(z) '{task_type}' feladat típushoz a(z) '{suggested_model}' modellt választottuk")
        return suggested_model
    
    def record_model_performance(self, 
                              model_id: str, 
                              task_type: str, 
                              response_time: float, 
                              success: bool = True) -> None:
        """
        Rögzíti egy modell teljesítményét.
        
        Args:
            model_id: A modell azonosítója
            task_type: A feladat típusa
            response_time: A válaszidő másodpercben
            success: Sikeres volt-e a kérés
        """
        # Ha a modell még nem szerepel a teljesítmény adatbázisban, adjuk hozzá
        if model_id not in self.performance_cache:
            self.performance_cache[model_id] = {}
            
        # Ha az adott feladattípushoz még nincs adat, inicializáljuk
        if task_type not in self.performance_cache[model_id]:
            self.performance_cache[model_id][task_type] = {
                "request_count": 0,
                "success_count": 0,
                "failure_count": 0,
                "total_response_time": 0,
                "avg_response_time": 0,
                "last_used": datetime.now().isoformat()
            }
            
        # Frissítjük a statisztikákat
        stats = self.performance_cache[model_id][task_type]
        stats["request_count"] += 1
        if success:
            stats["success_count"] += 1
        else:
            stats["failure_count"] += 1
            
        stats["total_response_time"] += response_time
        stats["avg_response_time"] = stats["total_response_time"] / stats["request_count"]
        stats["last_used"] = datetime.now().isoformat()
        
        # Elmentjük a frissített cache-t
        self._save_performance_cache()
            
    async def execute_task_with_model(self, 
                                    query: str,
                                    system_message: Optional[str] = None,
                                    model: Optional[str] = None,
                                    task_type: Optional[str] = None,
                                    temperature: Optional[float] = None) -> Dict[str, Any]:
        """
        Végrehajt egy feladatot a legmegfelelőbb modellel vagy a megadott modellel.
        
        Args:
            query: A felhasználói lekérdezés
            system_message: Opcionális rendszerüzenet
            model: Explicit modell azonosító, ha meg van adva
            task_type: Explicit feladat típus, ha meg van adva 
            temperature: Opcionális hőmérséklet beállítás
            
        Returns:
            Dict: A válasz szótár a tartalommal és metaadatokkal
        """
        # Ha nincs explicit feladat típus, meghatározzuk
        if task_type is None:
            task_type = self.determine_task_type(query)
            
        # Ha nincs explicit modell, kiválasztjuk
        if model is None:
            model = await self.select_model_for_task(query, task_type)
              # Mérjük a válaszidőt
        start_time = time.time()
        success = True
        
        try:
            # Végrehajtjuk a feladatot
            result = await self.ai_client.generate_response(
                prompt=query,
                system_message=system_message,
                model=model,
                task_type=task_type,
                temperature=temperature
            )
            
        except Exception as e:
            logger.error(f"Hiba a modell végrehajtása közben ({model}): {e}")
            success = False
            
            # Visszaesés az alapértelmezett modellre
            logger.info(f"Visszaesés az alapértelmezett modellre ({self.default_model})")
            try:
                result = await self.ai_client.generate_response(
                    prompt=query,
                    system_message=system_message,
                    model=self.default_model,
                    task_type=task_type,
                    temperature=temperature
                )
                model = self.default_model
            except Exception as fallback_e:
                logger.error(f"Hiba a visszaesési modell végrehajtása közben: {fallback_e}")
                result = None  # Explicit None meghatározás
                model = self.default_model
        
        # Kiszámoljuk a válaszidőt
        end_time = time.time()
        response_time = end_time - start_time
        
        # Rögzítjük a teljesítményt
        self.record_model_performance(model, task_type, response_time, success)
        
        # Ha a result None, string vagy dict, mindent kezelünk
        if result is None:
            result = {
                "response": "No response received",
                "model": model,
                "task_type": task_type,
                "success": False,
                "response_time": response_time,
                "error": "Response was None"
            }
        elif isinstance(result, str):
            result = {
                "response": result,
                "model": model,
                "task_type": task_type,
                "success": success,
                "response_time": response_time
            }
        elif isinstance(result, dict):
            # Hozzáadjuk a válaszidőt a válaszhoz
            result["response_time"] = response_time
            result["model"] = model
            result["task_type"] = task_type
        else:
            # Egyéb típusok esetén string reprezentációt használunk
            result = {
                "response": str(result),
                "model": model,
                "task_type": task_type,
                "success": success,
                "response_time": response_time
            }
        
        return result
    
    async def run_task_with_multiple_models(self, 
                                         query: str,
                                         system_message: Optional[str] = None,
                                         models: List[str] = [],
                                         task_type: Optional[str] = None,
                                         temperature: Optional[float] = None) -> Dict[str, Any]:
        """
        Végrehajt egy feladatot több különböző modellel.
        
        Args:
            query: A felhasználói lekérdezés
            system_message: Opcionális rendszerüzenet
            models: A használandó modellek listája
            task_type: Explicit feladat típus, ha meg van adva
            temperature: Opcionális hőmérséklet beállítás
            
        Returns:
            Dict: A válaszok szótára modell azonosítókkal
        """
        # Ha nincs explicit feladat típus, meghatározzuk
        if task_type is None:
            task_type = self.determine_task_type(query)
            
        # Ha nincs megadva modellek, akkor javaslatot kérünk
        if not models:
            # Ha a feladathoz tartoznak ajánlott modellek a konfigban, használjuk azokat
            task_models = self.ai_client.config.get("task_model_mapping", {}).get(task_type, [])
            if task_models:
                models = task_models[:2]  # Első 2 ajánlott modell használata 
            else:
                # Különben használjuk az alapértelmezettet és egy másikat
                models = [self.default_model, "claude-3-sonnet"]
                
        # Párhuzamosan futtatjuk a lekérdezéseket minden modellel
        tasks = []
        for model in models:
            tasks.append(self.execute_task_with_model(
                query=query,
                system_message=system_message,
                model=model,
                task_type=task_type,
                temperature=temperature
            ))
            
        # Várjuk meg az összes feladat befejezését
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Feldolgozzuk az eredményeket
        model_responses = {}
        for model, result in zip(models, results):
            if isinstance(result, Exception):
                model_responses[model] = {
                    "error": True,
                    "message": str(result),
                    "model": model
                }
            else:
                model_responses[model] = result
                
        return {
            "task_type": task_type,
            "models_used": models,
            "responses": model_responses
        }
    
    async def execute_task_with_tools(self, 
                                     query: str,
                                     system_message: Optional[str] = None,
                                     model: Optional[str] = None,
                                     task_type: Optional[str] = None,
                                     temperature: Optional[float] = None) -> Dict[str, Any]:
        """
        🔥 KRITIKUS JAVÍTÁS: Végrehajtja a feladatot AI tervezéssel ÉS valódi tool végrehajtással.
        
        Ez a metódus hidalja át az AI válaszok és a valódi tool végrehajtások közötti hézagot.
        
        Args:
            query: A felhasználói lekérdezés
            system_message: Opcionális rendszerüzenet
            model: Explicit modell azonosító
            task_type: Explicit feladat típus
            temperature: Opcionális hőmérséklet beállítás
            
        Returns:
            Dict: AI válasz + valódi tool végrehajtások eredménye
        """
        if not TOOLS_AVAILABLE:
            logger.warning("Tools not available, falling back to AI-only response")
            return await self.execute_task_with_model(query, system_message, model, task_type, temperature)
        
        # 1. FÁZIS: AI Elemzés és Tool Tervezés
        planning_prompt = f"""
        Elemezd ezt a feladatot és határozd meg, milyen konkrét tools-okat kell használni:
        
        FELADAT: {query}
        
        Elérhető tools: {list(tool_registry.tool_classes.keys()) if tool_registry else []}
        
        Válaszolj ebben a formátumban:
        ELEMZÉS: [rövid elemzés]
        TOOLS_NEEDED: [tool1, tool2, tool3]
        PARAMETERS: 
        - tool1: {{param1: value1, param2: value2}}
        - tool2: {{param1: value1}}
        EXECUTION_ORDER: [tool1, tool2, tool3]
        
        Csak azokat a tools-okat használd, amik a listában vannak!
        """
        
        planning_result = await self.execute_task_with_model(
            query=planning_prompt,
            system_message="Te egy task elemző és tool planner vagy. Legyél specifikus a tool paraméterekkel.",
            model=model,
            task_type="planning"
        )
        
        # 2. FÁZIS: Tool Paraméterek Kinyerése
        ai_response = planning_result.get("content", "")
        tools_executed = []
        
        try:
            # Betöltjük a tools-okat
            await tool_registry.load_tools()
            
            # Egyszerű parsing a tool nevekhez (ezt később lehet javítani)
            lines = ai_response.split('\n')
            tools_to_execute = []
            
            for line in lines:
                if line.startswith('TOOLS_NEEDED:'):
                    tools_part = line.replace('TOOLS_NEEDED:', '').strip()
                    # Kivesszük a tool neveket
                    tools_part = tools_part.replace('[', '').replace(']', '')
                    tool_names = [t.strip() for t in tools_part.split(',') if t.strip()]
                    tools_to_execute = tool_names
                    break
            
            logger.info(f"Tools to execute: {tools_to_execute}")
            
            # 3. FÁZIS: Valódi Tool Végrehajtás
            for tool_name in tools_to_execute:
                tool_name_clean = tool_name.strip()
                
                if tool_name_clean in tool_registry.tool_classes:
                    try:
                        tool_instance = tool_registry.get_tool(tool_name_clean)
                          # Egyszerű paraméter generálás a feladat alapján
                        if "FileWriteTool" in tool_name_clean and ("fájl" in query.lower() or "file" in query.lower() or "írj" in query.lower()):
                            # Fájl írás - intelligens fájlnév kinyerés
                            filename = self._extract_filename_from_query(query)
                            content = f"Project-S végrehajtás eredménye:\n{query}\n\nLétrehozva: {datetime.now()}"
                            
                            result = await tool_instance.execute(path=filename, content=content)
                            tools_executed.append({
                                "tool": tool_name_clean,
                                "parameters": {"path": filename, "content": content[:50] + "..."},
                                "result": result,
                                "success": result.get("success", False)
                            })
                            
                        elif "FileReadTool" in tool_name_clean:
                            # Próbáljunk olvasni egy létező fájlt
                            import os
                            for filename in ["project_s_output.txt", "README.md", "requirements.txt"]:
                                if os.path.exists(filename):
                                    result = await tool_instance.execute(path=filename)
                                    tools_executed.append({
                                        "tool": tool_name_clean,
                                        "parameters": {"path": filename},
                                        "result": result,
                                        "success": result.get("success", False)
                                    })
                                    break
                                    
                        elif "SystemCommandTool" in tool_name_clean:
                            # Biztonságos parancs végrehajtás
                            safe_commands = {
                                "lista": "dir",
                                "list": "dir", 
                                "files": "dir",
                                "hello": "echo Hello from Project-S",
                                "test": "echo Tool execution working!"
                            }
                            
                            command = "echo Tool execution successful!"
                            for keyword, cmd in safe_commands.items():
                                if keyword in query.lower():
                                    command = cmd
                                    break
                            
                            result = await tool_instance.execute(command=command)
                            tools_executed.append({
                                "tool": tool_name_clean,
                                "parameters": {"command": command},
                                "result": result,
                                "success": result.get("success", False)
                            })
                            
                        else:
                            logger.info(f"Tool {tool_name_clean} requires specific parameter handling")
                            
                    except Exception as e:
                        logger.error(f"Error executing tool {tool_name_clean}: {e}")
                        tools_executed.append({
                            "tool": tool_name_clean,
                            "error": str(e),
                            "success": False
                        })
                else:
                    logger.warning(f"Tool {tool_name_clean} not found in registry")
            
        except Exception as e:
            logger.error(f"Error in tool execution phase: {e}")
        
        # 4. FÁZIS: Eredmény Összegzés
        summary_prompt = f"""
        Eredeti feladat: {query}
        
        AI tervezés: {ai_response[:200]}...
        
        Végrehajtott tools: {len(tools_executed)}
        Tool eredmények: {[t.get('success', False) for t in tools_executed]}
        
        Készíts egy rövid összegzést: mi történt valójában, milyen fájlok/műveletek jöttek létre.
        """
        
        summary_result = await self.execute_task_with_model(
            query=summary_prompt,
            system_message="Készíts rövid, faktikus összegzést a végrehajtott műveletekről.",
            model=model,
            task_type="summary"
        )
        
        # Teljes eredmény visszaadása
        return {
            "ai_planning": planning_result,
            "tools_executed": tools_executed,
            "tools_count": len(tools_executed),
            "tools_successful": len([t for t in tools_executed if t.get('success', False)]),
            "summary": summary_result,
            "execution_type": "AI_PLUS_TOOLS",  # Jelzi, hogy ez valódi végrehajtás volt
            "response_time": planning_result.get("response_time", 0)
        }
    
    async def get_model_performance_stats(self, model_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Visszaadja a modell(ek) teljesítmény statisztikáit.
        
        Args:
            model_id: Opcionális modell azonosító, ha csak egy modellre vagyunk kíváncsiak
            
        Returns:
            Dict: A modellek teljesítmény statisztikái
        """
        if model_id:
            # Ha csak egy modellet kérünk
            if model_id in self.performance_cache:
                return {model_id: self.performance_cache[model_id]}
            return {model_id: "Nincs teljesítmény adat a modellhez"}
            
        # Minden modellhez visszaadjuk a statisztikákat
        return self.performance_cache

    async def execute_task_with_model_in_session(self, 
                                         session_id: str,
                                         query: str,
                                         system_message: Optional[str] = None,
                                         model: Optional[str] = None,
                                         task_type: Optional[str] = None,
                                         temperature: Optional[float] = None,
                                         persist_history: bool = True) -> Dict[str, Any]:
        """
        Végrehajtja a feladatot egy adott modellel, egy adott munkamenetben,
        opcionálisan mentve a beszélgetés történetét.
        
        Args:
            session_id: A munkamenet azonosítója
            query: A felhasználói lekérdezés
            system_message: Opcionális rendszerüzenet
            model: Opcionális modell azonosító (ha nincs megadva, kiválasztásra kerül)
            task_type: Opcionális feladat típus
            temperature: Opcionális hőmérséklet érték
            persist_history: Ha True, a beszélgetés bekerül a perzisztens tárolóba
            
        Returns:
            Dict: A válasz szótár a tartalommal és metaadatokkal
        """
        # Az előző beszélgetések betöltése a munkamenetből
        conversation_history = []
        if persist_history:
            conversation_history = await self.state_manager.get_conversation_history(session_id)
        
        # Ha nincs explicit feladat típus, meghatározzuk
        if task_type is None:
            task_type = self.determine_task_type(query)
            
        # Ha nincs explicit modell, kiválasztjuk
        if model is None:
            model = await self.select_model_for_task(query, task_type)
        
        # Ha van beszélgetési előzmény, hozzáadjuk a prompt elejéhez
        enhanced_prompt = query
        if conversation_history:
            # Az utolsó néhány beszélgetés hozzáadása kontextusként
            recent_history = conversation_history[-5:]  # Utolsó 5 beszélgetés
            context = "\n".join([
                f"{msg['role']}: {msg['content']}" 
                for msg in recent_history
            ])
            enhanced_prompt = f"Előzmények:\n{context}\n\nAktuális kérdés:\n{query}"
            
        # Mérjük a válaszidőt
        start_time = time.time()
        success = True
        
        try:
            # Végrehajtjuk a feladatot
            result = await self.ai_client.generate_response(
                prompt=enhanced_prompt,
                system_message=system_message,
                model=model,
                task_type=task_type,
                temperature=temperature
            )
            
        except Exception as e:
            logger.error(f"Hiba a modell végrehajtása közben ({model}): {e}")
            success = False
            
            # Visszaesés az alapértelmezett modellre
            logger.info(f"Visszaesés az alapértelmezett modellre ({self.default_model})")
            result = await self.ai_client.generate_response(
                prompt=enhanced_prompt,
                system_message=system_message,
                model=self.default_model,
                task_type=task_type,
                temperature=temperature
            )
            model = self.default_model
        
        # Kiszámoljuk a válaszidőt
        end_time = time.time()
        response_time = end_time - start_time
        
        # Rögzítjük a teljesítményt
        self.record_model_performance(
            model_id=model,
            task_type=task_type,
            response_time=response_time,
            success=success
        )
          # A válaszok mentése a perzisztens tárolóba, ha szükséges
        if persist_history:
            # Felhasználói üzenet mentése
            await self.state_manager.add_conversation_entry(
                session_id=session_id, 
                role="user", 
                content=query,
                metadata={"task_type": task_type}
            )
            
            # Handle both string and dictionary responses
            if isinstance(result, str):
                content = result
                provider = self._get_provider_for_model(model)
            else:
                content = result.get("content", str(result)) if result else "No response"
                provider = result.get("provider") if result else None
            
            # Asszisztens válaszának mentése
            await self.state_manager.add_conversation_entry(
                session_id=session_id, 
                role="assistant", 
                content=content,
                metadata={
                    "model": model,
                    "provider": provider,
                    "response_time": response_time
                }
            )
        
        # Visszaadjuk az eredményt a válaszidővel és egyéb metaadatokkal
        if isinstance(result, str):
            return {
                "content": result,
                "model": model,
                "provider": self._get_provider_for_model(model),
                "response_time": response_time,
                "session_id": session_id
            }
        elif isinstance(result, dict):
            result.update({
                "response_time": response_time,
                "session_id": session_id
            })
            return result
        else:
            return {
                "content": str(result) if result else "No response",
                "model": model,
                "provider": self._get_provider_for_model(model),
                "response_time": response_time,
                "session_id": session_id
            }
    
    async def run_task_with_multiple_models_in_session(self, 
                                                    session_id: str,
                                                    query: str,
                                                    system_message: Optional[str] = None,
                                                    models: List[str] = [],
                                                    task_type: Optional[str] = None,
                                                    temperature: Optional[float] = None,
                                                    persist_history: bool = True) -> Dict[str, Any]:
        """
        Végrehajtja a feladatot több modellel egy adott munkamenetben,
        és összehasonlítja az eredményeiket.
        
        Args:
            session_id: A munkamenet azonosítója
            query: A felhasználói lekérdezés
            system_message: Opcionális rendszerüzenet
            models: A használandó modellek listája. Ha üres, automatikusan kiválaszt néhányat.
            task_type: Opcionális feladat típus
            temperature: Opcionális hőmérséklet érték
            persist_history: Ha True, a beszélgetés bekerül a perzisztens tárolóba
            
        Returns:
            Dict: Szótár a különböző modellek válaszaival
        """
        # Az előző beszélgetések betöltése a munkamenetből
        conversation_history = []
        if persist_history:
            conversation_history = await self.state_manager.get_conversation_history(session_id)
            
        # Ha nincs explicit feladat típus, meghatározzuk
        if task_type is None:
            task_type = self.determine_task_type(query)
            
        # Ha nincs megadva modell, akkor a feladattípusra ajánlott modelleket használjuk
        if not models:
            task_models = self.ai_client.config.get("task_model_mapping", {}).get(task_type, [])
            if task_models:
                models = task_models[:2]  # Első 2 ajánlott modell használata 
            else:
                # Különben használjuk az alapértelmezettet és egy másikat
                models = [self.default_model, "claude-3-sonnet"]
        
        # Ha van beszélgetési előzmény, hozzáadjuk a prompt elejéhez
        enhanced_prompt = query
        if conversation_history:
            # Az utolsó néhány beszélgetés hozzáadása kontextusként
            recent_history = conversation_history[-5:]  # Utolsó 5 beszélgetés
            context = "\n".join([
                f"{msg['role']}: {msg['content']}" 
                for msg in recent_history
            ])
            enhanced_prompt = f"Előzmények:\n{context}\n\nAktuális kérdés:\n{query}"
                
        # Párhuzamosan futtatjuk a lekérdezéseket minden modellel
        tasks = []
        for model in models:
            task = self.ai_client.generate_response(
                prompt=enhanced_prompt,
                system_message=system_message,
                model=model,
                task_type=task_type,
                temperature=temperature
            )
            tasks.append(task)
            
        # Várjuk meg az összes eredményt
        results = await asyncio.gather(*tasks, return_exceptions=True)
          # Feldolgozzuk az eredményeket
        model_responses = {}
        for i, result in enumerate(results):
            model = models[i]
            
            # Ellenőrizzük, hogy sikeres volt-e a végrehajtás
            if isinstance(result, Exception):
                model_responses[model] = {
                    "error": True,
                    "message": str(result),
                    "model": model
                }
            elif result is None:
                model_responses[model] = {
                    "error": True,
                    "message": "No response received",
                    "model": model
                }
            else:
                # Ha a válasz string, akkor csomagoljuk be dictionary-ba
                if isinstance(result, str):
                    model_responses[model] = {
                        "content": result,
                        "model": model,
                        "success": True
                    }
                else:
                    model_responses[model] = result
                    
                    # Rögzítjük a teljesítményt sikeres futtatásnál
                    if isinstance(result, dict) and "response_time" in result:
                        self.record_model_performance(
                            model_id=model,
                            task_type=task_type,
                            response_time=result["response_time"],
                            success=True
                        )
                
        # Elmentjük a felhasználói kérdést, ha szükséges
        if persist_history:
            await self.state_manager.add_conversation_entry(
                session_id=session_id, 
                role="user", 
                content=query,
                metadata={"task_type": task_type}
            )
            
            # Elmentjük az összes asszisztens választ
            for model, response in model_responses.items():
                if not isinstance(response, dict) or "error" in response:
                    continue
                    
                await self.state_manager.add_conversation_entry(
                    session_id=session_id, 
                    role="assistant", 
                    content=response.get("content", ""),                    metadata={
                        "model": model,
                        "provider": response.get("provider"),
                        "multi_model_comparison": True,
                        "response_time": response.get("response_time")
                    }
                )
        
        return {
            "task_type": task_type,
            "models_used": models,
            "responses": model_responses,
            "session_id": session_id
        }
    
    def _get_provider_for_model(self, model_id: str) -> Optional[str]:
        """Get the provider for a specific model."""
        return self.ai_client._get_provider_for_model(model_id)

    async def execute_task_with_core_system(self,
                                           query: str,
                                           system_message: Optional[str] = None,
                                           model: Optional[str] = None,
                                           task_type: Optional[str] = None,
                                           temperature: Optional[float] = None) -> Dict[str, Any]:
        """
        🔥 KRITIKUS JAVÍTÁS: Végrehajtja a feladatot az eredeti core_old rendszerrel.
        Ez a metódus használja a core_old execution bridge-et a VALÓDI tool végrehajtáshoz.
        PLUS: Intelligent workflow integráció a komplex feladatokhoz.
        """
        start_time = time.time()
        
        # 🚀 ÚJ: Intelligent workflow ellenőrzés
        if INTELLIGENT_WORKFLOWS_AVAILABLE:
            try:
                workflow_result = await process_with_intelligent_workflow(query)
                if workflow_result.get("workflow_detected"):
                    # Ha intelligent workflow-t detektáltunk, használjuk azt
                    logger.info(f"🎯 Intelligent workflow használata: {query}")
                    execution_time = time.time() - start_time
                    
                    # Intelligent workflow eredmény formázása
                    if workflow_result.get("success"):
                        return {
                            "status": "success",
                            "command_type": "INTELLIGENT_WORKFLOW", 
                            "execution_result": workflow_result,
                            "ai_summary": f"✅ Intelligent workflow sikeresen végrehajtva: {workflow_result.get('workflow_type', 'unknown')}",
                            "execution_type": "INTELLIGENT_WORKFLOW",
                            "response_time": execution_time,
                            "model_used": model or "intelligent_workflow_system"
                        }
                    else:
                        # Ha a workflow hibázott, folytassuk a hagyományos feldolgozással
                        logger.warning(f"⚠️ Intelligent workflow failed: {workflow_result.get('error', 'Unknown error')}")
                        
            except Exception as e:
                logger.warning(f"⚠️ Intelligent workflow processing failed: {e}")
                # Continue with traditional processing
        
        try:
            # 1. FÁZIS: AI elemzés és parancs felismerés
            analysis_prompt = f"""
            Elemezd ezt a feladatot és határozd meg, milyen konkrét parancsokat kell végrehajtani:
            
            FELADAT: {query}
            
            Elérhető parancs típusok:
            - ASK: AI kérdés (pl. 'explain something', 'analyze this')
            - CMD: Shell parancs (pl. 'list files', 'run command')
            - FILE: Fájl műveletek (pl. 'read file', 'write file', 'create file')
            - CODE: Kód műveletek (pl. 'generate code', 'execute python')
            
            Válaszolj ebben a formátumban:
            COMMAND_TYPE: [ASK/CMD/FILE/CODE]
            COMMAND_ACTION: [specific action]
            PARAMETERS: [specific parameters needed]
            """
            if model is None:
                model = await self.select_model_for_task(query, task_type or "planning")
            analysis_result = await self.ai_client.generate_response(
                prompt=analysis_prompt,
                system_message="Te egy parancs elemző vagy. Legyél specifikus és pontos.",
                model=model,
                task_type="planning"
            )
            # Handle both string and dict responses
            if isinstance(analysis_result, dict):
                ai_response = analysis_result.get("content", "")
            else:
                ai_response = str(analysis_result)
            logger.info(f"AI parancs elemzés: {ai_response[:200]}...")
            # 2. FÁZIS: Parancs típus és paraméterek kinyerése            command_type = "ASK"  # alapértelmezett
            command_action = query
            parameters = {}
            lines = ai_response.split('\n')
            for line in lines:
                line = line.strip()
                if line.startswith('COMMAND_TYPE:'):
                    command_type = line.replace('COMMAND_TYPE:', '').strip()
                elif line.startswith('COMMAND_ACTION:'):
                    command_action = line.replace('COMMAND_ACTION:', '').strip()
                elif line.startswith('PARAMETERS:'):
                    params_text = line.replace('PARAMETERS:', '').strip()
                    # --- ÚJ: JSON és egyszerű paraméter felismerése ---
                    try:
                        # Próbáljuk JSON-ként értelmezni
                        if params_text.startswith('{') and params_text.endswith('}'):
                            import json
                            parameters = json.loads(params_text)
                        else:
                            # Egyszerű string feldolgozás
                            # Speciális kezelés a "filename = xyz.txt" formátumra
                            if 'filename' in params_text.lower() and '=' in params_text:
                                # Extract filename after "filename = "
                                filename_part = params_text.split('=', 1)[1].strip()
                                if filename_part.endswith(('.txt', '.md', '.log', '.py', '.json', '.html', '.css', '.js')):
                                    parameters['path'] = filename_part
                            elif 'content' in params_text.lower() and '=' in params_text:
                                # Extract content after "content = "
                                content_part = params_text.split('=', 1)[1].strip()
                                parameters['content'] = content_part
                            else:
                                # Ha több fájlnév és/vagy tartalom is van vesszővel elválasztva
                                parts = [p.strip() for p in params_text.split(',') if p.strip()]
                                file_names = [p for p in parts if p.endswith('.txt') or p.endswith('.md') or p.endswith('.log')]
                                other_parts = [p for p in parts if not (p.endswith('.txt') or p.endswith('.md') or p.endswith('.log'))]
                                if len(file_names) == 1:
                                    parameters['path'] = file_names[0]
                                elif len(file_names) >= 2:
                                    parameters['path'] = file_names[0]
                                    parameters['target_path'] = file_names[1]
                                # Ha van explicit content
                                for p in other_parts:
                                    if p.lower().startswith('content='):
                                        parameters['content'] = p[len('content='):].strip()
                                    elif p:
                                        parameters['content'] = p  # fallback: bármilyen szöveg
                                if not parameters and params_text:
                                    parameters['data'] = params_text
                    except json.JSONDecodeError:
                        # Ha a JSON parsing nem sikerül, visszatérünk az egyszerű feldolgozásra
                        parts = [p.strip() for p in params_text.split(',') if p.strip()]
                        if params_text:
                            parameters['data'] = params_text
            logger.info(f"Észlelt parancs: {command_type}, akció: {command_action}, paraméterek: {parameters}")
            # 3. FÁZIS: Végrehajtás a core_old rendszerrel
            execution_result = None
            if command_type.upper() == "CMD":
                cmd = command_action if command_action else "echo Hello from Project-S"
                execution_result = await core_execution_bridge.execute_shell_command(cmd)
            elif command_type.upper() == "FILE":
                # Fájl művelet végrehajtás
                # Paraméterek normalizálása                # --- JAVÍTOTT LOGIKA ---
                action = "write"
                path = None
                content = None
                # Ha a PARAMETERS csak egy fájlnevet tartalmaz
                if 'path' in parameters:
                    path = parameters['path']
                elif 'data' in parameters and isinstance(parameters['data'], str) and parameters['data'].endswith('.txt'):
                    path = parameters['data']
                else:
                    # Intelligens fájlnév kinyerés a query-ból
                    path = self._extract_filename_from_query(query)
                content = parameters.get('content', f"Project-S output: {query}")
                # --- ACTION LOGIKA ---
                if "create" in command_action.lower():
                    action = "write"  # 'create file' helyett 'write' kell ide!
                elif "read" in command_action.lower() or "olvas" in query.lower():
                    action = "read"
                    content = None
                # Mindig legyen action és path
                file_command = {"action": action, "path": path}
                if content is not None:
                    file_command["content"] = content
                execution_result = await core_execution_bridge.execute_file_operation(file_command)
                if isinstance(execution_result, str):
                    execution_result = {"status": "success", "content": execution_result, "path": path}
            elif command_type.upper() == "CODE":
                action = "generate"
                if "execute" in command_action.lower() or "run" in command_action.lower():
                    action = "execute"
                execution_result = await core_execution_bridge.execute_code_operation(
                    action=action,
                    description=command_action
                )
            else:
                ai_query = command_action if command_action else query
                execution_result = await core_execution_bridge.ask_ai(ai_query)
            execution_time = time.time() - start_time
            if execution_result and isinstance(execution_result, dict) and execution_result.get("status") == "success":
                # --- AI magyarázó szöveg hozzáadása az eredményhez ---
                ai_summary = None
                try:
                    ai_summary = await self.ai_client.generate_response(
                        prompt=f"A következő feladatot sikeresen végrehajtottad: {query}\n\nÍrd le röviden, hogy mit csinált a rendszer, és mi lett az eredmény!",
                        system_message="Feladat végrehajtási összefoglaló. Légy rövid, informatív, magyarul válaszolj!",
                        model=model,
                        task_type="summary"
                    )
                except Exception as e:
                    ai_summary = f"(Nem sikerült AI összefoglalót generálni: {e})"
                return {
                    "status": "success",
                    "command_type": command_type,
                    "command_action": command_action,
                    "ai_analysis": ai_response[:200] + "..." if len(ai_response) > 200 else ai_response,
                    "execution_result": execution_result,
                    "ai_summary": ai_summary if isinstance(ai_summary, str) else getattr(ai_summary, 'content', str(ai_summary)),
                    "execution_type": "CORE_OLD_SYSTEM",
                    "response_time": execution_time,
                    "model_used": model
                }
            else:
                fallback_result = await self.execute_task_with_model(
                    query=query,
                    system_message=system_message,
                    model=model,
                    task_type=task_type,
                    temperature=temperature
                )
                # Robust error extraction
                if isinstance(execution_result, dict):
                    exec_error = execution_result.get("error")
                else:
                    exec_error = str(execution_result)
                return {
                    "status": "fallback",
                    "command_type": command_type,
                    "ai_analysis": ai_response[:200] + "..." if len(ai_response) > 200 else ai_response,
                    "execution_error": exec_error,
                    "fallback_response": fallback_result,
                    "execution_type": "AI_FALLBACK",
                    "response_time": execution_time,
                    "model_used": model
                }
        except Exception as e:
            logger.error(f"Error in core system execution: {e}")
            execution_time = time.time() - start_time
            try:
                fallback_result = await self.execute_task_with_model(
                    query=query,
                    system_message=system_message,
                    model=model,
                    task_type=task_type,
                    temperature=temperature
                )
                return {
                    "status": "error_fallback",
                    "error": str(e),
                    "fallback_response": fallback_result,
                    "execution_type": "ERROR_FALLBACK",
                    "response_time": execution_time,
                    "model_used": model
                }
            except Exception as fallback_error:
                return {
                    "status": "complete_failure",
                    "error": str(e),
                    "fallback_error": str(fallback_error),
                    "execution_type": "COMPLETE_FAILURE",
                    "response_time": execution_time
                }
    
    def _get_default_model_from_config(self) -> str:
        """
        Betölti az alapértelmezett modellt a konfigurációból.
        
        Returns:
            str: Az alapértelmezett modell azonosítója
        """
        try:
            # Try to get default model from ai_client config
            if hasattr(self.ai_client, 'config') and self.ai_client.config:
                default_model = self.ai_client.config.get("default_model", "qwen3-235b")
                logger.info(f"Alapértelmezett modell konfigurációból betöltve: {default_model}")
                return default_model
        except Exception as e:
            logger.warning(f"Nem sikerült betölteni az alapértelmezett modellt a konfigurációból: {e}")
          # Fallback to qwen3-235b (intended primary model)
        logger.info("Alapértelmezett modell: qwen3-235b (fallback)")
        return "qwen3-235b"
    
    def _extract_filename_from_query(self, query: str) -> str:
        """
        Intelligens fájlnév kinyerés a felhasználói kérdésből.
        
        Args:
            query (str): A felhasználói lekérdezés
            
        Returns:
            str: A kinyert fájlnév vagy alapértelmezett "project_s_output.txt"
        """
        import re
        
        # 1. Közvetlenül megadott fájlnevek keresése (idézőjelek között vagy kiterjesztéssel)
        # Keresés idézőjelek között: "filename.txt", 'filename.py'
        quoted_files = re.findall(r'["\']([^"\']+\.[a-zA-Z0-9]+)["\']', query)
        if quoted_files:
            return quoted_files[0]
        
        # 2. Kiterjesztéssel rendelkező szavak keresése
        # Pattern: szó.kiterjesztés (pl. "test.txt", "main.py", "config.json")
        extension_files = re.findall(r'\b([a-zA-Z0-9_-]+\.[a-zA-Z0-9]+)\b', query)
        if extension_files:
            # Kizárjuk a domain neveket és URL-eket
            filtered_files = [f for f in extension_files if not f.startswith(('www.', 'http', 'https'))]
            if filtered_files:
                return filtered_files[0]
        
        # 3. Fájlnév kulcsszavak alapján
        filename_patterns = {
            # Magyar kulcsszavak
            r'\b(?:hozz\s*létre|készíts|írj)\s+(?:egy\s+)?([a-zA-Z0-9_-]+)\s+(?:fájlt|file)': r'\1.txt',
            r'\b(?:nevű|néven)\s+([a-zA-Z0-9_-]+)(?:\s+fájl)?': r'\1.txt',
            r'\b([a-zA-Z0-9_-]+)\s+(?:nevű|néven)\s+fájl': r'\1.txt',
            # Angol kulcsszavak
            r'\b(?:create|make|write)\s+(?:a\s+)?(?:file\s+)?(?:called\s+|named\s+)?([a-zA-Z0-9_-]+)': r'\1.txt',
            r'\b(?:file\s+)?(?:called\s+|named\s+)([a-zA-Z0-9_-]+)': r'\1.txt',
            r'\b([a-zA-Z0-9_-]+)\s+(?:file|fájl)': r'\1.txt',
        }
        
        for pattern, replacement in filename_patterns.items():
            matches = re.findall(pattern, query, re.IGNORECASE)
            if matches:
                filename = re.sub(pattern, replacement, matches[0], flags=re.IGNORECASE)
                # Tisztítjuk a fájlnevet
                clean_filename = re.sub(r'[^\w\.-]', '_', filename)
                if clean_filename and not clean_filename.startswith('.'):
                    return clean_filename
        
        # 4. Speciális esetek - gyakori fájltípusok felismerése
        content_type_mapping = {
            r'\b(?:html|webpage|weboldal)': 'index.html',
            r'\b(?:css|stylesheet|stílus)': 'style.css',
            r'\b(?:js|javascript)': 'script.js',
            r'\b(?:py|python)': 'main.py',
            r'\b(?:json|config|konfig)': 'config.json',
            r'\b(?:md|markdown|readme)': 'README.md',
            r'\b(?:txt|text|szöveg)': 'document.txt',
            r'\b(?:log|napló)': 'log.txt',
            r'\b(?:csv|táblázat)': 'data.csv',
        }
        
        for pattern, filename in content_type_mapping.items():
            if re.search(pattern, query, re.IGNORECASE):
                return filename
        
        # 5. Utolsó esély: kulcsszavak alapján generálás
        if any(word in query.lower() for word in ['list', 'lista', 'jegyzék']):
            return 'lista.txt'
        elif any(word in query.lower() for word in ['note', 'jegyzet', 'memo']):
            return 'jegyzet.txt'
        elif any(word in query.lower() for word in ['test', 'teszt', 'próba']):
            return 'test.txt'
        elif any(word in query.lower() for word in ['hello', 'helló', 'üdvözlet']):
            return 'hello.txt'
          # 6. Alapértelmezett visszatérés
        logger.info(f"Nem sikerült kinyerni a fájlnevet a query-ból: '{query}', alapértelmezett használata")
        return "project_s_output.txt"
    
    async def process_user_command(self, user_input: str) -> dict:
        """
        Process user command - main entry point for CLI commands.
        Routes to the appropriate execution method based on command type.
        """
        try:
            logger.info(f"Processing user command: {user_input}")
            
            # Use the core system for execution
            result = await self.execute_task_with_core_system(
                query=user_input,
                model="qwen3-235b"  # Default model
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Error processing user command: {e}")
            return {
                "status": "error",
                "error": str(e),
                "command": user_input
            }
    
# Singleton példány létrehozása
model_manager = ModelManager()
