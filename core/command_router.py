import logging
import importlib
import inspect
import os
from typing import Dict, Callable, Any, List, Optional, Tuple
from core.ai_command_handler import AICommandHandler, ai_handler
from core.error_handler import error_handler
from core.event_bus import event_bus

logger = logging.getLogger(__name__)

class CommandRouter:
    def __init__(self):
        self.handlers = {}
        self.ai_handler = AICommandHandler()
        self.plugin_handlers = {}
        self.plugin_paths = []
        self.register_default_handlers()

    def register_default_handlers(self):
        # Register all supported command handlers
        self.register("ASK", self.ai_handler.handle_ask_command)
        self.register("CMD", self.ai_handler.handle_cmd_command)
        self.register("CODE", self.ai_handler.handle_code_command) 
        self.register("FILE", self.ai_handler.handle_file_command)

    def register(self, cmd_type: str, handler):
        self.handlers[cmd_type] = handler
        logger.info(f"Registered handler for command type: {cmd_type}")
        print(f"[Router] Registered handler for: {cmd_type}")
        
    def register_plugin_handler(self, plugin_id: str, cmd_type: str, handler) -> None:
        """
        Register a handler from a plugin.
        
        Args:
            plugin_id (str): The unique identifier for the plugin
            cmd_type (str): The command type this handler should process
            handler (Callable): The handler function to call
        """
        if plugin_id not in self.plugin_handlers:
            self.plugin_handlers[plugin_id] = {}
            
        self.plugin_handlers[plugin_id][cmd_type] = handler
        
        # Also register in the main handlers map for routing
        self.register(cmd_type, handler)
        
        logger.info(f"Registered plugin handler '{plugin_id}' for command type: {cmd_type}")
        print(f"[Router] Registered plugin handler '{plugin_id}' for: {cmd_type}")
        
        # Publish event about new handler registration
        asyncio.create_task(event_bus.publish("handler.registered", {
            "plugin_id": plugin_id,
            "cmd_type": cmd_type
        }))
        
    def unregister_plugin_handler(self, plugin_id: str, cmd_type: Optional[str] = None) -> bool:
        """
        Unregister a plugin handler.
        
        Args:
            plugin_id (str): The unique identifier for the plugin
            cmd_type (str, optional): The specific command type to unregister.
                                     If None, all handlers for this plugin will be unregistered.
        
        Returns:
            bool: True if the handler(s) were successfully unregistered
        """
        if plugin_id not in self.plugin_handlers:
            logger.warning(f"No handlers registered for plugin '{plugin_id}'")
            return False
            
        success = False
        
        if cmd_type is None:
            # Unregister all handlers for this plugin
            for handler_type in list(self.plugin_handlers[plugin_id].keys()):
                if handler_type in self.handlers:
                    del self.handlers[handler_type]
                    success = True
                    logger.info(f"Unregistered plugin handler '{plugin_id}' for: {handler_type}")
            
            # Remove plugin from registry
            del self.plugin_handlers[plugin_id]
            
        elif cmd_type in self.plugin_handlers[plugin_id]:
            # Unregister specific handler
            if cmd_type in self.handlers:
                del self.handlers[cmd_type]
                success = True
                logger.info(f"Unregistered plugin handler '{plugin_id}' for: {cmd_type}")
            
            # Remove from plugin registry
            del self.plugin_handlers[plugin_id][cmd_type]
            
            # Clean up empty plugin entries
            if not self.plugin_handlers[plugin_id]:
                del self.plugin_handlers[plugin_id]
        
        if success:
            # Publish event about handler unregistration
            asyncio.create_task(event_bus.publish("handler.unregistered", {
                "plugin_id": plugin_id,
                "cmd_type": cmd_type
            }))
            
        return success
            
    def add_plugin_path(self, path: str) -> None:
        """
        Add a directory to search for plugin modules.
        
        Args:
            path (str): Path to the directory containing plugin modules
        """
        if path not in self.plugin_paths:
            self.plugin_paths.append(path)
            logger.info(f"Added plugin path: {path}")
    
    async def scan_for_plugins(self) -> List[str]:
        """
        Scan registered paths for plugin modules and load them.
        
        Returns:
            List[str]: List of loaded plugin IDs
        """
        loaded_plugins = []
        
        for path in self.plugin_paths:
            if not os.path.exists(path):
                logger.warning(f"Plugin path does not exist: {path}")
                continue
                
            logger.info(f"Scanning for plugins in: {path}")
            
            # Get Python files in the directory
            for file_name in os.listdir(path):
                if file_name.endswith('.py') and not file_name.startswith('_'):
                    module_name = file_name[:-3]  # Remove .py extension
                    full_path = os.path.join(path, file_name)
                    
                    try:
                        # Dynamically import the module
                        spec = importlib.util.spec_from_file_location(module_name, full_path)
                        if spec and spec.loader:
                            module = importlib.util.module_from_spec(spec)
                            spec.loader.exec_module(module)
                            
                            # Look for handler registration
                            loaded_plugin = await self._register_handlers_from_module(module, module_name)
                            if loaded_plugin:
                                loaded_plugins.append(loaded_plugin)
                                
                    except Exception as e:
                        logger.error(f"Error loading plugin module {module_name}: {str(e)}")
        
        return loaded_plugins
    
    async def _register_handlers_from_module(self, module, module_name: str) -> Optional[str]:
        """
        Find and register handlers from a loaded module.
        
        Args:
            module: The loaded Python module
            module_name (str): The name of the module
            
        Returns:
            Optional[str]: The plugin ID if handlers were registered, None otherwise
        """
        try:
            # Check if module has a register_handlers function
            if hasattr(module, 'register_handlers'):
                plugin_id = getattr(module, 'PLUGIN_ID', module_name)
                
                # Call the registration function with this router
                await module.register_handlers(self)
                logger.info(f"Registered handlers from plugin: {plugin_id}")
                return plugin_id
                
            # Alternative: Look for a plugin class with handlers
            for name, obj in inspect.getmembers(module):
                if inspect.isclass(obj) and hasattr(obj, 'register_handlers'):
                    plugin_id = getattr(obj, 'PLUGIN_ID', name)
                    
                    # Instantiate the plugin class
                    plugin_instance = obj()
                    
                    # Call the registration method
                    await plugin_instance.register_handlers(self)
                    logger.info(f"Registered handlers from plugin class: {plugin_id}")
                    return plugin_id
                    
            return None
            
        except Exception as e:
            logger.error(f"Error registering handlers from module {module_name}: {str(e)}")
            return None

    async def route_command(self, command: dict):
        cmd_type = command.get("type")
        
        if not cmd_type:
            logger.error("Command missing 'type' field")
            return {"error": "Missing command type"}
            
        logger.info(f"Received command of type: {cmd_type}")
        print(f"[Router] Processing command: {cmd_type}")
        
        # Publish command received event
        await event_bus.publish("command.received", command)
        
        handler = self.handlers.get(cmd_type)
        if not handler:
            logger.warning(f"No handler for command type: {cmd_type}")
            return {"error": f"No handler for command type: {cmd_type}"}
            
        try:
            result = await handler(command)
            
            # Publish command completed event
            await event_bus.publish("command.completed", {
                "command": command,
                "result": result
            })
            
            return result
        except Exception as e:
            error_context = {"component": "router", "command_type": cmd_type}
            error_result = await error_handler.handle_error(e, error_context)
            
            # Publish command error event
            await event_bus.publish("command.error", {
                "command": command,
                "error": str(e)
            })
            
            return {"error": f"Command execution failed: {str(e)}"}
            
    def get_registered_command_types(self) -> List[str]:
        """Get a list of all registered command types."""
        return list(self.handlers.keys())
        
    def get_plugin_command_types(self, plugin_id: str) -> List[str]:
        """Get a list of command types registered by a specific plugin."""
        if plugin_id in self.plugin_handlers:
            return list(self.plugin_handlers[plugin_id].keys())
        return []

# Import asyncio for event publishing
import asyncio

# Create a singleton router instance
router = CommandRouter()