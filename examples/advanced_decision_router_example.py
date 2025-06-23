"""
Advanced Decision Router Example
-------------------------------
This example demonstrates how to use the advanced decision router
to create complex adaptive workflows in the Project-S hybrid system.
"""
import asyncio
import logging
from typing import Dict, Any, List, Optional, Union
import os
import json
import time
import uuid

from langgraph.graph import StateGraph

from core.event_bus import event_bus
from core.error_handler import error_handler
from integrations.langgraph_integration import GraphState, langgraph_integrator
from integrations.decision_router import decision_router
from integrations.advanced_decision_router import (
    advanced_decision_router,
    check_context_contains,
    check_system_supports,
    route_by_model_capabilities,
    route_by_confidence
)

# Set up logging with formatting for better readability
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("advanced_decision_example")

# Register event handlers
async def on_workflow_started(event_data):
    """Handle workflow started events."""
    logger.info(f"Workflow started: {event_data.get('workflow_name')} (ID: {event_data.get('graph_id')})")
    logger.info(f"Initial context: {json.dumps(event_data.get('context', {}), indent=2)}")

async def on_workflow_node_entered(event_data):
    """Handle node entered events."""
    logger.info(f"Node entered: {event_data.get('node_name')} in {event_data.get('graph_id')}")

async def on_workflow_decision_made(event_data):
    """Handle decision made events."""
    logger.info(f"Decision made in {event_data.get('graph_id')}:")
    logger.info(f"  From: {event_data.get('source_node')}")
    logger.info(f"  Selected: {event_data.get('decision')}")
    logger.info(f"  Based on: {event_data.get('criterion_value')}")
    logger.info(f"  Source used: {event_data.get('source_used')}")

async def on_workflow_completed(event_data):
    """Handle workflow completed events."""
    logger.info(f"Workflow completed: {event_data.get('graph_id')}")
    logger.info(f"Final context: {json.dumps(event_data.get('final_context', {}), indent=2)}")
    
    # Analyze decision patterns and detect any issues
    graph_id = event_data.get('graph_id')
    if graph_id:
        analysis = advanced_decision_router.analyze_decision_patterns(graph_id)
        logger.info(f"Decision pattern analysis:\n{json.dumps(analysis, indent=2)}")
        
        # Detect patterns
        patterns = advanced_decision_router.detect_decision_patterns(graph_id)
        if patterns["status"] == "patterns_detected":
            logger.info(f"Decision patterns detected:\n{json.dumps(patterns, indent=2)}")

async def on_workflow_pattern_detected(event_data):
    """Handle pattern detected events."""
    logger.info(f"Decision pattern detected: {event_data.get('pattern_type')}")
    logger.info(f"Pattern data: {json.dumps(event_data.get('pattern_data', {}), indent=2)}")

# Register custom decision criteria functions

def route_by_data_complexity(state: GraphState) -> str:
    """Route based on data complexity."""
    context = state.get("context", {})
    input_data = context.get("input_data", {})
    
    # Assess complexity based on structure and content
    if isinstance(input_data, dict) and len(input_data) > 10:
        return "complex"
    elif isinstance(input_data, list) and len(input_data) > 50:
        return "complex"
    elif isinstance(input_data, str) and len(input_data) > 5000:
        return "complex"
    else:
        return "simple"

def route_by_processing_stage(state: GraphState) -> str:
    """Route based on current processing stage."""
    context = state.get("context", {})
    stage = context.get("processing_stage", "initial")
    return stage

def check_needs_external_data(state: GraphState) -> bool:
    """Check if workflow needs external data."""
    context = state.get("context", {})
    input_data = context.get("input_data", {})
    external_references = context.get("external_references", [])
    
    # Check if there are external references or missing data flags
    if external_references:
        return True
        
    # Look for special markers in input data
    if isinstance(input_data, str) and ("{external_data}" in input_data or "[lookup]" in input_data):
        return True
        
    return False

def route_by_required_tools(state: GraphState) -> str:
    """Route based on required tools for processing."""
    context = state.get("context", {})
    required_tools = context.get("required_tools", [])
    
    if "code_analyzer" in required_tools:
        return "code_tools"
    elif "text_processor" in required_tools:
        return "text_tools"
    elif "data_visualizer" in required_tools:
        return "visualization_tools"
    else:
        return "basic_tools"

# Node functions for the example workflow

async def start_process(state: GraphState) -> GraphState:
    """Initialize the workflow."""
    logger.info("Starting advanced decision workflow...")
    
    # Add initial metadata to context
    state["context"]["process_started_at"] = time.time()
    state["context"]["workflow_instance_id"] = str(uuid.uuid4())
    state["context"]["processing_stage"] = "initial"
    
    # Determine required capabilities based on input
    input_type = state["context"].get("input_type", "text")
    input_data = state["context"].get("input_data", "")
    
    required_capabilities = []
    required_tools = []
    
    # Analyze input to determine required capabilities
    if input_type == "code":
        required_capabilities.extend(["code_generation", "code_analysis"])
        required_tools.extend(["code_analyzer", "syntax_checker"])
    elif input_type == "data":
        required_capabilities.extend(["data_analysis", "visualization"])
        required_tools.extend(["data_visualizer", "statistics_analyzer"])
    else:
        required_capabilities.extend(["text_processing", "summarization"])
        required_tools.extend(["text_processor", "sentiment_analyzer"])
    
    # Add complexity assessment
    if isinstance(input_data, str):
        complexity = len(input_data) // 1000
        state["context"]["complexity_score"] = min(10, complexity)
        
        # Flag for external data if certain keywords are present
        if "[reference]" in input_data or "[citation]" in input_data:
            state["context"]["external_references"] = True
    
    # Update context with determined capabilities and tools
    state["context"]["required_capabilities"] = required_capabilities
    state["context"]["required_tools"] = required_tools
    
    # Publish an event
    await event_bus.publish("process.started", {
        "graph_id": state["context"].get("graph_id"),
        "input_type": state["context"].get("input_type"),
        "required_capabilities": required_capabilities
    })
    
    return state

async def analyze_requirements(state: GraphState) -> GraphState:
    """Analyze input requirements."""
    logger.info("Analyzing processing requirements...")
    
    # Simulate requirements analysis
    input_type = state["context"].get("input_type", "text")
    input_data = state["context"].get("input_data", "")
    
    # Create analysis results
    analysis_result = {
        "input_type": input_type,
        "estimated_processing_time": len(str(input_data)) // 100,
        "confidence": 0.8 if len(str(input_data)) > 1000 else 0.95,
        "recommendations": []
    }
    
    # Add specific recommendations based on input type
    if input_type == "code":
        analysis_result["recommendations"].append({
            "tool": "code_analyzer",
            "reason": "Code quality assessment needed"
        })
    elif input_type == "data":
        analysis_result["recommendations"].append({
            "tool": "data_visualizer",
            "reason": "Data visualization recommended"
        })
    
    # Update processing stage
    state["context"]["processing_stage"] = "requirements_analyzed"
    state["context"]["analysis_result"] = analysis_result
    
    # Add analysis result to last_result for routing decisions
    state["context"]["last_result"] = analysis_result
    
    return state

async def process_simple_data(state: GraphState) -> GraphState:
    """Process simple data inputs."""
    logger.info("Processing simple data input...")
    
    input_data = state["context"].get("input_data", "")
    input_type = state["context"].get("input_type", "text")
    
    # Simulate processing
    processing_result = {
        "type": input_type,
        "processed": True,
        "summary": f"Processed {input_type} data (simple approach)",
        "confidence": 0.9
    }
    
    # Add type-specific processing results
    if input_type == "text":
        processing_result["word_count"] = len(input_data.split())
        processing_result["processed_text"] = input_data.upper()[:100] + "..."
    elif input_type == "code":
        processing_result["line_count"] = len(input_data.splitlines())
        processing_result["language"] = "python" if "def " in input_data else "other"
    elif input_type == "data":
        processing_result["entries"] = len(input_data) if isinstance(input_data, list) else 1
        
    # Update context with processing results
    state["context"]["processing_result"] = processing_result
    state["context"]["last_result"] = processing_result
    state["context"]["processing_stage"] = "data_processed"
    
    return state

async def process_complex_data(state: GraphState) -> GraphState:
    """Process complex data inputs with advanced techniques."""
    logger.info("Processing complex data input with advanced techniques...")
    
    input_data = state["context"].get("input_data", "")
    input_type = state["context"].get("input_type", "text")
    
    # Simulate advanced processing
    processing_result = {
        "type": input_type,
        "processed": True,
        "summary": f"Processed {input_type} data (advanced approach)",
        "processing_level": "complex",
        "confidence": 0.75
    }
    
    # Add type-specific processing details
    if input_type == "text":
        processing_result["word_count"] = len(input_data.split())
        processing_result["processed_text"] = f"ADVANCED PROCESSING: {input_data[:50]}..."
        processing_result["sentiment"] = "positive" if "good" in input_data.lower() else "neutral"
    elif input_type == "code":
        processing_result["line_count"] = len(input_data.splitlines())
        processing_result["complexity_analysis"] = {
            "cyclomatic_complexity": 12,
            "maintainability_index": 75
        }
    elif input_type == "data":
        processing_result["entries"] = len(input_data) if isinstance(input_data, list) else 1
        processing_result["statistical_summary"] = {
            "mean": 42.5,
            "median": 38.0,
            "std_dev": 12.3
        }
        
    # Update context with processing results
    state["context"]["processing_result"] = processing_result
    state["context"]["last_result"] = processing_result
    state["context"]["processing_stage"] = "data_processed"
    
    return state

async def fetch_external_data(state: GraphState) -> GraphState:
    """Fetch external data needed for processing."""
    logger.info("Fetching external data...")
    
    # Simulate fetching external data
    external_data = {
        "source": "external_api",
        "timestamp": time.time(),
        "data": {
            "supplementary_info": "This is additional data fetched from an external source",
            "metadata": {
                "source_reliability": 0.95,
                "last_updated": "2023-04-15"
            }
        }
    }
    
    # Update context with external data
    state["context"]["external_data"] = external_data
    state["context"]["processing_stage"] = "external_data_fetched"
    
    return state

async def apply_code_tools(state: GraphState) -> GraphState:
    """Apply code-specific tools to the input."""
    logger.info("Applying code tools...")
    
    input_data = state["context"].get("input_data", "")
    
    # Simulate code tools processing
    tools_result = {
        "tool": "code_analyzer",
        "issues_found": 3,
        "recommendations": [
            "Add proper error handling",
            "Improve function documentation",
            "Consider breaking down complex functions"
        ],
        "code_quality_score": 72
    }
    
    # Update context with tools results
    state["context"]["tools_result"] = tools_result
    state["context"]["last_result"] = tools_result
    state["context"]["processing_stage"] = "tools_applied"
    
    return state

async def apply_text_tools(state: GraphState) -> GraphState:
    """Apply text-specific tools to the input."""
    logger.info("Applying text tools...")
    
    input_data = state["context"].get("input_data", "")
    
    # Simulate text tools processing
    tools_result = {
        "tool": "text_processor",
        "sentiment": "positive" if "good" in input_data.lower() else "neutral",
        "key_phrases": ["example", "decision", "router"],
        "readability_score": 85
    }
    
    # Update context with tools results
    state["context"]["tools_result"] = tools_result
    state["context"]["last_result"] = tools_result
    state["context"]["processing_stage"] = "tools_applied"
    
    return state

async def apply_visualization_tools(state: GraphState) -> GraphState:
    """Apply visualization tools to the data."""
    logger.info("Applying visualization tools...")
    
    # Simulate visualization processing
    tools_result = {
        "tool": "data_visualizer",
        "visualizations_generated": 2,
        "chart_types": ["bar_chart", "line_graph"],
        "visual_insights": ["Upward trend detected", "Outliers present in Q3"]
    }
    
    # Update context with tools results
    state["context"]["tools_result"] = tools_result
    state["context"]["last_result"] = tools_result
    state["context"]["processing_stage"] = "tools_applied"
    
    return state

async def apply_basic_tools(state: GraphState) -> GraphState:
    """Apply basic tools when no specific tools are required."""
    logger.info("Applying basic tools...")
    
    # Simulate basic tools processing
    tools_result = {
        "tool": "basic_processor",
        "processing_applied": "standard",
        "execution_time": 1.2
    }
    
    # Update context with tools results
    state["context"]["tools_result"] = tools_result
    state["context"]["last_result"] = tools_result
    state["context"]["processing_stage"] = "tools_applied"
    
    return state

async def quality_check(state: GraphState) -> GraphState:
    """Perform quality check on processed data."""
    logger.info("Performing quality check...")
    
    # Get processing result
    processing_result = state["context"].get("processing_result", {})
    tools_result = state["context"].get("tools_result", {})
    
    # Calculate confidence scores
    processing_confidence = processing_result.get("confidence", 0.5)
    
    # Determine overall quality score based on available data
    quality_factors = {}
    
    if "code_quality_score" in tools_result:
        quality_factors["code_quality"] = tools_result["code_quality_score"] / 100
        
    if "readability_score" in tools_result:
        quality_factors["readability"] = tools_result["readability_score"] / 100
        
    # Default quality is based on processing confidence
    if quality_factors:
        quality_score = sum(quality_factors.values()) / len(quality_factors) * 100
    else:
        quality_score = processing_confidence * 100
    
    # Create quality check result
    quality_check_result = {
        "score": quality_score,
        "passed": quality_score >= 70,
        "factors": quality_factors,
        "timestamp": time.time()
    }
    
    # Update context with quality check results
    state["context"]["quality_check"] = quality_check_result
    state["context"]["quality_passed"] = quality_check_result["passed"]
    state["context"]["processing_stage"] = "quality_checked"
    
    return state

async def enhance_output(state: GraphState) -> GraphState:
    """Enhance output that didn't pass quality check."""
    logger.info("Enhancing output quality...")
    
    # Get processing result and quality check
    processing_result = state["context"].get("processing_result", {})
    quality_check = state["context"].get("quality_check", {})
    input_type = state["context"].get("input_type", "text")
    
    # Enhance based on input type
    if input_type == "text":
        # Enhance text output
        if "processed_text" in processing_result:
            enhanced_text = processing_result["processed_text"] + " [ENHANCED]"
            processing_result["processed_text"] = enhanced_text
            processing_result["enhancements_applied"] = ["formatting", "clarity"]
            
    elif input_type == "code":
        # Enhance code output
        processing_result["enhancements_applied"] = ["documentation", "error_handling"]
        processing_result["comments_added"] = 5
        
    elif input_type == "data":
        # Enhance data output
        processing_result["enhancements_applied"] = ["normalization", "cleaning"]
    
    # Update quality score
    if "score" in quality_check:
        quality_check["score"] += 15
        quality_check["passed"] = quality_check["score"] >= 70
        state["context"]["quality_passed"] = quality_check["passed"]
    
    # Update context
    state["context"]["processing_result"] = processing_result
    state["context"]["quality_check"] = quality_check
    state["context"]["enhanced"] = True
    state["context"]["processing_stage"] = "output_enhanced"
    
    return state

async def finalize_high_confidence(state: GraphState) -> GraphState:
    """Finalize workflow with high confidence output."""
    logger.info("Finalizing workflow with high confidence...")
    
    # Calculate processing time
    start_time = state["context"].get("process_started_at", 0)
    processing_time = time.time() - start_time
    
    # Create final result with high confidence emphasis
    final_result = {
        "input_type": state["context"].get("input_type"),
        "processing_result": state["context"].get("processing_result"),
        "quality_check": state["context"].get("quality_check"),
        "tools_applied": state["context"].get("tools_result", {}).get("tool", "none"),
        "confidence_level": "high",
        "processing_time_seconds": processing_time,
        "workflow_id": state["context"].get("graph_id")
    }
    
    # Add to state
    state["context"]["final_result"] = final_result
    state["context"]["processing_stage"] = "completed"
    
    # Publish result via event bus
    await event_bus.publish("process.completed", {
        "graph_id": state["context"].get("graph_id"),
        "confidence_level": "high",
        "result": final_result
    })
    
    return state

async def finalize_medium_confidence(state: GraphState) -> GraphState:
    """Finalize workflow with medium confidence output."""
    logger.info("Finalizing workflow with medium confidence...")
    
    # Calculate processing time
    start_time = state["context"].get("process_started_at", 0)
    processing_time = time.time() - start_time
    
    # Create final result with medium confidence emphasis
    final_result = {
        "input_type": state["context"].get("input_type"),
        "processing_result": state["context"].get("processing_result"),
        "quality_check": state["context"].get("quality_check"),
        "tools_applied": state["context"].get("tools_result", {}).get("tool", "none"),
        "confidence_level": "medium",
        "processing_time_seconds": processing_time,
        "workflow_id": state["context"].get("graph_id"),
        "review_recommended": True
    }
    
    # Add to state
    state["context"]["final_result"] = final_result
    state["context"]["processing_stage"] = "completed"
    
    # Publish result via event bus
    await event_bus.publish("process.completed", {
        "graph_id": state["context"].get("graph_id"),
        "confidence_level": "medium",
        "result": final_result
    })
    
    return state

async def finalize_low_confidence(state: GraphState) -> GraphState:
    """Finalize workflow with low confidence output."""
    logger.info("Finalizing workflow with low confidence...")
    
    # Calculate processing time
    start_time = state["context"].get("process_started_at", 0)
    processing_time = time.time() - start_time
    
    # Create final result with low confidence emphasis
    final_result = {
        "input_type": state["context"].get("input_type"),
        "processing_result": state["context"].get("processing_result"),
        "quality_check": state["context"].get("quality_check"),
        "tools_applied": state["context"].get("tools_result", {}).get("tool", "none"),
        "confidence_level": "low",
        "processing_time_seconds": processing_time,
        "workflow_id": state["context"].get("graph_id"),
        "manual_review_required": True,
        "alternative_approaches": [
            "Try processing with different model",
            "Gather more context information"
        ]
    }
    
    # Add to state
    state["context"]["final_result"] = final_result
    state["context"]["processing_stage"] = "completed"
    
    # Publish result via event bus
    await event_bus.publish("process.completed", {
        "graph_id": state["context"].get("graph_id"),
        "confidence_level": "low",
        "result": final_result
    })
    
    return state

async def create_advanced_decision_workflow():
    """Create a workflow with advanced decision routing."""
    # Create a new workflow graph
    graph = StateGraph(GraphState)
    
    # Add the process nodes
    graph.add_node("start", start_process)
    graph.add_node("analyze_requirements", analyze_requirements)
    graph.add_node("process_simple_data", process_simple_data)
    graph.add_node("process_complex_data", process_complex_data)
    graph.add_node("fetch_external_data", fetch_external_data)
    graph.add_node("apply_code_tools", apply_code_tools)
    graph.add_node("apply_text_tools", apply_text_tools)
    graph.add_node("apply_visualization_tools", apply_visualization_tools)
    graph.add_node("apply_basic_tools", apply_basic_tools)
    graph.add_node("quality_check", quality_check)
    graph.add_node("enhance_output", enhance_output)
    graph.add_node("finalize_high_confidence", finalize_high_confidence)
    graph.add_node("finalize_medium_confidence", finalize_medium_confidence)
    graph.add_node("finalize_low_confidence", finalize_low_confidence)
    
    # Register custom decision criteria
    advanced_decision_router.register_decision_criteria(
        "data_complexity", route_by_data_complexity
    )
    advanced_decision_router.register_decision_criteria(
        "needs_external_data", check_needs_external_data
    )
    advanced_decision_router.register_decision_criteria(
        "required_tools", route_by_required_tools
    )
    advanced_decision_router.register_decision_criteria(
        "confidence_level", route_by_confidence
    )
    
    # Add decision nodes with the advanced decision router
    
    # 1. First decision: Check if we need external data
    advanced_decision_router.add_adaptive_decision_node(
        graph=graph,
        node_name="external_data_decision",
        criteria_sources=[
            {"type": "function", "name": "needs_external_data"}
        ],
        destinations={
            "True": "fetch_external_data",
            "False": "complexity_decision"
        },
        fallback="complexity_decision"
    )
    
    # 2. Second decision: Route based on data complexity
    advanced_decision_router.add_adaptive_decision_node(
        graph=graph,
        node_name="complexity_decision",
        criteria_sources=[
            {"type": "function", "name": "data_complexity"}
        ],
        destinations={
            "complex": "process_complex_data",
            "simple": "process_simple_data"
        },
        fallback="process_simple_data"
    )
    
    # 3. Third decision: Choose tools based on requirements
    advanced_decision_router.add_adaptive_decision_node(
        graph=graph,
        node_name="tools_decision",
        criteria_sources=[
            {"type": "function", "name": "required_tools"},
            {"type": "path", "path": "context.required_tools"}
        ],
        destinations={
            "code_tools": "apply_code_tools",
            "text_tools": "apply_text_tools",
            "visualization_tools": "apply_visualization_tools",
            "basic_tools": "apply_basic_tools"
        },
        fallback="apply_basic_tools"
    )
    
    # 4. Fourth decision: Quality check decision
    advanced_decision_router.add_decision_node(
        graph=graph,
        node_name="quality_decision",
        criteria_func=lambda state: state["context"].get("quality_passed", False),
        destinations={
            "True": "confidence_decision",
            "False": "enhance_output"
        },
        default="enhance_output"
    )
    
    # 5. Fifth decision: Confidence-based finalization
    advanced_decision_router.add_adaptive_decision_node(
        graph=graph,
        node_name="confidence_decision",
        criteria_sources=[
            {"type": "function", "name": "confidence_level"},
            {"type": "cognitive", "question": "Based on the context, what is the confidence level (high, medium, or low)?"}
        ],
        destinations={
            "high_confidence": "finalize_high_confidence",
            "medium_confidence": "finalize_medium_confidence",
            "low_confidence": "finalize_low_confidence"
        },
        fallback="finalize_medium_confidence"
    )
    
    # Add regular edges
    graph.add_edge("start", "analyze_requirements")
    graph.add_edge("analyze_requirements", "external_data_decision")
    graph.add_edge("fetch_external_data", "complexity_decision")
    graph.add_edge("process_simple_data", "tools_decision")
    graph.add_edge("process_complex_data", "tools_decision")
    graph.add_edge("apply_code_tools", "quality_check")
    graph.add_edge("apply_text_tools", "quality_check")
    graph.add_edge("apply_visualization_tools", "quality_check")
    graph.add_edge("apply_basic_tools", "quality_check")
    graph.add_edge("quality_check", "quality_decision")
    graph.add_edge("enhance_output", "confidence_decision")
    
    # Set the entry point
    graph.set_entry_point("start")
    
    # Compile the graph
    compiled_graph = graph.compile()
    
    return compiled_graph

async def run_advanced_decision_workflow(input_type: str, input_data: Any) -> Dict[str, Any]:
    """
    Run the advanced decision workflow with the given input.
    
    Args:
        input_type: The type of input ("text", "code", or "data")
        input_data: The input data to process
        
    Returns:
        The final workflow state
    """
    # Subscribe to events
    event_bus.subscribe("workflow.started", on_workflow_started)
    event_bus.subscribe("workflow.node.entered", on_workflow_node_entered)
    event_bus.subscribe("workflow.decision.made", on_workflow_decision_made)
    event_bus.subscribe("workflow.completed", on_workflow_completed)
    event_bus.subscribe("workflow.pattern.detected", on_workflow_pattern_detected)
    
    # Create the workflow
    workflow = await create_advanced_decision_workflow()
    
    # Create initial state with system context
    initial_state = {
        "messages": [],
        "context": {
            "input_type": input_type,
            "input_data": input_data,
            "graph_id": f"advanced_decision_{int(time.time())}",
            "workflow_name": "Advanced Decision Routing Example",
            "system_state": {
                "capabilities": ["text_processing", "code_generation", "data_analysis"],
                "available_memory": 8589934592,  # 8 GB
                "active_plugins": ["code_analyzer", "text_processor"]
            }
        },
        "command_history": [],
        "status": "created",
        "current_task": None,
        "error_info": None,
        "retry_count": 0,
        "branch": None
    }
    
    logger.info(f"Starting advanced workflow with input_type={input_type}")
    
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
            "component": "advanced_decision_workflow",
            "workflow_id": initial_state["context"]["graph_id"],
            "input_type": input_type
        }
        await error_handler.handle_error(e, error_context)
        
        return {
            "error": str(e),
            "context": initial_state["context"]
        }

async def main():
    """Run examples of the advanced decision workflow."""
    logger.info("Starting Advanced Decision Router Example")
    
    # Example 1: Text processing
    logger.info("\n=== Example 1: Text Processing with Medium Complexity ===")
    text_sample = "This is a medium-length text that will be processed through our workflow. " * 10
    text_result = await run_advanced_decision_workflow(
        input_type="text",
        input_data=text_sample
    )
    
    # Example 2: Code processing with external data needs
    logger.info("\n=== Example 2: Code Processing with External References ===")
    code_sample = """
def process_data(input_data):
    # [reference] We should look up the latest processing algorithm
    results = []
    for item in input_data:
        # Apply transformation
        results.append(item * 2)
    return results
    
if __name__ == "__main__":
    test_data = [1, 2, 3, 4, 5]
    print(process_data(test_data))
"""
    code_result = await run_advanced_decision_workflow(
        input_type="code",
        input_data=code_sample
    )
    
    # Example 3: Complex data processing
    logger.info("\n=== Example 3: Complex Data Processing ===")
    data_sample = [{"id": i, "value": i * 2.5, "metadata": {"timestamp": time.time()}} for i in range(100)]
    data_result = await run_advanced_decision_workflow(
        input_type="data",
        input_data=data_sample
    )
    
    # Example 4: Low quality content that needs enhancement
    logger.info("\n=== Example 4: Content Needing Enhancement ===")
    low_quality_result = await run_advanced_decision_workflow(
        input_type="text",
        input_data="Short text"  # This should trigger quality enhancement
    )
    
    # Analyze global decision trends
    logger.info("\n=== Global Decision Analysis ===")
    global_analysis = advanced_decision_router.analyze_global_decision_trends()
    logger.info(f"Global decision trends:\n{json.dumps(global_analysis, indent=2)}")
    
    logger.info("\n=== Advanced Decision Router Examples Completed ===")

if __name__ == "__main__":
    asyncio.run(main())
