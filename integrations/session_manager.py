"""
Project-S AI Session Manager
---------------------------
This module provides session management capabilities for the Project-S system,
allowing for persistent conversations and context across interactions.
"""

import asyncio
import logging
import json
import uuid
from typing import Dict, Any, List, Optional, Union
from datetime import datetime

from integrations.persistent_state_manager import persistent_state_manager
from integrations.simplified_model_manager import model_manager
from integrations.advanced_langgraph_workflow import AdvancedLangGraphWorkflow
from core.event_bus import event_bus

logger = logging.getLogger(__name__)

class SessionManager:
    """
    Manages AI sessions, including creation, tracking, and persistence.
    Provides a high-level API for session-based AI interactions.
    """
    
    def __init__(self):
        """Initialize the session manager."""
        self.state_manager = persistent_state_manager
        self.model_manager = model_manager
        self.langgraph_workflow = AdvancedLangGraphWorkflow()
        
        # Active sessions cache
        self.active_sessions = {}
        
        # Subscribe to events
        event_bus.subscribe("session.created", self._on_session_created)
        event_bus.subscribe("session.ended", self._on_session_ended)
        
        logger.info("Session manager initialized")
        
    async def _on_session_created(self, data: Dict[str, Any]) -> None:
        """Handle session created event."""
        session_id = data.get("session_id")
        if session_id:
            self.active_sessions[session_id] = {
                "created_at": datetime.now().isoformat(),
                "last_activity": datetime.now().isoformat(),
                "metadata": data.get("metadata", {})
            }
            
            logger.info(f"Session created and tracked: {session_id}")
    
    async def _on_session_ended(self, data: Dict[str, Any]) -> None:
        """Handle session ended event."""
        session_id = data.get("session_id")
        if session_id and session_id in self.active_sessions:
            del self.active_sessions[session_id]
            logger.info(f"Session ended and removed from tracking: {session_id}")
    
    async def create_session(self, metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        Create a new AI session.
        
        Args:
            metadata: Optional metadata for the session
            
        Returns:
            str: The session ID
        """
        session_id = await self.state_manager.create_session(metadata or {})
        
        # Publish event
        await event_bus.publish("session.created", {
            "session_id": session_id,
            "metadata": metadata or {}
        })
        
        return session_id
    
    async def end_session(self, session_id: str) -> bool:
        """
        End an AI session.
        
        Args:
            session_id: The session ID
            
        Returns:
            bool: True if successful, False otherwise
        """
        success = await self.state_manager.end_session(session_id)
        
        if success:
            # Publish event
            await event_bus.publish("session.ended", {
                "session_id": session_id
            })
            
        return success
    
    async def get_session_info(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Get information about a session.
        
        Args:
            session_id: The session ID
            
        Returns:
            Optional[Dict[str, Any]]: Session information if found, None otherwise
        """
        # Get from memory if available
        if session_id in self.active_sessions:
            # Update with latest conversation data
            session_data = self.active_sessions[session_id].copy()
            
            # Add conversation history
            history = await self.state_manager.get_conversation_history(session_id)
            session_data["message_count"] = len(history)
            session_data["history"] = history
            
            return session_data
            
        # Otherwise try to load from persistent storage
        session = await self.state_manager.get_session(session_id)
        if session:
            # Also get conversation history
            history = await self.state_manager.get_conversation_history(session_id)
            session["message_count"] = len(history)
            
            return session
            
        return None
    
    async def process_in_session(self, 
                               session_id: Optional[str], 
                               query: str, 
                               task_type: Optional[str] = None,
                               model: Optional[str] = None,
                               workflow_type: str = "basic") -> Dict[str, Any]:
        """
        Process a query in a specified session with persistence.
        
        Args:
            session_id: Optional session ID. If None, creates a new session.
            query: The user query
            task_type: Optional task type
            model: Optional preferred model
            workflow_type: The type of workflow to use (basic, multi_step, or multi_model)
            
        Returns:
            Dict[str, Any]: Result of processing
        """
        # Create session if needed
        if not session_id:
            metadata = {
                "first_query": query,
                "workflow_type": workflow_type,
                "created_at": datetime.now().isoformat()
            }
            session_id = await self.create_session(metadata)
            logger.info(f"Created new session for processing: {session_id}")
        
        # Process based on workflow type
        if workflow_type == "multi_model":
            return await self.langgraph_workflow.process_with_multi_model_graph_with_persistence(
                command=query,
                session_id=session_id
            )
        elif workflow_type == "multi_step":
            # Use existing multi_step method with persistence for now
            # We could enhance this later
            result = await self.langgraph_workflow.process_with_multi_step_graph(query)
            
            # Save the conversation in the persistent storage
            await self.state_manager.add_conversation_entry(
                session_id=session_id,
                role="user",
                content=query
            )
            
            await self.state_manager.add_conversation_entry(
                session_id=session_id,
                role="assistant",
                content=result.get("result", ""),
                metadata={"workflow_type": "multi_step"}
            )
            
            result["session_id"] = session_id
            return result
        else:
            # Basic workflow - just use the model manager with session
            return await self.model_manager.execute_task_with_model_in_session(
                session_id=session_id,
                query=query,
                task_type=task_type,
                model=model,
                persist_history=True
            )
    
    async def process_with_multiple_models(self, 
                                        session_id: Optional[str], 
                                        query: str,
                                        models: List[str] = [],
                                        task_type: Optional[str] = None) -> Dict[str, Any]:
        """
        Process a query using multiple models in parallel and compare results.
        
        Args:
            session_id: Optional session ID. If None, creates a new session.
            query: The user query
            models: List of models to use. If empty, will auto-select.
            task_type: Optional task type for model selection
            
        Returns:
            Dict[str, Any]: Results from all models
        """
        # Create session if needed
        if not session_id:
            metadata = {
                "first_query": query,
                "workflow_type": "multi_model_comparison",
                "created_at": datetime.now().isoformat()
            }
            session_id = await self.create_session(metadata)
            logger.info(f"Created new session for multi-model comparison: {session_id}")
        
        # Run the query with multiple models
        return await self.model_manager.run_task_with_multiple_models_in_session(
            session_id=session_id,
            query=query,
            models=models,
            task_type=task_type,
            persist_history=True
        )

# Create singleton instance
session_manager = SessionManager()
