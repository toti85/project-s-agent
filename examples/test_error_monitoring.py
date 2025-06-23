"""
Test script for LangGraph error monitoring capabilities.
This script creates workflows that will error in different ways
to demonstrate the error monitoring and recovery features.
"""
import asyncio
import logging
import os
import sys
from typing import Dict, Any

# Add the parent directory to the path so we can import the Project-S modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.event_bus import event_bus
from core.command_router import router
from integrations.langgraph_integration import langgraph_integrator
from integrations.langgraph_error_monitor import error_monitor

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("LangGraph_Error_Test")

# Event handlers
async def on_workflow_error(event_data):
    """Handler for workflow error events"""
    logger.error(f"Workflow error: {event_data.get('error')}")

async def on_workflow_retry(event_data):
    """Handler for workflow retry events"""
    logger.info(f"Workflow retry: Graph {event_data.get('graph_id')}, Attempt {event_data.get('retry_count')}")

async def on_error_analysis(event_data):
    """Handler for error analysis events"""
    logger.info(f"Error analysis: {event_data}")

async def create_error_workflows():
    """Create various workflows that will error in different ways"""
    # Register event handlers
    event_bus.subscribe("workflow.error", on_workflow_error)
    event_bus.subscribe("workflow.retry", on_workflow_retry)
    event_bus.subscribe("workflow.error.analysis", on_error_analysis)
    
    # Wait for a bit to ensure system is ready
    await asyncio.sleep(1)
    
    # 1. Command not found error
    logger.info("Creating workflow with invalid command")
    invalid_command_workflow = {
        "type": "WORKFLOW",
        "operation": "create",
        "name": "invalid_command_test",
        "steps": [
            {
                "type": "CMD",
                "cmd": "echo Starting workflow"
            },
            {
                "type": "CMD",
                "cmd": "non_existent_command"  # This command doesn't exist
            }
        ]
    }
    result1 = await router.route_command(invalid_command_workflow)
    graph_id1 = result1.get("graph_id")
    
    # Start the workflow
    await router.route_command({
        "type": "WORKFLOW",
        "operation": "start",
        "graph_id": graph_id1
    })
    
    # 2. Node not found error (invalid node reference)
    logger.info("Creating workflow with invalid node reference")
    invalid_node_workflow = {
        "type": "WORKFLOW",
        "operation": "create",
        "name": "invalid_node_test",
        "nodes": {
            "start": {
                "type": "tool",
                "command": {"type": "CMD", "cmd": "echo Starting workflow"}
            },
            "process": {
                "type": "tool",
                "command": {"type": "CMD", "cmd": "echo Processing"}
            }
        },
        "edges": [
            {"from": "start", "to": "process"},
            {"from": "process", "to": "end"}  # 'end' node doesn't exist
        ]
    }
    result2 = await router.route_command(invalid_node_workflow)
    graph_id2 = result2.get("graph_id")
    
    # Start the workflow
    await router.route_command({
        "type": "WORKFLOW",
        "operation": "start",
        "graph_id": graph_id2
    })
    
    # 3. State access error (missing required field)
    logger.info("Creating workflow that will have a state access error")
    
    async def access_missing_field(state):
        """This function will try to access a field that doesn't exist"""
        # Try to access a field that doesn't exist
        missing_value = state["nonexistent_field"]["some_subfield"]
        return state
    
    # Add the function to the module namespace
    import sys
    module = sys.modules[__name__]
    setattr(module, "access_missing_field", access_missing_field)
    
    state_error_workflow = {
        "type": "WORKFLOW",
        "operation": "create",
        "name": "state_access_test",
        "nodes": {
            "start": {
                "type": "tool",
                "command": {"type": "CMD", "cmd": "echo Starting workflow"}
            },
            "access_error": {
                "type": "function",
                "function": "access_missing_field"
            }
        },
        "edges": [
            {"from": "start", "to": "access_error"}
        ]
    }
    result3 = await router.route_command(state_error_workflow)
    graph_id3 = result3.get("graph_id")
    
    # Start the workflow
    await router.route_command({
        "type": "WORKFLOW",
        "operation": "start",
        "graph_id": graph_id3
    })
    
    # Wait for workflows to process
    await asyncio.sleep(5)
    
    # Get error reports
    logger.info("Generating error reports...")
    
    # Get report for each workflow
    report1 = error_monitor.get_error_report(graph_id1)
    report2 = error_monitor.get_error_report(graph_id2)
    report3 = error_monitor.get_error_report(graph_id3)
    
    # Get overall error report
    overall_report = error_monitor.get_error_report()
    
    # Log the reports
    logger.info(f"Report for workflow 1 (Invalid Command): {report1['total_errors']} errors")
    logger.info(f"Report for workflow 2 (Invalid Node): {report2['total_errors']} errors")
    logger.info(f"Report for workflow 3 (State Access): {report3['total_errors']} errors")
    logger.info(f"Overall error trends: {overall_report['error_trends']}")
    logger.info(f"Most common error: {overall_report['most_common_error']}")
    
    # Export error data to file
    log_dir = os.path.join(os.getcwd(), "logs")
    os.makedirs(log_dir, exist_ok=True)
    export_path = os.path.join(log_dir, "error_report.json")
    
    success = error_monitor.export_error_data(export_path)
    if success:
        logger.info(f"Error data exported to {export_path}")
    
    # Test error report command
    report_cmd_result = await router.route_command({
        "type": "ERROR_REPORT",
        "operation": "summary"
    })
    
    logger.info(f"Error report command result: {report_cmd_result['status']}")
    logger.info(f"Total errors: {report_cmd_result['report']['total_errors']}")
    
    return "Error monitoring test complete"

if __name__ == "__main__":
    # Initialize LangGraph components
    from integrations.langgraph_init import setup_langgraph
    setup_langgraph()
    
    # Run the error test
    result = asyncio.run(create_error_workflows())
    print(result)
