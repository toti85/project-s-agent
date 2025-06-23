"""
LangGraph Integration with enhanced state management
--------------------------------------------------
This module enhances the LangGraph integration with state persistence
and synchronization capabilities.
"""
import logging
import asyncio
from typing import Dict, Any, List, Optional, Tuple
import os
import time

from integrations.langgraph_integration import langgraph_integrator, GraphState
from integrations.langgraph_state_manager import state_manager
from core.event_bus import event_bus
from core.conversation_manager import conversation_manager

logger = logging.getLogger(__name__)

async def initialize_state_enhanced_integration():
    """
    Initialize the enhanced state management integration between
    LangGraph and Project-S.
    """
    # Register enhanced methods with the LangGraphIntegrator
    langgraph_integrator.create_state_linked_workflow = create_state_linked_workflow
    langgraph_integrator.load_workflow_from_state = load_workflow_from_state
    langgraph_integrator.save_workflow_state = save_workflow_state
    langgraph_integrator.link_workflow_to_conversation = link_workflow_to_conversation
    
    # Subscribe to additional events
    event_bus.subscribe("workflow.state.save", on_state_save_request)
    event_bus.subscribe("workflow.state.load", on_state_load_request)
    event_bus.subscribe("conversation.message.added", on_conversation_updated)
    
    logger.info("Enhanced state management for LangGraph initialized")

async def create_state_linked_workflow(
    name: str,
    steps: List[Dict[str, Any]],
    conversation_id: Optional[str] = None,
    context: Optional[Dict[str, Any]] = None,
    branches: Optional[Dict[str, List[Dict[str, Any]]]] = None
) -> Tuple[str, GraphState]:
    """
    Create a new workflow with enhanced state management,
    optionally linked to a Project-S conversation.
    
    Args:
        name: Name of the workflow
        steps: List of command steps to execute
        conversation_id: Optional ID of a Project-S conversation to link with
        context: Additional context for the workflow
        branches: Optional dict of named branch paths with their own steps
        
    Returns:
        Tuple[str, GraphState]: The graph ID and initial state
    """
    # Create context if not provided
    if context is None:
        context = {}
    
    # Add conversation ID to context if provided
    if conversation_id:
        context["conversation_id"] = conversation_id
    
    # Create the workflow using standard method
    graph_id = langgraph_integrator.create_workflow(
        name=name,
        steps=steps,
        context=context,
        branches=branches
    )
    
    # Get the initial state
    state = langgraph_integrator.graph_states[graph_id]
    
    # Add Project-S specific fields
    state["conversation_id"] = conversation_id
    state["session_data"] = {}
    state["memory_references"] = []
    state["system_state"] = {}
    state["persistence_metadata"] = {
        "last_saved": time.time(),
        "save_version": 0,
        "checkpoints": [],
        "save_path": ""
    }
    
    # If conversation_id is provided, update with conversation data
    if conversation_id:
        try:
            conversation = await conversation_manager.get_conversation(conversation_id)
            if conversation:
                # Update state with conversation messages
                state["messages"] = conversation.get("messages", [])
                
                # Publish event about the linkage
                await event_bus.publish("workflow.conversation.linked", {
                    "graph_id": graph_id,
                    "conversation_id": conversation_id
                })
        except Exception as e:
            logger.error(f"Error importing conversation {conversation_id}: {e}")
    
    # Register the state with the state manager
    state_manager.register_state(graph_id, state)
    
    # Update the stored state in the integrator
    langgraph_integrator.graph_states[graph_id] = state
    
    logger.info(f"Created state-linked workflow {graph_id} with name '{name}'")
    
    return graph_id, state

async def load_workflow_from_state(graph_id: str) -> Optional[GraphState]:
    """
    Load a workflow state from persistent storage.
    
    Args:
        graph_id: ID of the workflow graph
        
    Returns:
        Optional[GraphState]: The loaded state or None if not found
    """
    # Try to load state from the state manager
    state = await state_manager.load_state(graph_id)
    
    if state:
        # Update the integrator's state
        langgraph_integrator.graph_states[graph_id] = state
        
        # Recreate the graph with LangGraph
        # This is required since the graph itself is not serialized
        graph = None
        
        # Check if this is a node-based workflow
        if "nodes" in state["context"] and "edges" in state["context"]:
            # Create a node-based graph
            try:
                # Re-create the graph from nodes and edges
                nodes = state["context"]["nodes"]
                edges = state["context"]["edges"]
                
                # Create a new graph without modifying the state
                graph_id_temp = langgraph_integrator.create_node_based_workflow(
                    name=state["context"].get("workflow_name", "restored"),
                    nodes=nodes,
                    edges=edges,
                    context={}  # Empty context to avoid overwriting
                )
                
                # Get the graph object and store it with the original ID
                graph = langgraph_integrator.active_graphs.pop(graph_id_temp)
                langgraph_integrator.active_graphs[graph_id] = graph
                
                # Remove temporary state
                if graph_id_temp in langgraph_integrator.graph_states:
                    del langgraph_integrator.graph_states[graph_id_temp]
                
            except Exception as e:
                logger.error(f"Error recreating node-based graph {graph_id}: {e}")
                return None
        else:
            # Create a regular sequential workflow
            try:
                steps = state["context"].get("workflow_steps", [])
                
                # Create a new graph without modifying the state
                graph_id_temp = langgraph_integrator.create_workflow(
                    name=state["context"].get("workflow_name", "restored"),
                    steps=steps,
                    context={}  # Empty context to avoid overwriting
                )
                
                # Get the graph object and store it with the original ID
                graph = langgraph_integrator.active_graphs.pop(graph_id_temp)
                langgraph_integrator.active_graphs[graph_id] = graph
                
                # Remove temporary state
                if graph_id_temp in langgraph_integrator.graph_states:
                    del langgraph_integrator.graph_states[graph_id_temp]
                
            except Exception as e:
                logger.error(f"Error recreating sequential graph {graph_id}: {e}")
                return None
        
        # Ensure the graph is properly stored
        if graph:
            langgraph_integrator.active_graphs[graph_id] = graph
            logger.info(f"Successfully loaded workflow {graph_id} from state")
            
            # Publish event about restored workflow
            await event_bus.publish("workflow.state.restored", {
                "graph_id": graph_id,
                "workflow_name": state["context"].get("workflow_name"),
                "status": state["status"]
            })
            
            return state
    
    logger.warning(f"Failed to load workflow {graph_id} from state")
    return None

async def save_workflow_state(graph_id: str, create_checkpoint: bool = False) -> bool:
    """
    Save a workflow state to persistent storage.
    
    Args:
        graph_id: ID of the workflow graph
        create_checkpoint: Whether to also create a checkpoint copy
        
    Returns:
        bool: True if save was successful
    """
    # Check if graph exists
    if graph_id not in langgraph_integrator.graph_states:
        logger.warning(f"Cannot save unknown graph: {graph_id}")
        return False
    
    # Get the current state
    state = langgraph_integrator.graph_states[graph_id]
    
    # Ensure the state is registered with the state manager
    state_manager.register_state(graph_id, state)
    
    # Save the state
    success = await state_manager.save_state(graph_id, create_checkpoint)
    
    if success:
        # Publish event about saved state
        await event_bus.publish("workflow.state.saved", {
            "graph_id": graph_id,
            "checkpoint_created": create_checkpoint
        })
    
    return success

async def link_workflow_to_conversation(
    graph_id: str,
    conversation_id: str
) -> bool:
    """
    Link an existing workflow to a Project-S conversation.
    
    Args:
        graph_id: ID of the workflow graph
        conversation_id: ID of the Project-S conversation
        
    Returns:
        bool: True if linking was successful
    """
    # Check if graph exists
    if graph_id not in langgraph_integrator.graph_states:
        logger.warning(f"Cannot link unknown graph: {graph_id}")
        return False
    
    # Get the current state
    state = langgraph_integrator.graph_states[graph_id]
    
    # Update the conversation ID
    state["conversation_id"] = conversation_id
    
    try:
        # Get the conversation from Project-S
        conversation = await conversation_manager.get_conversation(conversation_id)
        
        if conversation:
            # Update state with conversation messages
            state["messages"] = conversation.get("messages", [])
            
            # Update the state manager
            state_manager.session_mappings[conversation_id] = graph_id
            
            # Publish event about the linkage
            await event_bus.publish("workflow.conversation.linked", {
                "graph_id": graph_id,
                "conversation_id": conversation_id
            })
            
            logger.info(f"Linked workflow {graph_id} to conversation {conversation_id}")
            return True
    except Exception as e:
        logger.error(f"Error linking workflow {graph_id} to conversation {conversation_id}: {e}")
    
    return False

# Event handlers
async def on_state_save_request(event_data):
    """Handle workflow.state.save events"""
    graph_id = event_data.get("graph_id")
    create_checkpoint = event_data.get("create_checkpoint", False)
    
    if not graph_id:
        logger.error("Received state save request without graph_id")
        return
    
    await save_workflow_state(graph_id, create_checkpoint)

async def on_state_load_request(event_data):
    """Handle workflow.state.load events"""
    graph_id = event_data.get("graph_id")
    
    if not graph_id:
        logger.error("Received state load request without graph_id")
        return
    
    state = await load_workflow_from_state(graph_id)
    
    # Publish response with loaded state status
    await event_bus.publish("workflow.state.load.response", {
        "graph_id": graph_id,
        "success": state is not None,
        "state": state
    })

async def on_conversation_updated(event_data):
    """Handle conversation.message.added events"""
    conversation_id = event_data.get("conversation_id")
    
    if not conversation_id:
        return
    
    # Check if this conversation is linked to a workflow
    graph_id = await state_manager.get_graph_for_conversation(conversation_id)
    
    if not graph_id or graph_id not in langgraph_integrator.graph_states:
        return
      # Get the current workflow state
    state = langgraph_integrator.graph_states[graph_id]
    
    # Update messages from the conversation
    try:
        conversation = await conversation_manager.get_conversation(conversation_id)
        if conversation:
            state["messages"] = conversation.get("messages", [])
            
            # Save state after conversation update
            await save_workflow_state(graph_id)
            
            logger.info(f"Updated workflow {graph_id} with messages from conversation {conversation_id}")
    except Exception as e:
        logger.error(f"Error updating workflow from conversation: {e}")

# Initialize the enhanced state management when this module is imported
# Note: Only create task if there's a running event loop
def _initialize_if_event_loop_running():
    """Initialize state enhanced integration only if event loop is running"""
    try:
        loop = asyncio.get_running_loop()
        asyncio.create_task(initialize_state_enhanced_integration())
        logger.info("State enhanced integration initialized successfully")
    except RuntimeError:
        # No event loop running, initialization will be done manually when needed
        logger.debug("No event loop running, state enhanced integration will be initialized manually")

# Try to initialize if event loop is available
_initialize_if_event_loop_running()
