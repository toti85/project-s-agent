import logging
import asyncio
import json
import os
from typing import Dict, List, Any, Optional, Set, Tuple, Union, Callable
from datetime import datetime
from pydantic import BaseModel, Field

from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langgraph.graph.message import add_messages

from core.event_bus import event_bus
from core.central_executor import executor
from core.error_handler import error_handler
from core.ai_command_handler import AICommandHandler
from core.multi_model_integration import multi_model_manager
from utils.performance_monitor import monitor_performance
from integrations.langgraph_integration import langgraph_integrator, GraphState
from integrations.langgraph_state_manager import state_manager
from integrations.langgraph_state_enhanced import create_state_linked_workflow

logger = logging.getLogger(__name__)

# Define structured state classes for cognitive workflows
class Memory(BaseModel):
    conversation: List[Dict[str, Any]] = Field(default_factory=list)
    entities: Dict[str, List[str]] = Field(default_factory=dict)
    context: Dict[str, Any] = Field(default_factory=dict)

class Task(BaseModel):
    id: str
    description: str
    status: str = "pending"  # pending, in_progress, completed, failed
    steps: List[Dict[str, Any]] = Field(default_factory=list)
    current_step: Optional[int] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[Dict[str, Any]] = None

class CognitiveGraphState(BaseModel):
    memory: Memory = Field(default_factory=Memory)
    tasks: Dict[str, Task] = Field(default_factory=dict)
    current_task_id: Optional[str] = None
    active_tasks: List[str] = Field(default_factory=list)
    completed_tasks: List[str] = Field(default_factory=list)
    failed_tasks: List[str] = Field(default_factory=list)
    messages: List[Dict[str, Any]] = Field(default_factory=list)
    next_action: Optional[Dict[str, Any]] = None
    session_start: str = Field(default_factory=lambda: datetime.now().isoformat())
    workspace: Dict[str, Any] = Field(default_factory=dict)
    model_config: Dict[str, Any] = Field(default_factory=dict)
    status: str = "idle"  # idle, planning, executing, waiting, complete, error

class CognitiveCoreGraph:
    """
    Graph-based implementation of the cognitive core using LangGraph.
    
    This class implements the graph-based workflow for cognitive processing,
    breaking complex tasks into steps and executing them in a structured manner.
    """
    
    def __init__(self, model_config: Optional[Dict[str, Any]] = None):
        """
        Initialize the cognitive graph with optional model configuration.
        
        Args:
            model_config (Dict[str, Any], optional): Configuration for the LLM models used
                in different nodes of the graph
        """
        self.model_config = model_config or {}
        self.ai_handler = AICommandHandler()
        
        # Define the graph nodes
        self.nodes = {
            "planner": self._create_planner_node(),
            "executor": self._create_executor_node(),
            "analyser": self._create_analyser_node(),
            "memory_updater": self._create_memory_updater_node(),
            "error_handler": self._create_error_handler_node(),
            "reflector": self._create_reflector_node()
        }
        
        # Build the cognitive graph
        self.graph = self._build_graph()
        logger.info("CognitiveCoreGraph initialized with LangGraph integration")
        
    def _create_planner_node(self) -> Callable:
        """Create the planner node that breaks down tasks into steps."""
        async def planner(state: CognitiveGraphState) -> CognitiveGraphState:
            logger.info("Planning task execution")
            
            # If there's no current task, check if we have any active tasks
            if not state.current_task_id and state.active_tasks:
                state.current_task_id = state.active_tasks[0]
                
            if not state.current_task_id:
                logger.warning("No task to plan")
                state.status = "idle"
                return state
                
            # Get the current task
            task = state.tasks.get(state.current_task_id)
            if not task:
                logger.error(f"Task {state.current_task_id} not found")
                state.status = "error"
                return state
                
            # Update task status
            task.status = "in_progress"
            
            # If the task already has steps defined, use them
            if task.steps:
                logger.info(f"Task {task.id} already has {len(task.steps)} steps defined")
                # Set the current step to the first one if not already set
                if task.current_step is None and task.steps:
                    task.current_step = 0
                state.status = "executing"
                return state
                
            # Use an appropriate LLM to break down the task into steps
            # This is where we'd use a specialized planning model
            try:
                planning_result = await self._break_down_task(task.description)
                
                # Process the planning result
                if planning_result and "steps" in planning_result:
                    task.steps = planning_result["steps"]
                    # Initialize current step
                    task.current_step = 0 if task.steps else None
                    
                    state.status = "executing"
                    logger.info(f"Task {task.id} broken down into {len(task.steps)} steps")
                else:
                    logger.warning(f"Planning failed for task {task.id}: {planning_result}")
                    # Create a single default step if planning failed
                    task.steps = [{
                        "type": "ASK",
                        "command": task.description,
                        "description": "Execute task as a direct question"
                    }]
                    task.current_step = 0
                    
            except Exception as e:
                logger.error(f"Error planning task {task.id}: {str(e)}")
                error_context = {"component": "cognitive_core_graph", "operation": "planner"}
                await error_handler.handle_error(e, error_context)
                
                # Set error and change status
                task.error = {"message": str(e), "timestamp": datetime.now().isoformat()}
                task.status = "failed"
                state.status = "error"
                
                if state.current_task_id in state.active_tasks:
                    state.active_tasks.remove(state.current_task_id)
                state.failed_tasks.append(state.current_task_id)
                
            return state
        
        return planner
        
    def _create_executor_node(self) -> Callable:
        """Create the executor node that executes individual task steps."""
        async def executor(state: CognitiveGraphState) -> CognitiveGraphState:
            logger.info("Executing task step")
            
            # Check if we have a current task
            if not state.current_task_id or state.current_task_id not in state.tasks:
                logger.warning("No current task to execute")
                state.status = "idle"
                return state
                
            # Get the current task
            task = state.tasks[state.current_task_id]
            
            # Check if we have a current step to execute
            if task.current_step is None or task.current_step >= len(task.steps):
                logger.info(f"No more steps to execute for task {task.id}")
                task.status = "completed"
                
                if state.current_task_id in state.active_tasks:
                    state.active_tasks.remove(state.current_task_id)
                state.completed_tasks.append(state.current_task_id)
                
                # Clear current task
                state.current_task_id = None
                state.status = "idle"
                
                return state
                
            # Get the current step
            current_step = task.steps[task.current_step]
            
            try:
                # Execute the step
                logger.info(f"Executing step {task.current_step + 1}/{len(task.steps)}: {current_step.get('description', '')}")
                
                # Create command from step
                command = self._create_command_from_step(current_step)
                
                # Execute the command using the AICommandHandler
                cmd_type = command.get("type", "ASK").upper()
                
                # Route to appropriate handler based on type
                result = None
                if cmd_type == "ASK":
                    result = await self.ai_handler.handle_ask_command(command)
                elif cmd_type == "CMD":
                    result = await self.ai_handler.handle_cmd_command(command)
                elif cmd_type == "CODE":
                    result = await self.ai_handler.handle_code_command(command)
                elif cmd_type == "FILE":
                    result = await self.ai_handler.handle_file_command(command)
                else:
                    # Use the process_json_command for other command types
                    result = await self.ai_handler.process_json_command(command)
                
                # Update step with result
                current_step["result"] = result
                current_step["status"] = "completed"
                current_step["completed_at"] = datetime.now().isoformat()
                
                # Move to the next step
                task.current_step += 1
                
                # Add to conversation history
                state.memory.conversation.append({
                    "timestamp": datetime.now().isoformat(),
                    "type": "command",
                    "command": command,
                    "result": result
                })
                
                # Update state status
                if task.current_step >= len(task.steps):
                    # Task is completed
                    task.status = "completed"
                    task.result = {
                        "steps": task.steps,
                        "completed_at": datetime.now().isoformat()
                    }
                    
                    if state.current_task_id in state.active_tasks:
                        state.active_tasks.remove(state.current_task_id)
                    state.completed_tasks.append(state.current_task_id)
                    
                    # Clear current task and go to idle state
                    state.current_task_id = None
                    state.status = "idle"
                else:
                    # More steps to execute
                    state.status = "executing"
                
            except Exception as e:
                logger.error(f"Error executing step {task.current_step} of task {task.id}: {str(e)}")
                error_context = {"component": "cognitive_core_graph", "operation": "executor"}
                await error_handler.handle_error(e, error_context)
                
                # Update step with error
                current_step["status"] = "failed"
                current_step["error"] = str(e)
                current_step["failed_at"] = datetime.now().isoformat()
                
                # Check if this is a critical step
                if current_step.get("critical", False):
                    task.status = "failed"
                    task.error = {
                        "message": f"Critical step {task.current_step} failed: {str(e)}",
                        "timestamp": datetime.now().isoformat()
                    }
                    
                    if state.current_task_id in state.active_tasks:
                        state.active_tasks.remove(state.current_task_id)
                    state.failed_tasks.append(state.current_task_id)
                    
                    # Clear current task and set error state
                    state.current_task_id = None
                    state.status = "error"
                else:
                    # Non-critical step, move to next
                    task.current_step += 1
                    state.status = "executing"
                    
                    # Add error to conversation history
                    state.memory.conversation.append({
                        "timestamp": datetime.now().isoformat(),
                        "type": "error",
                        "command": command,
                        "error": str(e)
                    })
            
            return state
                
        return executor
        
    def _create_analyser_node(self) -> Callable:
        """Create the analyser node that processes execution results."""
        async def analyser(state: CognitiveGraphState) -> CognitiveGraphState:
            logger.info("Analysing execution results")
            
            # Check if we have a completed task to analyze
            if not state.completed_tasks:
                # Nothing to analyze
                return state
                
            # Get the most recently completed task
            latest_completed_task_id = state.completed_tasks[-1]
            task = state.tasks.get(latest_completed_task_id)
            
            if not task or not task.result:
                return state
                
            try:
                # Extract relevant information from the task result
                for step in task.steps:
                    if not step.get("result"):
                        continue
                        
                    # For code analysis steps, extract entities
                    if step.get("type") == "CODE" and step.get("command", {}).get("action") == "analyze":
                        analysis_result = step.get("result", {}).get("analysis", {})
                        if analysis_result:
                            self._extract_entities_from_analysis(analysis_result, state.memory.entities)
                    
                    # For file operations, update workspace information
                    if step.get("type") == "FILE":
                        self._update_workspace_info(step.get("command", {}), step.get("result", {}), state.workspace)
                
            except Exception as e:
                logger.error(f"Error analysing results: {str(e)}")
                error_context = {"component": "cognitive_core_graph", "operation": "analyser"}
                await error_handler.handle_error(e, error_context)
            
            return state
        
        return analyser
        
    def _create_memory_updater_node(self) -> Callable:
        """Create the memory updater node to consolidate information into memory."""
        async def memory_updater(state: CognitiveGraphState) -> CognitiveGraphState:
            logger.info("Updating memory with new information")
            
            # Currently this is a simple implementation that could be expanded
            # with more sophisticated memory management using vector stores or similar
            
            # Ensure conversation doesn't grow too large
            max_conversation_items = 100
            if len(state.memory.conversation) > max_conversation_items:
                state.memory.conversation = state.memory.conversation[-max_conversation_items:]
                
            return state
        
        return memory_updater
        
    def _create_error_handler_node(self) -> Callable:
        """Create the error handler node for graceful recovery from errors."""
        async def error_handler_node(state: CognitiveGraphState) -> CognitiveGraphState:
            logger.info("Handling errors in cognitive workflow")
            
            # Check if we're in an error state
            if state.status != "error":
                return state
                
            # Reset state to idle
            state.status = "idle"
            
            # If there's a current task with an error, try to recover
            if state.current_task_id and state.current_task_id in state.tasks:
                task = state.tasks[state.current_task_id]
                
                if task.status == "failed":
                    # Log the error
                    logger.error(f"Task {task.id} failed: {task.error.get('message') if task.error else 'Unknown error'}")
                    
                    # Add to failed tasks if not already there
                    if state.current_task_id not in state.failed_tasks:
                        state.failed_tasks.append(state.current_task_id)
                        
                    # Remove from active tasks if present
                    if state.current_task_id in state.active_tasks:
                        state.active_tasks.remove(state.current_task_id)
                        
                    # Clear current task
                    state.current_task_id = None
            
            return state
        
        return error_handler_node
        
    def _create_reflector_node(self) -> Callable:
        """Create the reflector node that suggests next actions."""
        async def reflector(state: CognitiveGraphState) -> CognitiveGraphState:
            logger.info("Reflecting on state and suggesting next actions")
            
            # Only suggest if we're idle and not actively working on tasks
            if state.status != "idle" or state.current_task_id:
                return state
                
            try:
                # Analyze recent conversation
                recent_items = state.memory.conversation[-5:] if len(state.memory.conversation) > 5 else state.memory.conversation
                
                # Simple rule-based suggestions
                for item in reversed(recent_items):
                    if item.get("type") == "command" and item.get("command", {}).get("type") == "ASK":
                        # After an ASK command, suggest a follow-up
                        state.next_action = {
                            "type": "suggestion",
                            "action": {
                                "type": "ASK",
                                "command": "Would you like me to explain this in more detail?"
                            },
                            "confidence": 0.7,
                            "reason": "Follow-up to previous query"
                        }
                        break
                    
                    if item.get("type") == "command" and item.get("command", {}).get("type") == "FILE" and item.get("command", {}).get("action") == "read":
                        # After reading a file, suggest analysis
                        state.next_action = {
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
                        break
                
            except Exception as e:
                logger.error(f"Error in reflection: {str(e)}")
                error_context = {"component": "cognitive_core_graph", "operation": "reflector"}
                await error_handler.handle_error(e, error_context)
            
            return state
        
        return reflector
        
    def _build_graph(self) -> StateGraph:
        """Build the cognitive processing graph with all nodes and connections."""
        # Create a new state graph with our state type
        graph = StateGraph(CognitiveGraphState)
        
        # Add all nodes
        for name, node_func in self.nodes.items():
            graph.add_node(name, node_func)
        
        # Define the edges and flow
        graph.add_edge("planner", "executor")
        graph.add_edge("executor", "analyser")
        graph.add_edge("analyser", "memory_updater")
        graph.add_edge("memory_updater", "reflector")
        graph.add_edge("reflector", END)
        
        # Add conditional edges
        graph.add_conditional_edges(
            "planner",
            lambda state: "error_handler" if state.status == "error" else "executor"
        )
        
        graph.add_conditional_edges(
            "executor",
            lambda state: "error_handler" if state.status == "error" else "analyser"
        )
        
        graph.add_edge("error_handler", "reflector")
        
        # Set the entry point
        graph.set_entry_point("planner")
        
        # Compile the graph
        return graph.compile()
          async def _break_down_task(self, task_description: str) -> Dict[str, Any]:
        """
        Use an LLM to break down a complex task into simpler steps.
        
        Args:
            task_description (str): Description of the task to break down
            
        Returns:
            Dict[str, Any]: Task breakdown with steps
        """
        prompt = f"""
        Break down the following task into a series of simple steps that can be executed:
        
        TASK: {task_description}
        
        For each step, include:
        1. A command type (ASK, CMD, CODE, FILE)
        2. The specific command details
        3. A description of what the step does
        
        Format your response as JSON with the following structure:
        {{
            "steps": [
                {{
                    "type": "COMMAND_TYPE",
                    "command": "command_text_or_object",
                    "description": "Step description"
                }},
                ...
            ]
        }}
        """
        
        try:
            # Use the specialized planning model from multi_model_manager
            response = await multi_model_manager.execute_task(
                task_type="planning",
                prompt=prompt
            )
            
            if response and response.get("status") == "success" and "response" in response:
                # Try to extract JSON from the response
                response_text = response["response"]
                
                # Find JSON block in the text if not pure JSON
                try:
                    # Try to parse the entire response as JSON
                    result = json.loads(response_text)
                except json.JSONDecodeError:
                    # Try to extract a JSON block using regex
                    import re
                    json_pattern = r'```(?:json)?\s*([\s\S]*?)\s*```|(\{[\s\S]*\})'
                    matches = re.search(json_pattern, response_text)
                    
                    if matches:
                        json_str = matches.group(1) or matches.group(2)
                        try:
                            result = json.loads(json_str)
                        except json.JSONDecodeError:
                            logger.error("Could not parse JSON from LLM response")
                            return {"error": "Invalid task breakdown format"}
                    else:
                        logger.error("No JSON found in LLM response")
                        return {"error": "Invalid task breakdown format"}
                
                logger.info(f"Task broken down using {response.get('model_used', 'unknown')} model")
                return result
            else:
                # Fall back to using the AICommandHandler if the specialized model fails
                fallback_response = await self.ai_handler.handle_ask_command({"query": prompt})
                
                if fallback_response and "response" in fallback_response:
                    # Process the response as before
                    response_text = fallback_response["response"]
                    
                    try:
                        result = json.loads(response_text)
                    except json.JSONDecodeError:
                        # Try to extract a JSON block using regex
                        import re
                        json_pattern = r'```(?:json)?\s*([\s\S]*?)\s*```|(\{[\s\S]*\})'
                        matches = re.search(json_pattern, response_text)
                        
                        if matches:
                            json_str = matches.group(1) or matches.group(2)
                            try:
                                result = json.loads(json_str)
                            except json.JSONDecodeError:
                                logger.error("Could not parse JSON from LLM response")
                                return {"error": "Invalid task breakdown format"}
                        else:
                            logger.error("No JSON found in LLM response")
                            return {"error": "Invalid task breakdown format"}
                    
                    logger.info("Task broken down using fallback model")
                    return result
                else:
                    logger.error("Invalid response from LLM")
                    return {"error": "Invalid response from LLM"}
                
        except Exception as e:
            logger.error(f"Error breaking down task: {str(e)}")
            return {"error": str(e)}
            
    def _create_command_from_step(self, step: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a command object from a step definition.
        
        Args:
            step (Dict[str, Any]): The step definition
            
        Returns:
            Dict[str, Any]: The command to execute
        """
        command = {
            "type": step.get("type", "ASK")
        }
        
        # Handle different command formats
        if "command" in step:
            cmd_content = step["command"]
            
            if isinstance(cmd_content, dict):
                # For structured commands like {"action": "read", "path": "file.txt"}
                command.update(cmd_content)
            else:
                # For string commands
                if command["type"] == "ASK":
                    command["query"] = cmd_content
                elif command["type"] == "CMD":
                    command["cmd"] = cmd_content
                else:
                    # Generic handling
                    command["command"] = cmd_content
        
        # Copy any additional fields from the step
        for key, value in step.items():
            if key not in ["type", "command", "description", "critical", "depends_on", "result", "status"]:
                command[key] = value
        
        return command
            
    def _extract_entities_from_analysis(self, analysis: Dict[str, Any], entities: Dict[str, List[str]]) -> None:
        """
        Extract entities from code analysis results and add to entities dict.
        
        Args:
            analysis (Dict[str, Any]): The code analysis data
            entities (Dict[str, List[str]]): The entities dictionary to update
        """
        # Extract functions
        if "functions" in analysis:
            if "function" not in entities:
                entities["function"] = []
            
            for func in analysis["functions"]:
                func_name = func.get("name", "")
                if func_name and func_name not in entities["function"]:
                    entities["function"].append(func_name)
        
        # Extract classes
        if "classes" in analysis:
            if "class" not in entities:
                entities["class"] = []
            
            for cls in analysis["classes"]:
                class_name = cls.get("name", "")
                if class_name and class_name not in entities["class"]:
                    entities["class"].append(class_name)
        
        # Extract variables
        if "variables" in analysis:
            if "variable" not in entities:
                entities["variable"] = []
            
            for var in analysis["variables"]:
                var_name = var.get("name", "")
                if var_name and var_name not in entities["variable"]:
                    entities["variable"].append(var_name)
                    
        # Extract imports
        if "imports" in analysis:
            if "import" not in entities:
                entities["import"] = []
            
            for imp in analysis["imports"]:
                import_name = imp.get("name", "")
                if import_name and import_name not in entities["import"]:
                    entities["import"].append(import_name)
    
    def _update_workspace_info(self, command: Dict[str, Any], result: Dict[str, Any], workspace: Dict[str, Any]) -> None:
        """
        Update workspace information based on file operations.
        
        Args:
            command (Dict[str, Any]): The FILE command
            result (Dict[str, Any]): The result of the command
            workspace (Dict[str, Any]): The workspace dictionary to update
        """
        # Extract command details
        cmd_obj = command
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
            workspace[path] = {
                "last_read": datetime.now().isoformat(),
                "content_preview": result["content"][:100] + "..." if len(result["content"]) > 100 else result["content"]
            }
        elif action == "write":
            workspace[path] = {
                "last_write": datetime.now().isoformat()
            }
        elif action == "list" and "files" in result:
            directory = path
            for file in result["files"]:
                file_path = f"{directory}/{file}" if directory != "." else file
                if file_path not in workspace:
                    workspace[file_path] = {
                        "discovered": datetime.now().isoformat()
                    }

class CognitiveCoreWithLangGraph:
    """
    Enhanced cognitive core for Project-S using LangGraph.
    
    This implementation replaces the linear task processing with a graph-based
    workflow that can handle complex tasks with specialized models.
    """
      def __init__(self, model_config: Optional[Dict[str, Any]] = None):
        """
        Initialize the cognitive core with LangGraph integration.
        
        Args:
            model_config (Dict[str, Any], optional): Configuration for which LLM models
                should be used for different cognitive tasks
        """
        # Load model configuration if not provided
        if model_config is None:
            config_path = os.path.join("config", "multi_model_config.json")
            if os.path.exists(config_path):
                try:
                    with open(config_path, 'r') as f:
                        model_config = json.load(f)
                    logger.info(f"Loaded model configuration from {config_path}")
                except Exception as e:
                    logger.error(f"Error loading model configuration: {str(e)}")
                    model_config = {}
        
        # Initialize the multi-model manager with our config
        if os.path.exists(os.path.join("config", "multi_model_config.json")):
            multi_model_manager._load_config(os.path.join("config", "multi_model_config.json"))
        
        # Initialize the core graph
        self.core_graph = CognitiveCoreGraph(model_config)
        
        # Store persistent state
        self.context = {
            "conversation": [],
            "tasks": {},
            "entities": {},
            "workspace": {},
            "session_start": datetime.now().isoformat()
        }
        
        # Task tracking
        self.active_tasks = set()
        self.completed_tasks = set()
        self.task_dependencies = {}
        self.task_results = {}
        
        # Register for events
        event_bus.subscribe("command.completed", self._on_command_completed)
        event_bus.subscribe("command.error", self._on_command_error)
        
        logger.info("CognitiveCoreWithLangGraph initialized with multi-model support")
    
    async def process_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a high-level task using a LangGraph workflow.
        
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
            
            # Create initial state for the workflow
            initial_state = CognitiveGraphState(
                memory=Memory(
                    conversation=self.context["conversation"],
                    entities=self.context["entities"],
                    context={"task": task}
                ),
                tasks={
                    task_id: Task(
                        id=task_id,
                        description=task.get("description", str(task))
                    )
                },
                current_task_id=task_id,
                active_tasks=[task_id],
                workspace=self.context["workspace"],
                model_config=self.core_graph.model_config,
                status="planning"
            )
            
            # Create a LangGraph workflow for this task
            workflow_name = f"task_{task_id}_workflow"
            
            # Set up the workflow to use the core graph
            final_state = await self.core_graph.graph.invoke(initial_state)
            
            # Extract results from the final state
            task_result = {
                "task_id": task_id,
                "status": "completed",
                "completed_at": datetime.now().isoformat()
            }
            
            # Include task-specific results if available
            if task_id in final_state.tasks:
                task_obj = final_state.tasks[task_id]
                task_result["steps"] = task_obj.steps
                if task_obj.result:
                    task_result["result"] = task_obj.result
                if task_obj.error:
                    task_result["error"] = task_obj.error
                    task_result["status"] = "failed"
            
            # Store the results
            self.task_results[task_id] = task_result
            
            # Update tracking sets
            self.active_tasks.discard(task_id)
            if task_result["status"] == "completed":
                self.completed_tasks.add(task_id)
            
            # Update the context
            self._update_context_from_state(final_state)
            
            return task_result
            
        except Exception as e:
            logger.error(f"Error processing task with LangGraph: {str(e)}")
            error_context = {"component": "cognitive_core_langgraph", "operation": "process_task"}
            await error_handler.handle_error(e, error_context)
            
            if task_id in self.active_tasks:
                self.active_tasks.remove(task_id)
            
            return {
                "task_id": task_id,
                "status": "failed",
                "error": str(e)
            }
    
    def _update_context_from_state(self, state: CognitiveGraphState) -> None:
        """
        Update the persistent context with information from a workflow state.
        
        Args:
            state (CognitiveGraphState): The final state of a workflow
        """
        # Update conversation history
        if state.memory and state.memory.conversation:
            self.context["conversation"] = state.memory.conversation
        
        # Update entities
        if state.memory and state.memory.entities:
            for entity_type, entities in state.memory.entities.items():
                if entity_type not in self.context["entities"]:
                    self.context["entities"][entity_type] = []
                
                for entity in entities:
                    if entity not in self.context["entities"][entity_type]:
                        self.context["entities"][entity_type].append(entity)
        
        # Update workspace info
        if state.workspace:
            self.context["workspace"].update(state.workspace)
        
        # Update tasks
        for task_id, task in state.tasks.items():
            self.context["tasks"][task_id] = {
                "id": task.id,
                "description": task.description,
                "status": task.status,
                "result": task.result
            }
    
    async def _on_command_completed(self, event_data: Any) -> None:
        """Event handler for command.completed events."""
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
    
    async def _on_command_error(self, event_data: Any) -> None:
        """Event handler for command.error events."""
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
    
    async def suggest_next_action(self) -> Optional[Dict[str, Any]]:
        """
        Suggest the next action based on current context.
        
        Returns:
            Optional[Dict[str, Any]]: A suggested action or None
        """
        # If there are active tasks, don't suggest anything
        if self.active_tasks:
            return None
            
        # Create a temporary state to use the reflector node
        state = CognitiveGraphState(
            memory=Memory(conversation=self.context["conversation"]),
            workspace=self.context["workspace"],
            status="idle"
        )
        
        # Use the reflector node to get suggestions
        reflector = self.core_graph._create_reflector_node()
        updated_state = await reflector(state)
        
        return updated_state.next_action
    
    def get_context(self) -> Dict[str, Any]:
        """Get the current context."""
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

# Create a singleton instance
cognitive_core_langgraph = CognitiveCoreWithLangGraph()
