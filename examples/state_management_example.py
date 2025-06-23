"""
Session and State Management Example with LangGraph and Project-S
----------------------------------------------------------------
This example demonstrates the enhanced state management capabilities for
long-running interactions and state persistence.
"""
import asyncio
import logging
import os
import sys
import json
import time
from typing import Dict, Any, Optional

# Add the parent directory to the path so we can import the Project-S modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.event_bus import event_bus
from core.conversation_manager import conversation_manager
from integrations.langgraph_integration import langgraph_integrator
from integrations.langgraph_state_manager import state_manager
from integrations.langgraph_state_enhanced import (
    create_state_linked_workflow,
    load_workflow_from_state,
    save_workflow_state,
    link_workflow_to_conversation
)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("LangGraph_State_Management_Example")

# Event handlers
async def on_workflow_state_saved(event_data):
    """Handler for workflow.state.saved events"""
    logger.info(f"Workflow state saved: {event_data}")

async def on_workflow_state_restored(event_data):
    """Handler for workflow.state.restored events"""
    logger.info(f"Workflow state restored: {event_data}")

async def on_workflow_conversation_linked(event_data):
    """Handler for workflow.conversation.linked events"""
    logger.info(f"Workflow linked to conversation: {event_data}")

async def create_conversation():
    """Create a test conversation in Project-S"""
    conversation = {
        "id": f"conv_{int(time.time())}",
        "messages": [
            {
                "role": "system",
                "content": "You are a helpful assistant."
            },
            {
                "role": "user",
                "content": "I need help with a workflow that persists across sessions."
            },
            {
                "role": "assistant",
                "content": "I'd be happy to help you create a persistent workflow. What kind of task would you like to accomplish?"
            }
        ],
        "metadata": {
            "created_at": time.time(),
            "title": "Persistent Workflow Test"
        }
    }
    
    # Create the conversation through the conversation manager
    await conversation_manager.create_conversation(conversation)
    
    logger.info(f"Created test conversation with ID: {conversation['id']}")
    return conversation["id"]

async def demonstrate_state_enhanced_workflow():
    """Demonstrate creating and persisting a workflow with state management"""
    # Register event handlers
    event_bus.subscribe("workflow.state.saved", on_workflow_state_saved)
    event_bus.subscribe("workflow.state.restored", on_workflow_state_restored)
    event_bus.subscribe("workflow.conversation.linked", on_workflow_conversation_linked)
    
    # 1. Create a test conversation
    conversation_id = await create_conversation()
    
    # 2. Create a workflow linked to the conversation
    workflow_steps = [
        {
            "type": "ASK",
            "query": "What should we accomplish in this persistent workflow?"
        },
        {
            "type": "CODE",
            "content": "Write a Python function that processes data incrementally across sessions",
            "options": {"language": "python"}
        },
        {
            "type": "CMD",
            "cmd": "echo 'Processing workflow data...'"
        }
    ]
    
    # Create the workflow and link it to the conversation
    graph_id, initial_state = await create_state_linked_workflow(
        name="persistent_session_demo",
        steps=workflow_steps,
        conversation_id=conversation_id,
        context={
            "purpose": "Demonstrate state persistence",
            "session_data": {
                "start_time": time.time(),
                "progress": 0
            }
        }
    )
    
    logger.info(f"Created workflow with ID: {graph_id}")
    logger.info(f"Initial state: {json.dumps(initial_state, indent=2)[:200]}...")
    
    # 3. Start the workflow
    await langgraph_integrator.start_workflow(graph_id)
    
    # 4. Wait briefly to simulate some progress
    await asyncio.sleep(2)
    
    # 5. Update workflow state with progress
    state = langgraph_integrator.get_workflow_state(graph_id)
    if state:
        # Update session data
        if "session_data" not in state:
            state["session_data"] = {}
        state["session_data"]["progress"] = 30
        state["session_data"]["last_update"] = time.time()
        
        # Add a checkpoint message
        state["messages"].append({
            "role": "system",
            "content": "Session checkpoint reached at 30% progress"
        })
    
    # 6. Save the workflow state with a checkpoint
    await save_workflow_state(graph_id, create_checkpoint=True)
    logger.info("Saved workflow state with progress update")
    
    # 7. Simulate ending the session
    logger.info("Simulating end of session - closing workflow")
    
    # Clear the workflow from active graphs to simulate closing the session
    original_state = langgraph_integrator.graph_states.pop(graph_id, None)
    graph = langgraph_integrator.active_graphs.pop(graph_id, None)
    
    await asyncio.sleep(1)
    logger.info("Session ended, workflow state is persisted")
    
    # 8. Simulate starting a new session and restoring the workflow
    logger.info("Starting new session - restoring workflow from state")
    await asyncio.sleep(1)
    
    # Load the workflow state
    restored_state = await load_workflow_from_state(graph_id)
    
    if restored_state:
        logger.info("Successfully restored workflow state")
        logger.info(f"Restored progress: {restored_state.get('session_data', {}).get('progress')}%")
        
        # 9. Update the workflow with new progress
        restored_state["session_data"]["progress"] = 60
        restored_state["session_data"]["last_update"] = time.time()
        restored_state["messages"].append({
            "role": "system",
            "content": "Session restored and progressed to 60% completion"
        })
        
        # Save the updated state
        await save_workflow_state(graph_id, create_checkpoint=True)
        logger.info("Saved updated workflow state with new progress")
        
        # 10. Add a new message to the conversation directly
        await conversation_manager.add_message(
            conversation_id,
            {
                "role": "user",
                "content": "Can we continue this workflow where we left off?"
            }
        )
        
        # Wait briefly for the system to process
        await asyncio.sleep(1)
        
        # 11. Get the current workflow state to see if conversation update was synchronized
        current_state = langgraph_integrator.get_workflow_state(graph_id)
        if current_state:
            logger.info(f"Current message count: {len(current_state.get('messages', []))}")
            
            # Check if the new message was synchronized
            last_message = current_state.get('messages', [])[-1] if current_state.get('messages') else None
            if last_message:
                logger.info(f"Last message: {last_message.get('role')} - {last_message.get('content')[:50]}...")
    else:
        logger.error("Failed to restore workflow state")
    
    # 12. Demonstrate migration of a conversation to a workflow
    new_conversation_id = await create_conversation()
    
    # Create a new workflow without linking to the conversation
    new_graph_id, _ = await create_state_linked_workflow(
        name="migration_demo",
        steps=workflow_steps
    )
    
    # Now link the workflow to the conversation after creation
    linked = await link_workflow_to_conversation(new_graph_id, new_conversation_id)
    
    if linked:
        logger.info(f"Successfully linked workflow {new_graph_id} to conversation {new_conversation_id}")
        
        # Verify the linkage by checking the state
        linked_state = langgraph_integrator.get_workflow_state(new_graph_id)
        if linked_state and linked_state.get("conversation_id") == new_conversation_id:
            logger.info("Verified conversation linkage in workflow state")
    else:
        logger.error("Failed to link workflow to conversation")
    
    # Return information about the created resources
    return {
        "primary_workflow": graph_id,
        "conversation_id": conversation_id,
        "migration_workflow": new_graph_id,
        "new_conversation_id": new_conversation_id
    }

async def demonstrate_state_migration():
    """
    Demonstrate migrating an existing Project-S conversation state to LangGraph
    """
    # 1. Create a standalone conversation in Project-S
    conversation_id = await create_conversation()
    
    # Add more messages to the conversation
    await conversation_manager.add_message(
        conversation_id,
        {
            "role": "user",
            "content": "This is a standalone conversation that will be migrated to a LangGraph workflow"
        }
    )
    
    await conversation_manager.add_message(
        conversation_id,
        {
            "role": "assistant",
            "content": "I understand! I'll help you migrate this conversation to a LangGraph workflow."
        }
    )
    
    logger.info(f"Created standalone conversation: {conversation_id}")
    
    # 2. Migrate the conversation to a LangGraph workflow
    success, graph_id = await state_manager.migrate_project_s_state_to_graph(conversation_id)
    
    if success and graph_id:
        logger.info(f"Successfully migrated conversation {conversation_id} to workflow {graph_id}")
        
        # Check the migrated state
        state = langgraph_integrator.get_workflow_state(graph_id)
        if state:
            logger.info(f"Migrated state has {len(state.get('messages', []))} messages")
            
            # Define workflow steps for the migrated conversation
            workflow_steps = [
                {
                    "type": "ASK",
                    "query": "This conversation was migrated from Project-S to LangGraph. What should we do next?"
                }
            ]
            
            # Update the migrated workflow with steps
            state["context"]["workflow_steps"] = workflow_steps
            state["context"]["workflow_name"] = "Migrated Workflow"
            
            # Save the updated state
            await save_workflow_state(graph_id)
            
            # Start the workflow
            await langgraph_integrator.start_workflow(graph_id)
            
            logger.info(f"Started migrated workflow {graph_id}")
            
            return {
                "migrated_workflow": graph_id,
                "conversation_id": conversation_id,
                "message_count": len(state.get('messages', []))
            }
    else:
        logger.error(f"Failed to migrate conversation {conversation_id}")
    
    return None

if __name__ == "__main__":
    # Ensure system is initialized
    from integrations.langgraph_init import setup_langgraph
    setup_langgraph()
    
    # Run the example
    results = asyncio.run(demonstrate_state_enhanced_workflow())
    logger.info(f"Example completed with results: {results}")
    
    # Run migration example
    migration_results = asyncio.run(demonstrate_state_migration())
    logger.info(f"Migration example completed with results: {migration_results}")
