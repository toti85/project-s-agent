"""
Project-S Simplified Model Manager
---------------------------------
Streamlined version focusing on intelligent routing with Qwen3-235B primary model.
Removes over-engineering while preserving core functionality.
"""

import os
import logging
import asyncio
import time
from typing import Dict, Any, List, Optional
from datetime import datetime

from integrations.multi_model_ai_client import multi_model_ai_client

# Tool integration for actual task execution
logger = logging.getLogger(__name__)

try:
    from tools.tool_registry import tool_registry
    TOOLS_AVAILABLE = True
    logger.info("Tool registry available for execution")
except ImportError as e:
    TOOLS_AVAILABLE = False
    logger.warning(f"Tool registry not available: {e}")

# Intelligent workflow integration - lazy loaded for faster startup
INTELLIGENT_WORKFLOWS_AVAILABLE = False
intelligent_workflow_orchestrator = None
process_with_intelligent_workflow = None

def _load_intelligent_workflows():
    """Lazy load intelligent workflow integration."""
    global INTELLIGENT_WORKFLOWS_AVAILABLE, intelligent_workflow_orchestrator, process_with_intelligent_workflow
    
    if not INTELLIGENT_WORKFLOWS_AVAILABLE:
        try:
            from integrations.intelligent_workflow_integration import (
                intelligent_workflow_orchestrator as iwo,
                process_with_intelligent_workflow as pwiw
            )
            intelligent_workflow_orchestrator = iwo
            process_with_intelligent_workflow = pwiw
            INTELLIGENT_WORKFLOWS_AVAILABLE = True
            logger.info("✅ Intelligent workflow integration loaded on demand")
        except ImportError as e:
            logger.warning(f"⚠️ Intelligent workflow integration not available: {e}")
    
    return INTELLIGENT_WORKFLOWS_AVAILABLE

class SimplifiedModelManager:
    """
    Simplified model manager focusing on fast, intelligent routing.
    """
    
    def __init__(self):
        """Initialize simplified model manager."""
        self.ai_client = multi_model_ai_client
        self.default_model = "qwen3-235b"  # Primary model
        self.command_count = 0
        
        # Simple task type mapping
        self.task_keywords = {
            "file": ["create", "file", "write file", "save", "hozz létre", "fájl"],
            "code": ["function", "script", "code", "python", "javascript", "implement", "kód", "függvény"],
            "web": ["website", "url", "analyze", "scrape", "web", "weboldal", "elemezd"],
            "system": ["command", "run", "execute", "shell", "parancs", "futtat"]
        }
        
        logger.info("Simplified Model Manager initialized")
    
    def determine_task_type(self, query: str) -> str:
        """
        Simple task type detection based on keywords.
        
        Args:
            query: User query
            
        Returns:
            Task type string
        """
        query_lower = query.lower()
        
        # Check for specific task types
        for task_type, keywords in self.task_keywords.items():
            if any(keyword in query_lower for keyword in keywords):
                return task_type
        
        # Default to general
        return "general"
    
    async def execute_task_with_core_system(self, user_input: str) -> Dict[str, Any]:
        """
        Main execution method - handles routing and execution.
        
        Args:
            user_input: User command/query
            
        Returns:
            Execution result
        """
        start_time = time.time()
        self.command_count += 1
        
        logger.info(f"Processing command #{self.command_count}: {user_input[:50]}...")
        
        try:
            # 1. Determine task type
            task_type = self.determine_task_type(user_input)
            logger.info(f"Task type: {task_type}")
              # 2. Check for intelligent workflows first (complex tasks)
            if self._is_complex_workflow(user_input) and _load_intelligent_workflows():
                return await self._execute_intelligent_workflow(user_input)
            
            # 3. Check for direct tool execution (simple tasks)
            if TOOLS_AVAILABLE and self._is_direct_tool_task(user_input, task_type):
                return await self._execute_direct_tool(user_input, task_type)
            
            # 4. Default: AI-powered execution with tool integration
            return await self._execute_with_ai_and_tools(user_input, task_type)
            
        except Exception as e:
            logger.error(f"Execution failed: {e}")
            return {
                "status": "error",
                "error": str(e),
                "execution_time": time.time() - start_time
            }
    
    def _is_complex_workflow(self, query: str) -> bool:
        """Check if query requires intelligent workflow."""
        complex_indicators = [
            "analyze website", "scrape", "download", "organize", 
            "elemezd", "weboldal", "letölt", "rendezd"
        ]
        return any(indicator in query.lower() for indicator in complex_indicators)
    
    def _is_direct_tool_task(self, query: str, task_type: str) -> bool:
        """Check if task can be handled directly by tools."""
        if task_type == "file":
            # Simple file operations
            simple_file_ops = ["create", "hozz létre", "write", "save"]
            return any(op in query.lower() for op in simple_file_ops)
        elif task_type == "system":
            # Simple system commands
            return "run" in query.lower() or "execute" in query.lower()
        return False
    
    async def _execute_intelligent_workflow(self, user_input: str) -> Dict[str, Any]:
        """Execute via intelligent workflow system."""
        try:
            result = await process_with_intelligent_workflow(user_input)
            return {
                "command_type": "INTELLIGENT_WORKFLOW",
                "execution_result": result,
                "status": "success"
            }
        except Exception as e:
            logger.error(f"Intelligent workflow failed: {e}")
            # Fallback to regular AI execution
            return await self._execute_with_ai_and_tools(user_input, "workflow")
    
    async def _execute_direct_tool(self, user_input: str, task_type: str) -> Dict[str, Any]:
        """Execute simple tasks directly via tools."""
        try:
            # For file operations
            if task_type == "file":
                return await self._handle_file_operation(user_input)
            elif task_type == "system":
                return await self._handle_system_command(user_input)
            
            # Fallback
            return await self._execute_with_ai_and_tools(user_input, task_type)
            
        except Exception as e:
            logger.error(f"Direct tool execution failed: {e}")
            return {"status": "error", "error": str(e)}
    
    async def _handle_file_operation(self, user_input: str) -> Dict[str, Any]:
        """Handle simple file operations directly, including multiple commands separated by 'and' or 'then'."""
        try:
            from core.ai_command_handler import ai_handler
            import re
            # Split on 'and' or 'then' (case-insensitive, with comma or space)
            commands = re.split(r"\s*(?:,?\s*(?:and|then)\s*)+", user_input, flags=re.IGNORECASE)
            results = []
            for cmd in commands:
                cmd = cmd.strip()
                if not cmd:
                    continue
                match = re.match(r"create\s+([\w.\\/-]+)\s+with content\s+(.+)", cmd, re.IGNORECASE)
                if match:
                    path = match.group(1)
                    content = match.group(2)
                    file_command = {"action": "write", "path": path, "content": content}
                else:
                    match2 = re.match(r"create\s+([\w.\\/-]+)", cmd, re.IGNORECASE)
                    if match2:
                        path = match2.group(1)
                        file_command = {"action": "write", "path": path, "content": ""}
                    else:
                        file_command = {"command": cmd}
                result = await ai_handler.handle_file_command(file_command)
                results.append({"command": cmd, "result": result})
            # If only one command, return as before
            if len(results) == 1:
                return {
                    "command_type": "FILE",
                    "execution_result": results[0]["result"],
                    "status": "success"
                }
            # If multiple, return all
            return {
                "command_type": "FILE",
                "execution_result": results,
                "status": "success"
            }
        except Exception as e:
            logger.error(f"File operation failed: {e}")
            return {"status": "error", "error": str(e)}
    
    async def _handle_system_command(self, user_input: str) -> Dict[str, Any]:
        """Handle system commands."""
        try:
            # Import here to avoid circular dependencies
            from core.ai_command_handler import ai_handler
            
            # Extract command from user input
            command = user_input.replace("run", "").replace("execute", "").strip()
            
            result = await ai_handler.handle_cmd_command({"cmd": command})
            
            return {
                "command_type": "CMD",
                "execution_result": result,
                "status": "success"
            }
            
        except Exception as e:
            logger.error(f"System command failed: {e}")
            return {"status": "error", "error": str(e)}
    
    async def _execute_with_ai_and_tools(self, user_input: str, task_type: str) -> Dict[str, Any]:
        """Execute with AI analysis and potential tool integration."""
        try:
            # 1. Get AI response using the primary model
            ai_response = await self.ai_client.generate_response(
                prompt=user_input,
                model=self.default_model,
                task_type=task_type,
                temperature=0.7
            )
            
            # 2. Check if tools are needed based on AI response
            if TOOLS_AVAILABLE and self._should_use_tools(ai_response, task_type):
                # Enhance with tool execution
                return await self._enhance_with_tools(user_input, ai_response, task_type)
            
            # 3. Return AI-only response
            return {
                "command_type": "AI_RESPONSE",
                "execution_result": {
                    "content": ai_response,
                    "model": self.default_model,
                    "task_type": task_type
                },
                "status": "success"
            }
            
        except Exception as e:
            logger.error(f"AI execution failed: {e}")
            return {"status": "error", "error": str(e)}
    
    def _should_use_tools(self, ai_response: str, task_type: str) -> bool:
        """Determine if tools should be used based on response and task type."""
        tool_indicators = [
            "create file", "write file", "save to", "execute command",
            "run script", "analyze", "scrape", "download"
        ]
        return any(indicator in ai_response.lower() for indicator in tool_indicators)
    
    async def _enhance_with_tools(self, user_input: str, ai_response: str, task_type: str) -> Dict[str, Any]:
        """Enhance AI response with actual tool execution."""
        try:
            # Simple tool mapping based on task type
            if task_type == "file" or "file" in ai_response.lower():
                from core.ai_command_handler import ai_handler
                tool_result = await ai_handler.handle_file_command({"command": user_input})
                
                return {
                    "command_type": "AI_WITH_TOOLS",
                    "execution_result": {
                        "ai_response": ai_response,
                        "tool_result": tool_result,
                        "model": self.default_model
                    },
                    "status": "success"
                }
            
            # Default: return AI response only
            return {
                "command_type": "AI_RESPONSE",
                "execution_result": {
                    "content": ai_response,
                    "model": self.default_model
                },
                "status": "success"
            }
            
        except Exception as e:
            logger.error(f"Tool enhancement failed: {e}")
            # Return AI response as fallback
            return {
                "command_type": "AI_RESPONSE",
                "execution_result": {
                    "content": ai_response,
                    "model": self.default_model,
                    "note": f"Tool enhancement failed: {e}"
                },
                "status": "partial_success"
            }
    
    def get_stats(self) -> Dict[str, Any]:
        """Get simple statistics."""
        return {
            "commands_processed": self.command_count,
            "primary_model": self.default_model,
            "tools_available": TOOLS_AVAILABLE,
            "workflows_available": INTELLIGENT_WORKFLOWS_AVAILABLE
        }


# Create singleton instance
model_manager = SimplifiedModelManager()
