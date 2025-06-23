"""
Shared type definitions for Project-S
"""
from typing import Dict, Any, List, Optional
from datetime import datetime
from pydantic import BaseModel, Field

class Conversation(BaseModel):
    """Conversation data model"""
    id: str
    title: str
    created_at: datetime
    updated_at: datetime
    metadata: Dict[str, Any] = Field(default_factory=dict)

class Message(BaseModel):
    """Message data model"""
    id: str
    conversation_id: str
    content: str
    role: str  # user, assistant, system
    timestamp: datetime
    metadata: Dict[str, Any] = Field(default_factory=dict)

class Command(BaseModel):
    """Command data model"""
    id: str
    conversation_id: str
    command: str
    parameters: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime
    status: str = "pending"  # pending, executing, completed, failed
    result: Optional[Dict[str, Any]] = None

class Context(BaseModel):
    """Context data model"""
    conversation_id: str
    current_state: Dict[str, Any] = Field(default_factory=dict)
    history: List[Dict[str, Any]] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
