"""
Decision Router for Project-S Hybrid System
------------------------------------------
This module implements a flexible decision-making and routing logic
for the Project-S hybrid system using LangGraph.

Key features:
1. Flexible router function for directing workflow between components
2. Conditional edges in LangGraph based on system state
3. Integration with Project-S Event Bus
4. Dynamic decision criteria based on context and history
5. Comprehensive logging and transparency of decisions
"""
import logging
import asyncio
import json
from datetime import datetime
import uuid
from typing import Dict, Any, List, Optional, Callable, Union, TypeVar, cast

from langgraph.graph import StateGraph
from langgraph.prebuilt import ToolNode

from core.event_bus import event_bus
from core.error_handler import error_handler
from integrations.langgraph_types import GraphState
from integrations.langgraph_integration import langgraph_integrator
from integrations.langgraph_state_manager import state_manager

# Create a logger for this module
logger = logging.getLogger("decision_router")

# Type for decision criteria functions
T = TypeVar("T")
DecisionCriteriaFunc = Callable[[GraphState], Union[str, bool]]

class DecisionMetadata:
    """
    Metadata for tracking decisions made in the workflow.
    """
    def __init__(self, 
                decision_id: str,
                timestamp: float,
                source_node: str,
                decision_criteria: str,
                considered_options: List[str],
                selected_option: str,
                context_snapshot: Dict[str, Any]):
        self.decision_id = decision_id
        self.timestamp = timestamp
        self.source_node = source_node
        self.decision_criteria = decision_criteria
        self.considered_options = considered_options
        self.selected_option = selected_option
        self.context_snapshot = context_snapshot
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert metadata to a dictionary for serialization."""
        return {
            "decision_id": self.decision_id,
            "timestamp": self.timestamp,
            "source_node": self.source_node,
            "decision_criteria": self.decision_criteria,
            "considered_options": self.considered_options,
            "selected_option": self.selected_option,
            "context_snapshot": {
                k: v for k, v in self.context_snapshot.items() 
                if k not in ["full_history", "messages"]  # Exclude large fields
            }
        }


class DecisionRouter:
    """
    Implements decision-making logic for directing workflow between components
    in the Project-S hybrid system.
    """
    
    def __init__(self):
        """Initialize the decision router."""
        self.decision_history: Dict[str, List[DecisionMetadata]] = {}
        
        # Register for events
        event_bus.subscribe("workflow.node.entered", self._on_node_entered)
        event_bus.subscribe("workflow.decision.made", self._on_decision_made)
        
        logger.info("Decision Router initialized")
        
    async def _on_node_entered(self, event_data: Dict[str, Any]) -> None:
        """
        Handle node entry events.
        Log when a workflow enters a new node.
        
        Args:
            event_data: Event data containing node information
        """
        graph_id = event_data.get("graph_id")
        node_name = event_data.get("node_name")
        
        if graph_id and node_name:
            logger.info(f"Workflow {graph_id} entered node: {node_name}")
            
            # Add to history in state if available
            if graph_id in state_manager.active_states:
                state = state_manager.active_states[graph_id]
                if "node_history" not in state["context"]:
                    state["context"]["node_history"] = []
                    
                state["context"]["node_history"].append({
                    "node": node_name,
                    "timestamp": asyncio.get_event_loop().time(),
                })
    
    async def _on_decision_made(self, event_data: Dict[str, Any]) -> None:
        """
        Handle decision events.
        Log the decision made by the workflow.
        
        Args:
            event_data: Event data containing decision information
        """
        graph_id = event_data.get("graph_id")
        decision_id = event_data.get("decision_id")
        source_node = event_data.get("source_node")
        decision = event_data.get("decision")
        options = event_data.get("options", [])
        
        if graph_id and decision:
            logger.info(f"Workflow {graph_id} made decision at {source_node}: {decision}")
            logger.info(f"Options considered: {options}")
            
            # Create a display-friendly representation for the logs
            decision_display = f"{source_node} → {decision}"
            if options:
                decision_display += f" (from {', '.join(options)})"
                
            # Log the decision with formatting for better visibility
            logger.info(f"DECISION: {decision_display}")
            
    def create_decision_node(self, name: str, 
                          criteria_func: DecisionCriteriaFunc,
                          options: Dict[str, str],
                          default_option: Optional[str] = None) -> Callable:
        """
        Create a decision node function for use in a LangGraph workflow.
        
        Args:
            name: Name of the decision point
            criteria_func: Function that determines which option to select
            options: Dictionary mapping criterion values to destination nodes
            default_option: Default option if criteria_func result isn't in options
            
        Returns:
            A node function for use in LangGraph
        """
        async def decision_node(state: GraphState) -> GraphState:
            # Generate a decision ID
            decision_id = f"decision_{uuid.uuid4().hex[:8]}"
            
            try:
                # Execute the criteria function
                logger.info(f"Evaluating decision criteria for {name}")
                result = criteria_func(state)
                
                # Determine the next node
                next_node = None
                
                if isinstance(result, str) and result in options:
                    next_node = options[result]
                elif isinstance(result, bool) and str(result) in options:
                    next_node = options[str(result)]
                elif default_option:
                    next_node = default_option
                    result = "default"
                else:
                    # If no valid result and no default, use the first option
                    next_node = list(options.values())[0]
                    result = "fallback"
                
                # Create decision metadata
                decision_meta = DecisionMetadata(
                    decision_id=decision_id,
                    timestamp=asyncio.get_event_loop().time(),
                    source_node=name,
                    decision_criteria=str(result),
                    considered_options=list(options.keys()),
                    selected_option=next_node,
                    context_snapshot={
                        "status": state.get("status", "unknown"),
                        "retry_count": state.get("retry_count", 0),
                        "current_task": state.get("current_task"),
                        "context": {
                            k: v for k, v in state.get("context", {}).items()
                            if not isinstance(v, (dict, list)) or k == "last_result"
                        }
                    }
                )
                
                # Store in decision history
                graph_id = state["context"].get("graph_id", "unknown")
                if graph_id not in self.decision_history:
                    self.decision_history[graph_id] = []
                self.decision_history[graph_id].append(decision_meta)
                
                # Add to state
                if "decisions" not in state["context"]:
                    state["context"]["decisions"] = []
                state["context"]["decisions"].append(decision_meta.to_dict())
                
                # Set next node in state for conditional edge to use
                state["next_node"] = next_node
                
                # Publish event
                await event_bus.publish("workflow.decision.made", {
                    "graph_id": graph_id,
                    "decision_id": decision_id,
                    "source_node": name,
                    "decision": next_node,
                    "criterion_value": str(result),
                    "options": list(options.keys()),
                    "timestamp": asyncio.get_event_loop().time()
                })
                
                return state
                
            except Exception as e:
                logger.error(f"Error in decision node {name}: {e}")
                error_context = {
                    "component": "decision_router",
                    "decision_node": name,
                    "state": {k: v for k, v in state.items() if k != "messages"}
                }
                asyncio.create_task(error_handler.handle_error(e, error_context))
                
                # Fallback to default or first option in case of error
                next_node = default_option or list(options.values())[0]
                state["next_node"] = next_node
                
                return state
                
        # Return the decision node function
        return decision_node
    
    def create_condition_function(self, criterion: str) -> Callable[[GraphState], str]:
        """
        Create a condition function for use with conditional edges in LangGraph.
        
        Args:
            criterion: The criterion to evaluate (can be a path in the state)
            
        Returns:
            A function that evaluates the condition based on state
        """
        def condition_func(state: GraphState) -> str:
            # Handle simple next_node field
            if criterion == "next_node" and "next_node" in state:
                return state["next_node"]
            
            # Handle dot notation for nested fields
            if "." in criterion:
                parts = criterion.split(".")
                value = state
                for part in parts:
                    if isinstance(value, dict) and part in value:
                        value = value[part]
                    else:
                        return None
                return value
            
            # Handle direct field access
            return state.get(criterion)
        
        return condition_func
    
    def add_decision_node(self, graph: StateGraph, 
                         node_name: str,
                         criteria_func: DecisionCriteriaFunc,
                         destinations: Dict[str, str],
                         default: Optional[str] = None) -> StateGraph:
        """
        Add a decision node to a LangGraph with proper conditional edges.
        
        Args:
            graph: The LangGraph to add the node to
            node_name: Name of the decision node
            criteria_func: Function that evaluates the decision criteria
            destinations: Mapping of criterion values to destination nodes
            default: Default destination if criteria_func result isn't in destinations
            
        Returns:
            The modified graph
        """
        # Create the decision node
        decision_func = self.create_decision_node(
            node_name, 
            criteria_func, 
            destinations,
            default
        )
        
        # Add the node to the graph
        graph.add_node(node_name, decision_func)
        
        # Add conditional edge based on next_node
        condition_func = self.create_condition_function("next_node")
        
        # Create mapping of possible values to destinations
        conditional_map = {dest: dest for dest in destinations.values()}
        
        # Add the conditional edge
        graph.add_conditional_edges(
            node_name,
            condition_func,
            conditional_map
        )
        
        return graph
    
    def get_decision_history(self, graph_id: str) -> List[Dict[str, Any]]:
        """
        Get the decision history for a specific workflow.
        
        Args:
            graph_id: The ID of the workflow graph
            
        Returns:
            List of decision metadata as dictionaries
        """
        if graph_id in self.decision_history:
            return [decision.to_dict() for decision in self.decision_history[graph_id]]
        return []
    
    def analyze_decision_patterns(self, graph_id: str) -> Dict[str, Any]:
        """
        Analyze decision patterns in a workflow for insights.
        
        Args:
            graph_id: The ID of the workflow graph
            
        Returns:
            Analysis of decision patterns
        """
        if graph_id not in self.decision_history:
            return {"error": "No decision history found for this graph"}
            
        decisions = self.decision_history[graph_id]
        
        # Count decisions per source node
        node_counts = {}
        for decision in decisions:
            if decision.source_node not in node_counts:
                node_counts[decision.source_node] = 0
            node_counts[decision.source_node] += 1
        
        # Count option selection frequency
        option_counts = {}
        for decision in decisions:
            if decision.selected_option not in option_counts:
                option_counts[decision.selected_option] = 0
            option_counts[decision.selected_option] += 1
        
        # Identify most common decision paths
        decision_paths = []
        for i in range(1, len(decisions)):
            path = f"{decisions[i-1].source_node}->{decisions[i].source_node}"
            decision_paths.append(path)
            
        path_counts = {}
        for path in decision_paths:
            if path not in path_counts:
                path_counts[path] = 0
            path_counts[path] += 1
        
        return {
            "total_decisions": len(decisions),
            "decision_points": node_counts,
            "option_frequencies": option_counts,
            "common_paths": dict(sorted(path_counts.items(), key=lambda x: x[1], reverse=True)[:5]),
            "timestamp_range": {
                "first": decisions[0].timestamp if decisions else None,
                "last": decisions[-1].timestamp if decisions else None,
                "duration": decisions[-1].timestamp - decisions[0].timestamp if decisions else 0
            }
        }


# Example decision criteria functions

def check_error_condition(state: GraphState) -> bool:
    """
    Check if the workflow has encountered an error.
    
    Args:
        state: The current workflow state
        
    Returns:
        True if there's an error, False otherwise
    """
    return state.get("error_info") is not None


def route_by_content_type(state: GraphState) -> str:
    """
    Route based on the content type in the workflow.
    
    Args:
        state: The current workflow state
        
    Returns:
        The content type to route by
    """
    content_type = state["context"].get("content_type", "")
    
    if "code" in content_type.lower():
        return "code"
    elif "image" in content_type.lower():
        return "image"
    elif "text" in content_type.lower():
        return "text"
    else:
        return "unknown"


def check_retry_needed(state: GraphState) -> bool:
    """
    Check if a retry is needed based on error and retry count.
    
    Args:
        state: The current workflow state
        
    Returns:
        True if retry is needed, False otherwise
    """
    has_error = state.get("error_info") is not None
    retry_count = state.get("retry_count", 0)
    max_retries = state["context"].get("max_retries", 3)
    
    return has_error and retry_count < max_retries


def check_has_required_context(state: GraphState, required_keys: List[str]) -> bool:
    """
    Check if the state has all required context keys.
    
    Args:
        state: The current workflow state
        required_keys: List of required context keys
        
    Returns:
        True if all required keys are present, False otherwise
    """
    context = state.get("context", {})
    return all(key in context for key in required_keys)


# Create singleton instance
decision_router = DecisionRouter()
