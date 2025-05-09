import logging
import asyncio
import json
from typing import Dict, List, Any, Optional, Set
from datetime import datetime
from core.event_bus import event_bus
from core.central_executor import executor
from core.error_handler import error_handler
from utils.performance_monitor import monitor_performance

logger = logging.getLogger(__name__)

class CognitiveCore:
    """
    Cognitive Core for the Project-S agent system.
    Acts as the 'brain' of the system, interpreting events, planning tasks, and maintaining context.
    """
    
    def __init__(self):
        """Initialize the cognitive core."""
        logger.info("Cognitive core initializing")
        self.short_term_memory = []
        self.long_term_memory = {}
        self.active_context = {}
        self.current_plan = None
        
        # Subscribe to events
        event_bus.subscribe("event_channel", self.process_event)
        
    async def process_event(self, event: Dict[str, Any]) -> None:
        """
        Process an incoming event.
        
        Args:
            event: The event to process
        """
        event_type = event.get("type")
        logger.info(f"Processing event of type: {event_type}")
        
        # Update context with this event
        self.update_context(event)
        
        # Determine goals based on the event
        goals = self.determine_goals(event)
        
        # Create a plan for the goals
        if goals:
            await self.create_plan(goals)
            
    def update_context(self, event: Dict[str, Any]) -> None:
        """
        Update the active context with a new event.
        
        Args:
            event: The event to add to the context
        """
        # Add the event to short-term memory
        self.short_term_memory.append(event)
        
        # Keep short-term memory from growing too large
        if len(self.short_term_memory) > 20:
            self.short_term_memory.pop(0)
            
        # Extract relevant information from the event
        event_type = event.get("type")
        if event_type in self.active_context:
            # Merge with existing context
            self.active_context[event_type].append(event)
        else:
            # Create new context entry
            self.active_context[event_type] = [event]
            
    def determine_goals(self, event: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Determine goals based on an event.
        
        Args:
            event: The event to determine goals from
            
        Returns:
            A list of goals to achieve
        """
        goals = []
        event_type = event.get("type")
        
        if event_type == "command":
            # For command events, the goal is to execute the command
            goals.append({
                "type": "execute_command",
                "command": event.get("command"),
                "priority": event.get("priority", "normal")
            })
        elif event_type == "query":
            # For query events, the goal is to answer the query
            goals.append({
                "type": "answer_query",
                "query": event.get("query"),
                "priority": event.get("priority", "normal")
            })
        elif event_type == "error":
            # For error events, the goal is to handle the error
            goals.append({
                "type": "handle_error",
                "error": event.get("error"),
                "priority": "high"
            })
            
        return goals
        
    async def create_plan(self, goals: List[Dict[str, Any]]) -> None:
        """
        Create a plan to achieve a set of goals.
        
        Args:
            goals: The goals to achieve
        """
        # Sort goals by priority
        sorted_goals = sorted(goals, key=lambda g: self.priority_value(g.get("priority", "normal")))
        
        # Create a plan for each goal
        for goal in sorted_goals:
            goal_type = goal.get("type")
            logger.info(f"Creating plan for goal: {goal_type}")
            
            if goal_type == "execute_command":
                # For command execution, delegate to the central executor
                command = goal.get("command")
                if command:
                    await executor.submit(command)
            elif goal_type == "answer_query":
                # For query answering, create a query command
                query = goal.get("query")
                if query:
                    await executor.submit({
                        "type": "ask",
                        "content": query
                    })
            elif goal_type == "handle_error":
                # For error handling, create an error handling command
                error = goal.get("error")
                if error:
                    await executor.submit({
                        "type": "system",
                        "command": "handle_error",
                        "error": error
                    })
                    
    def priority_value(self, priority: str) -> int:
        """
        Convert a priority string to a numeric value.
        
        Args:
            priority: The priority string
            
        Returns:
            A numeric value for the priority (lower is higher priority)
        """
        priority_map = {
            "critical": 0,
            "high": 1,
            "normal": 2,
            "low": 3
        }
        return priority_map.get(priority.lower(), 2)
        
    def get_relevant_context(self, event_type: str) -> List[Dict[str, Any]]:
        """
        Get relevant context for an event type.
        
        Args:
            event_type: The type of event to get context for
            
        Returns:
            A list of relevant context events
        """
        return self.active_context.get(event_type, [])
        
    async def store_in_long_term_memory(self, key: str, value: Any) -> None:
        """
        Store a value in long-term memory.
        
        Args:
            key: The key to store the value under
            value: The value to store
        """
        self.long_term_memory[key] = value
        
    def retrieve_from_long_term_memory(self, key: str) -> Optional[Any]:
        """
        Retrieve a value from long-term memory.
        
        Args:
            key: The key to retrieve
            
        Returns:
            The value, or None if the key doesn't exist
        """
        return self.long_term_memory.get(key)

# Create a singleton instance
cognitive_core = CognitiveCore()