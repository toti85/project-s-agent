import logging
import asyncio
from typing import Dict, List, Any, Callable, Optional, Union
from collections import defaultdict

logger = logging.getLogger(__name__)

# Típus definíciók a jobb érthetőségért
EventHandler = Callable[[Dict[str, Any]], Any]
AsyncEventHandler = Callable[[Dict[str, Any]], asyncio.Future]
AnyEventHandler = Union[EventHandler, AsyncEventHandler]

class EventBus:
    """
    Event bus for publish/subscribe pattern communication between components.
    Allows loose coupling between components and event-driven architecture.
    """
    
    def __init__(self):
        """Initialize the event bus."""
        logger.info("Event bus initialized")
        self.subscribers: Dict[str, List[AnyEventHandler]] = defaultdict(list)
        
    async def publish(self, channel: str, event: Dict[str, Any]) -> None:
        """
        Publish an event to a channel.
        
        Args:
            channel: The channel to publish to
            event: The event data to publish
        """
        if not self.subscribers[channel]:
            logger.debug(f"No subscribers for channel {channel}")
            return
            
        logger.debug(f"Publishing event to channel {channel}: {event}")
        
        # Create tasks for all subscribers
        tasks = []
        for handler in self.subscribers[channel]:
            task = self._call_handler(handler, event)
            if task:
                tasks.append(task)
                
        # Wait for all tasks to complete if there are any
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
            
    async def _call_handler(self, handler: AnyEventHandler, event: Dict[str, Any]) -> Optional[asyncio.Task]:
        """
        Call an event handler with the event data.
        
        Args:
            handler: The handler to call
            event: The event data to pass to the handler
            
        Returns:
            A task if the handler is async, None otherwise
        """
        try:
            if asyncio.iscoroutinefunction(handler):
                # Async handler
                return asyncio.create_task(handler(event))
            else:
                # Sync handler
                handler(event)
                return None
        except Exception as e:
            logger.error(f"Error calling event handler: {str(e)}")
            return None
            
    def subscribe(self, channel: str, handler: AnyEventHandler) -> None:
        """
        Subscribe to events on a channel.
        
        Args:
            channel: The channel to subscribe to
            handler: The handler to call when an event is published to the channel
        """
        logger.debug(f"Subscribing to channel {channel}")
        self.subscribers[channel].append(handler)
        
    def unsubscribe(self, channel: str, handler: AnyEventHandler) -> None:
        """
        Unsubscribe from events on a channel.
        
        Args:
            channel: The channel to unsubscribe from
            handler: The handler to remove
        """
        if handler in self.subscribers[channel]:
            logger.debug(f"Unsubscribing from channel {channel}")
            self.subscribers[channel].remove(handler)
            
    def get_subscribers(self, channel: str) -> List[AnyEventHandler]:
        """
        Get all subscribers for a channel.
        
        Args:
            channel: The channel to get subscribers for
            
        Returns:
            The list of subscribers for the channel
        """
        return self.subscribers[channel]

# Create a singleton instance
event_bus = EventBus()