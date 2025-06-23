"""
Unit Tests for LangGraph Integration Components
-------------------------------------------
This module tests the LangGraph integration components in isolation.
"""
import os
import sys
import pytest
import asyncio
import json
from typing import Dict, Any
from pathlib import Path
from unittest import mock

# Import test configuration
sys.path.insert(0, str(Path(__file__).parent.resolve()))
from test_config import TEST_CONFIG, test_logger, TEST_DATA_DIR, TEST_OUTPUT_DIR
from langgraph_mock_objects import (
    MockStateGraph,
    MockToolNode,
    MockLangGraphAgent,
    MockStateManager,
    setup_mock_langgraph_environment
)
from mock_objects import MockLLMClient, MockWebAccess

# Import Project-S components
from integrations.langgraph_integration import LangGraphIntegrator
from integrations.system_operations_manager import system_operations_manager


@pytest.mark.asyncio
class TestLangGraphCore:
    """Test LangGraph core components"""
    
    def setup_method(self):
        """Set up the test environment"""
        # Create mocks
        self.mock_env = setup_mock_langgraph_environment()
        
    @pytest.fixture
    async def simple_graph(self):
        """Create a simple graph for testing"""
        graph = MockStateGraph()
        
        # Define node functions
        async def node1(state):
            return {**state, "node1_executed": True}
        
        async def node2(state):
            return {**state, "node2_executed": True}
        
        async def node3(state):
            return {**state, "node3_executed": True}
        
        # Add nodes
        graph.add_node("node1", node1)
        graph.add_node("node2", node2)
        graph.add_node("node3", node3)
        
        # Add edges
        graph.add_edge("node1", "node2")
        graph.add_edge("node2", "node3")
        
        # Set entry point
        graph.set_entry_point("node1")
        
        return graph
    
    async def test_state_graph_execution(self, simple_graph):
        """Test execution of a simple state graph"""
        # Setup initial state
        initial_state = {"test_value": 123}
        
        # Execute graph
        result = await simple_graph.invoke(initial_state)
        
        # Verify results
        assert "test_value" in result
        assert result["test_value"] == 123
        assert "node1_executed" in result
        assert result["node1_executed"] == True
        assert "node2_executed" in result
        assert result["node2_executed"] == True
        assert "node3_executed" in result
        assert result["node3_executed"] == True
    
    async def test_tool_node_execution(self):
        """Test execution of a tool node"""
        # Define tools
        async def tool1(state):
            return {**state, "tool1_executed": True}
        
        async def tool2(state):
            return {**state, "tool2_result": 42}
        
        # Create tool node
        tool_node = MockToolNode([tool1, tool2])
        
        # Execute tool node
        initial_state = {"input": "test"}
        result = await tool_node(initial_state)
        
        # Verify results
        assert "input" in result
        assert result["input"] == "test"
        assert "tool1_executed" in result
        assert result["tool1_executed"] == True
        assert "tool2_result" in result
        assert result["tool2_result"] == 42
    
    async def test_agent_message_handling(self):
        """Test agent message handling"""
        agent = self.mock_env["agent"]
        
        # Handle a message
        result = await agent.handle_message("Hello, agent!")
        
        # Verify results
        assert "messages" in result
        assert len(result["messages"]) == 2
        assert result["messages"][0]["role"] == "user"
        assert result["messages"][0]["content"] == "Hello, agent!"
        assert result["messages"][1]["role"] == "assistant"
        assert "output" in result
    
    async def test_workflow_invocation(self):
        """Test workflow invocation"""
        agent = self.mock_env["agent"]
        
        # Invoke file operations workflow
        file_ops_result = await agent.invoke_workflow("file_operations", {
            "file_path": os.path.join(TEST_DATA_DIR, "test_file.txt")
        })
        
        # Verify results
        assert "file_content" in file_ops_result
        assert "processed_content" in file_ops_result
        assert "output_file" in file_ops_result
        
        # Invoke tech analysis workflow
        tech_analysis_result = await agent.invoke_workflow("tech_analysis", {
            "technology": "LangGraph"
        })
        
        # Verify results
        assert "analysis" in tech_analysis_result
        assert "overview" in tech_analysis_result["analysis"]
        assert "pros" in tech_analysis_result["analysis"]
        assert "cons" in tech_analysis_result["analysis"]
        assert "use_cases" in tech_analysis_result["analysis"]
    
    async def test_state_management(self):
        """Test state management"""
        state_manager = self.mock_env["state_manager"]
        
        # Save a state
        state_id = await state_manager.save_state("test_workflow", {
            "key1": "value1",
            "key2": 42
        })
        
        # Load the state
        loaded_state = await state_manager.load_state(state_id)
        
        # Verify loaded state
        assert "key1" in loaded_state
        assert loaded_state["key1"] == "value1"
        assert "key2" in loaded_state
        assert loaded_state["key2"] == 42
        
        # Update the state
        updated_state = await state_manager.update_state(state_id, {
            "key1": "new_value",
            "key3": "value3"
        })
        
        # Verify updated state
        assert updated_state["key1"] == "new_value"
        assert updated_state["key2"] == 42
        assert updated_state["key3"] == "value3"
        
        # Delete the state
        delete_result = await state_manager.delete_state(state_id)
        
        # Verify deletion
        assert delete_result == True
        
        # Try to load the deleted state
        with pytest.raises(ValueError):
            await state_manager.load_state(state_id)


@pytest.mark.asyncio
class TestLangGraphIntegration:
    """Test LangGraph integration with Project-S components"""
    
    @mock.patch("integrations.langgraph_integration.StateGraph")
    @mock.patch("integrations.langgraph_integration.ToolNode")
    async def test_langgraph_integrator_initialization(self, mock_tool_node, mock_state_graph):
        """Test initialization of LangGraph integrator"""
        # Setup mocks
        mock_state_graph.return_value = MockStateGraph()
        mock_tool_node.return_value = MockToolNode([])
        
        # Initialize integrator
        integrator = LangGraphIntegrator()
        
        # Verify integrator
        assert hasattr(integrator, "create_workflow")
        assert hasattr(integrator, "execute_workflow")
        assert hasattr(integrator, "register_tool")
    
    @mock.patch("integrations.system_operations_manager.StateGraph")
    async def test_system_operations_workflow_creation(self, mock_state_graph):
        """Test creation of system operations workflow"""
        # Setup mock
        mock_state_graph.return_value = MockStateGraph()
        
        # Create workflow
        workflow = system_operations_manager.create_file_operations_workflow("test_workflow")
        
        # Verify workflow
        assert workflow is not None


if __name__ == "__main__":
    pytest.main(["-xvs", __file__])
