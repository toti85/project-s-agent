import logging
import asyncio
import json
from typing import Dict, List, Any, Optional, Set
from datetime import datetime
from core.event_bus import event_bus
from core.central_executor import executor
from core.error_handler import error_handler
from utils.performance_monitor import monitor_performance
from core.cognitive_core_langgraph import cognitive_core_langgraph, CognitiveCoreWithLangGraph

logger = logging.getLogger(__name__)

class CognitiveCore:
    """
    Cognitive core for the Project-S agent system.
    
    Responsible for:
    1. Maintaining context between commands
    2. Breaking down complex tasks into simpler steps
    3. Learning from past interactions and results
    4. Suggesting next actions based on current context
    """
      def __init__(self):
        """Initialize the cognitive core with empty context and task history."""
        # Current context of the agent's operations
        self.context = {
            "conversation": [],
            "tasks": {},
            "entities": {},
            "workspace": {},
            "session_start": datetime.now().isoformat()
        }
        
        # Task processing state
        self.active_tasks = set()
        self.completed_tasks = set()
        self.task_dependencies = {}
        self.task_results = {}
        
        # Register for events
        event_bus.subscribe("command.completed", self._on_command_completed)
        event_bus.subscribe("command.error", self._on_command_error)
        
        logger.info("Legacy CognitiveCore initialized")
    
    async def process_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a high-level task by breaking it into steps and executing them.
        
        Args:
            task (Dict[str, Any]): The high-level task specification
            
        Returns:
            Dict[str, Any]: The result of the task processing
        """
        try:
            task_id = task.get("id", f"task_{len(self.context['tasks']) + 1}")
            logger.info(f"Processing task: {task_id}")
            
            # Add to active tasks
            self.active_tasks.add(task_id)
            self.context["tasks"][task_id] = task
            
            # Break down the task into steps
            steps = await self._break_down_task(task)
            logger.info(f"Task {task_id} broken down into {len(steps)} steps")
            
            # Execute each step
            results = []
            for step_num, step in enumerate(steps, 1):
                step_id = f"{task_id}_step_{step_num}"
                logger.info(f"Executing step {step_id}: {step.get('description', '')}")
                
                # Create command from step
                command = self._create_command_from_step(step, task_context=task)
                
                # Execute the command
                try:
                    step_result = await executor.execute(command)
                    results.append({
                        "step_id": step_id,
                        "step": step,
                        "result": step_result,
                        "status": "completed"
                    })
                except Exception as e:
                    error_context = {"component": "cognitive_core", "task_id": task_id, "step_id": step_id}
                    await error_handler.handle_error(e, error_context)
                    results.append({
                        "step_id": step_id,
                        "step": step,
                        "error": str(e),
                        "status": "failed"
                    })
                    
                    # Check if this is a critical step
                    if step.get("critical", False):
                        logger.error(f"Critical step {step_id} failed, aborting task {task_id}")
                        break
            
            # Move from active to completed
            self.active_tasks.remove(task_id)
            self.completed_tasks.add(task_id)
            
            # Store the results
            task_result = {
                "task_id": task_id,
                "steps": results,
                "status": "completed",
                "completed_at": datetime.now().isoformat()
            }
            self.task_results[task_id] = task_result
            
            # Update the context with task results
            self._update_context_from_task(task_id, task_result)
            
            return task_result
            
        except Exception as e:
            logger.error(f"Error processing task: {str(e)}")
            error_context = {"component": "cognitive_core", "operation": "process_task"}
            await error_handler.handle_error(e, error_context)
            
            if task_id in self.active_tasks:
                self.active_tasks.remove(task_id)
            
            return {
                "task_id": task_id,
                "status": "failed",
                "error": str(e)
            }
    
    async def _break_down_task(self, task: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Break down a complex task into simpler steps that can be executed.
        
        Args:
            task (Dict[str, Any]): The task to break down
            
        Returns:
            List[Dict[str, Any]]: List of step definitions
        """
        task_type = task.get("type", "").lower()
        steps = []
        
        # If steps are already defined, use them
        if "steps" in task and isinstance(task["steps"], list):
            return task["steps"]
        
        # Otherwise, determine steps based on task type
        if task_type == "query":
            # Simple query task
            steps = [{
                "type": "ASK",
                "command": task.get("query", ""),
                "description": "Process query"
            }]
        
        elif task_type == "file_operation":
            # File operation task
            action = task.get("action", "")
            path = task.get("path", "")
            
            steps = [{
                "type": "FILE",
                "command": {
                    "action": action,
                    "path": path
                },
                "description": f"Perform {action} operation on {path}"
            }]
        
        elif task_type == "code_analysis":
            # Code analysis task - break into retrieve and analyze steps
            code_path = task.get("path", "")
            
            # Step 1: Read the file
            steps.append({
                "type": "FILE",
                "command": {
                    "action": "read",
                    "path": code_path
                },
                "description": f"Read code file {code_path}",
                "critical": True  # Mark as critical - if this fails, abort the task
            })
            
            # Step 2: Analyze the code
            steps.append({
                "type": "CODE",
                "command": {
                    "action": "analyze",
                    "code": "{step_1_result}"  # Will be replaced with actual result
                },
                "description": "Analyze the code",
                "depends_on": "step_1"
            })
        
        else:
            # Default to a single step that passes through the task
            steps = [{
                "type": task.get("command_type", "ASK"),
                "command": task.get("command", ""),
                "description": "Execute command"
            }]
        
        return steps
    
    def _create_command_from_step(self, step: Dict[str, Any], task_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a command object from a step definition.
        
        Args:
            step (Dict[str, Any]): The step definition
            task_context (Dict[str, Any]): The context of the parent task
            
        Returns:
            Dict[str, Any]: The command to execute
        """
        command = {
            "type": step.get("type", "ASK"),
            "command": step.get("command", "")
        }
        
        # Handle template substitution for dynamic values
        if isinstance(command["command"], str) and "{" in command["command"]:
            # Simple template substitution
            for key, value in task_context.items():
                placeholder = "{" + key + "}"
                if placeholder in command["command"]:
                    command["command"] = command["command"].replace(placeholder, str(value))
        
        # Copy any additional fields from the step
        for key, value in step.items():
            if key not in ["type", "command", "description", "critical", "depends_on"]:
                command[key] = value
        
        return command
    
    def _update_context_from_task(self, task_id: str, task_result: Dict[str, Any]) -> None:
        """
        Update the context with information from a completed task.
        
        Args:
            task_id (str): The ID of the completed task
            task_result (Dict[str, Any]): The result of the task execution
        """
        # Store the task result
        self.context["tasks"][task_id] = {
            **self.context["tasks"].get(task_id, {}),
            "result": task_result,
            "status": task_result.get("status", "unknown")
        }
        
        # Extract entities if available
        for step_result in task_result.get("steps", []):
            result = step_result.get("result", {})
            
            # For code analysis, store code entities
            if step_result.get("step", {}).get("type") == "CODE" and "analysis" in result:
                # Extract entities from analysis (simplified example)
                self._extract_entities_from_analysis(result.get("analysis", ""))
    
    def _extract_entities_from_analysis(self, analysis: str) -> None:
        """
        Extract entities from code analysis results and add to context.
        
        Args:
            analysis (str): The code analysis text
        """
        # Simple entity extraction (in a real system, this would be more sophisticated)
        # Example: Look for mentions of classes, functions, variables
        # This is a placeholder implementation
        entities = set()
        
        # Very naive extraction for demonstration purposes only
        lines = analysis.split("\n")
        for line in lines:
            line = line.strip()
            # Look for mentions of classes
            if "class " in line:
                parts = line.split("class ")[1].split("(")[0].split(":")
                class_name = parts[0].strip()
                entities.add(("class", class_name))
            
            # Look for mentions of functions
            if "function " in line or "method " in line:
                for marker in ["function ", "method "]:
                    if marker in line:
                        parts = line.split(marker)[1].split("(")[0]
                        func_name = parts.strip()
                        entities.add(("function", func_name))
        
        # Add entities to context
        for entity_type, entity_name in entities:
            if entity_type not in self.context["entities"]:
                self.context["entities"][entity_type] = []
            
            if entity_name not in self.context["entities"][entity_type]:
                self.context["entities"][entity_type].append(entity_name)
    
    async def _on_command_completed(self, event_data: Any) -> None:
        """
        Event handler for command.completed events.
        Update context based on command results.
        
        Args:
            event_data (Any): The event data containing command and result
        """
        if not isinstance(event_data, dict):
            return
            
        command = event_data.get("command", {})
        result = event_data.get("result", {})
        
        # Add to conversation history
        self.context["conversation"].append({
            "timestamp": datetime.now().isoformat(),
            "type": "command",
            "command": command,
            "result": result
        })
        
        # Update workspace information for FILE commands
        if command.get("type") == "FILE":
            self._update_workspace_info(command, result)
    
    async def _on_command_error(self, event_data: Any) -> None:
        """
        Event handler for command.error events.
        Update context with error information.
        
        Args:
            event_data (Any): The event data containing command and error
        """
        if not isinstance(event_data, dict):
            return
            
        command = event_data.get("command", {})
        error = event_data.get("error", "Unknown error")
        
        # Add to conversation history
        self.context["conversation"].append({
            "timestamp": datetime.now().isoformat(),
            "type": "error",
            "command": command,
            "error": error
        })
    
    def _update_workspace_info(self, command: Dict[str, Any], result: Dict[str, Any]) -> None:
        """
        Update workspace information based on file operations.
        
        Args:
            command (Dict[str, Any]): The FILE command
            result (Dict[str, Any]): The result of the command
        """
        # Extract command details
        cmd_obj = command.get("command", {})
        if isinstance(cmd_obj, str):
            # Try to parse JSON string
            try:
                cmd_obj = json.loads(cmd_obj)
            except:
                cmd_obj = {"action": "unknown", "path": cmd_obj}
        
        action = cmd_obj.get("action", "")
        path = cmd_obj.get("path", "")
        
        if not path:
            return
            
        # Update workspace based on the action
        if action == "read" and "content" in result:
            self.context["workspace"][path] = {
                "last_read": datetime.now().isoformat(),
                "content_preview": result["content"][:100] + "..." if len(result["content"]) > 100 else result["content"]
            }
        elif action == "write":
            self.context["workspace"][path] = {
                "last_write": datetime.now().isoformat()
            }
        elif action == "list" and "files" in result:
            directory = path
            for file in result["files"]:
                file_path = f"{directory}/{file}" if directory != "." else file
                if file_path not in self.context["workspace"]:
                    self.context["workspace"][file_path] = {
                        "discovered": datetime.now().isoformat()
                    }
    
    @monitor_performance
    async def suggest_next_action(self) -> Optional[Dict[str, Any]]:
        """
        Suggest the next action based on current context.
        
        Returns:
            Optional[Dict[str, Any]]: A suggested action or None
        """
        # This is a simple implementation that could be expanded with more intelligence
        
        # If there are active tasks, don't suggest anything
        if self.active_tasks:
            return None
        
        # Analyze recent conversation
        recent_items = self.context["conversation"][-5:] if len(self.context["conversation"]) > 5 else self.context["conversation"]
        
        # Simple rule-based suggestions
        for item in reversed(recent_items):
            if item["type"] == "command" and item["command"].get("type") == "ASK":
                # After an ASK command, suggest a follow-up
                return {
                    "type": "suggestion",
                    "action": {
                        "type": "ASK",
                        "command": "Would you like me to explain this in more detail?"
                    },
                    "confidence": 0.7,
                    "reason": "Follow-up to previous query"
                }
            
            if item["type"] == "command" and item["command"].get("type") == "FILE" and item["command"].get("action") == "read":
                # After reading a file, suggest analysis
                return {
                    "type": "suggestion",
                    "action": {
                        "type": "CODE",
                        "command": {
                            "action": "analyze",
                            "code": "The previously read file content"
                        }
                    },
                    "confidence": 0.8,
                    "reason": "Analyze the file you just read"
                }
        
        return None
    
    def get_context(self) -> Dict[str, Any]:
        """
        Get the current context.
        
        Returns:
            Dict[str, Any]: The current context
        """
        return self.context
    
    def clear_context(self) -> None:
        """Clear the current context."""
        self.context = {
            "conversation": [],
            "tasks": {},
            "entities": {},
            "workspace": {},
            "session_start": datetime.now().isoformat()
        }
        self.active_tasks = set()
        self.completed_tasks = set()
        self.task_dependencies = {}
        self.task_results = {}
        
        logger.info("Context cleared")

# Create a default cognitive core instance
legacy_cognitive_core = CognitiveCore()

# Create the enhanced LangGraph-based cognitive core
# This is now the default cognitive core used throughout the system
cognitive_core = cognitive_core_langgraph