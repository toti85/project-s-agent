"""
LangGraph Router Integration for Project-S
------------------------------------------
This module registers the LangGraph integrator with the command router.
"""
import logging
import asyncio
from typing import Dict, Any
from core.command_router import router
from core.error_handler import error_handler
from integrations.langgraph_integration import langgraph_integrator

logger = logging.getLogger("LangGraph_Router")

async def handle_workflow_command(command: Dict[str, Any]) -> Dict[str, Any]:
    """
    Handle WORKFLOW commands by routing to appropriate operations.
    
    Args:
        command: Dictionary containing the command data
        
    Returns:
        Dict[str, Any]: The result of the workflow operation
    """
    return await langgraph_integrator.handle_workflow_command(command)

def register_langgraph_handlers(command_router=None):
    """Register LangGraph command handlers with the command router"""
    
    if command_router is None:
        command_router = router  # Use the default singleton router
    
    # Register the WORKFLOW command type handler
    command_router.register("WORKFLOW", langgraph_integrator.handle_workflow_command)
    
    logger.info("LangGraph command handlers registered successfully")
