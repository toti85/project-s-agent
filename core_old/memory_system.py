import json
import os
import pickle
from typing import Dict, Any, List, Optional
import time

class MemorySystem:
    def __init__(self, storage_dir: str = "memory"):
        self.storage_dir = storage_dir
        self.session_memory: Dict[str, Any] = {}
        self.long_term_memory: Dict[str, Any] = {}
        self.context_stack: List[Dict[str, Any]] = [{}]  # Current context at the end
        
        # Ensure directory exists
        os.makedirs(storage_dir, exist_ok=True)
        
        # Try to load long-term memory
        self._load_long_term_memory()
        
    def _load_long_term_memory(self):
        """Load long-term memory from disk"""
        memory_file = os.path.join(self.storage_dir, "long_term_memory.json")
        if os.path.exists(memory_file):
            try:
                with open(memory_file, 'r') as f:
                    self.long_term_memory = json.load(f)
            except Exception as e:
                print(f"Error loading long-term memory: {str(e)}")
                
    def _save_long_term_memory(self):
        """Save long-term memory to disk"""
        memory_file = os.path.join(self.storage_dir, "long_term_memory.json")
        try:
            with open(memory_file, 'w') as f:
                json.dump(self.long_term_memory, f, indent=2)
        except Exception as e:
            print(f"Error saving long-term memory: {str(e)}")
            
    def remember_session(self, key: str, value: Any):
        """Store a value in session memory"""
        self.session_memory[key] = value
        
    def remember_long_term(self, key: str, value: Any):
        """Store a value in long-term memory"""
        self.long_term_memory[key] = value
        self._save_long_term_memory()
        
    def recall_session(self, key: str, default: Any = None) -> Any:
        """Recall a value from session memory"""
        return self.session_memory.get(key, default)
        
    def recall_long_term(self, key: str, default: Any = None) -> Any:
        """Recall a value from long-term memory"""
        return self.long_term_memory.get(key, default)
        
    def forget_session(self, key: str):
        """Remove a value from session memory"""
        if key in self.session_memory:
            del self.session_memory[key]
            
    def forget_long_term(self, key: str):
        """Remove a value from long-term memory"""
        if key in self.long_term_memory:
            del self.long_term_memory[key]
            self._save_long_term_memory()
            
    def push_context(self, context: Dict[str, Any]):
        """Push a new context onto the stack"""
        self.context_stack.append(context)
        
    def pop_context(self) -> Dict[str, Any]:
        """Pop the current context from the stack"""
        if len(self.context_stack) > 1:
            return self.context_stack.pop()
        else:
            # Don't pop the last (base) context
            return self.context_stack[-1]
            
    def get_current_context(self) -> Dict[str, Any]:
        """Get the current context"""
        return self.context_stack[-1]
        
    def update_context(self, updates: Dict[str, Any]):
        """Update the current context with new values"""
        self.context_stack[-1].update(updates)
        
    def save_state(self, name: Optional[str] = None):
        """Save the current state to disk"""
        if name is None:
            name = f"state_{int(time.time())}"
            
        state = {
            "session_memory": self.session_memory,
            "context_stack": self.context_stack,
            "timestamp": time.time()
        }
        
        state_file = os.path.join(self.storage_dir, f"{name}.state")
        try:
            with open(state_file, 'wb') as f:
                pickle.dump(state, f)
            return True
        except Exception as e:
            print(f"Error saving state: {str(e)}")
            return False
            
    def load_state(self, name: str) -> bool:
        """Load a saved state from disk"""
        state_file = os.path.join(self.storage_dir, f"{name}.state")
        if not os.path.exists(state_file):
            return False
            
        try:
            with open(state_file, 'rb') as f:
                state = pickle.load(f)
                
            self.session_memory = state["session_memory"]
            self.context_stack = state["context_stack"]
            return True
        except Exception as e:
            print(f"Error loading state: {str(e)}")
            return False
            
    def list_saved_states(self) -> List[str]:
        """List all saved states"""
        states = []
        for file in os.listdir(self.storage_dir):
            if file.endswith(".state"):
                states.append(file[:-6])  # Remove .state extension
        return states