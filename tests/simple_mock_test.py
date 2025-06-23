import sys
from pathlib import Path

# Import mock objects directly
sys.path.insert(0, str(Path(__file__).parent.resolve()))
from langgraph_mock_objects import MockStateGraph

# Create a simple test
async def test_mock_graph():
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
    
    # Print results
    print(f"State after execution: {final_state}")
    
    # Check results
    assert final_state["node1_executed"] == True
    assert final_state["node2_executed"] == True
    assert final_state["input"] == "test"
    print("All tests passed!")

# Run the test
if __name__ == "__main__":
    import asyncio
    asyncio.run(test_mock_graph())
