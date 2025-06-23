"""
Example for using the enhanced cognitive core with LangGraph integration
----------------------------------------------------------------------
This example demonstrates how to process complex tasks with the enhanced
cognitive core that uses LangGraph for workflow management.
"""
import asyncio
import logging
import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.cognitive_core import cognitive_core
from core.event_bus import event_bus

# Set up logging
logging.basicConfig(level=logging.INFO, 
                   format='[%(asctime)s] [%(levelname)s] %(name)s - %(message)s')
logger = logging.getLogger("cognitive_core_example")

async def on_task_completed(event_data):
    """Handler for task completion events"""
    logger.info(f"Task completed: {event_data.get('task_id')}")
    logger.info(f"Status: {event_data.get('status')}")
    
    # Print results summary
    if event_data.get("steps"):
        logger.info(f"Steps completed: {len(event_data.get('steps'))}")
        
        for i, step in enumerate(event_data.get("steps")):
            status = step.get("status", "unknown")
            step_type = step.get("step", {}).get("type", "unknown")
            desc = step.get("step", {}).get("description", "No description")
            logger.info(f"  Step {i+1}: [{status}] {step_type} - {desc}")

async def on_task_error(event_data):
    """Handler for task error events"""
    logger.error(f"Task error: {event_data.get('error')}")

async def run_complex_task():
    """Run a complex task with the cognitive core"""
    # Register event handlers
    event_bus.subscribe("task.completed", on_task_completed)
    event_bus.subscribe("task.error", on_task_error)
    
    # Define a complex task that requires planning and multi-step execution
    task = {
        "id": "complex_task_1",
        "description": "Analyze the Python files in the core directory and create a summary of their functionality",
        "type": "code_analysis"
    }
    
    logger.info(f"Submitting complex task: {task['description']}")
    
    # Process the task
    result = await cognitive_core.process_task(task)
    
    logger.info(f"Task processing complete. Overall status: {result.get('status')}")
    
    if result.get("status") == "completed":
        # Get the context to see what we learned
        context = cognitive_core.get_context()
        
        # Show discovered entities
        if "entities" in context and "class" in context["entities"]:
            logger.info(f"Discovered classes: {context['entities']['class']}")
            
        if "entities" in context and "function" in context["entities"]:
            logger.info(f"Discovered functions: {len(context['entities']['function'])} functions")
    
    # Ask for a suggested next action
    next_action = await cognitive_core.suggest_next_action()
    if next_action:
        logger.info(f"Suggested next action: {next_action.get('type')}")
        logger.info(f"Reason: {next_action.get('reason')}")

if __name__ == "__main__":
    asyncio.run(run_complex_task())
