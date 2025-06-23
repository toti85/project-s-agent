"""
Tool Integration with Cognitive Core
-----------------------------------
This module integrates tools with Project-S's cognitive core.
"""
import logging
import asyncio
from typing import Dict, Any, List, Optional, Union

from core.event_bus import event_bus
from core.cognitive_core import cognitive_core
from integrations.tool_manager import tool_manager
from integrations.example_tools import register_all_example_tools

logger = logging.getLogger(__name__)

# Register example tools
register_all_example_tools()


class CognitiveToolIntegration:
    """
    Integrate tools with the cognitive core.
    
    This class enhances the cognitive core's capabilities by integrating 
    the tool management system, allowing the core to discover, execute,
    and learn from tools.
    """
    
    def __init__(self):
        """Initialize the cognitive tool integration."""
        # Register event handlers
        event_bus.subscribe("tool.executed", self._on_tool_executed)
        event_bus.subscribe("cognitive.task.created", self._on_task_created)
        event_bus.subscribe("cognitive.tool.request", self._on_tool_request)
        
        # Track which tools are relevant for different tasks
        self.task_tool_relevance = {}
        
        logger.info("Cognitive tool integration initialized")
    
    async def _on_tool_executed(self, event_data: Dict[str, Any]):
        """
        Update cognitive core context when a tool is executed.
        
        Args:
            event_data: Tool execution event data
        """
        tool_name = event_data.get("tool_name", "unknown")
        success = event_data.get("success", False)
        parameters = event_data.get("parameters", {})
        result = event_data.get("result")
        error = event_data.get("error")
        execution_time = event_data.get("execution_time", 0)
        
        # Get core context and update tool information
        context = cognitive_core.get_context()
        
        # Initialize tool context if needed
        if "tools" not in context:
            context["tools"] = {}
            
        if tool_name not in context["tools"]:
            context["tools"][tool_name] = {
                "executions": [],
                "success_rate": 1.0,
                "avg_execution_time": 0.0,
                "total_calls": 0
            }
            
        # Add this execution to history
        tool_context = context["tools"][tool_name]
        execution_data = {
            "timestamp": asyncio.get_event_loop().time(),
            "success": success,
            "parameters": parameters,
            "execution_time": execution_time
        }
        
        if success and result is not None:
            execution_data["result"] = result
        elif not success and error is not None:
            execution_data["error"] = error
            
        # Keep only the last 5 executions
        tool_context["executions"].append(execution_data)
        if len(tool_context["executions"]) > 5:
            tool_context["executions"] = tool_context["executions"][-5:]
            
        # Update statistics
        tool_context["total_calls"] += 1
        
        success_count = sum(1 for e in tool_context["executions"] if e["success"])
        tool_context["success_rate"] = success_count / len(tool_context["executions"])
        
        avg_time = sum(e["execution_time"] for e in tool_context["executions"]) / len(tool_context["executions"])
        tool_context["avg_execution_time"] = avg_time
        
        # Add recent tool execution to conversation context
        if "conversation" in context:
            context["conversation"].append({
                "timestamp": asyncio.get_event_loop().time(),
                "type": "tool_execution",
                "tool": tool_name,
                "success": success,
                "parameters": parameters,
                "result": result if success else None,
                "error": error if not success else None
            })
    
    async def _on_task_created(self, event_data: Dict[str, Any]):
        """
        When a new task is created, determine which tools might be relevant.
        
        Args:
            event_data: Task created event data
        """
        task = event_data.get("task")
        if not task:
            return
            
        task_id = task.get("id", "unknown")
        task_type = task.get("type", "").lower()
        task_description = task.get("description", "")
        
        # Determine relevant tools based on task type
        relevant_tools = []
        
        if task_type == "file_operation" or "file" in task_description.lower():
            # File operation tasks - add file tools
            relevant_tools.extend(tool_manager.list_tools(category="file"))
            
        elif task_type == "web_search" or any(kw in task_description.lower() for kw in ["web", "search", "internet"]):
            # Web search tasks - add web tools
            relevant_tools.extend(tool_manager.list_tools(category="web"))
            
        elif task_type == "code_analysis" or any(kw in task_description.lower() for kw in ["code", "execute", "python"]):
            # Code tasks - add code tools
            relevant_tools.extend(tool_manager.list_tools(category="code"))
            
        elif task_type == "system_info" or any(kw in task_description.lower() for kw in ["system", "info", "status"]):
            # System info tasks - add system tools
            relevant_tools.extend(tool_manager.list_tools(category="system"))
            
        # Store relevant tools for this task
        self.task_tool_relevance[task_id] = relevant_tools
        
        logger.info(f"Determined relevant tools for task {task_id}: {relevant_tools}")
        
        # Publish event with tool suggestions
        await event_bus.publish("cognitive.tool.suggestions", {
            "task_id": task_id,
            "suggested_tools": relevant_tools
        })
    
    async def _on_tool_request(self, event_data: Dict[str, Any]):
        """
        Handle a request to execute a tool from the cognitive core.
        
        Args:
            event_data: Tool request event data
        """
        tool_name = event_data.get("tool_name")
        parameters = event_data.get("parameters", {})
        task_id = event_data.get("task_id")
        
        if not tool_name:
            logger.error("Tool request missing tool_name")
            return
            
        try:
            # Execute the tool
            result = await tool_manager.execute_tool(tool_name, **parameters)
            
            # Publish result
            await event_bus.publish("cognitive.tool.result", {
                "task_id": task_id,
                "tool_name": tool_name,
                "parameters": parameters,
                "success": result.success,
                "result": result.result,
                "error": result.error
            })
        except Exception as e:
            logger.error(f"Error executing tool {tool_name}: {e}")
            
            # Publish error
            await event_bus.publish("cognitive.tool.result", {
                "task_id": task_id,
                "tool_name": tool_name,
                "parameters": parameters,
                "success": False,
                "error": str(e)
            })
    
    async def suggest_tools_for_query(self, query: str) -> List[Dict[str, Any]]:
        """
        Suggest relevant tools based on a query.
        
        Args:
            query: The user query or task description
            
        Returns:
            A list of tool suggestions with metadata
        """
        # Simple keyword matching to find relevant tools
        query_lower = query.lower()
        suggestions = []
        
        # Check for file-related keywords
        if any(kw in query_lower for kw in ["file", "read", "write", "directory", "folder", "list"]):
            file_tools = tool_manager.list_tools(category="file")
            for tool_name in file_tools:
                metadata = tool_manager.get_tool_metadata(tool_name)
                suggestions.append({
                    "tool_name": tool_name,
                    "description": metadata.description,
                    "relevance_score": 0.8,
                    "category": "file"
                })
        
        # Check for web-related keywords
        if any(kw in query_lower for kw in ["web", "search", "internet", "page", "online", "url"]):
            web_tools = tool_manager.list_tools(category="web")
            for tool_name in web_tools:
                metadata = tool_manager.get_tool_metadata(tool_name)
                suggestions.append({
                    "tool_name": tool_name,
                    "description": metadata.description,
                    "relevance_score": 0.8,
                    "category": "web"
                })
        
        # Check for code-related keywords
        if any(kw in query_lower for kw in ["code", "execute", "python", "run", "analyze"]):
            code_tools = tool_manager.list_tools(category="code")
            for tool_name in code_tools:
                metadata = tool_manager.get_tool_metadata(tool_name)
                suggestions.append({
                    "tool_name": tool_name,
                    "description": metadata.description,
                    "relevance_score": 0.8,
                    "category": "code"
                })
        
        # Check for system-related keywords
        if any(kw in query_lower for kw in ["system", "info", "status", "metrics", "performance"]):
            system_tools = tool_manager.list_tools(category="system")
            for tool_name in system_tools:
                metadata = tool_manager.get_tool_metadata(tool_name)
                suggestions.append({
                    "tool_name": tool_name,
                    "description": metadata.description,
                    "relevance_score": 0.8,
                    "category": "system"
                })
        
        # If no specific matches, suggest the most frequently used tools
        if not suggestions:
            # Get top 3 most frequently used tools from the tool usage stats
            usage_stats = tool_manager.get_tool_stats()
            top_tools = sorted(usage_stats.items(), key=lambda x: x[1]["calls"], reverse=True)[:3]
            
            for tool_name, stats in top_tools:
                if tool_name in tool_manager.tools:
                    metadata = tool_manager.get_tool_metadata(tool_name)
                    suggestions.append({
                        "tool_name": tool_name,
                        "description": metadata.description,
                        "relevance_score": 0.6,
                        "category": metadata.category,
                        "usage_count": stats["calls"]
                    })
        
        return suggestions
    
    async def execute_tool_for_task(self, task_id: str, tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a tool for a specific task and update the cognitive core context.
        
        Args:
            task_id: The ID of the task
            tool_name: The name of the tool to execute
            parameters: Tool parameters
            
        Returns:
            The tool execution result
        """
        try:
            # Execute the tool
            result = await tool_manager.execute_tool(tool_name, **parameters)
            
            # Update task context
            context = cognitive_core.get_context()
            if "tasks" in context and task_id in context["tasks"]:
                task = context["tasks"][task_id]
                
                if "tool_executions" not in task:
                    task["tool_executions"] = []
                    
                task["tool_executions"].append({
                    "tool_name": tool_name,
                    "parameters": parameters,
                    "success": result.success,
                    "result": result.result if result.success else None,
                    "error": result.error if not result.success else None,
                    "timestamp": asyncio.get_event_loop().time()
                })
                
                # If this was a successful file operation, update workspace context
                if result.success and tool_name in ["read_file", "write_file", "list_directory"]:
                    if "workspace" not in context:
                        context["workspace"] = {}
                        
                    # Handle different file tools
                    if tool_name == "read_file" and "file_path" in parameters:
                        file_path = parameters["file_path"]
                        context["workspace"][file_path] = {
                            "content": result.result["content"],
                            "last_read": asyncio.get_event_loop().time()
                        }
                    elif tool_name == "write_file" and "file_path" in parameters:
                        file_path = parameters["file_path"]
                        context["workspace"][file_path] = {
                            "last_write": asyncio.get_event_loop().time()
                        }
                    elif tool_name == "list_directory" and "directory_path" in parameters:
                        directory_path = parameters["directory_path"]
                        files = result.result["files"]
                        context["workspace"][directory_path] = {
                            "is_directory": True,
                            "files": files,
                            "last_listed": asyncio.get_event_loop().time()
                        }
            
            return {
                "task_id": task_id,
                "tool_name": tool_name,
                "success": result.success,
                "result": result.result,
                "error": result.error,
                "error_type": result.error_type,
                "metadata": result.metadata
            }
                
        except Exception as e:
            logger.error(f"Error executing tool {tool_name} for task {task_id}: {e}")
            return {
                "task_id": task_id,
                "tool_name": tool_name,
                "success": False,
                "error": str(e),
                "error_type": type(e).__name__
            }


# Create singleton instance
cognitive_tool_integration = CognitiveToolIntegration()
