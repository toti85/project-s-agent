"""
Core Execution Bridge for Project-S

Ez a modul hidat képez a jelenlegi workflow rendszer és az eredeti működő 
core_old végrehajtási rendszer között. Lehetővé teszi a tényleges tool 
végrehajtást a workflow-kban.
"""

import asyncio
import logging
import sys
from pathlib import Path
from typing import Dict, Any, Optional, List
import importlib.util

logger = logging.getLogger(__name__)

class CoreExecutionBridge:
    """
    Híd a jelenlegi workflow rendszer és az eredeti core_old végrehajtási 
    rendszer között.
    """
    
    def __init__(self):
        """Initialize the execution bridge."""
        self.core_old_path = Path(__file__).parent.parent / "core_old"
        self.central_executor = None
        self.command_router = None
        self.initialized = False
        
        logger.info("CoreExecutionBridge initialized")
    
    async def initialize(self) -> bool:
        """
        Initialize the core_old execution system.
        
        Returns:
            bool: True if initialization was successful
        """
        try:
            if self.initialized:
                return True
                
            logger.info("Initializing core_old execution system...")
            
            # Add core_old to Python path temporarily
            core_old_str = str(self.core_old_path)
            if core_old_str not in sys.path:
                sys.path.insert(0, core_old_str)
            
            # Dinamikus import central_executor
            import importlib.util
            ce_path = self.core_old_path / "central_executor.py"
            cr_path = self.core_old_path / "command_router.py"
            spec_ce = importlib.util.spec_from_file_location("central_executor", ce_path)
            ce_module = importlib.util.module_from_spec(spec_ce)
            spec_ce.loader.exec_module(ce_module)
            spec_cr = importlib.util.spec_from_file_location("command_router", cr_path)
            cr_module = importlib.util.module_from_spec(spec_cr)
            spec_cr.loader.exec_module(cr_module)
            
            # Példányosítás
            self.central_executor = ce_module.CentralExecutor()
            self.command_router = cr_module.router
            
            # Initialize the central executor
            await self.central_executor.initialize()
            
            self.initialized = True
            logger.info("✅ Core_old execution system initialized successfully (dynamic import)")
            return True
            
        except Exception as e:
            logger.error(f"Error initializing core_old execution system: {e}")
            return False
    
    async def execute_command(self, command_type: str, command_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a command using the core_old system.
        
        Args:
            command_type (str): Type of command (ASK, CMD, FILE, CODE, etc.)
            command_data (Dict[str, Any]): Command data
            
        Returns:
            Dict[str, Any]: Execution result
        """
        if not self.initialized:
            success = await self.initialize()
            if not success:
                return {
                    "status": "error",
                    "error": "Failed to initialize core_old execution system"
                }
        
        try:
            # --- JAVÍTOTT: a command_data mezőit root szintre emeljük ---
            command = {"type": command_type.upper(), "id": f"bridge_{id(command_data)}"}
            if isinstance(command_data, dict):
                command.update(command_data)
            else:
                command["data"] = command_data
            
            logger.info(f"Executing {command_type} command via core_old system")
            
            # Execute through the central executor
            result = await self.central_executor.execute(command)
            
            logger.info(f"Command executed successfully: {command_type}")
            return result
            
        except Exception as e:
            logger.error(f"Error executing command via core_old: {e}")
            return {
                "status": "error", 
                "error": str(e)
            }
    
    async def execute_shell_command(self, command: str) -> Dict[str, Any]:
        """
        Execute a shell command using the core_old CMD handler.
        
        Args:
            command (str): Shell command to execute
            
        Returns:
            Dict[str, Any]: Execution result with stdout, stderr, return_code
        """
        return await self.execute_command("CMD", {"cmd": command})
    
    async def execute_file_operation(self, file_command: dict) -> Dict[str, Any]:
        """
        Execute a file operation using the core_old FILE handler.
        
        Args:
            file_command (dict): Dict with action, path, (content)
            
        Returns:
            Dict[str, Any]: Execution result
        """
        return await self.execute_command("FILE", file_command)
    
    async def execute_code_operation(self, action: str, **kwargs) -> Dict[str, Any]:
        """
        Execute a code operation using the core_old CODE handler.
        
        Args:
            action (str): Code action (generate, execute, analyze)
            **kwargs: Additional parameters for the code operation
            
        Returns:
            Dict[str, Any]: Execution result
        """
        code_data = {"action": action, **kwargs}
        return await self.execute_command("CODE", code_data)
    
    async def ask_ai(self, query: str) -> Dict[str, Any]:
        """
        Ask a question to the AI using the core_old ASK handler.
        
        Args:
            query (str): The question to ask
            
        Returns:
            Dict[str, Any]: AI response
        """
        return await self.execute_command("ASK", {"query": query})

# Create a singleton instance
core_execution_bridge = CoreExecutionBridge()
