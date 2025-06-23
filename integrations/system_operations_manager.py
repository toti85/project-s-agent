"""
System Operations Manager for Project-S
-------------------------------------
Ez a modul integrálja az összes rendszerszintű műveletet egy közös menedzserbe,
és LangGraph munkafolyamatokat biztosít a rendszerszintű feladatok végrehajtásához.
"""
import os
import logging
import asyncio
from typing import Dict, List, Any, Optional, Union, TypedDict
import platform

from langgraph.graph import StateGraph
from langgraph.prebuilt import ToolNode

from integrations.system_operations import SystemOperationState
from integrations.file_system_operations import FileSystemOperations, file_system_operations
from integrations.process_operations import ProcessOperations, process_operations
from integrations.config_operations import ConfigOperations, config_operations
from integrations.tool_manager import tool_manager

from core.event_bus import event_bus
from core.error_handler import error_handler

logger = logging.getLogger(__name__)


class SystemOperationsManager:
    """
    Rendszerszintű műveletek menedzser osztálya.
    
    Ez az osztály integrálja:
    - Fájlrendszerműveletek
    - Folyamatkezelés
    - Konfigurációkezelés
    """
    
    def __init__(self):
        """Inicializálja a SystemOperationsManager osztályt"""
        self.file_operations = file_system_operations
        self.process_operations = process_operations
        self.config_operations = config_operations
        
        # Rendszerinformációk gyűjtése
        self.os_info = {
            "system": platform.system(),
            "release": platform.release(),
            "version": platform.version(),
            "architecture": platform.machine(),
            "processor": platform.processor(),
            "python_version": platform.python_version()
        }
        
        # Alap jogosultságok beállítása
        self.permissions = {
            "file_read": True,
            "file_write": True,
            "file_delete": False,  # Alapértelmezetten a törlés tiltott
            "process_execute": True,
            "process_kill": False,  # Alapértelmezetten a kilövés tiltott
            "config_write": True
        }
        
    def get_all_tool_nodes(self) -> Dict[str, ToolNode]:
        """
        Visszaadja az összes elérhető rendszerművelet ToolNode-ját.
        
        Returns:
            Dict[str, ToolNode]: Az eszköznevek és ToolNode-ok szótára
        """
        tool_nodes = {}
        
        # Fájlrendszer műveletek
        tool_nodes.update(self.file_operations.register_langgraph_tools())
        
        # Folyamatkezelő műveletek
        tool_nodes.update(self.process_operations.register_langgraph_tools())
        
        # Konfigurációkezelő műveletek
        tool_nodes.update(self.config_operations.register_langgraph_tools())
        
        return tool_nodes
        
    def create_file_operations_workflow(self, workflow_id: str = None) -> StateGraph:
        """
        Létrehoz egy fájlműveletekre specializált munkafolyamatot.
        
        Args:
            workflow_id: A munkafolyamat azonosítója (opcionális)
            
        Returns:
            StateGraph: A létrehozott munkafolyamat
        """
        # Eszközök lekérdezése
        file_tools = self.file_operations.register_langgraph_tools()
        
        # Munkafolyamat létrehozása
        graph = StateGraph()
        
        # Csomópontok hozzáadása
        for name, tool_node in file_tools.items():
            graph.add_node(name, tool_node)
        
        # Élek definiálása - példa: list_directory -> read_file -> write_file
        if "list_directory" in file_tools and "read_file" in file_tools:
            graph.add_edge("list_directory", "read_file")
        
        if "read_file" in file_tools and "write_file" in file_tools:
            graph.add_edge("read_file", "write_file")
            
        # Alapértelmezett kezdőpont
        if "list_directory" in file_tools:
            graph.set_entry_point("list_directory")
        elif "read_file" in file_tools:
            graph.set_entry_point("read_file")
        
        return graph
        
    def create_process_operations_workflow(self, workflow_id: str = None) -> StateGraph:
        """
        Létrehoz egy folyamatkezelésre specializált munkafolyamatot.
        
        Args:
            workflow_id: A munkafolyamat azonosítója (opcionális)
            
        Returns:
            StateGraph: A létrehozott munkafolyamat
        """
        # Eszközök lekérdezése
        process_tools = self.process_operations.register_langgraph_tools()
        
        # Munkafolyamat létrehozása
        graph = StateGraph()
        
        # Csomópontok hozzáadása
        for name, tool_node in process_tools.items():
            graph.add_node(name, tool_node)
        
        # Élek definiálása - példa: list_processes -> execute_process -> get_process_info
        if "list_processes" in process_tools and "execute_process" in process_tools:
            graph.add_edge("list_processes", "execute_process")
        
        if "execute_process" in process_tools and "get_process_info" in process_tools:
            graph.add_edge("execute_process", "get_process_info")
        
        if "get_process_info" in process_tools and "stop_process" in process_tools:
            graph.add_edge("get_process_info", "stop_process")
            
        # Alapértelmezett kezdőpont
        if "list_processes" in process_tools:
            graph.set_entry_point("list_processes")
        elif "execute_process" in process_tools:
            graph.set_entry_point("execute_process")
        
        return graph
        
    def create_config_operations_workflow(self, workflow_id: str = None) -> StateGraph:
        """
        Létrehoz egy konfigurációkezelésre specializált munkafolyamatot.
        
        Args:
            workflow_id: A munkafolyamat azonosítója (opcionális)
            
        Returns:
            StateGraph: A létrehozott munkafolyamat
        """
        # Eszközök lekérdezése
        config_tools = self.config_operations.register_langgraph_tools()
        
        # Munkafolyamat létrehozása
        graph = StateGraph()
        
        # Csomópontok hozzáadása
        for name, tool_node in config_tools.items():
            graph.add_node(name, tool_node)
        
        # Élek definiálása - példa: list_config_files -> load_config -> update_config
        if "list_config_files" in config_tools and "load_config" in config_tools:
            graph.add_edge("list_config_files", "load_config")
        
        if "load_config" in config_tools and "update_config" in config_tools:
            graph.add_edge("load_config", "update_config")
        
        if "load_config" in config_tools and "get_config_value" in config_tools:
            graph.add_edge("load_config", "get_config_value")
            
        # Alapértelmezett kezdőpont
        if "list_config_files" in config_tools:
            graph.set_entry_point("list_config_files")
        elif "load_config" in config_tools:
            graph.set_entry_point("load_config")
        
        return graph
        
    def create_combined_system_workflow(self, workflow_id: str = None) -> StateGraph:
        """
        Létrehoz egy kombinált rendszerműveleteket tartalmazó munkafolyamatot.
        
        Args:
            workflow_id: A munkafolyamat azonosítója (opcionális)
            
        Returns:
            StateGraph: A létrehozott munkafolyamat
        """
        # Összes eszköz lekérdezése
        all_tools = self.get_all_tool_nodes()
        
        # Munkafolyamat létrehozása
        graph = StateGraph()
        
        # Csomópontok hozzáadása
        for name, tool_node in all_tools.items():
            graph.add_node(name, tool_node)
        
        # Élek definiálása kategóriák között
        # Fájlrendszer -> Konfiguráció
        if "read_file" in all_tools and "load_config" in all_tools:
            graph.add_edge("read_file", "load_config")
            
        # Konfiguráció -> Folyamat
        if "load_config" in all_tools and "execute_process" in all_tools:
            graph.add_edge("load_config", "execute_process")
            
        # Folyamat -> Fájl
        if "execute_process" in all_tools and "write_file" in all_tools:
            graph.add_edge("execute_process", "write_file")
            
        # Feltételes elágazások kezelése
        def route_after_load_config(state):
            # Példa: ha a config tartalmaz command mezőt, akkor process, egyébként file
            if state.get("loaded_config", {}).get("command"):
                return "execute_process"
            else:
                return "write_file"
        
        # Feltételes edges hozzáadása
        if "load_config" in all_tools:
            graph.add_conditional_edges("load_config", route_after_load_config)
            
        # Alapértelmezett kezdőpont
        if "list_directory" in all_tools:
            graph.set_entry_point("list_directory")
        elif "load_config" in all_tools:
            graph.set_entry_point("load_config")
        elif "execute_process" in all_tools:
            graph.set_entry_point("execute_process")
        
        return graph
        
    def create_error_handling_workflow(self, workflow_id: str = None) -> StateGraph:
        """
        Létrehoz egy hibakezelt rendszerműveleteket tartalmazó munkafolyamatot.
        
        Args:
            workflow_id: A munkafolyamat azonosítója (opcionális)
            
        Returns:
            StateGraph: A létrehozott munkafolyamat
        """
        # Eszközök lekérdezése
        all_tools = self.get_all_tool_nodes()
        
        # Munkafolyamat létrehozása
        graph = StateGraph()
        
        # Csomópontok hozzáadása
        for name, tool_node in all_tools.items():
            graph.add_node(name, tool_node)
        
        # Hibakezelő függvény
        def handle_error_state(state):
            if state.get("error_state", False):
                # Ha hiba történt, próbáljunk meg helyreállítani
                if state.get("retry_count", 0) < 3:  # Maximum 3 próbálkozás
                    return "error_recovery"
                else:
                    return "error_abort"
            # Ha nincs hiba, sikeres ág
            return "success"
        
        # Hozzunk létre egy hibafelismerő és egy helyreállító csomópontot
        def error_recovery_node(state):
            # Egyszerű visszaállítás: retry_count növelése
            retry_count = state.get("retry_count", 0) + 1
            return {**state, "retry_count": retry_count}
        
        def error_abort_node(state):
            # Hiba regisztrálása és leállítás
            return {**state, "final_status": "error_aborted"}
        
        def success_node(state):
            # Sikeres végrehajtás
            return {**state, "final_status": "success"}
        
        # Adjuk hozzá a speciális csomópontokat
        graph.add_node("error_recovery", error_recovery_node)
        graph.add_node("error_abort", error_abort_node)
        graph.add_node("success", success_node)
        
        # Kiválasztunk néhány alap eszközt a hibakezelés demonstrálására
        key_operations = ["read_file", "execute_process", "load_config"]
        
        # Csak a létező műveletekre állítunk be feltételes éleket
        for op in key_operations:
            if op in all_tools:
                graph.add_conditional_edges(op, handle_error_state)
                
                # Helyreállításból visszatérés az eredeti művelethez
                graph.add_edge("error_recovery", op)
        
        # Alapértelmezett belépési pont
        for op in key_operations:
            if op in all_tools:
                graph.set_entry_point(op)
                break
        
        return graph
        
    async def execute_example_workflow(self):
        """
        Példa egy munkafolyamat végrehajtására.
        
        Returns:
            Dict: A végrehajtás eredménye
        """
        # Példa: konfiguráció munkafolyamat létrehozása
        workflow = self.create_config_operations_workflow("example_config_workflow")
        
        # YAML konfigurációs fájl útvonala
        config_path = os.path.join(self.config_operations.config_dir, "config.yaml")
        
        # Kezdeti állapot
        initial_state = {
            "config_path": config_path,
            "error_state": False,
            "retry_count": 0
        }
        
        # Itt végrehajtanánk a munkafolyamatot a LangGraph API-val
        logger.info(f"Példa munkafolyamat létrehozva: {workflow}")
        logger.info(f"Kezdeti állapot: {initial_state}")
        
        # Valós környezetben itt hívnánk meg a LangGraph executor-t
        
        return {
            "workflow": "config_operations",
            "status": "created",
            "initial_state": initial_state
        }


# Singleton példány létrehozása
system_operations_manager = SystemOperationsManager()
