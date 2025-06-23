"""
LangGraph Types for Project-S
-----------------------------
Shared type definitions to avoid circular imports.
"""

from typing import Dict, Any, List, TypedDict, Optional

class GraphState(TypedDict):
    """
    Enhanced type definition for the state managed by LangGraph,
    harmonized with Project-S state model
    """
    # Core LangGraph fields
    messages: List[Dict[str, Any]]  # Chat messages in the conversation
    context: Dict[str, Any]  # Workflow context data
    command_history: List[Dict[str, Any]]  # History of executed commands
    status: str  # Current workflow status (created, running, completed, error, cancelled)
    current_task: Optional[Dict[str, Any]]  # Currently executing task
    error_info: Optional[Dict[str, Any]]  # Information about errors
    retry_count: int  # Number of command retries
    branch: Optional[str]  # Current execution branch if using branched workflows
    
    # Project-S integration fields
    conversation_id: Optional[str]  # Link to Project-S conversation
    session_data: Optional[Dict[str, Any]]  # Session-specific data
    memory_references: Optional[List[str]]  # References to Project-S memory items
    system_state: Optional[Dict[str, Any]]  # Global system state from Project-S
    persistence_metadata: Optional[Dict[str, Any]]  # Metadata for state persistence
