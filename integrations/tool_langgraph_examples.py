"""
Tool Integration with LangGraph Workflows
----------------------------------------
This module provides examples of how to integrate Project-S tools with LangGraph workflows.
"""
import logging
import asyncio
from typing import Dict, Any, List, Tuple, Optional, Union
from langgraph.graph import StateGraph
from langgraph.prebuilt import ToolNode

from integrations.tool_manager import tool_manager
from integrations.example_tools import register_all_example_tools
from integrations.langgraph_integration import GraphState

logger = logging.getLogger(__name__)

# Register all example tools
register_all_example_tools()


def create_file_operations_graph() -> StateGraph:
    """
    Create a LangGraph workflow for file operations.
    
    Returns:
        A StateGraph configured with file operation tools
    """
    # Get file operation tool nodes
    tool_nodes = tool_manager.create_all_tool_nodes(category="file")
    
    # Create a state graph
    graph = StateGraph()
    
    # Add nodes to graph
    for tool_name, tool_node in tool_nodes.items():
        graph.add_node(tool_name, tool_node)
    
    # Define edges based on task logic
    # For example, after listing a directory, we might want to read a file
    
    # Start with listing a directory
    graph.add_edge("list_directory", "read_file")
    
    # After reading a file, potentially write to it
    graph.add_edge("read_file", "write_file")
    
    # Set the entry point
    graph.set_entry_point("list_directory")
    
    return graph


def create_web_search_graph() -> StateGraph:
    """
    Create a LangGraph workflow for web search operations.
    
    Returns:
        A StateGraph configured with web search tools
    """
    # Get web search tool nodes
    tool_nodes = tool_manager.create_all_tool_nodes(category="web")
    
    # Create a state graph
    graph = StateGraph()
    
    # Add nodes to graph
    for tool_name, tool_node in tool_nodes.items():
        graph.add_node(tool_name, tool_node)
    
    # Define edges - search first, then fetch page content
    graph.add_edge("web_search", "fetch_webpage")
    
    # Set the entry point
    graph.set_entry_point("web_search")
    
    return graph


def create_composite_workflow() -> StateGraph:
    """
    Create a more complex workflow combining multiple tool categories.
    
    Returns:
        A StateGraph with a composite workflow
    """
    # Get tools from different categories
    file_tools = tool_manager.create_all_tool_nodes(category="file")
    web_tools = tool_manager.create_all_tool_nodes(category="web")
    code_tools = tool_manager.create_all_tool_nodes(category="code")
    
    # Create the graph
    graph = StateGraph()
    
    # Add file operation nodes
    for tool_name, tool_node in file_tools.items():
        graph.add_node(tool_name, tool_node)
        
    # Add web search nodes
    for tool_name, tool_node in web_tools.items():
        graph.add_node(tool_name, tool_node)
        
    # Add code execution nodes
    for tool_name, tool_node in code_tools.items():
        graph.add_node(tool_name, tool_node)
    
    # Add a router node for deciding what to do next
    async def router_node(state: GraphState):
        """Route to the next tool based on state."""
        # Example routing logic
        if "search_query" in state:
            return "web_search"
        elif "file_path" in state and "read" in state.get("action", ""):
            return "read_file"
        elif "file_path" in state and "write" in state.get("action", ""):
            return "write_file"
        elif "code" in state:
            return "execute_python"
        else:
            return "list_directory"  # Default action
    
    graph.add_node("router", router_node)
    
    # Add conditional edges
    # From router to tools
    graph.add_conditional_edges(
        "router",
        lambda state: state.get("next_step", "list_directory"),
        {
            "web_search": "web_search",
            "read_file": "read_file",
            "write_file": "write_file",
            "execute_python": "execute_python",
            "list_directory": "list_directory"
        }
    )
    
    # All tools go back to router for next step
    for tool_name in [*file_tools.keys(), *web_tools.keys(), *code_tools.keys()]:
        graph.add_edge(tool_name, "router")
    
    # Set the entry point
    graph.set_entry_point("router")
    
    return graph


async def run_file_workflow_example():
    """Example of running a file operations workflow."""
    graph = create_file_operations_graph()
    
    # Configure and compile the graph
    graph_instance = graph.compile()
    
    # Initial state with directory to list
    initial_state = {
        "parameters": {
            "directory_path": ".",  # Current directory
        },
        "messages": [],
        "next_step": "list_directory"
    }
    
    # Run the workflow
    result = await graph_instance.ainvoke(initial_state)
    
    return result


async def run_web_search_workflow_example():
    """Example of running a web search workflow."""
    graph = create_web_search_graph()
    
    # Configure and compile the graph
    graph_instance = graph.compile()
    
    # Initial state with search query
    initial_state = {
        "parameters": {
            "query": "Project-S agent framework",
            "num_results": 3
        },
        "messages": [],
        "next_step": "web_search"
    }
    
    # Run the workflow
    result = await graph_instance.ainvoke(initial_state)
    
    return result


async def run_composite_workflow_example():
    """Example of running a composite workflow."""
    graph = create_composite_workflow()
    
    # Configure and compile the graph
    graph_instance = graph.compile()
    
    # Initial state with multiple potential actions
    initial_state = {
        "parameters": {
            "directory_path": ".",  # Current directory for listing
            "search_query": "Python async tools",  # For web search
            "code": "print('Hello, Project-S!')"  # For code execution
        },
        "action": "list",
        "messages": [],
        "next_step": "router"
    }
    
    # Run the workflow
    result = await graph_instance.ainvoke(initial_state)
    
    return result


# Main example function to demonstrate tool integration
async def run_examples():
    """Run examples of tool integration with LangGraph workflows."""
    logger.info("Running file operations workflow example...")
    file_result = await run_file_workflow_example()
    logger.info(f"File workflow result: {file_result}")
    
    logger.info("Running web search workflow example...")
    web_result = await run_web_search_workflow_example()
    logger.info(f"Web search workflow result: {web_result}")
    
    logger.info("Running composite workflow example...")
    composite_result = await run_composite_workflow_example()
    logger.info(f"Composite workflow result: {composite_result}")
    
    return {
        "file_workflow": file_result,
        "web_workflow": web_result,
        "composite_workflow": composite_result
    }


# If run as script
if __name__ == "__main__":
    # Set up logging
    logging.basicConfig(level=logging.INFO)
    
    # Run examples
    asyncio.run(run_examples())
