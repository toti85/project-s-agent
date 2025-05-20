from fastapi import FastAPI, HTTPException, Body
from pydantic import BaseModel
from typing import List, Optional, Dict
from datetime import datetime
import uuid
import asyncio

app = FastAPI(title="Project-S API Agent")

# In-memory storage
conversations = {}
messages = {}

# --- Data models ---
class Command(BaseModel):
    type: str
    action: Optional[str] = None
    params: Optional[Dict] = None    # típus-specifikus paraméterek
    options: Optional[Dict] = None   # végrehajtási beállítások
    # Kompatibilitás kedvéért:
    path: Optional[str] = None
    cmd: Optional[str] = None
    content: Optional[str] = None

class Message(BaseModel):
    id: str
    conversation_id: str
    role: str  # "user", "agent", "command", "response", "system"
    content: Optional[str] = None    # szöveges vagy strukturált
    structured_content: Optional[Dict] = None  # opcionális strukturált tartalom
    command: Optional[Command] = None
    created_at: datetime
    references: Optional[List[str]] = None  # hivatkozások más üzenetekre

class Response(BaseModel):
    status: str  # "success" vagy "error"
    result: Optional[Dict] = None    # strukturált vagy szöveges eredmény
    error: Optional[str] = None
    meta: Optional[Dict] = None      # végrehajtási metaadatok (időtartam, erőforrás, stb.)

class Conversation(BaseModel):
    id: str
    title: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    metadata: Optional[Dict] = None  # pl. projekt, címkék, leírás
    summary: Optional[str] = None    # összegzés vagy állapot

class ConversationCreate(BaseModel):
    title: Optional[str] = None
    metadata: Optional[Dict] = None

class Context(BaseModel):
    conversation_id: str
    summary: Optional[str] = None
    relevant_messages: List[Message]
    active_states: Optional[Dict] = None
    memory: Optional[Dict] = None

# --- API endpoints ---
@app.post("/api/conversations", response_model=Conversation)
def create_conversation(conv: ConversationCreate):
    conv_id = f"conv_{uuid.uuid4().hex[:8]}"
    now = datetime.utcnow()
    conversation = Conversation(
        id=conv_id,
        title=conv.title or f"Project-S {now:%Y-%m-%d %H:%M}",
        created_at=now,
        updated_at=now,
        metadata=conv.metadata or {},
    )
    conversations[conv_id] = conversation
    return conversation

@app.get("/api/conversations", response_model=List[Conversation])
def list_conversations():
    return list(conversations.values())

@app.get("/api/conversations/{conv_id}", response_model=Conversation)
def get_conversation(conv_id: str):
    if conv_id not in conversations:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return conversations[conv_id]

@app.put("/api/conversations/{conv_id}", response_model=Conversation)
def update_conversation(conv_id: str, update: Dict = Body(...)):
    if conv_id not in conversations:
        raise HTTPException(status_code=404, detail="Conversation not found")
    conv = conversations[conv_id]
    if "title" in update:
        conv.title = update["title"]
    if "metadata" in update:
        conv.metadata = update["metadata"]
    conv.updated_at = datetime.utcnow()
    conversations[conv_id] = conv
    return conv

@app.delete("/api/conversations/{conv_id}")
def delete_conversation(conv_id: str):
    if conv_id in conversations:
        del conversations[conv_id]
    # Delete related messages
    to_delete = [mid for mid, m in messages.items() if m.conversation_id == conv_id]
    for mid in to_delete:
        del messages[mid]
    return {"status": "deleted"}

@app.post("/api/conversations/{conv_id}/messages", response_model=Message)
def add_message(conv_id: str, msg: Message):
    if conv_id not in conversations:
        raise HTTPException(status_code=404, detail="Conversation not found")
    msg_id = f"msg_{uuid.uuid4().hex[:8]}"
    now = datetime.utcnow()
    message = Message(
        id=msg_id,
        conversation_id=conv_id,
        role=msg.role,
        content=msg.content,
        command=msg.command,
        created_at=now,
    )
    messages[msg_id] = message
    conversations[conv_id].updated_at = now
    return message

@app.get("/api/conversations/{conv_id}/messages", response_model=List[Message])
def list_messages(conv_id: str):
    if conv_id not in conversations:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return [m for m in messages.values() if m.conversation_id == conv_id]

@app.get("/api/conversations/{conv_id}/context", response_model=List[Message])
def get_context(conv_id: str, limit: int = 20):
    if conv_id not in conversations:
        raise HTTPException(status_code=404, detail="Conversation not found")
    msgs = [m for m in messages.values() if m.conversation_id == conv_id]
    msgs.sort(key=lambda m: m.created_at)
    return msgs[-limit:]

@app.post("/api/conversations/{conv_id}/execute")
async def execute_command(conv_id: str, cmd: Command):
    if conv_id not in conversations:
        raise HTTPException(status_code=404, detail="Conversation not found")
    # --- Integrációs hely: Project-S command_router ---
    try:
        from core.command_router import router
        result = await router.route_command(cmd.dict())
    except Exception as e:
        result = {"error": str(e)}
    # Store response as message
    msg_id = f"msg_{uuid.uuid4().hex[:8]}"
    now = datetime.utcnow()
    response_msg = Message(
        id=msg_id,
        conversation_id=conv_id,
        role="response",
        content=str(result),
        command=cmd,
        created_at=now,
    )
    messages[msg_id] = response_msg
    conversations[conv_id].updated_at = now
    return {"result": result, "message_id": msg_id}

@app.post("/api/execute")
async def execute_direct(cmd: Command):
    try:
        from core.command_router import router
        result = await router.route_command(cmd.dict())
    except Exception as e:
        result = {"error": str(e)}
    return {"result": result}

@app.get("/api/status")
def api_status():
    return {
        "status": "ok",
        "conversations": len(conversations),
        "messages": len(messages),
        "time": datetime.utcnow().isoformat()
    }

@app.get("/api/capabilities")
def api_capabilities():
    # Statikus példa, később dinamikus lehet
    return {
        "command_types": ["CMD", "ASK", "FILE"],
        "file_actions": ["read", "write", "append", "delete"],
        "system": ["status", "capabilities"]
    }

# --- Root endpoint ---
@app.get("/")
def root():
    return {"status": "Project-S API Agent running"}
