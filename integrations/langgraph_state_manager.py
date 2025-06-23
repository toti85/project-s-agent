"""
LangGraph State Manager for Project-S
--------------------------------------
This module provides state synchronization and persistence between
Project-S's event-driven architecture and LangGraph's state management.
"""
import logging
import asyncio
import json
import os
import time
from datetime import datetime
from typing import Dict, Any, List, Optional, TypedDict, Union, Set, Tuple
from pathlib import Path
import copy

from core.event_bus import event_bus
from core.memory_system import MemorySystem
from core.conversation_manager import conversation_manager

# Create memory system instance
memory_system = MemorySystem()
from integrations.langgraph_types import GraphState

logger = logging.getLogger(__name__)

class PersistenceMetadata(TypedDict):
    """Metadata for state persistence"""
    last_saved: float  # Timestamp of last save
    save_version: int  # Incremented version number
    checkpoints: List[str]  # List of checkpoint identifiers
    save_path: str  # Path where state is saved


class StateManager:
    """
    Manages state synchronization between LangGraph and Project-S.
    
    Provides:
    - Conversion between Project-S state and LangGraph GraphState
    - State persistence to disk
    - State migration strategies
    - Session management for long-running interactions
    """
    
    def __init__(self, base_persistence_dir: Optional[str] = None):
        """
        Initialize the state manager.
        
        Args:
            base_persistence_dir: Base directory for state persistence
        """
        self.active_states: Dict[str, GraphState] = {}
        self.session_mappings: Dict[str, str] = {}  # conversation_id -> graph_id
        self.modified_states: Set[str] = set()  # Track which states were modified
        
        # Setup persistence directory
        if base_persistence_dir:
            self.base_dir = Path(base_persistence_dir)
        else:
            self.base_dir = Path(os.getcwd()) / "data" / "graph_states"
            
        self.base_dir.mkdir(exist_ok=True, parents=True)
        
        # Auto-save interval (in seconds)
        self.auto_save_interval = 300  # 5 minutes
          # Register for events
        self._register_event_handlers()
        
        # Auto-save task will be started when needed
        self._auto_save_task = None
        
        logger.info(f"LangGraph StateManager initialized with persistence dir: {self.base_dir}")
    
    def _register_event_handlers(self):
        """Register handlers for state-related events"""
        event_bus.subscribe("workflow.started", self._on_workflow_started)
        event_bus.subscribe("workflow.completed", self._on_workflow_completed)
        event_bus.subscribe("workflow.state.updated", self._on_state_updated)
        event_bus.subscribe("conversation.created", self._on_conversation_created)
        event_bus.subscribe("conversation.updated", self._on_conversation_updated)
        
        logger.info("StateManager event handlers registered")
    
    def _start_auto_save(self):
        """Start the auto-save background task if not already running"""
        if self._auto_save_task is not None:
            return
            
        try:
            # Check if we have a running event loop
            loop = asyncio.get_running_loop()
        except RuntimeError:
            # No event loop, defer starting the task
            logger.info("No event loop available, auto-save will start when loop is available")
            return
        
        async def auto_save_task():
            """Background task for auto-saving states"""
            while True:
                try:
                    # Wait for auto-save interval
                    await asyncio.sleep(self.auto_save_interval)
                    
                    # Save any modified states
                    await self._auto_save_modified_states()
                except Exception as e:
                    logger.error(f"Error in auto-save task: {e}")
        
        # Start the task
        self._auto_save_task = asyncio.create_task(auto_save_task())
        logger.info(f"Auto-save task started with {self.auto_save_interval}s interval")
    
    async def _auto_save_modified_states(self):
        """Save any states that have been modified since last save"""
        if not self.modified_states:
            return
            
        logger.info(f"Auto-saving {len(self.modified_states)} modified states")
        
        for graph_id in list(self.modified_states):
            try:
                if graph_id in self.active_states:
                    await self.save_state(graph_id)
                    self.modified_states.remove(graph_id)
            except Exception as e:
                logger.error(f"Error auto-saving state {graph_id}: {e}")
    
    async def _on_workflow_started(self, event_data):
        """Handle workflow.started events"""
        graph_id = event_data.get("graph_id")
        
        if not graph_id:
            return
            
        # Mark the state as modified for auto-save
        self.modified_states.add(graph_id)
    
    async def _on_workflow_completed(self, event_data):
        """Handle workflow.completed events"""
        graph_id = event_data.get("graph_id")
        state = event_data.get("state")
        
        if not graph_id or not state:
            return
        
        # Update our copy of the state
        self.active_states[graph_id] = state
        
        # Save state immediately on workflow completion
        await self.save_state(graph_id, create_checkpoint=True)
        
        # Remove from modified set since we just saved it
        if graph_id in self.modified_states:
            self.modified_states.remove(graph_id)
    
    async def _on_state_updated(self, event_data):
        """Handle workflow.state.updated events"""
        graph_id = event_data.get("graph_id")
        
        if not graph_id:
            return
            
        # Mark state as modified for next auto-save
        self.modified_states.add(graph_id)
    
    async def _on_conversation_created(self, event_data):
        """Handle conversation.created events"""
        conversation_id = event_data.get("conversation_id")
        graph_id = event_data.get("graph_id")
        
        # If this conversation has an associated graph, record the mapping
        if conversation_id and graph_id:
            self.session_mappings[conversation_id] = graph_id
            logger.info(f"Mapped conversation {conversation_id} to graph {graph_id}")
    
    async def _on_conversation_updated(self, event_data):
        """Handle conversation.updated events"""
        conversation_id = event_data.get("conversation_id")
        
        # If this conversation is linked to a graph, mark the state as modified
        if conversation_id in self.session_mappings:
            graph_id = self.session_mappings[conversation_id]
            self.modified_states.add(graph_id)
    
    def create_initial_graph_state(
        self,
        conversation_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> GraphState:
        """
        Create a new initial GraphState, optionally linked to a Project-S conversation.
        
        Args:
            conversation_id: Optional conversation ID to link with
            context: Optional initial context
            
        Returns:
            GraphState: The newly created graph state
        """
        # Create new state with required fields
        state: GraphState = {
            "messages": [],
            "context": context or {},
            "command_history": [],
            "status": "created",
            "current_task": None,
            "error_info": None,
            "retry_count": 0,
            "branch": None,
            "conversation_id": conversation_id,
            "session_data": {},
            "memory_references": [],
            "system_state": {},
            "persistence_metadata": {
                "last_saved": time.time(),
                "save_version": 0,
                "checkpoints": [],
                "save_path": ""
            }
        }
        
        # If conversation_id provided, import conversation history
        if conversation_id:
            try:
                conversation = conversation_manager.get_conversation(conversation_id)
                if conversation:
                    # Import messages from conversation
                    state["messages"] = conversation.get("messages", [])
                    
                    # Record mapping between conversation and graph
                    self.session_mappings[conversation_id] = f"pending_{conversation_id}"
            except Exception as e:
                logger.error(f"Error importing conversation {conversation_id}: {e}")
        
        return state
    
    def update_from_project_s(
        self,
        state: GraphState,
        conversation_data: Optional[Dict[str, Any]] = None,
        memory_items: Optional[List[Dict[str, Any]]] = None,
        system_state: Optional[Dict[str, Any]] = None
    ) -> GraphState:
        """
        Update a LangGraph state with data from Project-S.
        
        Args:
            state: The graph state to update
            conversation_data: Conversation data from Project-S
            memory_items: Memory items from Project-S memory system
            system_state: Global system state from Project-S
            
        Returns:
            GraphState: The updated graph state
        """
        # Create a copy to avoid modifying the original
        updated_state = copy.deepcopy(state)
        
        # Update with conversation data if provided
        if conversation_data:
            # Import messages from conversation
            if "messages" in conversation_data:
                updated_state["messages"] = conversation_data["messages"]
            
            # Set conversation ID if not already set
            if "id" in conversation_data and not updated_state.get("conversation_id"):
                updated_state["conversation_id"] = conversation_data["id"]
        
        # Update with memory items if provided
        if memory_items:
            # Store memory references
            updated_state["memory_references"] = [item.get("id") for item in memory_items if "id" in item]
            
            # Add memory content to context
            if "context" not in updated_state:
                updated_state["context"] = {}
            
            memory_context = {}
            for item in memory_items:
                if "content" in item and "type" in item:
                    memory_context[item["id"]] = {
                        "content": item["content"],
                        "type": item["type"]
                    }
            
            updated_state["context"]["memory"] = memory_context
        
        # Update with system state if provided
        if system_state:
            updated_state["system_state"] = system_state
        
        return updated_state
    
    def extract_project_s_data(self, state: GraphState) -> Dict[str, Any]:
        """
        Extract Project-S relevant data from a LangGraph state.
        
        Args:
            state: The graph state to extract from
            
        Returns:
            Dict[str, Any]: Dictionary with Project-S formatted data
        """
        result = {
            "conversation": None,
            "memory_items": [],
            "system_state": {}
        }
        
        # Extract conversation data
        if state.get("conversation_id") and state.get("messages"):
            result["conversation"] = {
                "id": state["conversation_id"],
                "messages": state["messages"]
            }
        
        # Extract memory references
        if state.get("memory_references"):
            # Just return references, actual content would be fetched from memory system
            result["memory_items"] = [
                {"id": ref} for ref in state.get("memory_references", [])
            ]
        
        # Extract system state
        if state.get("system_state"):
            result["system_state"] = state.get("system_state", {})
        
        return result
    
    async def synchronize_with_project_s(self, graph_id: str) -> bool:
        """
        Synchronize a LangGraph state with Project-S systems.
        
        Args:
            graph_id: ID of the workflow graph
            
        Returns:
            bool: True if synchronization was successful
        """
        if graph_id not in self.active_states:
            logger.warning(f"Cannot synchronize unknown graph: {graph_id}")
            return False
        
        try:
            state = self.active_states[graph_id]
            
            # Get conversation ID from state
            conversation_id = state.get("conversation_id")
            
            if conversation_id:
                # Update Project-S conversation with messages from graph state
                messages = state.get("messages", [])
                
                if messages:
                    await conversation_manager.update_conversation(
                        conversation_id,
                        messages=messages
                    )
                    
                    logger.info(f"Synchronized {len(messages)} messages to conversation {conversation_id}")
            
            # Synchronize memory references if present
            memory_refs = state.get("memory_references", [])
            memory_context = state.get("context", {}).get("memory", {})
            
            for memory_id in memory_refs:
                if memory_id in memory_context:
                    # Update memory item in Project-S memory system
                    item_data = memory_context[memory_id]
                    await memory_system.store_memory(
                        memory_id=memory_id,
                        content=item_data.get("content", ""),
                        memory_type=item_data.get("type", "general")
                    )
            
            # Mark state as synchronized
            if "persistence_metadata" not in state:
                state["persistence_metadata"] = {}
                
            state["persistence_metadata"]["last_synced"] = time.time()
            self.active_states[graph_id] = state
            
            return True
            
        except Exception as e:
            logger.error(f"Error synchronizing graph {graph_id} with Project-S: {e}")
            return False
    
    def _get_state_save_path(self, graph_id: str, is_checkpoint: bool = False) -> Path:
        """Get the path where a state should be saved"""
        if is_checkpoint:
            checkpoint_dir = self.base_dir / "checkpoints" / graph_id
            checkpoint_dir.mkdir(exist_ok=True, parents=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            return checkpoint_dir / f"checkpoint_{timestamp}.json"
        else:
            states_dir = self.base_dir / "active"
            states_dir.mkdir(exist_ok=True, parents=True)
            return states_dir / f"{graph_id}.json"
    
    async def save_state(self, graph_id: str, create_checkpoint: bool = False) -> bool:
        """
        Save a graph state to disk.
        
        Args:
            graph_id: ID of the workflow graph
            create_checkpoint: Whether to also create a checkpoint copy
            
        Returns:
            bool: True if save was successful
        """
        if graph_id not in self.active_states:
            logger.warning(f"Cannot save unknown graph: {graph_id}")
            return False
        
        try:
            state = self.active_states[graph_id]
            
            # Ensure metadata field exists
            if "persistence_metadata" not in state:
                state["persistence_metadata"] = {
                    "last_saved": time.time(),
                    "save_version": 0,
                    "checkpoints": [],
                    "save_path": ""
                }
            
            # Update metadata
            metadata = state["persistence_metadata"]
            metadata["last_saved"] = time.time()
            metadata["save_version"] += 1
            
            # Get save path
            save_path = self._get_state_save_path(graph_id)
            metadata["save_path"] = str(save_path)
            
            # Save to disk
            with open(save_path, 'w', encoding='utf-8') as f:
                json.dump(state, f, indent=2)
                
            # Create checkpoint if requested
            if create_checkpoint:
                checkpoint_path = self._get_state_save_path(graph_id, is_checkpoint=True)
                with open(checkpoint_path, 'w', encoding='utf-8') as f:
                    json.dump(state, f, indent=2)
                
                # Record checkpoint
                checkpoint_id = checkpoint_path.stem
                metadata["checkpoints"].append(checkpoint_id)
                
                logger.info(f"Created checkpoint {checkpoint_id} for graph {graph_id}")
            
            logger.info(f"Saved graph state {graph_id} to {save_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving graph {graph_id}: {e}")
            return False
    
    async def load_state(self, graph_id: str) -> Optional[GraphState]:
        """
        Load a graph state from disk.
        
        Args:
            graph_id: ID of the workflow graph
            
        Returns:
            Optional[GraphState]: The loaded state or None if not found
        """
        try:
            # Check if state is already in memory
            if graph_id in self.active_states:
                return self.active_states[graph_id]
            
            # Otherwise try to load from disk
            save_path = self._get_state_save_path(graph_id)
            
            if not save_path.exists():
                logger.warning(f"No saved state found for graph {graph_id}")
                return None
            
            with open(save_path, 'r', encoding='utf-8') as f:
                state = json.load(f)
            
            # Validate loaded state
            required_fields = [
                "messages", "context", "command_history", "status"
            ]
            
            for field in required_fields:
                if field not in state:
                    logger.warning(f"Loaded state for {graph_id} is missing required field: {field}")
                    return None
            
            # Store in active states
            self.active_states[graph_id] = state
            
            # If this state has a conversation_id, update mapping
            if "conversation_id" in state and state["conversation_id"]:
                self.session_mappings[state["conversation_id"]] = graph_id
            
            logger.info(f"Loaded graph state {graph_id} from {save_path}")
            return state
            
        except Exception as e:
            logger.error(f"Error loading graph {graph_id}: {e}")
            return None
    
    async def migrate_project_s_state_to_graph(
        self,
        conversation_id: str
    ) -> Tuple[bool, Optional[str]]:
        """
        Migrate an existing Project-S conversation state to a LangGraph state.
        
        Args:
            conversation_id: ID of the Project-S conversation to migrate
            
        Returns:
            Tuple[bool, Optional[str]]: Success flag and graph_id if successful
        """
        try:
            # Check if already mapped
            if conversation_id in self.session_mappings:
                graph_id = self.session_mappings[conversation_id]
                logger.info(f"Conversation {conversation_id} already mapped to graph {graph_id}")
                return True, graph_id
            
            # Get conversation from Project-S
            conversation = await conversation_manager.get_conversation(conversation_id)
            
            if not conversation:
                logger.warning(f"Cannot migrate unknown conversation: {conversation_id}")
                return False, None
            
            # Get any memory items linked to this conversation
            memory_items = await memory_system.get_memory_by_conversation(conversation_id)
            
            # Create a unique ID for the new graph
            graph_id = f"migrated_{conversation_id}"
            
            # Create initial state
            state = self.create_initial_graph_state(conversation_id)
            
            # Update with conversation data
            state = self.update_from_project_s(
                state, 
                conversation_data=conversation, 
                memory_items=memory_items
            )
            
            # Store the state
            self.active_states[graph_id] = state
            
            # Record mapping
            self.session_mappings[conversation_id] = graph_id
            
            # Save to disk
            await self.save_state(graph_id)
            
            logger.info(f"Migrated conversation {conversation_id} to graph {graph_id}")
            return True, graph_id
            
        except Exception as e:
            logger.error(f"Error migrating conversation {conversation_id}: {e}")
            return False, None
    
    async def get_graph_for_conversation(self, conversation_id: str) -> Optional[str]:
        """
        Get the graph ID associated with a conversation, migrating if needed.
        
        Args:
            conversation_id: ID of the Project-S conversation
            
        Returns:
            Optional[str]: The graph ID if found or created
        """
        # Check if already mapped
        if conversation_id in self.session_mappings:
            return self.session_mappings[conversation_id]
        
        # If not mapped, try to migrate
        success, graph_id = await self.migrate_project_s_state_to_graph(conversation_id)
        
        if success:
            return graph_id
        return None
    
    def register_state(self, graph_id: str, state: GraphState) -> bool:
        """
        Register an existing graph state with the state manager.
        
        Args:
            graph_id: ID of the workflow graph
            state: The graph state
            
        Returns:
            bool: True if registration was successful
        """
        try:
            # Store the state
            self.active_states[graph_id] = state
            
            # If this state has a conversation_id, update mapping
            if "conversation_id" in state and state["conversation_id"]:
                self.session_mappings[state["conversation_id"]] = graph_id
            
            # Mark as modified for next auto-save
            self.modified_states.add(graph_id)
            
            logger.info(f"Registered graph state {graph_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error registering graph {graph_id}: {e}")
            return False

# Create a singleton instance
state_manager = StateManager()
