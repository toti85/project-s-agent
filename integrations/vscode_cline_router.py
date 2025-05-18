"""
VSCode Cline Command Router Integration for Project-S
---------------------------------------------------
This module integrates the VSCode Cline Controller with Project-S's command routing system.
It registers handlers for VSCode Cline operations like code generation, refactoring, and workflows.
"""

import logging
from typing import Dict, Any, Callable, Awaitable

from integrations.vscode_cline_controller import VSCodeClineController

logger = logging.getLogger("VSCode_Cline_Router")

def register_vscode_cline_handlers(command_router, vscode_cline_controller: VSCodeClineController) -> None:
    """Register VSCode Cline command handlers with the command router"""
    
    if not vscode_cline_controller:
        logger.error("Cannot register VSCode Cline handlers: controller is None")
        return
    
    @command_router.register_handler("vscode_cline")
    async def handle_vscode_cline_command(command_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle VSCode Cline commands"""
        operation = command_data.get("operation", "")
        logger.info(f"Processing VSCode Cline command: {operation}")
        
        if operation == "generate_code":
            # Code generation operation
            result = await vscode_cline_controller.generate_code(
                prompt=command_data.get("prompt", ""),
                language=command_data.get("language", "python"),
                filename=command_data.get("filename"),
                context=command_data.get("context")
            )
            return {"status": "success", "result": result}
            
        elif operation == "refactor_code":
            # Code refactoring operation
            result = await vscode_cline_controller.refactor_code(
                code=command_data.get("code", ""),
                instructions=command_data.get("instructions", ""),
                context=command_data.get("context")
            )
            return {"status": "success", "result": result}
            
        elif operation == "execute_workflow":
            # Workflow execution operation
            result = await vscode_cline_controller.execute_workflow(
                workflow_name=command_data.get("workflow", ""),
                parameters=command_data.get("parameters", {})
            )
            return {"status": "success", "result": result}
            
        else:
            logger.warning(f"Unknown VSCode Cline operation: {operation}")
            return {
                "status": "error", 
                "error": f"Unknown VSCode Cline operation: {operation}"
            }
    
    logger.info("VSCode Cline command handlers registered successfully")
