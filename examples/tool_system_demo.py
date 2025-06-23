"""
Tool Management System Demo
--------------------------
This script demonstrates the complete tool management system
integrated with the cognitive core and LangGraph workflows.
"""
import asyncio
import logging
from typing import Dict, Any, Optional
import os
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("tool_demo")

# Add parent directory to path to import Project-S modules
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

# Import required modules
from integrations.example_tools import register_all_example_tools
from integrations.tool_manager import tool_manager
from integrations.tool_langgraph_examples import create_file_operations_graph, create_web_search_graph
from integrations.cognitive_tool_integration import cognitive_tool_integration
from core.cognitive_core import cognitive_core
from core.event_bus import event_bus


# Event listeners for demo purposes
async def on_tool_executed(event_data: Any):
    """Event listener for tool.executed events."""
    tool_name = event_data.get("tool_name", "unknown")
    success = event_data.get("success", False)
    execution_time = event_data.get("execution_time", 0)
    
    if success:
        logger.info(f"Tool {tool_name} executed successfully in {execution_time:.3f}s")
    else:
        logger.error(f"Tool {tool_name} failed after {execution_time:.3f}s: {event_data.get('error')}")


async def on_cognitive_tool_suggestions(event_data: Any):
    """Event listener for cognitive.tool.suggestions events."""
    task_id = event_data.get("task_id", "unknown")
    suggested_tools = event_data.get("suggested_tools", [])
    
    if suggested_tools:
        logger.info(f"Cognitive core suggested tools for task {task_id}: {', '.join(suggested_tools)}")
    else:
        logger.info(f"No tool suggestions for task {task_id}")


async def on_cognitive_tool_result(event_data: Any):
    """Event listener for cognitive.tool.result events."""
    task_id = event_data.get("task_id", "unknown")
    tool_name = event_data.get("tool_name", "unknown")
    success = event_data.get("success", False)
    
    if success:
        logger.info(f"Tool {tool_name} executed successfully for task {task_id}")
    else:
        logger.error(f"Tool {tool_name} failed for task {task_id}: {event_data.get('error')}")


async def demonstrate_direct_tool_execution():
    """Demonstrate direct tool execution."""
    logger.info("\n=== DIRECT TOOL EXECUTION DEMO ===")
    
    # Create a temporary file for demonstration
    import tempfile
    with tempfile.NamedTemporaryFile(delete=False, mode='w') as temp:
        temp.write("Hello, Project-S Tool System!")
        temp_path = temp.name
    
    try:
        # Execute the read_file tool
        logger.info(f"Reading file: {temp_path}")
        result = await tool_manager.execute_tool("read_file", file_path=temp_path)
        
        if result.success:
            logger.info(f"File content: {result.result['content']}")
        else:
            logger.error(f"Error: {result.error}")
            
        # Execute the web_search tool
        logger.info("Performing web search for 'Project-S agent'")
        result = await tool_manager.execute_tool("web_search", query="Project-S agent")
        
        if result.success:
            logger.info(f"Found {len(result.result['results'])} results")
        else:
            logger.error(f"Error: {result.error}")
            
        # Execute the execute_python tool
        logger.info("Executing Python code")
        code = """
import platform
import os
result = {
    "system": platform.system(),
    "platform": platform.platform(),
    "current_dir": os.getcwd()
}
print(f"Running on {platform.system()}")
"""
        result = await tool_manager.execute_tool("execute_python", code=code)
        
        if result.success:
            logger.info(f"Code execution stdout: {result.result['stdout']}")
            logger.info(f"Code execution result: {result.result['locals'].get('result')}")
        else:
            logger.error(f"Error: {result.error}")
    
    finally:
        # Clean up the temporary file
        if os.path.exists(temp_path):
            os.unlink(temp_path)


async def demonstrate_langgraph_tool_integration():
    """Demonstrate integration with LangGraph workflows."""
    logger.info("\n=== LANGGRAPH INTEGRATION DEMO ===")
    
    # Create a temporary directory for demonstration
    import tempfile
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create some test files
        for i in range(3):
            with open(os.path.join(temp_dir, f"test_file_{i}.txt"), 'w') as f:
                f.write(f"This is test file {i}")
        
        # Create a file operations workflow
        logger.info("Creating file operations workflow")
        graph = create_file_operations_graph()
        graph_instance = graph.compile()
        
        # Execute the workflow
        logger.info(f"Executing file operations workflow with directory: {temp_dir}")
        initial_state = {
            "parameters": {
                "directory_path": temp_dir
            },
            "messages": [],
            "next_step": "list_directory"
        }
        
        result = await graph_instance.ainvoke(initial_state)
        
        # Log results
        if "tools" in result and "list_directory" in result["tools"]:
            files = result["tools"]["list_directory"]["result"]["files"]
            logger.info(f"Workflow listed {len(files)} files in directory")
        
        # Create a web search workflow
        logger.info("\nCreating web search workflow")
        web_graph = create_web_search_graph()
        web_graph_instance = web_graph.compile()
        
        # Execute the workflow
        logger.info("Executing web search workflow")
        web_state = {
            "parameters": {
                "query": "Project-S tool management"
            },
            "messages": [],
            "next_step": "web_search"
        }
        
        web_result = await web_graph_instance.ainvoke(web_state)
        
        # Log results
        if "tools" in web_result and "web_search" in web_result["tools"]:
            search_results = web_result["tools"]["web_search"]["result"]["results"]
            logger.info(f"Web search workflow found {len(search_results)} results")


async def demonstrate_cognitive_core_integration():
    """Demonstrate integration with the cognitive core."""
    logger.info("\n=== COGNITIVE CORE INTEGRATION DEMO ===")
    
    # Simulate a task creation
    task_id = "file_analysis_task"
    task = {
        "id": task_id,
        "type": "file_operation",
        "description": "Analyze files in the system directory"
    }
    
    # Publish task created event
    logger.info(f"Creating task: {task_id}")
    await event_bus.publish("cognitive.task.created", {"task": task})
    
    # Wait a moment for event handlers to process
    await asyncio.sleep(0.1)
    
    # Get suggested tools for a specific query
    logger.info("\nGetting tool suggestions for query")
    query = "search the web for information about Python programming"
    suggestions = await cognitive_tool_integration.suggest_tools_for_query(query)
    
    logger.info(f"Found {len(suggestions)} tool suggestions for query")
    for suggestion in suggestions:
        logger.info(f"- {suggestion['tool_name']} ({suggestion['category']}): {suggestion['description']}")
    
    # Execute a tool for the task
    logger.info("\nExecuting a tool for task")
    # Create a temporary file for demonstration
    import tempfile
    with tempfile.NamedTemporaryFile(delete=False, mode='w') as temp:
        temp.write("Task execution test file")
        temp_path = temp.name
    
    try:
        result = await cognitive_tool_integration.execute_tool_for_task(
            task_id=task_id,
            tool_name="read_file",
            parameters={"file_path": temp_path}
        )
        
        if result["success"]:
            logger.info(f"Tool execution successful for task {task_id}")
        else:
            logger.error(f"Tool execution failed: {result['error']}")
    
    finally:
        # Clean up temporary file
        if os.path.exists(temp_path):
            os.unlink(temp_path)
    
    # Check the cognitive core context after tool executions
    context = cognitive_core.get_context()
    if "tools" in context:
        logger.info("\nTools in cognitive core context:")
        for tool_name, tool_data in context.get("tools", {}).items():
            logger.info(f"- {tool_name}: {tool_data.get('total_calls', 0)} calls, " 
                        f"{tool_data.get('success_rate', 0):.2f} success rate")


async def main():
    """Main demo function."""
    logger.info("Starting Tool Management System Demo")
    
    # Register event listeners
    event_bus.subscribe("tool.executed", on_tool_executed)
    event_bus.subscribe("cognitive.tool.suggestions", on_cognitive_tool_suggestions)
    event_bus.subscribe("cognitive.tool.result", on_cognitive_tool_result)
    
    # Ensure example tools are registered
    tool_info = register_all_example_tools()
    logger.info(f"Registered example tools: {tool_info}")
    
    # Demonstrate direct tool execution
    await demonstrate_direct_tool_execution()
    
    # Demonstrate LangGraph integration
    await demonstrate_langgraph_tool_integration()
    
    # Demonstrate cognitive core integration
    await demonstrate_cognitive_core_integration()
    
    logger.info("\n=== Demo Completed ===")


if __name__ == "__main__":
    asyncio.run(main())
