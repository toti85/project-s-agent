"""
State Message Handling Example with LangGraph and Project-S
----------------------------------------------------------
This example demonstrates advanced state message handling features
of the LangGraph integration with Project-S.
"""
import asyncio
import logging
import json
import os
import sys
from typing import Dict, Any, List, Optional, TypedDict

# Add the parent directory to the path so we can import the Project-S modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.event_bus import event_bus
from core.command_router import router
from integrations.langgraph_integration import langgraph_integrator

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("LangGraph_State_Message_Example")

# Define event handlers
async def on_workflow_step_complete(event_data):
    """Handler for workflow.step.completed events"""
    logger.info(f"Step completed: {event_data}")
    if 'state' in event_data:
        # Log the updated state
        logger.info(f"Current message count: {len(event_data['state'].get('messages', []))}")

async def on_state_update(event_data):
    """Handler for workflow.state.updated events"""
    logger.info(f"State updated: Graph ID {event_data.get('graph_id')}")
    if 'updates' in event_data:
        logger.info(f"State updates: {event_data['updates']}")

class ProcessingState(TypedDict):
    """Type definition for our enhanced state with custom fields"""
    document_status: str
    analysis_results: List[Dict[str, Any]]
    entities: List[str]
    summary: str

async def process_document(state):
    """
    Node function that processes a document and extracts entities
    
    Args:
        state: The current graph state
        
    Returns:
        The updated state with entities list
    """
    logger.info("Processing document and extracting entities...")
    
    # Get document from last result or context
    document = state["context"].get("last_result", {}).get("content", "")
    if not document and "document" in state["context"]:
        document = state["context"]["document"]
    
    # Extract entities (in a real app this would use NLP)
    entities = []
    common_entities = ["person", "organization", "location", "date", "money", "percent"]
    
    # Simple simulation of entity extraction
    for entity in common_entities:
        if entity.lower() in document.lower():
            entities.append(entity)
    
    # Store entities in state
    if "processing_state" not in state:
        state["processing_state"] = ProcessingState(
            document_status="processed",
            analysis_results=[],
            entities=[],
            summary=""
        )
    
    state["processing_state"]["entities"] = entities
    
    # Add a message about the entities
    if hasattr(state, "add_message"):
        state.add_message({
            "role": "system",
            "content": f"Extracted entities: {', '.join(entities)}"
        })
    else:
        if "messages" not in state:
            state["messages"] = []
        state["messages"].append({
            "role": "system",
            "content": f"Extracted entities: {', '.join(entities)}"
        })
    
    # Publish event about the state update
    await event_bus.publish("workflow.state.updated", {
        "graph_id": state["context"].get("graph_id"),
        "updates": {
            "entities": entities,
            "document_status": "processed"
        }
    })
    
    return state

async def summarize_document(state):
    """
    Node function that summarizes the document based on entities
    
    Args:
        state: The current graph state
        
    Returns:
        The updated state with summary
    """
    logger.info("Summarizing document based on entities...")
    
    # Get entities from processing state
    if "processing_state" in state:
        entities = state["processing_state"].get("entities", [])
    else:
        entities = []
    
    # Get document from context
    document = state["context"].get("document", "")
    
    # Generate a simple summary (in real app, this would use an LLM)
    summary = f"Document analysis complete. Found {len(entities)} entities: {', '.join(entities)}."
    
    # Store summary in state
    if "processing_state" not in state:
        state["processing_state"] = ProcessingState(
            document_status="summarized",
            analysis_results=[],
            entities=entities,
            summary=""
        )
    
    state["processing_state"]["summary"] = summary
    state["processing_state"]["document_status"] = "summarized"
    
    # Add a message with the summary
    if hasattr(state, "add_message"):
        state.add_message({
            "role": "assistant",
            "content": summary
        })
    else:
        if "messages" not in state:
            state["messages"] = []
        state["messages"].append({
            "role": "assistant",
            "content": summary
        })
    
    # Publish event about the state update
    await event_bus.publish("workflow.state.updated", {
        "graph_id": state["context"].get("graph_id"),
        "updates": {
            "summary": summary,
            "document_status": "summarized"
        }
    })
    
    return state

async def generate_report(state):
    """
    Node function that generates a final report with all information
    
    Args:
        state: The current graph state
        
    Returns:
        The updated state with report
    """
    logger.info("Generating final report...")
    
    # Get all necessary information from state
    if "processing_state" in state:
        entities = state["processing_state"].get("entities", [])
        summary = state["processing_state"].get("summary", "")
    else:
        entities = []
        summary = ""
    
    # Generate report (in real app, this would be more complex)
    report = f"""
    === DOCUMENT ANALYSIS REPORT ===
    
    SUMMARY:
    {summary}
    
    ENTITIES FOUND:
    {', '.join(entities)}
    
    ANALYSIS COMPLETE
    """
    
    # Add report to state
    state["context"]["report"] = report
    
    # Add a message with the report
    if hasattr(state, "add_message"):
        state.add_message({
            "role": "system",
            "content": report
        })
    else:
        if "messages" not in state:
            state["messages"] = []
        state["messages"].append({
            "role": "system",
            "content": report
        })
    
    # Publish event about the state update
    await event_bus.publish("workflow.state.updated", {
        "graph_id": state["context"].get("graph_id"),
        "updates": {
            "report": "generated",
            "document_status": "report_complete"
        }
    })
    
    return state

async def analyze_sentiment(state):
    """
    Node function that performs sentiment analysis on the document
    Only called conditionally if sentiment analysis is requested
    
    Args:
        state: The current graph state
        
    Returns:
        The updated state with sentiment analysis
    """
    logger.info("Performing sentiment analysis...")
    
    # Get document from context
    document = state["context"].get("document", "")
    
    # Simple sentiment analysis (would be more complex in real app)
    positive_words = ["good", "great", "excellent", "positive", "happy", "wonderful"]
    negative_words = ["bad", "poor", "negative", "unhappy", "terrible", "awful"]
    
    positive_count = sum(1 for word in positive_words if word.lower() in document.lower())
    negative_count = sum(1 for word in negative_words if word.lower() in document.lower())
    
    sentiment = "positive" if positive_count > negative_count else "negative" if negative_count > positive_count else "neutral"
    
    # Store sentiment in state
    if "processing_state" not in state:
        state["processing_state"] = ProcessingState(
            document_status="analyzed",
            analysis_results=[],
            entities=[],
            summary=""
        )
    
    state["processing_state"]["analysis_results"].append({
        "type": "sentiment",
        "result": sentiment,
        "positive_score": positive_count,
        "negative_score": negative_count
    })
    
    # Add a message with the sentiment
    if hasattr(state, "add_message"):
        state.add_message({
            "role": "system",
            "content": f"Sentiment analysis: {sentiment.upper()} (Positive: {positive_count}, Negative: {negative_count})"
        })
    else:
        if "messages" not in state:
            state["messages"] = []
        state["messages"].append({
            "role": "system",
            "content": f"Sentiment analysis: {sentiment.upper()} (Positive: {positive_count}, Negative: {negative_count})"
        })
    
    # Publish event about the state update
    await event_bus.publish("workflow.state.updated", {
        "graph_id": state["context"].get("graph_id"),
        "updates": {
            "sentiment": sentiment
        }
    })
    
    return state

def should_analyze_sentiment(state):
    """
    Condition function to check if sentiment analysis should be performed
    
    Args:
        state: The current graph state
        
    Returns:
        str: "yes" if sentiment analysis should be performed, "no" otherwise
    """
    # Check if sentiment analysis is requested in context
    if state["context"].get("perform_sentiment", False):
        return "yes"
    return "no"

async def main():
    """Main function to run the example"""
    # Register event handlers
    event_bus.subscribe("workflow.step.completed", on_workflow_step_complete)
    event_bus.subscribe("workflow.state.updated", on_state_update)
    
    # Register LangGraph with the command router
    await langgraph_integrator.register_as_command_handler()
    
    # Define sample document for processing
    sample_document = """
    Apple Inc. announced on January 10, 2023 that its quarterly revenue reached $90.1 billion.
    CEO Tim Cook expressed great satisfaction with the results during a meeting in Cupertino, California.
    The company plans to open new offices in Seattle, Washington and Austin, Texas next year.
    """
    
    # Create a node-based workflow for document processing
    nodes = {
        "start": {
            "type": "passthrough"  # Just pass through the state
        },
        "process_document": {
            "type": "function", 
            "function": process_document  # Custom function to process document
        },
        "sentiment_analysis": {
            "type": "function",
            "function": analyze_sentiment  # Custom function for sentiment analysis
        },
        "summarize": {
            "type": "function",
            "function": summarize_document  # Custom function to summarize document
        },
        "generate_report": {
            "type": "function",
            "function": generate_report  # Custom function for report generation
        },
        "end": {
            "type": "passthrough"  # Just pass through the state
        }
    }
    
    # Define edges with conditions
    edges = [
        # Start to process document
        {"from": "start", "to": "process_document"},
        
        # Process document to sentiment analysis (conditional)
        {
            "from": "process_document",
            "to": "sentiment_analysis",
            "condition": {
                "type": "function",
                "function": should_analyze_sentiment,
                "value": "yes",
                "default_value": "no"
            }
        },
        
        # Process document to summarize (if not doing sentiment analysis)
        {
            "from": "process_document",
            "to": "summarize",
            "condition": {
                "type": "function",
                "function": should_analyze_sentiment,
                "value": "no",
                "default_value": "yes"
            }
        },
        
        # Sentiment analysis to summarize
        {"from": "sentiment_analysis", "to": "summarize"},
        
        # Summarize to generate report
        {"from": "summarize", "to": "generate_report"},
        
        # Generate report to end
        {"from": "generate_report", "to": "end"}
    ]
    
    # Create workflow command
    workflow_command = {
        "type": "WORKFLOW",
        "operation": "create",
        "name": "document_analysis_workflow",
        "nodes": nodes,
        "edges": edges,
        "context": {
            "document": sample_document,
            "perform_sentiment": True  # Set to True to include sentiment analysis
        }
    }
    
    # Execute the workflow through the command router
    logger.info("Creating and starting document analysis workflow...")
    result = await router.route_command(workflow_command)
    
    graph_id = result["graph_id"]
    logger.info(f"Created workflow with ID: {graph_id}")
    
    # Start the workflow
    await router.route_command({
        "type": "WORKFLOW",
        "operation": "start",
        "graph_id": graph_id
    })
    
    # Wait for workflow to complete (in a real application, you wouldn't block like this)
    waiting = 0
    while waiting < 30:  # Wait up to 30 seconds
        state = langgraph_integrator.get_workflow_state(graph_id)
        if state and state["status"] in ["completed", "error", "cancelled"]:
            logger.info(f"Workflow finished with status: {state['status']}")
            break
            
        await asyncio.sleep(1)
        waiting += 1
    
    # Get final state
    final_state = langgraph_integrator.get_workflow_state(graph_id)
    
    if final_state:
        logger.info("=== WORKFLOW COMPLETED ===")
        logger.info(f"Status: {final_state['status']}")
        logger.info(f"Message count: {len(final_state.get('messages', []))}")
        
        # Print all messages in order
        for i, msg in enumerate(final_state.get('messages', [])):
            logger.info(f"Message {i+1} ({msg.get('role', 'unknown')}): {msg.get('content', '')[:100]}...")
        
        # Print final report
        if "report" in final_state.get("context", {}):
            logger.info("\nFINAL REPORT:")
            logger.info(final_state["context"]["report"])
    else:
        logger.error(f"Failed to get final state for workflow {graph_id}")

if __name__ == "__main__":
    asyncio.run(main())
