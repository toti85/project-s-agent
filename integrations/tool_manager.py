"""
Tool Manager for Project-S with LangGraph Integration
----------------------------------------------------
This module provides a unified tool registration and management system for Project-S,
integrating with LangGraph's ToolNode capabilities for graph-based workflows.

Tools are discrete operations that can be executed by the agent, such as file operations,
web searches, code execution, etc. Each tool has a specific interface, validation rules,
and error handling.
"""
import logging
import inspect
import json
import asyncio
import traceback
from typing import Dict, Any, List, Callable, Optional, Union, Type, get_type_hints
from pydantic import BaseModel, Field, ValidationError, create_model
import functools
from langgraph.prebuilt import ToolNode

try:
    from langgraph.graph.message import add_messages, add_message
    HAS_LANGGRAPH_MESSAGES = True
except ImportError:
    HAS_LANGGRAPH_MESSAGES = False

from core.event_bus import event_bus
from core.error_handler import error_handler

logger = logging.getLogger(__name__)


class ToolMetadata(BaseModel):
    """Metadata for a registered tool."""
    name: str
    description: str
    category: str = "general"
    version: str = "1.0.0"
    author: str = "Project-S"
    requires_auth: bool = False
    is_dangerous: bool = False
    rate_limit: Optional[int] = None  # Rate limit in calls per minute
    timeout: Optional[int] = None  # Timeout in seconds
    example: Optional[str] = None
    tags: List[str] = Field(default_factory=list)


class ToolResult(BaseModel):
    """Common structure for tool execution results."""
    success: bool
    result: Any = None
    error: Optional[str] = None
    error_type: Optional[str] = None
    traceback: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ToolManager:
    """
    Manager for registering, validating, and executing tools.
    
    Provides a unified interface for:
    - Registering tools with metadata and validation
    - Executing tools with proper error handling
    - Converting tools to LangGraph ToolNodes
    - Monitoring tool performance and usage
    """
    
    def __init__(self):
        """Initialize the tool manager with empty registries."""
        self.tools: Dict[str, Dict[str, Any]] = {}
        self.categories: Dict[str, List[str]] = {}
        self.usage_stats: Dict[str, Dict[str, int]] = {}
        self.rate_limiters: Dict[str, Dict[str, Any]] = {}
        
        # Register events
        event_bus.subscribe("tool.executed", self._on_tool_executed)
        logger.info("Tool manager initialized")
    
    def register(self, name: str = None, metadata: Optional[Dict[str, Any]] = None):
        """
        Decorator to register a function as a tool.
        
        Args:
            name: Optional custom name for the tool. If not provided, the function name is used.
            metadata: Optional metadata for the tool.
            
        Returns:
            The decorated function
            
        Example:
            @tool_manager.register(
                metadata={
                    "description": "Search the web for information",
                    "category": "web",
                    "tags": ["search", "web"],
                    "is_dangerous": False
                }
            )
            async def web_search(query: str, limit: int = 10) -> Dict[str, Any]:
                # Implementation
                return {"results": [...]}
        """
        def decorator(func):
            # Get function name if custom name not provided
            tool_name = name or func.__name__
            
            # Extract metadata from docstring and function signature if not provided
            final_metadata = self._extract_metadata_from_function(func)
            
            # Override with provided metadata if any
            if metadata:
                final_metadata.update(metadata)
                
            # Create the tool metadata object
            tool_metadata = ToolMetadata(
                name=tool_name,
                description=final_metadata.get("description", func.__doc__ or "No description available"),
                category=final_metadata.get("category", "general"),
                version=final_metadata.get("version", "1.0.0"),
                author=final_metadata.get("author", "Project-S"),
                requires_auth=final_metadata.get("requires_auth", False),
                is_dangerous=final_metadata.get("is_dangerous", False),
                rate_limit=final_metadata.get("rate_limit"),
                timeout=final_metadata.get("timeout"),
                example=final_metadata.get("example"),
                tags=final_metadata.get("tags", [])
            )
            
            # Generate parameter model for validation
            param_model = self._generate_param_model(func)
            
            # Register the tool
            self.tools[tool_name] = {
                "func": func,
                "metadata": tool_metadata,
                "param_model": param_model,
                "is_async": asyncio.iscoroutinefunction(func)
            }
            
            # Add to category registry
            category = tool_metadata.category
            if category not in self.categories:
                self.categories[category] = []
            if tool_name not in self.categories[category]:
                self.categories[category].append(tool_name)
            
            # Initialize usage stats
            self.usage_stats[tool_name] = {
                "calls": 0,
                "successes": 0,
                "failures": 0,
                "total_time": 0,
                "avg_time": 0
            }
            
            # Set up rate limiter if needed
            if tool_metadata.rate_limit:
                self.rate_limiters[tool_name] = {
                    "limit": tool_metadata.rate_limit,
                    "calls": [],  # List of timestamps
                }
            
            logger.info(f"Registered tool: {tool_name} in category {category}")
            
            @functools.wraps(func)
            async def wrapper(*args, **kwargs):
                return await self.execute_tool(tool_name, *args, **kwargs)
                
            return wrapper
            
        return decorator
    
    def _extract_metadata_from_function(self, func) -> Dict[str, Any]:
        """Extract metadata from function docstring and signature."""
        metadata = {}
        
        # Extract description from docstring
        if func.__doc__:
            metadata["description"] = func.__doc__.strip().split("\n")[0]
            
            # Look for metadata tags in docstring like @category, @author, etc.
            for line in func.__doc__.strip().split("\n"):
                line = line.strip()
                if line.startswith("@"):
                    parts = line[1:].split(":", 1)
                    if len(parts) == 2:
                        key, value = parts
                        metadata[key.strip()] = value.strip()
        
        # Get parameter names and types from function signature
        metadata["parameters"] = {}
        sig = inspect.signature(func)
        for param_name, param in sig.parameters.items():
            if param_name == "self" or param_name == "cls":
                continue
                
            param_type = "Any"
            if param.annotation != inspect.Parameter.empty:
                param_type = str(param.annotation)
                if "typing." in param_type:
                    param_type = param_type.split(".")[-1]
                    
            default_value = None
            if param.default != inspect.Parameter.empty:
                default_value = param.default
                
            metadata["parameters"][param_name] = {
                "type": param_type,
                "default": default_value
            }
            
        return metadata
    
    def _generate_param_model(self, func) -> Type[BaseModel]:
        """Generate a pydantic model for validating tool parameters."""
        sig = inspect.signature(func)
        fields = {}
        annotations = get_type_hints(func)
        
        for param_name, param in sig.parameters.items():
            if param_name == "self" or param_name == "cls":
                continue
                
            # Get annotation or default to Any
            annotation = annotations.get(param_name, Any)
            
            # Set default if provided
            if param.default != inspect.Parameter.empty:
                fields[param_name] = (annotation, Field(default=param.default))
            else:
                fields[param_name] = (annotation, Field())
                
        # Create a dynamic model
        return create_model(f"{func.__name__}Parameters", **fields)
    
    def get_tool_schema(self, tool_name: str) -> Dict[str, Any]:
        """
        Get the JSON schema for a tool, including its parameters.
        
        Args:
            tool_name: The name of the tool
            
        Returns:
            Dict containing the tool's schema
        """
        if tool_name not in self.tools:
            raise ValueError(f"Tool not found: {tool_name}")
            
        tool = self.tools[tool_name]
        metadata = tool["metadata"]
        
        # Get schema from pydantic model
        schema = tool["param_model"].schema()
        
        return {
            "name": tool_name,
            "description": metadata.description,
            "parameters": schema,
            "category": metadata.category,
            "tags": metadata.tags
        }
    
    def list_tools(self, category: Optional[str] = None) -> List[str]:
        """
        List available tools, optionally filtered by category.
        
        Args:
            category: Optional category to filter tools
            
        Returns:
            List of tool names
        """
        if category:
            return self.categories.get(category, [])
        else:
            return list(self.tools.keys())
    
    def get_tool_metadata(self, tool_name: str) -> ToolMetadata:
        """
        Get metadata for a specific tool.
        
        Args:
            tool_name: The name of the tool
            
        Returns:
            ToolMetadata object
        """
        if tool_name not in self.tools:
            raise ValueError(f"Tool not found: {tool_name}")
        return self.tools[tool_name]["metadata"]
    
    async def execute_tool(self, tool_name: str, *args, **kwargs) -> ToolResult:
        """
        Execute a tool by name with provided arguments.
        
        Handles:
        - Parameter validation
        - Error handling
        - Rate limiting
        - Timeout
        - Usage statistics
        
        Args:
            tool_name: The name of the tool to execute
            *args, **kwargs: Arguments for the tool
            
        Returns:
            ToolResult with execution results or error information
        """
        if tool_name not in self.tools:
            return ToolResult(
                success=False, 
                error=f"Tool not found: {tool_name}",
                error_type="ToolNotFoundError"
            )
            
        tool = self.tools[tool_name]
        metadata = tool["metadata"]
        func = tool["func"]
        param_model = tool["param_model"]
        
        # Track start time for performance monitoring
        start_time = asyncio.get_event_loop().time()
        
        try:
            # Check rate limiting
            if tool_name in self.rate_limiters:
                limiter = self.rate_limiters[tool_name]
                current_time = asyncio.get_event_loop().time()
                
                # Clean old timestamps
                limiter["calls"] = [t for t in limiter["calls"] if current_time - t < 60]
                
                # Check if limit exceeded
                if len(limiter["calls"]) >= limiter["limit"]:
                    return ToolResult(
                        success=False, 
                        error=f"Rate limit exceeded for tool: {tool_name}. Try again later.",
                        error_type="RateLimitExceededError"
                    )
                    
                # Add current timestamp
                limiter["calls"].append(current_time)
            
            # Validate parameters
            try:
                # Convert positional args to keyword args for validation
                sig = inspect.signature(func)
                param_names = list(sig.parameters.keys())
                
                # Remove 'self' or 'cls' if present
                if param_names and param_names[0] in ('self', 'cls'):
                    param_names = param_names[1:]
                
                # Combine positional and keyword args
                all_kwargs = kwargs.copy()
                for i, arg in enumerate(args):
                    if i < len(param_names):
                        all_kwargs[param_names[i]] = arg
                
                # Validate with pydantic model
                validated_params = param_model(**all_kwargs)
                all_kwargs = validated_params.dict()
                
            except ValidationError as e:
                return ToolResult(
                    success=False, 
                    error=f"Invalid parameters for tool {tool_name}: {str(e)}",
                    error_type="ParameterValidationError"
                )
            
            # Execute the tool with timeout if specified
            if metadata.timeout:
                try:
                    if tool["is_async"]:
                        result = await asyncio.wait_for(
                            func(**all_kwargs),
                            timeout=metadata.timeout
                        )
                    else:
                        result = await asyncio.wait_for(
                            asyncio.to_thread(func, **all_kwargs),
                            timeout=metadata.timeout
                        )
                except asyncio.TimeoutError:
                    return ToolResult(
                        success=False, 
                        error=f"Tool {tool_name} execution timed out after {metadata.timeout} seconds",
                        error_type="ExecutionTimeoutError"
                    )
            else:
                # Execute without timeout
                if tool["is_async"]:
                    result = await func(**all_kwargs)
                else:
                    result = await asyncio.to_thread(func, **all_kwargs)
            
            # Calculate execution time
            execution_time = asyncio.get_event_loop().time() - start_time
            
            # Update usage statistics
            self.usage_stats[tool_name]["calls"] += 1
            self.usage_stats[tool_name]["successes"] += 1
            self.usage_stats[tool_name]["total_time"] += execution_time
            self.usage_stats[tool_name]["avg_time"] = (
                self.usage_stats[tool_name]["total_time"] / self.usage_stats[tool_name]["successes"]
            )
            
            # Publish tool execution event
            await event_bus.publish("tool.executed", {
                "tool_name": tool_name,
                "success": True,
                "execution_time": execution_time,
                "parameters": {k: v for k, v in all_kwargs.items() if not k.startswith("_")}
            })
            
            return ToolResult(
                success=True,
                result=result,
                metadata={
                    "execution_time": execution_time
                }
            )
            
        except Exception as e:
            # Calculate execution time
            execution_time = asyncio.get_event_loop().time() - start_time
            
            # Get exception details
            error_type = type(e).__name__
            error_message = str(e)
            error_traceback = traceback.format_exc()
            
            # Update usage statistics
            self.usage_stats[tool_name]["calls"] += 1
            self.usage_stats[tool_name]["failures"] += 1
            
            # Log error
            logger.error(f"Error executing tool {tool_name}: {error_message}\n{error_traceback}")
            
            # Handle error with error handler
            error_context = {
                "component": "tool_manager",
                "tool_name": tool_name,
                "parameters": kwargs
            }
            await error_handler.handle_error(e, error_context)
            
            # Publish tool execution event
            await event_bus.publish("tool.executed", {
                "tool_name": tool_name,
                "success": False,
                "error": error_message,
                "execution_time": execution_time
            })
            
            return ToolResult(
                success=False,
                error=error_message,
                error_type=error_type,
                traceback=error_traceback
            )
    
    def create_tool_node(self, tool_name: str) -> ToolNode:
        """
        Create a LangGraph ToolNode for a registered tool.
        
        Args:
            tool_name: The name of the tool
            
        Returns:
            A LangGraph ToolNode wrapper for the tool
        """
        if tool_name not in self.tools:
            raise ValueError(f"Tool not found: {tool_name}")
            
        tool = self.tools[tool_name]
        
        async def tool_func(state):
            """Tool function that executes the tool with state context."""
            # Extract parameters from state or context
            params = {}
            
            # Try to find parameters in different locations based on the state structure
            if isinstance(state, dict):
                if "tool_input" in state:
                    # Handle case where input is in tool_input field
                    tool_input = state["tool_input"]
                    if isinstance(tool_input, dict):
                        params.update(tool_input)
                    elif isinstance(tool_input, str):
                        # Try to parse as JSON if it's a string
                        try:
                            parsed = json.loads(tool_input)
                            if isinstance(parsed, dict):
                                params.update(parsed)
                        except json.JSONDecodeError:
                            # Use as a single parameter if parsing fails
                            param_model = tool["param_model"]
                            if len(param_model.__fields__) == 1:
                                param_name = list(param_model.__fields__.keys())[0]
                                params[param_name] = tool_input
                
                # Check for parameters in the state or context
                for location in ["parameters", "context", "tool_parameters"]:
                    if location in state and isinstance(state[location], dict):
                        params.update(state[location])
            
            # Execute the tool
            result = await self.execute_tool(tool_name, **params)
            
            # Update state with tool results
            new_state = dict(state) if isinstance(state, dict) else {"messages": []}
            
            if "tools" not in new_state:
                new_state["tools"] = {}
            
            new_state["tools"][tool_name] = {
                "success": result.success,
                "result": result.result,
                "error": result.error,
                "timestamp": asyncio.get_event_loop().time()
            }
            
            # Add a message if LangGraph messaging is supported
            if HAS_LANGGRAPH_MESSAGES:
                # Only import if we know it's available
                from langgraph.graph.message import add_message
                
                if result.success:
                    content = f"Tool {tool_name} executed successfully: {result.result}"
                else:
                    content = f"Tool {tool_name} failed: {result.error}"
                    
                new_state = add_message(new_state, "tool", content)
            
            return new_state
        
        # Create ToolNode with metadata
        metadata = tool["metadata"]
        
        # Generate a schema for the tool
        schema = self.get_tool_schema(tool_name)
        
        # Create and return the ToolNode
        return ToolNode(tool_func, name=tool_name, description=metadata.description)
    
    def create_all_tool_nodes(self, category: Optional[str] = None) -> Dict[str, ToolNode]:
        """
        Create LangGraph ToolNodes for all registered tools, optionally filtered by category.
        
        Args:
            category: Optional category to filter tools
            
        Returns:
            Dict of tool name to ToolNode
        """
        tools = {}
        
        # Get tool names based on category filter
        tool_names = self.list_tools(category)
        
        # Create a ToolNode for each tool
        for tool_name in tool_names:
            try:
                tools[tool_name] = self.create_tool_node(tool_name)
            except Exception as e:
                logger.error(f"Error creating ToolNode for {tool_name}: {e}")
                
        return tools
    
    async def _on_tool_executed(self, event_data: Any):
        """Handler for tool.executed events."""
        # This could be used for additional monitoring or logging
        pass
    
    def get_tool_stats(self, tool_name: Optional[str] = None) -> Union[Dict[str, Any], Dict[str, Dict[str, Any]]]:
        """
        Get usage statistics for a specific tool or all tools.
        
        Args:
            tool_name: Optional tool name to get stats for
            
        Returns:
            Dict of usage statistics
        """
        if tool_name:
            if tool_name not in self.usage_stats:
                raise ValueError(f"Tool not found: {tool_name}")
            return self.usage_stats[tool_name]
        else:
            return self.usage_stats
    
    def reset_stats(self, tool_name: Optional[str] = None):
        """
        Reset usage statistics for a specific tool or all tools.
        
        Args:
            tool_name: Optional tool name to reset stats for
        """
        if tool_name:
            if tool_name not in self.usage_stats:
                raise ValueError(f"Tool not found: {tool_name}")
            self.usage_stats[tool_name] = {
                "calls": 0,
                "successes": 0,
                "failures": 0,
                "total_time": 0,
                "avg_time": 0
            }
        else:
            for tool_name in self.usage_stats:
                self.usage_stats[tool_name] = {
                    "calls": 0,
                    "successes": 0,
                    "failures": 0,
                    "total_time": 0,
                    "avg_time": 0
                }


# Create singleton instance
tool_manager = ToolManager()
