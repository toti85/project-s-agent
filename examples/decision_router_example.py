"""
Decision Router Example
----------------------
This example demonstrates how to use the decision router with LangGraph
to create complex, dynamic workflows with decision-making logic.
"""
import asyncio
import logging
from typing import Dict, Any, List, Optional, Union
import os
import json
import time

from langgraph.graph import StateGraph

from core.event_bus import event_bus
from core.error_handler import error_handler
from integrations.langgraph_integration import GraphState, langgraph_integrator
from integrations.decision_router import decision_router

# Set up logging with formatting for better readability
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("decision_router_example")

# Define event handlers for tracking workflow execution
async def on_workflow_started(event_data):
    """Handle workflow.started events."""
    logger.info(f"Workflow started: {event_data.get('workflow_name')} (ID: {event_data.get('graph_id')})")
    logger.info(f"Initial context: {json.dumps(event_data.get('context', {}), indent=2)}")

async def on_workflow_node_entered(event_data):
    """Handle workflow.node.entered events."""
    logger.info(f"Node entered: {event_data.get('node_name')} in {event_data.get('graph_id')}")

async def on_workflow_decision_made(event_data):
    """Handle workflow.decision.made events."""
    logger.info(f"Decision made in {event_data.get('graph_id')}:")
    logger.info(f"  From: {event_data.get('source_node')}")
    logger.info(f"  Selected: {event_data.get('decision')}")
    logger.info(f"  Based on: {event_data.get('criterion_value')}")
    logger.info(f"  Options: {event_data.get('options')}")

async def on_workflow_completed(event_data):
    """Handle workflow.completed events."""
    logger.info(f"Workflow completed: {event_data.get('graph_id')}")
    logger.info(f"Final context: {json.dumps(event_data.get('final_context', {}), indent=2)}")
    
    # Analyze decision patterns
    graph_id = event_data.get('graph_id')
    if graph_id:
        analysis = decision_router.analyze_decision_patterns(graph_id)
        logger.info(f"Decision pattern analysis:\n{json.dumps(analysis, indent=2)}")

# Node functions for the example workflow

async def start_process(state: GraphState) -> GraphState:
    """Starting node for the workflow."""
    logger.info("Starting process...")
    
    # Add some initial data to the context
    state["context"]["process_started_at"] = time.time()
    state["context"]["input_type"] = state["context"].get("input_type", "text")
    
    # Publish an event through the event bus
    await event_bus.publish("process.started", {
        "graph_id": state["context"].get("graph_id"),
        "input_type": state["context"].get("input_type")
    })
    
    return state

async def process_text(state: GraphState) -> GraphState:
    """Process text content."""
    logger.info("Processing text content...")
    
    # Simulate text processing
    text = state["context"].get("input_data", "Default text")
    word_count = len(text.split())
    
    # Update context with results
    state["context"]["processed_data"] = {
        "type": "text",
        "word_count": word_count,
        "processed_text": text.upper()  # Simple transformation
    }
    
    state["context"]["last_result"] = {
        "success": True,
        "process": "text_processing"
    }
    
    return state

async def process_code(state: GraphState) -> GraphState:
    """Process code content."""
    logger.info("Processing code content...")
    
    # Simulate code processing
    code = state["context"].get("input_data", "print('Hello')")
    line_count = len(code.splitlines())
    
    # Update context with results
    state["context"]["processed_data"] = {
        "type": "code",
        "line_count": line_count,
        "language": "python" if "print" in code else "unknown"
    }
    
    state["context"]["last_result"] = {
        "success": True,
        "process": "code_processing"
    }
    
    return state

async def process_image(state: GraphState) -> GraphState:
    """Process image content."""
    logger.info("Processing image content...")
    
    # Simulate image processing
    image_data = state["context"].get("input_data", "image_placeholder")
    
    # Update context with results
    state["context"]["processed_data"] = {
        "type": "image",
        "size": len(image_data),
        "format": "jpeg"
    }
    
    state["context"]["last_result"] = {
        "success": True,
        "process": "image_processing"
    }
    
    return state

async def quality_check(state: GraphState) -> GraphState:
    """Perform quality check on processed data."""
    logger.info("Performing quality check...")
    
    # Get processed data
    processed_data = state["context"].get("processed_data", {})
    data_type = processed_data.get("type", "unknown")
    
    # Simulate quality check
    if data_type == "text":
        # Text quality check
        word_count = processed_data.get("word_count", 0)
        quality_score = min(100, word_count * 5)  # Simple quality metric
    elif data_type == "code":
        # Code quality check
        line_count = processed_data.get("line_count", 0)
        quality_score = min(100, line_count * 10)  # Simple quality metric
    elif data_type == "image":
        # Image quality check
        quality_score = 85  # Fixed score for this example
    else:
        quality_score = 0
    
    # Update context with quality check results
    state["context"]["quality_check"] = {
        "score": quality_score,
        "passed": quality_score >= 50,
        "timestamp": time.time()
    }
    
    # Set flag for quality decision
    state["context"]["quality_passed"] = quality_score >= 50
    
    return state

async def enhance_content(state: GraphState) -> GraphState:
    """Enhance content that didn't pass quality check."""
    logger.info("Enhancing content...")
    
    # Get processed data
    processed_data = state["context"].get("processed_data", {})
    data_type = processed_data.get("type", "unknown")
    
    # Simulate enhancement
    if data_type == "text":
        # Enhance text
        processed_text = processed_data.get("processed_text", "")
        enhanced_text = processed_text + " [ENHANCED]"
        state["context"]["processed_data"]["processed_text"] = enhanced_text
        state["context"]["processed_data"]["enhanced"] = True
    elif data_type == "code":
        # Enhance code
        state["context"]["processed_data"]["enhanced"] = True
        state["context"]["processed_data"]["comments_added"] = 5
    elif data_type == "image":
        # Enhance image
        state["context"]["processed_data"]["enhanced"] = True
        state["context"]["processed_data"]["filters_applied"] = ["sharpen", "contrast"]
    
    # Update quality score
    state["context"]["quality_check"]["score"] += 30
    state["context"]["quality_check"]["passed"] = True
    state["context"]["quality_passed"] = True
    
    return state

async def finalize_result(state: GraphState) -> GraphState:
    """Finalize the processing result."""
    logger.info("Finalizing result...")
    
    # Calculate processing time
    start_time = state["context"].get("process_started_at", 0)
    processing_time = time.time() - start_time
    
    # Create final result
    final_result = {
        "input_type": state["context"].get("input_type"),
        "processed_data": state["context"].get("processed_data"),
        "quality_check": state["context"].get("quality_check"),
        "processing_time_seconds": processing_time,
        "workflow_id": state["context"].get("graph_id")
    }
    
    # Add to state
    state["context"]["final_result"] = final_result
    
    # Publish result via event bus
    await event_bus.publish("process.completed", {
        "graph_id": state["context"].get("graph_id"),
        "result": final_result
    })
    
    return state

# Decision routing functions

def input_type_router(state: GraphState) -> str:
    """Route based on input type."""
    input_type = state["context"].get("input_type", "").lower()
    
    if input_type == "code":
        return "code"
    elif input_type == "image":
        return "image"
    else:
        return "text"

def quality_check_router(state: GraphState) -> str:
    """Route based on quality check results."""
    quality_passed = state["context"].get("quality_passed", False)
    return "passed" if quality_passed else "failed"

async def create_decision_workflow():
    """Create a workflow with decision routing."""
    # Create a new workflow graph
    graph = StateGraph(GraphState)
    
    # Add the process nodes
    graph.add_node("start", start_process)
    graph.add_node("process_text", process_text)
    graph.add_node("process_code", process_code)
    graph.add_node("process_image", process_image)
    graph.add_node("quality_check", quality_check)
    graph.add_node("enhance_content", enhance_content)
    graph.add_node("finalize", finalize_result)
    
    # Add decision nodes using the decision router
    decision_router.add_decision_node(
        graph=graph,
        node_name="content_type_decision",
        criteria_func=input_type_router,
        destinations={
            "text": "process_text",
            "code": "process_code",
            "image": "process_image"
        },
        default="process_text"
    )
    
    decision_router.add_decision_node(
        graph=graph,
        node_name="quality_decision",
        criteria_func=quality_check_router,
        destinations={
            "passed": "finalize",
            "failed": "enhance_content"
        },
        default="enhance_content"
    )
    
    # Add regular edges
    graph.add_edge("start", "content_type_decision")
    graph.add_edge("process_text", "quality_check")
    graph.add_edge("process_code", "quality_check")
    graph.add_edge("process_image", "quality_check")
    graph.add_edge("quality_check", "quality_decision")
    graph.add_edge("enhance_content", "finalize")
    
    # Set the entry point
    graph.set_entry_point("start")
    
    # Compile the graph
    compiled_graph = graph.compile()
    
    return compiled_graph

async def run_decision_workflow(input_type: str, input_data: Any) -> Dict[str, Any]:
    """
    Run the decision workflow with the given input.
    
    Args:
        input_type: The type of input ("text", "code", or "image")
        input_data: The input data to process
        
    Returns:
        The final workflow state
    """
    # Subscribe to events
    event_bus.subscribe("workflow.started", on_workflow_started)
    event_bus.subscribe("workflow.node.entered", on_workflow_node_entered)
    event_bus.subscribe("workflow.decision.made", on_workflow_decision_made)
    event_bus.subscribe("workflow.completed", on_workflow_completed)
    
    # Create the workflow
    workflow = await create_decision_workflow()
    
    # Create initial state
    initial_state = {
        "messages": [],
        "context": {
            "input_type": input_type,
            "input_data": input_data,
            "graph_id": f"decision_workflow_{int(time.time())}",
            "workflow_name": "Decision Routing Example"
        },
        "command_history": [],
        "status": "created",
        "current_task": None,
        "error_info": None,
        "retry_count": 0,
        "branch": None
    }
    
    logger.info(f"Starting workflow with input_type={input_type}")
    
    # Run the workflow
    try:
        # Publish event for workflow start
        await event_bus.publish("workflow.started", {
            "graph_id": initial_state["context"]["graph_id"],
            "workflow_name": initial_state["context"]["workflow_name"],
            "context": initial_state["context"]
        })
        
        result = await workflow.ainvoke(initial_state)
        
        # Publish event for workflow completion
        await event_bus.publish("workflow.completed", {
            "graph_id": initial_state["context"]["graph_id"],
            "workflow_name": initial_state["context"]["workflow_name"],
            "completion_status": "completed",
            "final_context": result.get("context", {})
        })
        
        return result
    except Exception as e:
        logger.error(f"Error running workflow: {e}")
        
        # Publish event for workflow error
        await event_bus.publish("workflow.completed", {
            "graph_id": initial_state["context"]["graph_id"],
            "workflow_name": initial_state["context"]["workflow_name"],
            "completion_status": "error",
            "error": str(e)
        })
        
        # Handle the error
        error_context = {
            "component": "decision_workflow",
            "workflow_id": initial_state["context"]["graph_id"],
            "input_type": input_type
        }
        await error_handler.handle_error(e, error_context)
        
        return {
            "error": str(e),
            "context": initial_state["context"]
        }

async def main():
    """Run examples of the decision workflow."""
    logger.info("Starting Decision Router Example")
    
    # Example 1: Text processing
    logger.info("\n=== Example 1: Text Processing ===")
    text_result = await run_decision_workflow(
        input_type="text",
        input_data="This is a sample text document that will be processed through our workflow."
    )
    
    # Example 2: Code processing
    logger.info("\n=== Example 2: Code Processing ===")
    code_result = await run_decision_workflow(
        input_type="code",
        input_data="def hello():\n    print('Hello, world!')\n\nif __name__ == '__main__':\n    hello()"
    )
    
    # Example 3: Image processing (simulated)
    logger.info("\n=== Example 3: Image Processing ===")
    image_result = await run_decision_workflow(
        input_type="image",
        input_data="[binary image data placeholder - 2048 bytes]"
    )
    
    # Example 4: Low quality content that needs enhancement
    logger.info("\n=== Example 4: Content Needing Enhancement ===")
    low_quality_result = await run_decision_workflow(
        input_type="text",
        input_data="Short"  # This should trigger quality enhancement
    )
    
    logger.info("\n=== Decision Router Examples Completed ===")

if __name__ == "__main__":
    asyncio.run(main())
