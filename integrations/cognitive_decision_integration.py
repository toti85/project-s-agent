"""
Cognitive Core Decision Integration
----------------------------------
This module integrates the advanced decision router with the cognitive core system,
enabling intelligent decision-making in hybrid workflows.
"""
import logging
import asyncio
from typing import Dict, Any, List, Optional, Union, Callable

from langgraph.graph import StateGraph

from core.event_bus import event_bus
from core.cognitive_core import cognitive_core
from core.memory_system import memory_system
from integrations.langgraph_types import GraphState
from integrations.langgraph_integration import langgraph_integrator
from integrations.decision_router import decision_router
from integrations.advanced_decision_router import advanced_decision_router

# Set up logging
logger = logging.getLogger("cognitive_decision_integration")

class CognitiveDecisionIntegration:
    """
    Integrates the cognitive core's reasoning capabilities with the 
    advanced decision router to create intelligent workflow decisions.
    """
    
    def __init__(self):
        """Initialize the cognitive decision integration."""
        self.decision_history = {}
        self.state_history = {}
        
        # Register event handlers
        event_bus.subscribe("workflow.decision.needed", self._on_decision_needed)
        event_bus.subscribe("cognitive.insight_generated", self._on_insight_generated)
        
        logger.info("Cognitive Decision Integration initialized")
    
    async def _on_decision_needed(self, event_data: Dict[str, Any]) -> None:
        """
        Handle events when a workflow needs a decision from cognitive core.
        
        Args:
            event_data: Event data including state and decision context
        """
        graph_id = event_data.get("graph_id")
        decision_point = event_data.get("decision_point")
        options = event_data.get("options", [])
        context = event_data.get("context", {})
        
        if graph_id and decision_point and options:
            logger.info(f"Cognitive decision requested for workflow {graph_id} at {decision_point}")
            
            # Store decision context in history
            if graph_id not in self.decision_history:
                self.decision_history[graph_id] = []
            
            self.decision_history[graph_id].append({
                "decision_point": decision_point,
                "options": options,
                "timestamp": asyncio.get_event_loop().time(),
                "context": context
            })
            
            # Request decision from cognitive core
            decision = await self.request_cognitive_decision(
                decision_point=decision_point,
                options=options,
                context=context,
                graph_id=graph_id
            )
            
            # Publish decision result
            await event_bus.publish("workflow.decision.provided", {
                "graph_id": graph_id,
                "decision_point": decision_point,
                "selected_option": decision,
                "options": options,
                "reasoning": decision.get("reasoning") if isinstance(decision, dict) else None
            })
    
    async def _on_insight_generated(self, event_data: Dict[str, Any]) -> None:
        """
        Handle events when cognitive core generates an insight relevant to decisions.
        
        Args:
            event_data: Event data including the insight
        """
        insight = event_data.get("insight")
        related_graphs = event_data.get("related_workflows", [])
        
        if insight:
            logger.info(f"Cognitive insight received: {insight}")
            
            # Apply insight to active workflows if applicable
            for graph_id in related_graphs:
                if graph_id in self.state_history:
                    await event_bus.publish("workflow.system_state_changed", {
                        "graph_id": graph_id,
                        "system_state": {
                            "cognitive_insight": insight
                        }
                    })
    
    async def request_cognitive_decision(self, 
                                    decision_point: str,
                                    options: List[str],
                                    context: Dict[str, Any],
                                    graph_id: str) -> Union[str, Dict[str, Any]]:
        """
        Request a decision from the cognitive core.
        
        Args:
            decision_point: The name of the decision point
            options: Available decision options
            context: Contextual information for making the decision
            graph_id: The workflow graph ID
            
        Returns:
            Selected option or dict with selection and reasoning
        """
        try:
            # Prepare context for cognitive core
            decision_context = {
                "decision_point": decision_point,
                "options": options,
                "workflow_context": context,
                "graph_id": graph_id,
                "workflow_history": self.decision_history.get(graph_id, [])
            }
            
            # Create decision prompt
            prompt = f"Make a decision for workflow point '{decision_point}'. "
            prompt += f"Choose from options: {', '.join(options)}.\n\n"
            prompt += "Consider the following context:\n"
            
            # Add relevant context details
            for key, value in context.items():
                if isinstance(value, (str, int, float, bool)) or value is None:
                    prompt += f"- {key}: {value}\n"
            
            # Add any cognitive insights if available
            if "cognitive_insight" in context.get("system_state", {}):
                prompt += f"\nRelevant insight: {context['system_state']['cognitive_insight']}"
            
            # Add request for reasoning
            prompt += "\n\nProvide your decision and reasoning in this format: "
            prompt += "{ 'decision': 'selected_option', 'reasoning': 'explanation' }"
            
            # Query cognitive core
            response = await cognitive_core.process_query(
                query=prompt,
                context=decision_context
            )
            
            # Extract decision from response
            if isinstance(response, dict) and "decision" in response:
                selected_option = response["decision"]
                reasoning = response.get("reasoning", "No reasoning provided")
                
                logger.info(f"Cognitive decision: {selected_option} (Reasoning: {reasoning})")
                
                # Validate decision is in options
                if selected_option not in options:
                    logger.warning(f"Invalid decision {selected_option}, defaulting to first option")
                    selected_option = options[0] if options else None
                    response["decision"] = selected_option
                
                # Store decision in memory system for reference
                memory_key = f"decision:{graph_id}:{decision_point}"
                await memory_system.store(
                    memory_key, 
                    {
                        "decision": selected_option,
                        "reasoning": reasoning,
                        "options": options,
                        "context": context
                    }
                )
                
                return response
            elif isinstance(response, str) and response in options:
                # Direct string response matching an option
                return response
            else:
                logger.warning(f"Unexpected response format from cognitive core: {response}")
                return options[0] if options else None
                
        except Exception as e:
            logger.error(f"Error getting decision from cognitive core: {e}")
            # Default to first option in case of error
            return options[0] if options else None
    
    def create_cognitive_decision_node(self, 
                                   name: str,
                                   question: str,
                                   options: Dict[str, str],
                                   context_keys: List[str] = None) -> Callable:
        """
        Create a decision node function that uses cognitive core for decisions.
        
        Args:
            name: Name of the decision point
            question: Question to ask the cognitive core
            options: Dictionary mapping decision values to destination nodes
            context_keys: List of context keys to include in decision request
            
        Returns:
            A decision node function for use in LangGraph
        """
        async def cognitive_decision_node(state: GraphState) -> GraphState:
            try:
                # Extract relevant context
                context = {}
                full_context = state.get("context", {})
                
                if context_keys:
                    for key in context_keys:
                        if key in full_context:
                            context[key] = full_context[key]
                else:
                    # Include common useful context keys
                    for key in ["input_type", "processing_stage", "last_result"]:
                        if key in full_context:
                            context[key] = full_context[key]
                
                # Request cognitive decision
                response = await self.request_cognitive_decision(
                    decision_point=name,
                    options=list(options.keys()),
                    context=context,
                    graph_id=state["context"].get("graph_id", "unknown")
                )
                
                # Determine the next node
                next_node = None
                decision_value = None
                reasoning = None
                
                if isinstance(response, dict):
                    decision_value = response.get("decision")
                    reasoning = response.get("reasoning")
                else:
                    decision_value = response
                
                # Map decision to node
                if decision_value in options:
                    next_node = options[decision_value]
                else:
                    # Default to first option if decision is invalid
                    next_node = list(options.values())[0]
                    decision_value = list(options.keys())[0]
                
                # Set decision in state
                state["next_node"] = next_node
                state["context"]["cognitive_decision"] = {
                    "value": decision_value,
                    "reasoning": reasoning,
                    "timestamp": asyncio.get_event_loop().time()
                }
                
                # Publish event
                await event_bus.publish("workflow.cognitive_decision.made", {
                    "graph_id": state["context"].get("graph_id", "unknown"),
                    "decision_point": name,
                    "selected_option": decision_value,
                    "selected_node": next_node,
                    "reasoning": reasoning,
                    "question": question
                })
                
                return state
                
            except Exception as e:
                logger.error(f"Error in cognitive decision node {name}: {e}")
                # Fallback to first option in case of error
                next_node = list(options.values())[0]
                state["next_node"] = next_node
                
                return state
                
        return cognitive_decision_node
    
    def add_cognitive_decision_node(self, 
                                graph: StateGraph,
                                node_name: str,
                                question: str,
                                options: Dict[str, str],
                                context_keys: List[str] = None) -> StateGraph:
        """
        Add a cognitive decision node to a LangGraph with proper conditional edges.
        
        Args:
            graph: The LangGraph to add the node to
            node_name: Name of the decision node
            question: Question to ask the cognitive core
            options: Dictionary mapping decision values to destination nodes
            context_keys: List of context keys to include in decision request
            
        Returns:
            The modified graph
        """
        # Create the cognitive decision node
        decision_node = self.create_cognitive_decision_node(
            node_name,
            question,
            options,
            context_keys
        )
        
        # Add the node to the graph
        graph.add_node(node_name, decision_node)
        
        # Add conditional edge based on next_node
        condition_func = advanced_decision_router.create_condition_function("next_node")
        
        # Create mapping of possible values to destinations
        conditional_map = {dest: dest for dest in options.values()}
        
        # Add the conditional edge
        graph.add_conditional_edges(
            node_name,
            condition_func,
            conditional_map
        )
        
        return graph
    
    def combine_with_advanced_router(self, 
                                 graph: StateGraph,
                                 node_name: str,
                                 question: str,
                                 decision_criteria: Callable,
                                 options: Dict[str, str],
                                 default_option: str) -> StateGraph:
        """
        Create a hybrid decision node that first tries the criteria function,
        then falls back to cognitive core if needed.
        
        Args:
            graph: The LangGraph to add the node to
            node_name: Name of the decision node
            question: Question to ask the cognitive core if criteria fails
            decision_criteria: Function that determines which option to select
            options: Dictionary mapping criterion values to destination nodes
            default_option: Default option if no decision can be made
            
        Returns:
            The modified graph
        """
        async def hybrid_decision_node(state: GraphState) -> GraphState:
            try:
                # First try the criteria function
                criteria_result = decision_criteria(state)
                source_used = "criteria_function"
                
                # If criteria function gives a valid result, use it
                if criteria_result in options:
                    next_node = options[criteria_result]
                    decision_value = criteria_result
                else:
                    # Otherwise, ask cognitive core
                    logger.info(f"Criteria function didn't match, asking cognitive core")
                    source_used = "cognitive_core"
                    
                    # Extract relevant context
                    context = {
                        "input_type": state["context"].get("input_type"),
                        "processing_stage": state["context"].get("processing_stage"),
                        "last_result": state["context"].get("last_result")
                    }
                    
                    # Request cognitive decision
                    response = await self.request_cognitive_decision(
                        decision_point=node_name,
                        options=list(options.keys()),
                        context=context,
                        graph_id=state["context"].get("graph_id", "unknown")
                    )
                    
                    if isinstance(response, dict):
                        decision_value = response.get("decision")
                        reasoning = response.get("reasoning")
                        
                        # Store reasoning in state
                        state["context"]["cognitive_reasoning"] = reasoning
                    else:
                        decision_value = response
                    
                    # Map decision to node
                    if decision_value in options:
                        next_node = options[decision_value]
                    else:
                        next_node = options[default_option]
                        decision_value = default_option
                
                # Set decision in state
                state["next_node"] = next_node
                state["context"]["hybrid_decision"] = {
                    "value": decision_value,
                    "source": source_used,
                    "timestamp": asyncio.get_event_loop().time()
                }
                
                # Publish event
                await event_bus.publish("workflow.hybrid_decision.made", {
                    "graph_id": state["context"].get("graph_id", "unknown"),
                    "decision_point": node_name,
                    "selected_option": decision_value,
                    "selected_node": next_node,
                    "source": source_used
                })
                
                return state
                
            except Exception as e:
                logger.error(f"Error in hybrid decision node {node_name}: {e}")
                # Fallback to default option in case of error
                next_node = options[default_option]
                state["next_node"] = next_node
                
                return state
        
        # Add the node to the graph
        graph.add_node(node_name, hybrid_decision_node)
        
        # Add conditional edge based on next_node
        condition_func = advanced_decision_router.create_condition_function("next_node")
        
        # Create mapping of possible values to destinations
        conditional_map = {dest: dest for dest in options.values()}
        
        # Add the conditional edge
        graph.add_conditional_edges(
            node_name,
            condition_func,
            conditional_map
        )
        
        return graph


# Create singleton instance
cognitive_decision_integration = CognitiveDecisionIntegration()
