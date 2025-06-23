"""
LangGraph Mock Objects for Project-S Testing
-----------------------------------------
This module provides specialized mock objects for testing LangGraph integrations.
"""
import os
import sys
import json
import asyncio
from typing import Dict, Any, List, Optional, Union, Callable
from unittest.mock import AsyncMock, MagicMock, patch
from pathlib import Path

# Import test configuration
sys.path.insert(0, str(Path(__file__).parent.resolve()))
from test_config import TEST_CONFIG, test_logger
from mock_objects import MockLLMResponse, MockLLMClient

# Mock LangGraph StateGraph
class MockStateGraph:
    """Mock for LangGraph StateGraph"""
    
    def __init__(self):
        """Initialize the mock state graph"""
        self.nodes = {}
        self.edges = {}
        self.entry_point = None
        self._entry_point = None
    
    def add_node(self, node_id: str, node_fn: Callable) -> None:
        """Add a node to the graph"""
        self.nodes[node_id] = node_fn
    
    def add_edge(self, start_node: str, end_node: str, condition: Optional[Callable] = None) -> None:
        """Add an edge to the graph"""
        if start_node not in self.edges:
            self.edges[start_node] = []
        self.edges[start_node].append((end_node, condition))
    
    def set_entry_point(self, node_id: str) -> None:
        """Set the entry point for the graph"""
        self.entry_point = node_id
        self._entry_point = node_id
    
    async def invoke(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate invoking the graph with a state"""
        if not self.entry_point:
            raise ValueError("No entry point set for the graph")
        
        current_node = self.entry_point
        current_state = state.copy()
        
        # Simple execution - go through nodes following edges
        visited = set()
        while current_node and current_node not in visited:
            visited.add(current_node)
            
            # Execute the node function
            if current_node in self.nodes:
                node_fn = self.nodes[current_node]
                current_state = await node_fn(current_state)
            
            # Find the next node
            next_node = None
            if current_node in self.edges:
                for end_node, condition in self.edges[current_node]:
                    if condition is None or condition(current_state):
                        next_node = end_node
                        break
            
            current_node = next_node
        
        return current_state

# Mock LangGraph ToolNode
class MockToolNode:
    """Mock for LangGraph ToolNode"""
    
    def __init__(self, tool_func: Callable, name: str = None):
        """Initialize the mock tool node"""
        self.tool_func = tool_func
        self.name = name or "mock_tool"
    
    async def __call__(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the tool node with a state"""
        # Simple implementation - execute the tool function with the state
        tool_result = await self.tool_func(state)
        if isinstance(tool_result, dict):
            return tool_result
        return state

# Mock LangGraph Agent
class MockLangGraphAgent:
    """Mock for a LangGraph-based agent"""
    
    def __init__(self, name: str = "mock_agent", tools: List[str] = None, system_prompt: str = ""):
        """Initialize the mock agent"""
        self.name = name
        self.tools = tools or []
        self.system_prompt = system_prompt
        self.model = MockLLMClient()
        self.mock_response = None
        self.state_history = []
        
    def set_mock_response(self, response: str):
        """Set a mock response to be returned"""
        self.mock_response = response
        
    async def invoke(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Invoke the agent with a state"""
        if self.mock_response:
            state["response"] = self.mock_response
            return state
        
        # Default behavior if no mock response set
        messages = state.get("messages", [])
        if messages:
            last_message = messages[-1]["content"]
            response = await self.model.generate(last_message)
            state["response"] = response
            
        return state
        self.state_history = []
        self.graph = MockStateGraph()
    
    async def handle_message(self, message: str, state: Dict[str, Any] = None) -> Dict[str, Any]:
        """Handle a message with the agent"""
        if state is None:
            state = {}
        
        state["input"] = message
        state["messages"] = state.get("messages", []) + [{"role": "user", "content": message}]
        
        # Process with the model
        response = await self.model.generate(message)
        
        # Update state
        state["messages"].append({"role": "assistant", "content": response})
        state["output"] = response
        
        # Save state history
        self.state_history.append(state.copy())
        
        return state
    
    async def invoke_workflow(self, workflow_name: str, initial_state: Dict[str, Any]) -> Dict[str, Any]:
        """Invoke a workflow with an initial state"""
        # Create a simple mock workflow
        if workflow_name == "file_operations":
            return await self._file_operations_workflow(initial_state)
        elif workflow_name == "tech_analysis":
            return await self._tech_analysis_workflow(initial_state)
        else:
            test_logger.warning(f"Unknown workflow: {workflow_name}")
            return {"error": f"Unknown workflow: {workflow_name}"}
    
    async def _file_operations_workflow(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Mock file operations workflow"""
        if "file_path" not in state:
            return {"error": "No file path specified"}
        
        # Simulate reading, processing, and writing a file
        state["file_content"] = f"Mock content for {state['file_path']}"
        state["processed_content"] = f"Processed: {state['file_content']}"
        state["output_file"] = state["file_path"] + ".output"
        
        return state
    
    async def _tech_analysis_workflow(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Mock technology analysis workflow"""
        if "technology" not in state:
            return {"error": "No technology specified"}
        
        # Simulate technology analysis
        state["analysis"] = {
            "overview": f"Analysis of {state['technology']}",
            "pros": ["Scalable", "Fast", "Reliable"],
            "cons": ["Complex", "Expensive"],
            "use_cases": ["Enterprise applications", "High-performance computing"]
        }
        
        return state

# Mock LangGraph State Manager
class MockStateManager:
    """Mock for LangGraph state manager"""
    
    def __init__(self):
        """Initialize the mock state manager"""
        self.states = {}
    
    async def save_state(self, workflow_id: str, state: Dict[str, Any]) -> str:
        """Save a workflow state"""
        state_id = f"{workflow_id}_{len(self.states)}"
        self.states[state_id] = state.copy()
        return state_id
    
    async def load_state(self, state_id: str) -> Dict[str, Any]:
        """Load a workflow state"""
        if state_id not in self.states:
            raise ValueError(f"State not found: {state_id}")
        return self.states[state_id].copy()
    
    async def update_state(self, state_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Update a workflow state"""
        if state_id not in self.states:
            raise ValueError(f"State not found: {state_id}")
        
        self.states[state_id].update(updates)
        return self.states[state_id].copy()
    
    async def delete_state(self, state_id: str) -> bool:
        """Delete a workflow state"""
        if state_id in self.states:
            del self.states[state_id]
            return True
        return False

# Function to set up a mock LangGraph environment
def setup_mock_langgraph_environment():
    """Set up a mock LangGraph environment for testing"""
    mock_model = MockLLMClient()
    mock_agent = MockLangGraphAgent(mock_model)
    mock_state_manager = MockStateManager()
    
    return {
        "model": mock_model,
        "agent": mock_agent,
        "state_manager": mock_state_manager,
        "graph": MockStateGraph(),
        "tool_node": MockToolNode([])
    }
