"""
Process Operations for Project-S
-------------------------------
Ez a modul a folyamatok kezeléséért felelős komponenseket tartalmazza.
Biztonságos folyamatindítást, leállítást és monitorozást biztosít
a LangGraph munkafolyamatokhoz.
"""
import os
import sys
import logging
import asyncio
import platform
import signal
import subprocess
import psutil
import time
from typing import Dict, List, Any, Optional, Union, Tuple
import shlex

from langgraph.prebuilt import ToolNode
from integrations.tool_manager import tool_manager
from integrations.system_operations import (
    security_check, is_command_allowed, SystemOperationState,
    DEFAULT_TIMEOUT
)
from core.event_bus import event_bus
from core.error_handler import error_handler

logger = logging.getLogger(__name__)

# Folyamatok nyilvántartása a Project-S rendszerben
process_registry = {}

class ProcessOperations:
    """
    Folyamatkezelő osztály, amely biztonságos folyamatindítást,
    leállítást és monitorozást biztosít a Project-S rendszer számára.
    """
    
    def __init__(self):
        """Inicializálja a ProcessOperations osztályt"""
        self.allowed_operations = {
            "start": True,
            "stop": True,
            "monitor": True,
            "kill": False,  # Alapértelmezetten a folyamat kilövés tiltott
        }
        
    @tool_manager.register(
        metadata={
            "name": "execute_process",
            "description": "Folyamat biztonságos indítása és kimenetének lekérdezése",
            "category": "process",
            "tags": ["process", "execute", "command"],
            "is_dangerous": True,  # Folyamatindítás veszélyes művelet lehet
        }
    )
    @security_check
    async def execute_process(self, command: Union[str, List[str]], 
                           timeout: int = DEFAULT_TIMEOUT,
                           capture_output: bool = True,
                           working_dir: Optional[str] = None,
                           env: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        Biztonságosan végrehajtja a megadott parancsot egy alfolyamatban.
        
        Args:
            command: A végrehajtandó parancs string vagy lista formában
            timeout: Időtúllépés másodpercekben (alapértelmezett: 30)
            capture_output: Ha True, akkor a parancs kimenete visszaadódik
            working_dir: A munkakönyvtár, ahol a parancs fut
            env: Környezeti változók szótára
            
        Returns:
            Dict: A művelet eredménye, tartalmazza a parancs kimenetét vagy a hibaüzenetet
        """
        try:
            # Parancs feldolgozása
            if isinstance(command, str):
                # Windows esetén más a parancs értelmezése
                if platform.system() == "Windows":
                    cmd_parts = command
                else:
                    cmd_parts = shlex.split(command)
            else:
                cmd_parts = command
                command = " ".join(map(str, command))  # Log célokra stringgé konvertálás
            
            logger.info(f"Folyamat végrehajtása: {command}")
            
            # Adjunk hozzá a környezetet az aktuális környezethez, ne írjuk felül teljesen
            merged_env = None
            if env:
                merged_env = os.environ.copy()
                merged_env.update(env)
            
            # Egyedi process ID generálása
            process_id = f"proc_{int(time.time() * 1000)}"
            
            start_time = time.time()
            
            # Aszinkron folyamatindítás
            process = await asyncio.create_subprocess_exec(
                *cmd_parts,
                stdout=asyncio.subprocess.PIPE if capture_output else None,
                stderr=asyncio.subprocess.PIPE if capture_output else None,
                cwd=working_dir,
                env=merged_env
            ) if not isinstance(cmd_parts, str) else await asyncio.create_subprocess_shell(
                cmd_parts,
                stdout=asyncio.subprocess.PIPE if capture_output else None,
                stderr=asyncio.subprocess.PIPE if capture_output else None,
                cwd=working_dir,
                env=merged_env
            )
            
            # Regisztráljuk a folyamatot
            process_registry[process_id] = {
                "pid": process.pid,
                "command": command,
                "start_time": start_time,
                "status": "running"
            }
            
            # Esemény kibocsátása
            event_bus.emit("process.started", {
                "id": process_id,
                "pid": process.pid,
                "command": command
            })
            
            # Várakozás a végrehajtásra a megadott időtúllépésig
            try:
                if capture_output:
                    stdout, stderr = await asyncio.wait_for(process.communicate(), timeout)
                    stdout_str = stdout.decode('utf-8', errors='replace') if stdout else ""
                    stderr_str = stderr.decode('utf-8', errors='replace') if stderr else ""
                else:
                    await asyncio.wait_for(process.wait(), timeout)
                    stdout_str = ""
                    stderr_str = ""
                    
                return_code = process.returncode
                
                # Frissítsük a folyamat állapotát
                process_registry[process_id]["status"] = "completed"
                process_registry[process_id]["end_time"] = time.time()
                process_registry[process_id]["return_code"] = return_code
                
                # Esemény kibocsátása
                event_bus.emit("process.completed", {
                    "id": process_id,
                    "pid": process.pid,
                    "return_code": return_code,
                    "execution_time": time.time() - start_time
                })
                
                # Eredmény összeállítása
                return {
                    "success": return_code == 0,
                    "command": command,
                    "stdout": stdout_str,
                    "stderr": stderr_str,
                    "return_code": return_code,
                    "execution_time": time.time() - start_time,
                    "process_id": process_id
                }
                
            except asyncio.TimeoutError:
                # Időtúllépés esetén megpróbáljuk leállítani a folyamatot
                process.terminate()
                
                # Frissítsük a folyamat állapotát
                process_registry[process_id]["status"] = "timeout"
                process_registry[process_id]["end_time"] = time.time()
                
                # Esemény kibocsátása
                event_bus.emit("process.timeout", {
                    "id": process_id,
                    "pid": process.pid,
                    "execution_time": time.time() - start_time
                })
                
                return {
                    "success": False,
                    "command": command,
                    "error": f"A folyamat időtúllépése: {timeout} másodperc",
                    "error_type": "TimeoutError",
                    "execution_time": time.time() - start_time,
                    "process_id": process_id
                }
                
        except Exception as e:
            error_msg = f"Hiba a folyamat végrehajtása közben: {str(e)}"
            logger.error(error_msg)
            error_handler.log_exception(e)
            
            # Hibaesemény kibocsátása
            event_bus.emit("process.error", {
                "command": command,
                "error": str(e)
            })
            
            return {
                "success": False,
                "command": command,
                "error": error_msg,
                "error_type": type(e).__name__
            }
    
    @tool_manager.register(
        metadata={
            "name": "stop_process",
            "description": "Folyamat biztonságos leállítása",
            "category": "process",
            "tags": ["process", "stop", "terminate"],
            "is_dangerous": True,
        }
    )
    @security_check
    async def stop_process(self, process_id: Optional[str] = None, 
                         pid: Optional[int] = None,
                         force: bool = False,
                         timeout: int = 5) -> Dict[str, Any]:
        """
        Biztonságosan leállít egy folyamatot azonosító vagy PID alapján.
        
        Args:
            process_id: A leállítandó folyamat azonosítója (a execute_process által visszaadott)
            pid: A leállítandó folyamat PID-je
            force: Ha True, akkor erőszakosan leállítja a folyamatot (SIGKILL/TASKKILL /F)
            timeout: Várakozási idő a folyamat leállására másodpercben
            
        Returns:
            Dict: A művelet eredménye
        """
        if process_id is None and pid is None:
            return {
                "success": False,
                "error": "Meg kell adni vagy a process_id vagy a pid értéket"
            }
        
        try:
            # Process ID alapján keressük meg a folyamatot
            if process_id is not None:
                if process_id not in process_registry:
                    return {
                        "success": False,
                        "error": f"A folyamat nem található: {process_id}"
                    }
                pid = process_registry[process_id].get("pid")
            
            # Ellenőrizzük, hogy a folyamat létezik-e
            if not psutil.pid_exists(pid):
                # Frissítsük a nyilvántartást, ha a folyamat már nem létezik
                if process_id and process_id in process_registry:
                    process_registry[process_id]["status"] = "not_found"
                
                return {
                    "success": False,
                    "error": f"A folyamat nem található: PID {pid}"
                }
            
            # A folyamat leállítása
            process = psutil.Process(pid)
            
            if force:
                # Erőszakos leállítás
                process.kill()
            else:
                # Normál leállítás
                process.terminate()
            
            # Várakozás a folyamat leállására
            try:
                process.wait(timeout=timeout)
                success = True
            except psutil.TimeoutExpired:
                # Ha a folyamat nem állt le időben
                if force:
                    # Ha már erőszakosan leállítottuk és még mindig fut, akkor hibajelzés
                    success = False
                else:
                    # Másodszori próbálkozás erőszakos leállítással
                    try:
                        process.kill()
                        process.wait(timeout=timeout)
                        success = True
                    except (psutil.NoSuchProcess, psutil.TimeoutExpired):
                        success = False
            except psutil.NoSuchProcess:
                # A folyamat már leállt
                success = True
            
            # Frissítsük a folyamat állapotát
            if process_id and process_id in process_registry:
                process_registry[process_id]["status"] = "stopped"
                process_registry[process_id]["end_time"] = time.time()
            
            # Esemény kibocsátása
            event_bus.emit("process.stopped", {
                "id": process_id if process_id else "unknown",
                "pid": pid,
                "force": force,
                "success": success
            })
            
            return {
                "success": success,
                "pid": pid,
                "process_id": process_id,
                "status": "stopped" if success else "failed_to_stop"
            }
            
        except Exception as e:
            error_msg = f"Hiba a folyamat leállítása közben: {str(e)}"
            logger.error(error_msg)
            error_handler.log_exception(e)
            
            # Hibaesemény kibocsátása
            event_bus.emit("process.error", {
                "operation": "stop",
                "process_id": process_id,
                "pid": pid,
                "error": str(e)
            })
            
            return {
                "success": False,
                "error": error_msg,
                "error_type": type(e).__name__
            }
    
    @tool_manager.register(
        metadata={
            "name": "list_processes",
            "description": "Futó folyamatok listázása",
            "category": "process",
            "tags": ["process", "list", "monitor"],
            "is_dangerous": False,
        }
    )
    async def list_processes(self, include_system: bool = False,
                          filter_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Lekérdezi a rendszeren futó folyamatokat.
        
        Args:
            include_system: Ha True, akkor a rendszerfolyamatokat is listázza
            filter_name: Szűrés a folyamat nevére
            
        Returns:
            Dict: A futó folyamatok listája
        """
        try:
            processes = []
            
            # Listázzuk a futó folyamatokat
            for proc in psutil.process_iter(['pid', 'name', 'username', 'cpu_percent', 'memory_percent', 'create_time', 'status']):
                try:
                    # Alapadatok lekérdezése
                    proc_info = proc.info
                    
                    # Rendszerfolyamatok szűrése
                    if not include_system:
                        # Windows esetén
                        if platform.system() == "Windows" and (
                            proc_info["name"].lower().endswith(".sys") or
                            proc_info["name"].lower() in ["system", "registry", "smss.exe", "csrss.exe"]
                        ):
                            continue
                        # Unix esetén
                        elif platform.system() != "Windows" and (
                            proc_info["username"] in ["root", "system"] and
                            proc_info["name"] in ["init", "systemd", "kthreadd"]
                        ):
                            continue
                    
                    # Névszűrés
                    if filter_name and filter_name.lower() not in proc_info["name"].lower():
                        continue
                    
                    # Parancssori argumentumok lekérdezése
                    try:
                        cmdline = proc.cmdline()
                    except (psutil.AccessDenied, psutil.ZombieProcess):
                        cmdline = []
                    
                    # Folyamatinformációk összeállítása
                    process_data = {
                        "pid": proc_info["pid"],
                        "name": proc_info["name"],
                        "status": proc_info["status"],
                        "username": proc_info["username"],
                        "cpu_percent": proc_info["cpu_percent"],
                        "memory_percent": proc_info["memory_percent"],
                        "create_time": proc_info["create_time"],
                        "command": " ".join(cmdline) if cmdline else ""
                    }
                    
                    # Ellenőrizzük, hogy ez a Project-S által indított folyamat-e
                    for proc_id, proc_data in process_registry.items():
                        if proc_data.get("pid") == proc_info["pid"]:
                            process_data["project_s_id"] = proc_id
                            process_data["project_s_info"] = proc_data
                            break
                    
                    processes.append(process_data)
                    
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    # Kihagyjuk azokat a folyamatokat, amelyekhez nincs hozzáférésünk
                    pass
            
            return {
                "success": True,
                "processes": processes,
                "count": len(processes),
                "system_info": {
                    "cpu_count": psutil.cpu_count(),
                    "total_memory": psutil.virtual_memory().total,
                    "platform": platform.system()
                }
            }
            
        except Exception as e:
            error_msg = f"Hiba a folyamatok listázása közben: {str(e)}"
            logger.error(error_msg)
            error_handler.log_exception(e)
            
            return {
                "success": False,
                "error": error_msg,
                "error_type": type(e).__name__
            }
    
    @tool_manager.register(
        metadata={
            "name": "get_process_info",
            "description": "Információk lekérdezése egy adott folyamatról",
            "category": "process",
            "tags": ["process", "info", "monitor"],
            "is_dangerous": False,
        }
    )
    async def get_process_info(self, process_id: Optional[str] = None,
                            pid: Optional[int] = None) -> Dict[str, Any]:
        """
        Részletes információkat kérdez le egy adott folyamatról.
        
        Args:
            process_id: A folyamat azonosítója (a execute_process által visszaadott)
            pid: A folyamat PID-je
            
        Returns:
            Dict: A folyamat részletes információi
        """
        if process_id is None and pid is None:
            return {
                "success": False,
                "error": "Meg kell adni vagy a process_id vagy a pid értéket"
            }
        
        try:
            # Process ID alapján keressük meg a folyamatot
            project_s_info = None
            if process_id is not None:
                if process_id not in process_registry:
                    return {
                        "success": False,
                        "error": f"A folyamat nem található a nyilvántartásban: {process_id}"
                    }
                pid = process_registry[process_id].get("pid")
                project_s_info = process_registry[process_id]
            
            # Ellenőrizzük, hogy a folyamat létezik-e
            if not psutil.pid_exists(pid):
                return {
                    "success": False,
                    "error": f"A folyamat nem található: PID {pid}"
                }
            
            # Folyamat adatok lekérdezése
            process = psutil.Process(pid)
            process_info = {
                "pid": pid,
                "name": process.name(),
                "status": process.status(),
                "create_time": process.create_time(),
                "cpu_percent": process.cpu_percent(),
                "memory_percent": process.memory_percent(),
                "memory_info": dict(process.memory_info()._asdict()),
                "username": process.username(),
                "terminal": process.terminal() if hasattr(process, 'terminal') else None
            }
            
            # Biztonságos módon próbáljuk meg lekérdezni az extra adatokat
            try:
                process_info["command_line"] = process.cmdline()
            except (psutil.AccessDenied, psutil.ZombieProcess):
                process_info["command_line"] = ["<hozzáférés megtagadva>"]
                
            try:
                process_info["connections"] = [conn._asdict() for conn in process.connections()]
            except (psutil.AccessDenied, psutil.ZombieProcess):
                process_info["connections"] = []
                
            try:
                process_info["open_files"] = [file._asdict() for file in process.open_files()]
            except (psutil.AccessDenied, psutil.ZombieProcess):
                process_info["open_files"] = []
                
            try:
                process_info["threads"] = [thread._asdict() for thread in process.threads()]
            except (psutil.AccessDenied, psutil.ZombieProcess):
                process_info["threads"] = []
                
            # Project-S adatok hozzáadása, ha van
            if project_s_info:
                process_info["project_s_id"] = process_id
                process_info["project_s_info"] = project_s_info
            
            return {
                "success": True,
                "process": process_info
            }
            
        except psutil.NoSuchProcess:
            return {
                "success": False,
                "error": f"A folyamat nem található: PID {pid}"
            }
            
        except Exception as e:
            error_msg = f"Hiba a folyamat információk lekérdezése közben: {str(e)}"
            logger.error(error_msg)
            error_handler.log_exception(e)
            
            return {
                "success": False,
                "error": error_msg,
                "error_type": type(e).__name__
            }
            
    def convert_to_tool_node(self, tool_name: str) -> ToolNode:
        """
        Konvertálja a metódust LangGraph ToolNode-dá.
        
        Args:
            tool_name: Az eszköz neve (metódus név)
            
        Returns:
            ToolNode: A létrehozott LangGraph ToolNode
        """
        # Ellenőrizzük, hogy a metódus létezik és regisztrálva van
        if not hasattr(self, tool_name) or not callable(getattr(self, tool_name)):
            raise ValueError(f"A(z) {tool_name} eszköz nem létezik")
        
        # Létrehozzuk a ToolNode-ot
        return tool_manager.create_tool_node(tool_name)
        
    def register_langgraph_tools(self) -> Dict[str, ToolNode]:
        """
        Létrehozza és regisztrálja az összes folyamatkezelő műveletet LangGraph eszközként.
        
        Returns:
            Dict[str, ToolNode]: Az eszköznevek és ToolNode-ok szótára
        """
        tool_nodes = {}
        
        # Az osztály nyilvános metódusait regisztráljuk
        for method_name in dir(self):
            if not method_name.startswith('_'):
                method = getattr(self, method_name)
                if callable(method) and hasattr(method, '__wrapped__'):
                    try:
                        tool_nodes[method_name] = self.convert_to_tool_node(method_name)
                    except ValueError:
                        # Ha nem sikerül konvertálni, akkor kihagyjuk
                        pass
        
        return tool_nodes


# Singleton példány létrehozása
process_operations = ProcessOperations()
