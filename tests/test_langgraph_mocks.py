"""
Test LangGraph Mock Objects
--------------------------
This module tests the mock objects for LangGraph without dependencies on the real LangGraph.
"""
import pytest
import asyncio
from typing import Dict, Any
import sys
from pathlib import Path

# Import mock objects
sys.path.insert(0, str(Path(__file__).parent.resolve()))
from langgraph_mock_objects import MockStateGraph, MockToolNode, MockLangGraphAgent

@pytest.mark.asyncio
class TestLangGraphMocks:
    """Test LangGraph mock objects"""
    
    async def test_mock_state_graph(self):
        """Test MockStateGraph functionality"""
        # Create a simple graph
        graph = MockStateGraph()
        
        # Define node functions
        async def node1(state):
            return {**state, "node1_executed": True}
        
        async def node2(state):
            return {**state, "node2_executed": True}
            
        # Add nodes to graph
        graph.add_node("node1", node1)
        graph.add_node("node2", node2)
        
        # Add edges
        graph.add_edge("node1", "node2")
        
        # Set entry point
        graph.set_entry_point("node1")
        
        # Invoke graph
        initial_state = {"input": "test"}
        final_state = await graph.invoke(initial_state)
        
        # Check results
        assert final_state["node1_executed"] == True
        assert final_state["node2_executed"] == True
        assert final_state["input"] == "test"
        
    async def test_mock_tool_node(self):
        """Test MockToolNode functionality"""
        # Create a tool node
        async def tool_function(state):
            return {**state, "result": "success"}
            
        tool_node = MockToolNode(tool_function, "test_tool")
        
        # Invoke tool node
        initial_state = {"input": "test"}
        result = await tool_node(initial_state)
        
        # Check results
        assert result["result"] == "success"
        assert result["input"] == "test"
        
    async def test_mock_langgraph_agent(self):
        """Test MockLangGraphAgent functionality"""
        # Create an agent
        agent = MockLangGraphAgent(
            name="test_agent",
            tools=["tool1", "tool2"],
            system_prompt="Test prompt"
        )
        
        # Set mock response
        agent.set_mock_response("This is a test response")
        
        # Invoke agent
        initial_state = {"messages": [{"content": "Hello", "role": "user"}]}
        result = await agent.invoke(initial_state)
        
        # Check results
        assert "response" in result
        assert result["response"] == "This is a test response"

if __name__ == "__main__":
    pytest.main(["-xvs", __file__])
