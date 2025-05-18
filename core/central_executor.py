import asyncio
import logging
import time
from typing import Dict, Any, Optional, Callable, Awaitable
from core.command_router import router
from core.event_bus import event_bus
from utils.performance_monitor import monitor_performance
from utils.structured_logger import log_command_event

logger = logging.getLogger(__name__)

class CentralExecutor:
    """
    Central executor for the Project-S system.
    
    Handles command execution through both:
    1. Traditional queue-based processing
    2. Event-driven publish/subscribe pattern
    """
    
    def __init__(self):
        """Initialize the central executor with an empty command queue."""
        self.queue = asyncio.Queue()
        self.running = False
        self._event_handlers = {}
        self._hooks = {
            "pre_execute": [],
            "post_execute": [],
            "error": []
        }
        logger.info("CentralExecutor initialized")
        
        # Register with the event bus for system events
        event_bus.subscribe("command.submitted", self._on_command_submitted)
    
    async def initialize(self):
        """
        Initialize the executor subsystem.
        This method is called during system startup.
        """
        logger.info("CentralExecutor initialization")
        # Perform any necessary initialization tasks
        # Currently, basic initialization is already done in __init__
        return True
    
    async def submit(self, command: Dict[str, Any]) -> None:
        """
        Submit a command to the queue for processing.
        
        Args:
            command (Dict[str, Any]): The command to process
        """
        logger.info(f"Command submitted: {command.get('type', 'unknown')}")
        await self.queue.put(command)
        
        # Publish an event that a command was submitted (event-driven approach)
        await event_bus.publish("command.submitted", command)
    
    @monitor_performance
    async def execute(self, command: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a command immediately without going through the queue.
        
        Args:
            command (Dict[str, Any]): The command to execute
            
        Returns:
            Dict[str, Any]: The result of the command execution
        """
        command_id = command.get("id", str(time.time()))
        command_type = command.get("type", "UNKNOWN")
        log_command_event(
            event="command_started",
            command_id=command_id,
            command_type=command_type,
            status="started",
            context={"command": command}
        )
        start_time = time.time()
        try:
            # Run pre-execution hooks
            for hook in self._hooks["pre_execute"]:
                await hook(command)
            
            # Execute the command through the router
            logger.info(f"Executing command: {command.get('type', 'unknown')}")
            result = await router.route_command(command)
            
            # Run post-execution hooks
            for hook in self._hooks["post_execute"]:
                await hook(command, result)
            
            # Publish event for command execution result
            await event_bus.publish("command.executed", {"command": command, "result": result})
            
            duration = time.time() - start_time
            log_command_event(
                event="command_completed",
                command_id=command_id,
                command_type=command_type,
                status="success",
                context={"result": result, "duration": duration}
            )
            
            return result
        except Exception as e:
            duration = time.time() - start_time
            log_command_event(
                event="command_failed",
                command_id=command_id,
                command_type=command_type,
                status="error",
                context={"error": str(e), "duration": duration}
            )
            logger.error(f"Error executing command: {str(e)}")
            error_data = {"command": command, "error": str(e)}
            
            # Run error hooks
            for hook in self._hooks["error"]:
                await hook(error_data)
            
            # Publish error event
            await event_bus.publish("command.error", error_data)
            
            # Re-raise or return error result
            return {"status": "error", "message": str(e)}
    
    async def run(self) -> None:
        """
        Start processing commands from the queue in an infinite loop.
        This maintains backward compatibility with the original implementation.
        """
        self.running = True
        logger.info("CentralExecutor started processing commands")
        
        try:
            while self.running:
                # Get the next command from the queue
                command = await self.queue.get()
                
                # Execute it
                await self.execute(command)
                
                # Mark the task as done
                self.queue.task_done()
        except asyncio.CancelledError:
            logger.info("CentralExecutor was cancelled")
            self.running = False
        except Exception as e:
            logger.error(f"Error in CentralExecutor run loop: {str(e)}")
            self.running = False
            raise
    
    def register_hook(self, hook_type: str, callback: Callable) -> None:
        """
        Register a hook to be called during command processing.
        
        Args:
            hook_type (str): Type of hook - 'pre_execute', 'post_execute', or 'error'
            callback (Callable): The function to call
        """
        if hook_type in self._hooks:
            self._hooks[hook_type].append(callback)
            logger.info(f"Registered {hook_type} hook")
        else:
            logger.warning(f"Unknown hook type: {hook_type}")
    
    def unregister_hook(self, hook_type: str, callback: Callable) -> bool:
        """
        Unregister a previously registered hook.
        
        Args:
            hook_type (str): Type of hook
            callback (Callable): The function to remove
            
        Returns:
            bool: True if the hook was found and removed, False otherwise
        """
        if hook_type in self._hooks and callback in self._hooks[hook_type]:
            self._hooks[hook_type].remove(callback)
            logger.info(f"Unregistered {hook_type} hook")
            return True
        return False
    
    async def _on_command_submitted(self, command: Dict[str, Any]) -> None:
        """
        Event handler for command.submitted events.
        This demonstrates the event-driven approach.
        
        Args:
            command (Dict[str, Any]): The submitted command
        """
        logger.debug(f"Event received: command.submitted - {command.get('type', 'unknown')}")
        # This method can be extended with additional logic as needed

# Create a singleton instance
executor = CentralExecutor()