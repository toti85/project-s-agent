"""
Project-S ConversationManager
Felelős a beszélgetések, üzenetek, kontextus és memória kezeléséért.
"""
from typing import List, Optional, Dict
from datetime import datetime
from core.types import Conversation, Message, Command, Context
import uuid

class ConversationManager:
    def __init__(self):
        # In-memory tárolás, később cserélhető perzisztens rétegre
        self.conversations: Dict[str, Conversation] = {}
        self.messages: Dict[str, Message] = {}
        self.memory: Dict[str, Dict] = {}  # hosszútávú memória beszélgetésenként

    # --- Beszélgetés életciklus ---
    def create_conversation(self, title: Optional[str] = None, metadata: Optional[Dict] = None) -> Conversation:
        conv_id = f"conv_{uuid.uuid4().hex[:8]}"
        now = datetime.utcnow()
        conv = Conversation(
            id=conv_id,
            title=title or f"Project-S {now:%Y-%m-%d %H:%M}",
            created_at=now,
            updated_at=now,
            metadata=metadata or {},
        )
        self.conversations[conv_id] = conv
        self.memory[conv_id] = {}
        return conv

    def get_conversation(self, conv_id: str) -> Optional[Conversation]:
        return self.conversations.get(conv_id)

    def list_conversations(self) -> List[Conversation]:
        return list(self.conversations.values())

    def update_conversation(self, conv_id: str, title: Optional[str] = None, metadata: Optional[Dict] = None) -> Optional[Conversation]:
        conv = self.conversations.get(conv_id)
        if not conv:
            return None
        if title:
            conv.title = title
        if metadata:
            conv.metadata = metadata
        conv.updated_at = datetime.utcnow()
        self.conversations[conv_id] = conv
        return conv

    def delete_conversation(self, conv_id: str):
        self.conversations.pop(conv_id, None)
        self.memory.pop(conv_id, None)
        # Törli a kapcsolódó üzeneteket is
        to_delete = [mid for mid, m in self.messages.items() if m.conversation_id == conv_id]
        for mid in to_delete:
            self.messages.pop(mid, None)

    # --- Üzenet és előzmény kezelés ---
    def add_message(self, conv_id: str, role: str, content: Optional[str], command: Optional[Command] = None, references: Optional[List[str]] = None, structured_content: Optional[Dict] = None) -> Optional[Message]:
        if conv_id not in self.conversations:
            return None
        msg_id = f"msg_{uuid.uuid4().hex[:8]}"
        now = datetime.utcnow()
        msg = Message(
            id=msg_id,
            conversation_id=conv_id,
            role=role,
            content=content,
            command=command,
            created_at=now,
            references=references,
            structured_content=structured_content,
        )
        self.messages[msg_id] = msg
        self.conversations[conv_id].updated_at = now
        return msg

    def list_messages(self, conv_id: str) -> List[Message]:
        return [m for m in self.messages.values() if m.conversation_id == conv_id]

    # --- Kontextus építés ---
    def build_context(self, conv_id: str, limit: int = 20) -> Optional[Context]:
        if conv_id not in self.conversations:
            return None
        msgs = self.list_messages(conv_id)
        msgs.sort(key=lambda m: m.created_at)
        relevant = msgs[-limit:]
        summary = self.conversations[conv_id].summary
        memory = self.memory.get(conv_id, {})
        return Context(
            conversation_id=conv_id,
            summary=summary,
            relevant_messages=relevant,
            active_states=None,  # később bővíthető
            memory=memory,
        )

    # --- Memória kezelés ---
    def update_memory(self, conv_id: str, key: str, value):
        if conv_id not in self.memory:
            self.memory[conv_id] = {}
        self.memory[conv_id][key] = value

    def get_memory(self, conv_id: str) -> Dict:
        return self.memory.get(conv_id, {})

    # --- Referencia rendszer (egyszerű keresés) ---
    def find_message_by_reference(self, conv_id: str, ref_id: str) -> Optional[Message]:
        msgs = self.list_messages(conv_id)
        for m in msgs:
            if m.id == ref_id or (m.references and ref_id in m.references):
                return m
        return None    # --- Archiválás, összegzés, tömörítés helye ---
    # (Később implementálható: automatikus összegzés, fontosság szerinti tömörítés, perzisztencia)

# Create a singleton instance
conversation_manager = ConversationManager()
