"""
Tool Integration Example for Project-S
-------------------------------------
This module demonstrates how to integrate tools with Project-S's cognitive core.
"""
import asyncio
import logging
from typing import Dict, Any, List, Optional

from core.event_bus import event_bus
from core.cognitive_core import CognitiveCore
from integrations.tool_manager import tool_manager
from integrations.example_tools import register_all_example_tools, read_file, web_search, execute_python

logger = logging.getLogger(__name__)

# Ensure example tools are registered
tool_info = register_all_example_tools()


class ToolIntegrationExample:
    """
    Example class showing how to integrate tools with Project-S's event system.
    """
    
    def __init__(self, cognitive_core: Optional[CognitiveCore] = None):
        """
        Initialize the tool integration example.
        
        Args:
            cognitive_core: Optional cognitive core instance to use
        """
        self.core = cognitive_core
        
        # Register event handlers
        event_bus.subscribe("command.file.read", self._handle_file_read)
        event_bus.subscribe("command.web.search", self._handle_web_search)
        event_bus.subscribe("command.code.execute", self._handle_code_execution)
        event_bus.subscribe("tool.executed", self._handle_tool_executed)
        
        logger.info("Tool integration example initialized")
    
    async def _handle_file_read(self, event_data: Dict[str, Any]):
        """
        Handle file read command.
        
        Args:
            event_data: Command data
        """
        try:
            file_path = event_data.get("file_path")
            if not file_path:
                await event_bus.publish("command.error", {
                    "error": "Missing file path",
                    "command": "file.read"
                })
                return
            
            # Execute the tool
            result = await tool_manager.execute_tool("read_file", file_path=file_path)
            
            # Publish results
            if result.success:
                await event_bus.publish("command.completed", {
                    "command": "file.read",
                    "result": result.result,
                    "file_path": file_path
                })
            else:
                await event_bus.publish("command.error", {
                    "command": "file.read",
                    "error": result.error,
                    "file_path": file_path
                })
        except Exception as e:
            logger.error(f"Error in file read handler: {str(e)}")
            await event_bus.publish("command.error", {
                "command": "file.read",
                "error": str(e)
            })
    
    async def _handle_web_search(self, event_data: Dict[str, Any]):
        """
        Handle web search command.
        
        Args:
            event_data: Command data
        """
        try:
            query = event_data.get("query")
            if not query:
                await event_bus.publish("command.error", {
                    "error": "Missing search query",
                    "command": "web.search"
                })
                return
                
            num_results = event_data.get("num_results", 5)
            
            # Execute the tool
            result = await tool_manager.execute_tool("web_search", query=query, num_results=num_results)
            
            # Publish results
            if result.success:
                await event_bus.publish("command.completed", {
                    "command": "web.search",
                    "result": result.result,
                    "query": query
                })
            else:
                await event_bus.publish("command.error", {
                    "command": "web.search",
                    "error": result.error,
                    "query": query
                })
        except Exception as e:
            logger.error(f"Error in web search handler: {str(e)}")
            await event_bus.publish("command.error", {
                "command": "web.search",
                "error": str(e)
            })
    
    async def _handle_code_execution(self, event_data: Dict[str, Any]):
        """
        Handle code execution command.
        
        Args:
            event_data: Command data
        """
        try:
            code = event_data.get("code")
            if not code:
                await event_bus.publish("command.error", {
                    "error": "Missing code to execute",
                    "command": "code.execute"
                })
                return
            
            # Execute the tool
            result = await tool_manager.execute_tool("execute_python", code=code)
            
            # Publish results
            if result.success:
                await event_bus.publish("command.completed", {
                    "command": "code.execute",
                    "result": result.result,
                    "code": code
                })
            else:
                await event_bus.publish("command.error", {
                    "command": "code.execute",
                    "error": result.error,
                    "code": code
                })
        except Exception as e:
            logger.error(f"Error in code execution handler: {str(e)}")
            await event_bus.publish("command.error", {
                "command": "code.execute",
                "error": str(e)
            })
    
    async def _handle_tool_executed(self, event_data: Dict[str, Any]):
        """
        Handle tool executed event for monitoring.
        
        Args:
            event_data: Event data
        """
        tool_name = event_data.get("tool_name", "unknown")
        success = event_data.get("success", False)
        execution_time = event_data.get("execution_time", 0)
        
        # Update the cognitive core context if available
        if self.core:
            if "tools" not in self.core.context:
                self.core.context["tools"] = {}
                
            if tool_name not in self.core.context["tools"]:
                self.core.context["tools"][tool_name] = {
                    "calls": 0,
                    "successes": 0,
                    "failures": 0,
                    "total_time": 0,
                    "last_result": None
                }
                
            # Update stats
            self.core.context["tools"][tool_name]["calls"] += 1
            if success:
                self.core.context["tools"][tool_name]["successes"] += 1
            else:
                self.core.context["tools"][tool_name]["failures"] += 1
                
            self.core.context["tools"][tool_name]["total_time"] += execution_time
            self.core.context["tools"][tool_name]["last_result"] = event_data.get("result") or event_data.get("error")
            
        logger.debug(f"Tool {tool_name} executed: success={success}, time={execution_time:.4f}s")


async def run_example():
    """
    Run the tool integration example.
    """
    # Initialize the example
    example = ToolIntegrationExample()
    
    # Example 1: Read a file
    logger.info("Example 1: Reading a file")
    await event_bus.publish("command.file.read", {
        "file_path": "README.md"
    })
    
    # Wait a bit for events to process
    await asyncio.sleep(0.5)
    
    # Example 2: Search the web
    logger.info("Example 2: Searching the web")
    await event_bus.publish("command.web.search", {
        "query": "Project-S agent framework",
        "num_results": 3
    })
    
    # Wait a bit for events to process
    await asyncio.sleep(0.5)
    
    # Example 3: Execute Python code
    logger.info("Example 3: Executing Python code")
    await event_bus.publish("command.code.execute", {
        "code": """
import os
result = {
    'current_dir': os.getcwd(),
    'files': os.listdir('.')[0:5],
    'message': 'Hello from Project-S!'
}
"""
    })
    
    # Wait for events to process
    await asyncio.sleep(0.5)
    
    logger.info("Tool integration example completed")


if __name__ == "__main__":
    # Set up logging
    logging.basicConfig(level=logging.INFO)
    
    # Run the example
    asyncio.run(run_example())