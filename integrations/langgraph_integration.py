"""
LangGraph Integration for Project-S
---------------------------------------
This module integrates LangGraph with Project-S's event-driven architecture.
It creates a hybrid system that combines Project-S's event bus with LangGraph's state management.
"""
import logging
import asyncio
from typing import Dict, Any, List, TypedDict, Optional, Callable, Union
import json
import os
import uuid
from langgraph.graph import StateGraph
from langgraph.prebuilt import ToolNode
try:
    from langgraph.graph.message import add_messages, add_message
    HAS_LANGGRAPH_MESSAGES = True
except ImportError:
    HAS_LANGGRAPH_MESSAGES = False
from core.event_bus import event_bus
from core.command_router import router
from core.error_handler import error_handler
from integrations.langgraph_state_manager import state_manager
from integrations.langgraph_types import GraphState

logger = logging.getLogger(__name__)

class LangGraphIntegrator:
    """
    Integrates LangGraph with Project-S's event-driven architecture.
    - Creates a StateGraph for managing workflow state
    - Connects LangGraph events to Project-S event bus
    - Provides methods to create and execute workflows
    """
    
    def __init__(self):
        """Initialize the LangGraph integrator"""
        self.active_graphs = {}
        self.graph_states = {}
        self._register_event_handlers()
        self.max_retries = 3  # Maximum number of retries for failed commands
        logger.info("LangGraph integrator initialized")
        
    def _register_event_handlers(self):
        """Register handlers for Project-S events"""
        event_bus.subscribe("command.received", self._on_command_received)
        event_bus.subscribe("command.completed", self._on_command_completed)
        event_bus.subscribe("command.error", self._on_command_error)
        logger.info("Event handlers registered with Project-S event bus")
    
    async def _on_command_received(self, event_data: Any):
        """Handler for command.received events"""
        command = event_data
        graph_id = command.get("graph_id")
        
        if graph_id and graph_id in self.active_graphs:
            # This command is part of a graph workflow
            logger.info(f"Received command for graph {graph_id}")
            
            # Update graph state
            if graph_id in self.graph_states:
                self.graph_states[graph_id]["command_history"].append(command)
                self.graph_states[graph_id]["current_task"] = command
    
    async def _on_command_completed(self, event_data: Any):
        """Handler for command.completed events"""
        command = event_data.get("command", {})
        result = event_data.get("result", {})
        graph_id = command.get("graph_id")
        
        if graph_id and graph_id in self.active_graphs:
            # This command completion is part of a graph workflow
            logger.info(f"Command completed for graph {graph_id}")
            
            # Update graph state with result
            if graph_id in self.graph_states:
                state = self.graph_states[graph_id]
                if state["current_task"] and state["current_task"].get("id") == command.get("id"):
                    # Add result to context
                    state["context"]["last_result"] = result
                    state["current_task"] = None
                      # Continue graph execution
                    await self._continue_graph_execution(graph_id)
                    
    async def _on_command_error(self, event_data: Any):
        """Handler for command.error events"""
        command = event_data.get("command", {})
        error = event_data.get("error", "Unknown error")
        graph_id = command.get("graph_id")
        
        if graph_id and graph_id in self.active_graphs:
            # This command error is part of a graph workflow
            logger.error(f"Command error for graph {graph_id}: {error}")
            
            # Update graph state with error
            if graph_id in self.graph_states:
                state = self.graph_states[graph_id]
                
                # Record error details
                if "error_info" not in state or state["error_info"] is None:
                    state["error_info"] = {
                        "last_error": error,
                        "failed_command": command,
                        "timestamp": asyncio.get_event_loop().time()
                    }
                
                # Increment retry count
                if "retry_count" not in state:
                    state["retry_count"] = 0
                state["retry_count"] += 1
                
                # Check if we should retry or handle the error
                if state["retry_count"] <= self.max_retries:
                    # Log retry attempt
                    logger.info(f"Retrying command for graph {graph_id}, attempt {state['retry_count']} of {self.max_retries}")
                    
                    # Publish retry event
                    await event_bus.publish("workflow.retry", {
                        "graph_id": graph_id,
                        "retry_count": state["retry_count"],
                        "error": error
                    })
                    
                    # Retry with a small delay
                    await asyncio.sleep(1)  # Small delay before retry
                    await self._continue_graph_execution(graph_id, retry=True)
                else:
                    # Max retries reached, mark as error and try to handle
                    state["status"] = "error"
                    state["context"]["last_error"] = error
                    
                    # Log error
                    logger.error(f"Max retries ({self.max_retries}) reached for graph {graph_id}, handling error")
                      # Try to continue with error handling
                    await self._continue_graph_execution(graph_id, error=True)
                    
    async def _continue_graph_execution(self, graph_id: str, error: bool = False, retry: bool = False):
        """
        Continue execution of the graph
        
        Args:
            graph_id: ID of the workflow graph
            error: Whether to handle as an error condition
            retry: Whether this is a retry attempt
        """
        if graph_id not in self.active_graphs:
            logger.warning(f"Graph {graph_id} not found for continuation")
            return
        
        graph = self.active_graphs[graph_id]
        state = self.graph_states[graph_id]
        
        try:
            # If retrying, get the failed command rather than next step
            next_step = None
            
            if retry and state["error_info"] and "failed_command" in state["error_info"]:
                # Use the same command that failed
                next_step = state["error_info"]["failed_command"]
                logger.info(f"Retrying failed command: {next_step.get('type')}")
            else:
                # Use the graph's internal state machine to determine next action
                next_step = await self._get_next_step(graph, state, error)
            
            if next_step:
                # Add graph_id to the command for tracking
                next_step["graph_id"] = graph_id
                
                # If this is a retry or error handler, log it
                if retry:
                    logger.info(f"Retrying step in graph {graph_id}")
                    await event_bus.publish("workflow.step.retrying", {
                        "graph_id": graph_id,
                        "step": next_step
                    })
                elif error:
                    logger.info(f"Executing error handler in graph {graph_id}")
                    await event_bus.publish("workflow.error.handling", {
                        "graph_id": graph_id,
                        "handler": next_step
                    })
                
                # Execute the command through the router
                asyncio.create_task(router.route_command(next_step))
            
            elif state["status"] != "completed":
                # Mark workflow as completed if no more steps
                state["status"] = "completed"
                
                # If we had errors but managed to complete, note it
                completion_status = "completed_with_errors" if state.get("error_info") else "completed"
                
                await event_bus.publish("workflow.completed", {
                    "graph_id": graph_id,
                    "state": state,
                    "completion_status": completion_status
                })
                
                logger.info(f"Workflow {graph_id} {completion_status}")
        
        except Exception as e:
            logger.error(f"Error continuing graph execution: {e}")
            
            # Update state with error details
            state["status"] = "error"
            state["error_info"] = {
                "last_error": str(e),
                "timestamp": asyncio.get_event_loop().time(),
                "location": "graph_execution"
            }
            
            # Send to global error handler
            await error_handler.handle_error(e, 
                context={
                    "component": "LangGraphIntegrator",
                    "graph_id": graph_id,
                    "state": state
                }
            )
            
            # Publish detailed error event
            await event_bus.publish("workflow.error", {
                "graph_id": graph_id,
                "error": str(e),                "state": state,
                "traceback": error_handler.format_traceback(e)
            })
            
    async def _get_next_step(self, graph: StateGraph, state: GraphState, error: bool = False) -> Optional[Dict[str, Any]]:
        """
        Get the next step from the graph based on current state.
        Supports branching paths, error handling, and custom decision functions.
        
        Args:
            graph: The StateGraph instance
            state: The current graph state
            error: Whether an error occurred
            
        Returns:
            Optional[Dict[str, Any]: The next command to execute, or None if done
        """
        try:
            # Handle error case first
            if error:
                # If there was an error, check if there's error handling in the graph
                if "error_handler" in state["context"]:
                    if callable(state["context"]["error_handler"]):
                        # If it's a callable, invoke it
                        handler_result = state["context"]["error_handler"](state)
                        if asyncio.iscoroutine(handler_result):
                            return await handler_result
                        return handler_result
                    else:
                        # Otherwise treat as a command
                        return state["context"]["error_handler"]
                else:
                    # No error handler defined, stop execution
                    return None
            
            # Check if workflow is already completed
            if state["status"] == "completed":
                return None
            
            # Check for a custom decision function in context
            if "decision_function" in state["context"]:
                decision_func_name = state["context"]["decision_function"]
                
                # Call the decision function if it exists
                if isinstance(decision_func_name, str):
                    # Find the function in the global scope or defined modules
                    try:
                        # Check if the function is defined in this module
                        import sys
                        this_module = sys.modules[__name__]
                        
                        if hasattr(this_module, decision_func_name):
                            decision_func = getattr(this_module, decision_func_name)
                            
                            # Call the function
                            logger.info(f"Calling decision function: {decision_func_name}")
                            decision_result = decision_func(state)
                            
                            # Handle coroutines
                            if asyncio.iscoroutine(decision_result):
                                state = await decision_result
                            else:
                                state = decision_result
                                
                            # Log the decision
                            logger.info(f"Decision function executed, new state branch: {state.get('branch')}")
                            
                            # Publish event about the decision
                            await event_bus.publish("workflow.decision.executed", {
                                "decision_function": decision_func_name,
                                "graph_id": state["context"].get("graph_id"),
                                "branch": state.get("branch")
                            })
                    except Exception as e:
                        logger.error(f"Error executing decision function {decision_func_name}: {e}")
            
            # Check if we have a current branch to follow
            if "branch" in state and state["branch"]:
                branch_name = state["branch"]
                branches = state["context"].get("branches", {})
                
                if branch_name in branches:
                    branch_steps = branches[branch_name]
                    step_index = len([s for s in state["command_history"] 
                                    if s.get("branch") == branch_name])
                    
                    if step_index < len(branch_steps):
                        next_step = branch_steps[step_index].copy()
                        next_step["branch"] = branch_name
                        return next_step
            
            # Default to sequential steps if no branch logic
            step_index = len(state["command_history"])
            steps = state["context"].get("workflow_steps", [])
            if step_index < len(steps):
                return steps[step_index]
            
            return None
        
        except Exception as e:
            logger.error(f"Error getting next step from graph: {e}")
            return None
            
    def create_workflow(self, name: str, steps: List[Dict[str, Any]], 
                      context: Optional[Dict[str, Any]] = None,
                      branches: Optional[Dict[str, List[Dict[str, Any]]]] = None) -> str:
        """
        Create a new workflow using LangGraph.
        
        Args:
            name: Name of the workflow
            steps: List of command steps to execute
            context: Additional context for the workflow
            branches: Optional dict of named branch paths with their own steps
            
        Returns:
            str: The ID of the created workflow graph
        """
        # Create a unique ID for the graph
        graph_id = f"graph_{uuid.uuid4().hex[:8]}"
        
        # Create a new StateGraph
        graph = StateGraph(GraphState)
        
        # Initialize the graph state
        initial_state: GraphState = {
            "messages": [],
            "context": context or {},
            "command_history": [],
            "status": "created",
            "current_task": None,
            "error_info": None,
            "retry_count": 0,
            "branch": None
        }
        
        # Add workflow metadata to context
        initial_state["context"]["workflow_steps"] = steps
        initial_state["context"]["workflow_name"] = name
        initial_state["context"]["graph_id"] = graph_id
        initial_state["context"]["created_at"] = asyncio.get_event_loop().time()
        
        # Add branches if provided
        if branches:
            initial_state["context"]["branches"] = branches
        
        # Store the graph and its state
        self.active_graphs[graph_id] = graph
        self.graph_states[graph_id] = initial_state
        
        logger.info(f"Created workflow graph {graph_id} with {len(steps)} steps")
        
        return graph_id
    
    def create_node_based_workflow(self, name: str, nodes: Dict[str, Any], 
                               edges: List[Dict[str, Any]], context: Optional[Dict[str, Any]] = None) -> str:
        """
        Create a more advanced workflow using LangGraph's node-based configuration.
        This allows for more complex workflow topologies beyond simple linear sequences.
        
        Args:
            name: Name of the workflow
            nodes: Dictionary of node_name -> node_definition
            edges: List of edge definitions (from_node, to_node, condition)
            context: Additional context for the workflow
            
        Returns:
            str: The ID of the created workflow graph
        """
        # Create a unique ID for the graph
        graph_id = f"graph_{uuid.uuid4().hex[:8]}"
        
        try:
            # Create a new StateGraph
            graph = StateGraph(GraphState)
            
            # Add nodes to the graph
            for node_name, node_config in nodes.items():
                # Handle different node types
                if node_config.get("type") == "tool":
                    # Create a ToolNode for this node
                    tool_func = self._create_tool_function(node_config.get("command", {}))
                    graph.add_node(node_name, ToolNode(tool_func))
                else:
                    # Default node type is a standard function
                    node_func = self._create_node_function(node_config)
                    graph.add_node(node_name, node_func)
            
            # Add edges to connect the nodes
            for edge in edges:
                from_node = edge.get("from")
                to_node = edge.get("to")
                condition = edge.get("condition")
                
                if condition:
                    # Add conditional edge
                    graph.add_conditional_edges(
                        from_node,
                        self._create_condition_function(condition),
                        {
                            condition.get("value", True): to_node,
                            # Default condition if not met
                            condition.get("default_value", False): condition.get("default", from_node)
                        }
                    )
                else:
                    # Add direct edge
                    graph.add_edge(from_node, to_node)
            
            # Set the entry point
            entry_point = nodes.get("entry_point", list(nodes.keys())[0])
            graph.set_entry_point(entry_point)
            
            # Initialize the graph state
            initial_state: GraphState = {
                "messages": [],
                "context": context or {},
                "command_history": [],
                "status": "created",
                "current_task": None,
                "error_info": None,
                "retry_count": 0,
                "branch": None
            }
            
            # Add workflow metadata to context
            initial_state["context"]["workflow_name"] = name
            initial_state["context"]["graph_id"] = graph_id
            initial_state["context"]["created_at"] = asyncio.get_event_loop().time()
            initial_state["context"]["nodes"] = nodes
            initial_state["context"]["edges"] = edges
            
            # Store the graph and its state
            self.active_graphs[graph_id] = graph
            self.graph_states[graph_id] = initial_state
            
            logger.info(f"Created node-based workflow graph {graph_id} with {len(nodes)} nodes")
            
            return graph_id
            
        except Exception as e:
            logger.error(f"Error creating node-based workflow: {e}")
            raise
    
    def _create_tool_function(self, command: Dict[str, Any]):
        """Create a tool function from a command configuration"""
        async def tool_function(state: GraphState):
            # Add graph_id to the command for tracking
            cmd = command.copy()
            cmd["graph_id"] = state["context"]["graph_id"]
            
            # Record the command in history and current task
            state["command_history"].append(cmd)
            state["current_task"] = cmd
            
            # Execute the command through the router
            try:
                result = await router.route_command(cmd)
                
                # Update state with result
                if "context" not in state:
                    state["context"] = {}
                state["context"]["last_result"] = result
                
                return state
                
            except Exception as e:
                logger.error(f"Error executing tool node: {e}")
                if "context" not in state:
                    state["context"] = {}
                state["context"]["last_error"] = str(e)
                state["error_info"] = {
                    "last_error": str(e),
                    "failed_command": cmd,
                    "timestamp": asyncio.get_event_loop().time()
                }
                raise
        
        return tool_function
    
    def _create_node_function(self, node_config: Dict[str, Any]):
        """Create a node function from configuration"""
        async def node_function(state: GraphState):
            # Execute the node logic
            node_type = node_config.get("type", "passthrough")
            
            if node_type == "passthrough":
                # Just pass the state through
                return state
                
            elif node_type == "command":
                # Execute a command
                cmd = node_config.get("command", {}).copy()
                cmd["graph_id"] = state["context"]["graph_id"]
                
                # Record the command
                state["command_history"].append(cmd)
                state["current_task"] = cmd
                
                # Execute the command
                try:
                    result = await router.route_command(cmd)
                    state["context"]["last_result"] = result
                    state["current_task"] = None
                except Exception as e:
                    state["context"]["last_error"] = str(e)
                    state["error_info"] = {
                        "last_error": str(e),
                        "failed_command": cmd,
                        "timestamp": asyncio.get_event_loop().time()
                    }
                
                return state
                
            elif node_type == "decision":
                # Execute a decision function
                decision_func_name = node_config.get("function")
                if decision_func_name and isinstance(decision_func_name, str):
                    try:
                        # Find and execute the decision function
                        import sys
                        this_module = sys.modules[__name__]
                        
                        if hasattr(this_module, decision_func_name):
                            decision_func = getattr(this_module, decision_func_name)
                            
                            # Call the function
                            logger.info(f"Calling decision function: {decision_func_name}")
                            decision_result = decision_func(state)
                            
                            # Handle coroutines
                            if asyncio.iscoroutine(decision_result):
                                state = await decision_result
                            else:
                                state = decision_result
                                
                            # Log the decision
                            logger.info(f"Decision function executed, result: {state.get('decision')}")
                            
                            # Publish event about the decision
                            await event_bus.publish("workflow.decision.executed", {
                                "decision_function": decision_func_name,
                                "graph_id": state["context"].get("graph_id"),
                                "result": state.get("decision")
                            })
                    except Exception as e:
                        logger.error(f"Error executing decision function {decision_func_name}: {e}")
                        state["context"]["last_error"] = str(e)
            
            return state
        
        return node_function
    
    def _create_condition_function(self, condition: Dict[str, Any]):
        """Create a condition function for conditional edges"""
        
        def condition_function(state: GraphState):
            # Get the condition type
            condition_type = condition.get("type", "field_check")
            
            if condition_type == "field_check":
                # Check if a field equals a value
                field_path = condition.get("field", "").split(".")
                field_value = state
                
                # Navigate down the path
                for part in field_path:
                    if isinstance(field_value, dict) and part in field_value:
                        field_value = field_value[part]
                    else:
                        # Path doesn't exist
                        return condition.get("default_value", False)
                
                # Check if the field matches the expected value
                expected_value = condition.get("value")
                return field_value == expected_value
                
            elif condition_type == "expression":
                # Evaluate a simple expression
                expr = condition.get("expression", "")
                try:
                    # Create a safe evaluation context with just the state
                    result = eval(expr, {"state": state, "__builtins__": {}})
                    return bool(result)
                except Exception as e:
                    logger.error(f"Error evaluating condition expression: {e}")
                    return condition.get("default_value", False)
            
            return condition.get("default_value", False)
        
        return condition_function
    
    def create_workflow(self, name: str, steps: List[Dict[str, Any]], 
                      context: Optional[Dict[str, Any]] = None,
                      branches: Optional[Dict[str, List[Dict[str, Any]]]] = None) -> str:
        """
        Create a new workflow using LangGraph.
        
        Args:
            name: Name of the workflow
            steps: List of command steps to execute
            context: Additional context for the workflow
            branches: Optional dict of named branch paths with their own steps
            
        Returns:
            str: The ID of the created workflow graph
        """
        # Create a unique ID for the graph
        graph_id = f"graph_{uuid.uuid4().hex[:8]}"
        
        # Create a new StateGraph
        graph = StateGraph(GraphState)
        
        # Initialize the graph state
        initial_state: GraphState = {
            "messages": [],
            "context": context or {},
            "command_history": [],
            "status": "created",
            "current_task": None,
            "error_info": None,
            "retry_count": 0,
            "branch": None
        }
        
        # Add workflow metadata to context
        initial_state["context"]["workflow_steps"] = steps
        initial_state["context"]["workflow_name"] = name
        initial_state["context"]["graph_id"] = graph_id
        initial_state["context"]["created_at"] = asyncio.get_event_loop().time()
        
        # Add branches if provided
        if branches:
            initial_state["context"]["branches"] = branches
        
        # Store the graph and its state
        self.active_graphs[graph_id] = graph
        self.graph_states[graph_id] = initial_state
        
        logger.info(f"Created workflow graph {graph_id} with {len(steps)} steps")
        
        return graph_id
    
    def create_node_based_workflow(self, name: str, nodes: Dict[str, Any], 
                               edges: List[Dict[str, Any]], context: Optional[Dict[str, Any]] = None) -> str:
        """
        Create a more advanced workflow using LangGraph's node-based configuration.
        This allows for more complex workflow topologies beyond simple linear sequences.
        
        Args:
            name: Name of the workflow
            nodes: Dictionary of node_name -> node_definition
            edges: List of edge definitions (from_node, to_node, condition)
            context: Additional context for the workflow
            
        Returns:
            str: The ID of the created workflow graph
        """
        # Create a unique ID for the graph
        graph_id = f"graph_{uuid.uuid4().hex[:8]}"
        
        try:
            # Create a new StateGraph
            graph = StateGraph(GraphState)
            
            # Add nodes to the graph
            for node_name, node_config in nodes.items():
                # Handle different node types
                if node_config.get("type") == "tool":
                    # Create a ToolNode for this node
                    tool_func = self._create_tool_function(node_config.get("command", {}))
                    graph.add_node(node_name, ToolNode(tool_func))
                else:
                    # Default node type is a standard function
                    node_func = self._create_node_function(node_config)
                    graph.add_node(node_name, node_func)
            
            # Add edges to connect the nodes
            for edge in edges:
                from_node = edge.get("from")
                to_node = edge.get("to")
                condition = edge.get("condition")
                
                if condition:
                    # Add conditional edge
                    graph.add_conditional_edges(
                        from_node,
                        self._create_condition_function(condition),
                        {
                            condition.get("value", True): to_node,
                            # Default condition if not met
                            condition.get("default_value", False): condition.get("default", from_node)
                        }
                    )
                else:
                    # Add direct edge
                    graph.add_edge(from_node, to_node)
            
            # Set the entry point
            entry_point = nodes.get("entry_point", list(nodes.keys())[0])
            graph.set_entry_point(entry_point)
            
            # Initialize the graph state
            initial_state: GraphState = {
                "messages": [],
                "context": context or {},
                "command_history": [],
                "status": "created",
                "current_task": None,
                "error_info": None,
                "retry_count": 0,
                "branch": None
            }
            
            # Add workflow metadata to context
            initial_state["context"]["workflow_name"] = name
            initial_state["context"]["graph_id"] = graph_id
            initial_state["context"]["created_at"] = asyncio.get_event_loop().time()
            initial_state["context"]["nodes"] = nodes
            initial_state["context"]["edges"] = edges
            
            # Store the graph and its state
            self.active_graphs[graph_id] = graph
            self.graph_states[graph_id] = initial_state
            
            logger.info(f"Created node-based workflow graph {graph_id} with {len(nodes)} nodes")
            
            return graph_id
            
        except Exception as e:
            logger.error(f"Error creating node-based workflow: {e}")
            raise
    
    async def start_workflow(self, graph_id: str) -> bool:
        """
        Start executing a workflow graph.
        
        Args:
            graph_id: ID of the workflow graph to start
            
        Returns:
            bool: True if the workflow was started successfully, False otherwise
        """
        if graph_id not in self.active_graphs or graph_id not in self.graph_states:
            logger.warning(f"Cannot start workflow {graph_id} - not found")
            return False
            
        # Update workflow status
        self.graph_states[graph_id]["status"] = "running"
        
        # Publish workflow start event
        await event_bus.publish("workflow.started", {
            "graph_id": graph_id,
            "workflow_name": self.graph_states[graph_id]["context"].get("workflow_name", "Unknown"),
            "timestamp": asyncio.get_event_loop().time()
        })
        
        # Start the workflow execution
        logger.info(f"Starting workflow {graph_id}")
        asyncio.create_task(self._continue_graph_execution(graph_id))
        
        return True
        
    async def cancel_workflow(self, graph_id: str) -> bool:
        """
        Cancel a running workflow.
        
        Args:
            graph_id: ID of the workflow graph to cancel
            
        Returns:
            bool: True if the workflow was cancelled, False if not found
        """
        if graph_id not in self.active_graphs or graph_id not in self.graph_states:
            logger.warning(f"Cannot cancel workflow {graph_id} - not found")
            return False
            
        # Update workflow status
        self.graph_states[graph_id]["status"] = "cancelled"
        
        # Publish workflow cancellation event
        await event_bus.publish("workflow.cancelled", {
            "graph_id": graph_id,
            "workflow_name": self.graph_states[graph_id]["context"].get("workflow_name", "Unknown"),
            "timestamp": asyncio.get_event_loop().time(),
            "reason": "User requested cancellation"
        })
        
        logger.info(f"Workflow {graph_id} cancelled")
        return True
    
    def get_workflow_state(self, graph_id: str) -> Optional[Dict[str, Any]]:
        """
        Get the current state of a workflow.
        
        Args:
            graph_id: ID of the workflow graph
            
        Returns:
            Optional[Dict[str, Any]]: The current state or None if not found        """
        if graph_id in self.graph_states:
            return self.graph_states[graph_id]
        return None
    
    async def register_as_command_handler(self) -> None:
        """Register this integrator as a workflow command handler with the router"""
        router.register("WORKFLOW", self.handle_workflow_command)
        logger.info("LangGraph command handlers registered successfully")
    
    async def handle_workflow_command(self, command: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle a WORKFLOW command.
        This method is called by the command router.
        
        Args:
            command: The command to handle
            
        Returns:
            Dict[str, Any]: The result of handling the command
        """
        try:
            operation = command.get("operation", "").lower()
            
            if operation == "create":
                # Create a new workflow
                workflow_name = command.get("name", f"workflow_{int(asyncio.get_event_loop().time())}")
                
                # Check if this is a node-based workflow
                if "nodes" in command and "edges" in command:
                    # Create a node-based workflow
                    graph_id = self.create_node_based_workflow(
                        workflow_name,
                        command.get("nodes"),
                        command.get("edges"),
                        command.get("context")
                    )
                else:
                    # Create a sequential workflow
                    graph_id = await self.create_workflow(
                        workflow_name,
                        command.get("steps", []),
                        command.get("context"),
                        command.get("branches")
                    )
                
                # Start the workflow immediately if requested
                if command.get("start", False):
                    await self.start_workflow(graph_id)
                    
                return {
                    "status": "success",
                    "graph_id": graph_id,
                    "message": f"Workflow {workflow_name} created successfully"
                }
                
            elif operation == "start":
                # Start an existing workflow
                graph_id = command.get("graph_id")
                if not graph_id:
                    return {
                        "status": "error",
                        "message": "Missing graph_id for workflow start operation"
                    }
                    
                await self.start_workflow(graph_id)
                return {
                    "status": "success",
                    "message": f"Workflow {graph_id} started"
                }
                
            elif operation == "cancel":
                # Cancel a running workflow
                graph_id = command.get("graph_id")
                if not graph_id:
                    return {
                        "status": "error",
                        "message": "Missing graph_id for workflow cancel operation"
                    }
                    
                await self.cancel_workflow(graph_id)
                return {
                    "status": "success",
                    "message": f"Workflow {graph_id} cancelled"
                }
                
            elif operation == "status":
                # Get workflow status
                graph_id = command.get("graph_id")
                if not graph_id:
                    return {
                        "status": "error",
                        "message": "Missing graph_id for workflow status operation"
                    }
                    
                status = self.get_workflow_state(graph_id)
                return {
                    "status": "success",
                    "workflow_status": status.get("status") if status else "not_found",
                    "workflow_data": status
                }
                
            else:
                return {
                    "status": "error",
                    "message": f"Unknown workflow operation: {operation}"
                }
                
        except Exception as e:
            # Log and handle errors
            logger.error(f"Error handling workflow command: {e}")
            await error_handler.handle_error(e, context={"command": command})
            
            return {
                "status": "error",
                "message": f"Error processing workflow command: {str(e)}"
            }


# Create a singleton instance
langgraph_integrator = LangGraphIntegrator()