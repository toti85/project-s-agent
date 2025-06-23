"""
Example code demonstrating LangGraph integration with Project-S
--------------------------------------------------------------
This example shows how to create and execute workflows using the LangGraph integrator.
"""
import asyncio
import logging
from core.event_bus import event_bus
from core.command_router import router
from integrations.langgraph_integration import langgraph_integrator

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("LangGraph_Example")

# Define event handlers for workflow events
async def on_workflow_started(event_data):
    logger.info(f"Workflow started: {event_data.get('workflow_name')} (ID: {event_data.get('graph_id')})")

async def on_workflow_completed(event_data):
    logger.info(f"Workflow completed: {event_data.get('graph_id')}")
    graph_state = event_data.get('state', {})
    logger.info(f"Final state: {graph_state.get('status')}")
    logger.info(f"Completed tasks: {len(graph_state.get('command_history', []))}")

async def on_workflow_error(event_data):
    logger.error(f"Workflow error: {event_data.get('graph_id')}")
    logger.error(f"Error: {event_data.get('error')}")

async def main():
    # Register event handlers
    event_bus.subscribe("workflow.started", on_workflow_started)
    event_bus.subscribe("workflow.completed", on_workflow_completed)
    event_bus.subscribe("workflow.error", on_workflow_error)
    
    # Register LangGraph with the command router
    await langgraph_integrator.register_as_command_handler()
    
    # Create a simple workflow to process files in a directory
    workflow_steps = [
        # Step 1: List files in the current directory
        {
            "type": "CMD",
            "cmd": "dir" if os.name == 'nt' else "ls -la"  # Windows or Unix command
        },
        # Step 2: Create a Python script to analyze those files
        {
            "type": "CODE",
            "content": "Write a Python script that counts lines in all text files in the current directory",
            "options": {"language": "python"}
        },
        # Step 3: Execute the script
        {
            "type": "CMD",
            "cmd": "python analyze_files.py"
        },
        # Step 4: Ask for a summary of the results
        {
            "type": "ASK",
            "query": "Summarize the results of the file analysis"
        }
    ]
    
    # Create the workflow through the command router
    result = await router.route_command({
        "type": "WORKFLOW",
        "operation": "create",
        "name": "file_analysis",
        "steps": workflow_steps,
        "context": {
            "purpose": "Analyze text files in current directory"
        },
        "start": True  # Start the workflow immediately
    })
    
    graph_id = result.get("graph_id")
    logger.info(f"Created workflow with ID: {graph_id}")
    
    # Wait for workflow to complete (in a real application, you wouldn't block like this)
    waiting = 0
    while waiting < 60:  # Wait up to 60 seconds
        state = langgraph_integrator.get_workflow_state(graph_id)
        if state and state["status"] in ["completed", "error", "cancelled"]:
            logger.info(f"Workflow finished with status: {state['status']}")
            break
        
        await asyncio.sleep(1)
        waiting += 1
    
    # Check final workflow status
    final_result = await router.route_command({
        "type": "WORKFLOW",
        "operation": "status",
        "graph_id": graph_id
    })
    
    logger.info(f"Final workflow status: {final_result}")

if __name__ == "__main__":
    import os
    asyncio.run(main())
