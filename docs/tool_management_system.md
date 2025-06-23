# Tool Management System for Project-S

This document describes the unified tool management system for Project-S, which integrates with LangGraph's ToolNode capabilities for graph-based workflows.

## Overview

The Tool Management System provides a unified mechanism for registering, validating, and executing tools within the Project-S agent framework. Tools are discrete operations that can be executed by the agent, such as:

- File operations
- Web searches
- Code execution
- System information retrieval
- And more...

## Key Features

- **Tool Registration**: Register tools with a simple decorator syntax
- **Parameter Validation**: Automatic parameter validation using Pydantic models
- **Error Handling**: Comprehensive error handling with detailed error reporting
- **LangGraph Integration**: Seamless integration with LangGraph's ToolNode for workflow graphs
- **Usage Statistics**: Track tool usage, success rates, and performance
- **Rate Limiting**: Optional rate limiting for tools that access external services
- **Timeouts**: Execution timeouts to prevent long-running operations
- **Categorization**: Organize tools by category for better management

## Registering a Tool

Tools are registered using the `@tool_manager.register()` decorator:

```python
from integrations.tool_manager import tool_manager

@tool_manager.register(
    metadata={
        "description": "Search the web for information",
        "category": "web",
        "tags": ["search", "web"],
        "is_dangerous": False,
        "rate_limit": 10,  # Limit to 10 calls per minute
        "timeout": 30      # Timeout after 30 seconds
    }
)
async def web_search(query: str, limit: int = 10) -> Dict[str, Any]:
    # Implementation
    return {"results": [...]}
```

The decorator automatically extracts parameter information from the function signature and generates a Pydantic model for validation.

## Tool Categories

Tools are organized into categories for easier management. Standard categories include:

- `file`: File operations (read, write, list, etc.)
- `web`: Web-related operations (search, fetch, etc.)
- `code`: Code execution and analysis
- `system`: System information and operations
- `general`: Miscellaneous tools

## Tool Execution

Tools can be executed directly or through the Tool Manager:

```python
# Direct execution (with automatic validation)
result = await web_search("Project-S agent")

# Through the tool manager
result = await tool_manager.execute_tool("web_search", query="Project-S agent")
```

All tool executions return a standardized `ToolResult` object with fields:

- `success`: Whether the execution was successful
- `result`: The result of the tool execution (if successful)
- `error`: Error message (if not successful)
- `error_type`: Type of error (if not successful)
- `traceback`: Error traceback (if not successful)
- `metadata`: Additional metadata about the execution

## LangGraph Integration

The Tool Manager can create LangGraph ToolNodes for any registered tool:

```python
# Create a ToolNode for a specific tool
tool_node = tool_manager.create_tool_node("web_search")

# Create ToolNodes for all tools in a category
file_tool_nodes = tool_manager.create_all_tool_nodes(category="file")
```

These ToolNodes can then be incorporated into LangGraph workflows:

```python
from langgraph.graph import StateGraph

# Create a graph
graph = StateGraph()

# Add tool nodes
for tool_name, tool_node in tool_nodes.items():
    graph.add_node(tool_name, tool_node)

# Define edges
graph.add_edge("web_search", "fetch_webpage")

# Set entry point
graph.set_entry_point("web_search")
```

## Error Handling

The Tool Manager provides comprehensive error handling:

1. **Parameter Validation**: Validates parameters before execution
2. **Execution Errors**: Catches and formats errors during execution
3. **Timeout Handling**: Handles execution timeouts
4. **Rate Limit Errors**: Reports when rate limits are exceeded

All errors are standardized in the `ToolResult` object and can be logged, reported to the user, or handled programmatically.

## Usage Statistics

The Tool Manager tracks usage statistics for all registered tools:

```python
# Get stats for a specific tool
stats = tool_manager.get_tool_stats("web_search")

# Get stats for all tools
all_stats = tool_manager.get_tool_stats()
```

Statistics include:
- Number of calls
- Success rate
- Average execution time
- Failure reasons

## Example Tools

The system includes example tools in several categories:

### File Operations

- `read_file`: Read the contents of a file
- `write_file`: Write content to a file
- `list_directory`: List files in a directory

### Web Operations

- `web_search`: Search the web for information
- `fetch_webpage`: Fetch and parse a web page

### Code Execution

- `execute_python`: Execute Python code and return the result
- `analyze_code`: Analyze code to extract structure and dependencies

### System Information

- `get_system_info`: Get system information and metrics

## Creating Tool Workflows

The Tool Management System integrates with LangGraph to create tool workflows. Example workflows include:

- File operations workflow
- Web search workflow
- Composite workflows combining multiple tool categories

## Best Practices

1. **Tool Design**:
   - Keep tools focused on a single responsibility
   - Use clear parameter names and types
   - Provide documentation and examples

2. **Error Handling**:
   - Always handle potential errors in tool implementations
   - Use try/except blocks to catch and format errors properly
   - Return standardized error responses

3. **Security**:
   - Mark dangerous tools with `is_dangerous=True`
   - Implement proper authorization checks
   - Sanitize inputs and validate parameters

4. **Performance**:
   - Use async functions for I/O-bound operations
   - Implement timeouts for external service calls
   - Use rate limiting for external API calls

5. **Integration**:
   - Follow the standard pattern for tool results
   - Organize tools into appropriate categories
   - Use tags for better discoverability

## Conclusion

The Tool Management System provides a unified and extensible way to register, validate, execute, and monitor tools within the Project-S agent framework. By integrating with LangGraph, it enables the creation of complex tool workflows for advanced agent capabilities.
