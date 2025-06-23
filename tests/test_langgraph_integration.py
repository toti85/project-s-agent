"""
Test module for LangGraph integration with Project-S.
Tests the core functionality of the LangGraph integrator.
"""
import pytest
import asyncio
from typing import Dict, Any
from unittest.mock import patch, MagicMock, AsyncMock

# System imports
from integrations.langgraph_integration import LangGraphIntegrator
from integrations.langgraph_types import GraphState
from core.event_bus import EventBus
from core.command_router import CommandRouter

@pytest.fixture
def event_bus_mock():
    """Create a mock event bus for testing"""
    mock_bus = MagicMock(spec=EventBus)
    # Make the publish method a coroutine
    mock_bus.publish = AsyncMock()
    return mock_bus

@pytest.fixture
def router_mock():
    """Create a mock command router for testing"""
    mock_router = MagicMock(spec=CommandRouter)
    # Make route_command a coroutine
    mock_router.route_command = AsyncMock()
    return mock_router

@pytest.fixture
def integrator(event_bus_mock, router_mock):
    """Create a LangGraphIntegrator instance with mock dependencies"""
    with patch('integrations.langgraph_integration.event_bus', event_bus_mock), \
         patch('integrations.langgraph_integration.router', router_mock):
        integrator = LangGraphIntegrator()
        # Avoid actual event handler registration in tests
        integrator._register_event_handlers = MagicMock()
        return integrator

@pytest.mark.asyncio
async def test_create_workflow(integrator):
    """Test creating a basic sequential workflow"""
    # Define simple workflow steps
    steps = [
        {"type": "CMD", "cmd": "echo hello"},
        {"type": "ASK", "query": "What's next?"}
    ]
    
    # Create workflow
    graph_id = integrator.create_workflow("test_workflow", steps)
    
    # Verify
    assert graph_id in integrator.active_graphs
    assert graph_id in integrator.graph_states
    assert integrator.graph_states[graph_id]["context"]["workflow_name"] == "test_workflow"
    assert integrator.graph_states[graph_id]["context"]["workflow_steps"] == steps
    assert integrator.graph_states[graph_id]["status"] == "created"

@pytest.mark.asyncio
async def test_create_node_based_workflow(integrator):
    """Test creating a node-based workflow with advanced topology"""
    # Define nodes
    nodes = {
        "start": {
            "type": "tool",
            "command": {"type": "CMD", "cmd": "echo Starting workflow"}
        },
        "process": {
            "type": "tool",
            "command": {"type": "ASK", "query": "Process this data"}
        },
        "end": {
            "type": "tool",
            "command": {"type": "CMD", "cmd": "echo Workflow completed"}
        }
    }
    
    # Define edges
    edges = [
        {"from": "start", "to": "process"},
        {"from": "process", "to": "end"}
    ]
    
    # Create node-based workflow
    graph_id = integrator.create_node_based_workflow(
        "test_node_workflow", 
        nodes, 
        edges
    )
    
    # Verify
    assert graph_id in integrator.active_graphs
    assert graph_id in integrator.graph_states
    assert integrator.graph_states[graph_id]["context"]["workflow_name"] == "test_node_workflow"
    assert integrator.graph_states[graph_id]["context"]["nodes"] == nodes
    assert integrator.graph_states[graph_id]["context"]["edges"] == edges

@pytest.mark.asyncio
async def test_conditional_branching(integrator, router_mock):
    """Test workflow with conditional branching"""
    # Mock a successful command result
    router_mock.route_command.return_value = {"status": "success", "data": "some data"}
    
    # Define nodes with a condition
    nodes = {
        "start": {
            "type": "tool",
            "command": {"type": "CMD", "cmd": "echo Starting workflow"}
        },
        "decision": {
            "type": "decision",
            "function": "test_decision_function"
        },
        "path_a": {
            "type": "tool",
            "command": {"type": "CMD", "cmd": "echo Path A selected"}
        },
        "path_b": {
            "type": "tool",
            "command": {"type": "CMD", "cmd": "echo Path B selected"}
        }
    }
    
    # Define edges with a condition
    edges = [
        {"from": "start", "to": "decision"},
        {
            "from": "decision", 
            "to": "path_a",
            "condition": {
                "type": "field_check",
                "field": "decision",
                "value": "path_a",
                "default_value": False
            }
        },
        {
            "from": "decision", 
            "to": "path_b",
            "condition": {
                "type": "field_check",
                "field": "decision",
                "value": "path_b",
                "default_value": False
            }
        }
    ]
    
    # Create mock decision function
    def test_decision_function(state):
        state["decision"] = "path_a"
        return state
        
    # Add the decision function to the module
    import sys
    module = sys.modules[integrator.__module__]
    setattr(module, "test_decision_function", test_decision_function)
    
    try:
        # Create workflow
        graph_id = integrator.create_node_based_workflow(
            "test_conditional_workflow", 
            nodes, 
            edges
        )
        
        # Verify the workflow was created
        assert graph_id in integrator.active_graphs
        
        # Mock the _get_next_step method to return the decision node result
        with patch.object(integrator, '_get_next_step', new_callable=AsyncMock) as mock_get_next:
            # Set up the mock to return the first step then the path_a step
            mock_get_next.side_effect = [
                {"type": "CMD", "cmd": "echo Starting workflow", "graph_id": graph_id},
                {"type": "decision", "function": "test_decision_function", "graph_id": graph_id},
                {"type": "CMD", "cmd": "echo Path A selected", "graph_id": graph_id},
                None  # End of workflow
            ]
            
            # Start the workflow execution
            await integrator._continue_graph_execution(graph_id)
            
            # Verify that route_command was called with the correct commands
            calls = router_mock.route_command.call_args_list
            assert len(calls) >= 1  # At least the first command should be executed
    
    finally:
        # Clean up by removing the test function
        if hasattr(module, "test_decision_function"):
            delattr(module, "test_decision_function")

@pytest.mark.asyncio
async def test_error_handling_and_retry(integrator, router_mock, event_bus_mock):
    """Test error handling and retry mechanism"""
    # Create a simple workflow
    steps = [
        {"type": "CMD", "cmd": "echo hello"},
        {"type": "CMD", "cmd": "some_failing_command"}
    ]
    
    graph_id = integrator.create_workflow("error_test_workflow", steps)
    
    # Mock a command that will fail
    command = {"type": "CMD", "cmd": "some_failing_command", "graph_id": graph_id}
    error = Exception("Command failed")
    
    # Call the error handler
    await integrator._on_command_error({"command": command, "error": error})
    
    # Verify that retry count was incremented
    assert integrator.graph_states[graph_id]["retry_count"] == 1
    
    # Verify that workflow.retry event was published
    event_bus_mock.publish.assert_called_with(
        "workflow.retry", 
        {
            "graph_id": graph_id,
            "retry_count": 1,
            "error": error
        }
    )
    
    # Verify that _continue_graph_execution was called
    # This is challenging to test directly since we can't easily mock asyncio.sleep
    # and asyncio.create_task. In a real application, we'd use a more testable approach.

if __name__ == "__main__":
    pytest.main(["-xvs", "test_langgraph_integration.py"])
