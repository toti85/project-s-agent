"""
More complex example showing advanced LangGraph integration with Project-S
------------------------------------------------------------------------
This example demonstrates a more complex workflow with conditional branching
and error handling using LangGraph's state management features.
"""
import asyncio
import logging
import os
from typing import Dict, Any, List
from core.event_bus import event_bus
from core.command_router import router
from integrations.langgraph_integration import langgraph_integrator
from langgraph.graph import StateGraph
from langgraph.prebuilt import ToolNode

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("LangGraph_Advanced_Example")

# Event handlers for workflow events
async def on_workflow_step_complete(event_data):
    logger.info(f"Step completed: {event_data.get('step_name')} - Result: {event_data.get('result')}")

async def on_workflow_decision(event_data):
    logger.info(f"Workflow decision: {event_data.get('decision')}")

# Custom function to create a more advanced workflow with conditional paths
def create_advanced_workflow(project_dir: str, task_description: str) -> Dict[str, Any]:
    # Define the steps with conditional logic
    analyze_step = {
        "type": "CODE",
        "content": f"Analyze the codebase in {project_dir} and identify areas for improvement",
        "options": {"language": "python"}
    }
    
    test_step = {
        "type": "CMD",
        "cmd": f"cd {project_dir} && python -m pytest -xvs"
    }
    
    refactor_step = {
        "type": "CODE",
        "content": f"Refactor the code based on your analysis to improve {task_description}",
        "options": {"language": "python"}
    }
    
    documentation_step = {
        "type": "CODE",
        "content": f"Generate documentation for the codebase explaining the improvements made for {task_description}",
        "options": {"language": "markdown"}
    }
    
    # Create condition-based steps
    workflow_command = {
        "type": "WORKFLOW",
        "operation": "create",
        "name": f"advanced_{task_description.replace(' ', '_')}",
        "steps": [analyze_step],  # Start with analysis step
        "context": {
            "purpose": task_description,
            "project_dir": project_dir,
            "conditional_steps": {
                "needs_tests": test_step,
                "needs_refactoring": refactor_step,
                "needs_documentation": documentation_step
            },
            "decision_function": "decide_next_steps"
        }
    }
    
    return workflow_command

# Define decision function that will be used by the workflow
async def decide_next_steps(state):
    """Decision function that determines next steps based on analysis results"""
    analysis_result = state["context"].get("last_result", {})
    
    # Extract information from analysis (in a real app, this would parse the actual result)
    needs_tests = "test" in str(analysis_result).lower()
    needs_refactoring = "refactor" in str(analysis_result).lower()
    needs_documentation = "documentation" in str(analysis_result).lower()
    
    # Create the next steps based on analysis
    next_steps = []
    
    if needs_tests:
        next_steps.append(state["context"]["conditional_steps"]["needs_tests"])
    
    if needs_refactoring:
        next_steps.append(state["context"]["conditional_steps"]["needs_refactoring"])
    
    if needs_documentation:
        next_steps.append(state["context"]["conditional_steps"]["needs_documentation"])
    
    # Publish decision event
    await event_bus.publish("workflow.decision", {
        "decision": f"Selected {len(next_steps)} next steps based on analysis",
        "steps": ["tests" if needs_tests else None,
                 "refactoring" if needs_refactoring else None,
                 "documentation" if needs_documentation else None]
    })
    
    # Update the workflow steps
    state["context"]["workflow_steps"] = next_steps
    
    return state

async def main():
    # Register event handlers
    event_bus.subscribe("workflow.step.completed", on_workflow_step_complete)
    event_bus.subscribe("workflow.decision", on_workflow_decision)
    
    # Register the LangGraph integrator with the command router
    await langgraph_integrator.register_as_command_handler()
    
    # Define a directory to analyze
    project_dir = "."  # Current directory
    task_description = "code quality and readability"
    
    # Create the advanced workflow
    workflow_command = create_advanced_workflow(project_dir, task_description)
    
    # Execute the workflow
    result = await router.route_command(workflow_command)
    
    graph_id = result.get("graph_id")
    logger.info(f"Created advanced workflow with ID: {graph_id}")
    
    # Start the workflow
    await router.route_command({
        "type": "WORKFLOW",
        "operation": "start",
        "graph_id": graph_id
    })
    
    # In a real application, you wouldn't block like this
    logger.info("Workflow started, waiting for completion...")
    
    # Wait for workflow to complete
    waiting = 0
    while waiting < 60:  # Wait up to 60 seconds
        state = langgraph_integrator.get_workflow_state(graph_id)
        if state and state["status"] in ["completed", "error", "cancelled"]:
            logger.info(f"Workflow finished with status: {state['status']}")
            break
        
        await asyncio.sleep(1)
        waiting += 1
    
    # Print the final workflow status
    final_status = await router.route_command({
        "type": "WORKFLOW",
        "operation": "status",
        "graph_id": graph_id
    })
    
    logger.info(f"Final advanced workflow status: {final_status}")

if __name__ == "__main__":
    asyncio.run(main())
