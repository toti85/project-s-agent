"""
Branching Workflow Example with LangGraph and Project-S
------------------------------------------------------
This example demonstrates how to create a workflow with branching paths
using the enhanced LangGraph integration with Project-S.
"""
import asyncio
import logging
import os
import json
from typing import Dict, Any, List, Optional
from core.event_bus import event_bus
from core.command_router import router
from integrations.langgraph_integration import langgraph_integrator

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Branching_LangGraph_Example")

# Define event handlers
async def on_workflow_started(event_data):
    logger.info(f"Workflow started: {event_data.get('workflow_name')} (ID: {event_data.get('graph_id')})")

async def on_workflow_completed(event_data):
    logger.info(f"Workflow completed: {event_data.get('graph_id')}")
    completion_status = event_data.get('completion_status', 'completed')
    logger.info(f"Final status: {completion_status}")

async def on_workflow_decision(event_data):
    logger.info(f"Workflow decision made: {event_data}")
    logger.info(f"Selected branch: {event_data.get('branch')}")

async def on_workflow_error(event_data):
    logger.error(f"Workflow error: {event_data.get('graph_id')}")
    logger.error(f"Error: {event_data.get('error')}")

# Decision function that will be used to determine which branch to follow
async def analyze_and_decide(state):
    """
    Analyze the current state and decide which branch to follow next.
    This is a demonstration of how to create dynamic workflows that can
    change their execution path based on intermediate results.
    
    Args:
        state: The current workflow state
    
    Returns:
        The updated state with branch selection
    """
    # Get the last result from context
    last_result = state["context"].get("last_result", {})
    result_content = json.dumps(last_result).lower()
    
    # Simulate decision logic based on the content of the result
    if "error" in result_content or "fail" in result_content:
        logger.info("Decision: Taking error recovery branch")
        state["branch"] = "error_recovery"
    elif "api" in result_content or "service" in result_content:
        logger.info("Decision: Taking API integration branch")
        state["branch"] = "api_integration"
    else:
        logger.info("Decision: Taking standard processing branch")
        state["branch"] = "standard_processing"
    
    # Publish event about the decision
    await event_bus.publish("workflow.decision", {
        "decision": f"Selected branch: {state['branch']}",
        "branch": state["branch"],
        "graph_id": state["context"].get("graph_id")
    })
    
    return state

async def main():
    # Register event handlers
    event_bus.subscribe("workflow.started", on_workflow_started)
    event_bus.subscribe("workflow.completed", on_workflow_completed) 
    event_bus.subscribe("workflow.decision", on_workflow_decision)
    event_bus.subscribe("workflow.error", on_workflow_error)
    
    # Register LangGraph with the command router
    await langgraph_integrator.register_as_command_handler()
    
    # Define initial analysis step
    initial_step = {
        "type": "ASK",
        "query": "Analyze this codebase and suggest integration approaches for external APIs"
    }
    
    # Define branches for different execution paths
    branches = {
        # Branch for standard processing
        "standard_processing": [
            {
                "type": "CODE",
                "content": "Generate a basic adapter class for integration",
                "options": {"language": "python"}
            },
            {
                "type": "ASK",
                "query": "Explain how this adapter fits into the system architecture"
            }
        ],
        
        # Branch for API integration
        "api_integration": [
            {
                "type": "CODE", 
                "content": "Create an API client with authentication and error handling",
                "options": {"language": "python"}
            },
            {
                "type": "ASK",
                "query": "What security considerations should we address with this API integration?"
            },
            {
                "type": "CODE",
                "content": "Add secure credential handling to the API client",
                "options": {"language": "python"}
            }
        ],
        
        # Branch for error recovery
        "error_recovery": [
            {
                "type": "ASK",
                "query": "Analyze the issues in the codebase that might affect integration"
            },
            {
                "type": "CODE",
                "content": "Create error handling and logging improvements",
                "options": {"language": "python"}
            }
        ]
    }
    
    # Create advanced workflow with branching
    result = await router.route_command({
        "type": "WORKFLOW",
        "operation": "create",
        "name": "branching_api_integration",
        "steps": [initial_step],  # Start with just the initial analysis step
        "branches": branches,      # Define the different branch paths
        "context": {
            "purpose": "API integration with branching workflows",
            "decision_function": "analyze_and_decide"  # Name of the decision function
        }
    })
    
    graph_id = result.get("graph_id")
    logger.info(f"Created branching workflow with ID: {graph_id}")
    
    # Start the workflow
    await router.route_command({
        "type": "WORKFLOW",
        "operation": "start",
        "graph_id": graph_id
    })
    
    # In a real application, you wouldn't block like this
    logger.info("Branching workflow started, waiting for completion...")
    
    # Wait for workflow to complete
    waiting = 0
    max_wait_time = 120  # 2 minutes max wait
    while waiting < max_wait_time:
        state = langgraph_integrator.get_workflow_state(graph_id)
        if state and state["status"] in ["completed", "error", "cancelled"]:
            logger.info(f"Workflow finished with status: {state['status']}")
            
            # Show which branch was taken
            branch = state.get("branch", "none")
            logger.info(f"Final branch selected: {branch}")
            
            # Show how many steps were completed
            steps_completed = len(state["command_history"])
            logger.info(f"Completed {steps_completed} steps in workflow")
            break
        
        await asyncio.sleep(1)
        waiting += 1
        
        if waiting % 10 == 0:  # Every 10 seconds show status
            logger.info(f"Still waiting for workflow, elapsed time: {waiting}s")
    
    # Print final workflow status
    if waiting >= max_wait_time:
        logger.warning(f"Workflow did not complete within {max_wait_time} seconds")
    
    final_status = await router.route_command({
        "type": "WORKFLOW",
        "operation": "status",
        "graph_id": graph_id
    })
    
    logger.info(f"Final workflow status: {final_status}")

if __name__ == "__main__":
    asyncio.run(main())
