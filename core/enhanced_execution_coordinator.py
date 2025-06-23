"""
Enhanced Multi-Step Execution Coordinator
-----------------------------------------
Coordinates complex multi-step workflows with improved error handling and performance.
Integrates with the Universal Request Processor for seamless operation.
"""

import asyncio
import logging
import json
import time
from datetime import datetime
from typing import Dict, List, Any, Optional, Union, Callable
from pathlib import Path

from core.event_bus import event_bus
from core.error_handler import error_handler
from core.universal_request_processor import SerializationHelper, AsyncIOManager
from utils.performance_monitor import monitor_performance

logger = logging.getLogger(__name__)

class StepExecutionContext:
    """Context for step execution with dependency tracking"""
    
    def __init__(self, step_id: str, step_data: Dict[str, Any]):
        self.step_id = step_id
        self.step_data = step_data
        self.status = "pending"
        self.result = None
        self.error = None
        self.start_time = None
        self.end_time = None
        self.dependencies_met = False
        self.retry_count = 0
        self.max_retries = 3

class WorkflowExecutionPlan:
    """Execution plan for multi-step workflows"""
    
    def __init__(self, workflow_id: str, steps: List[Dict[str, Any]]):
        self.workflow_id = workflow_id
        self.steps = steps
        self.step_contexts = {}
        self.execution_order = []
        self.dependency_graph = {}
        self.completed_steps = set()
        self.failed_steps = set()
        self.status = "initialized"
        
        self._build_execution_plan()
    
    def _build_execution_plan(self):
        """Build dependency graph and execution order"""
        
        # Create step contexts
        for i, step in enumerate(self.steps):
            step_id = step.get("step_id", f"step_{i}")
            self.step_contexts[step_id] = StepExecutionContext(step_id, step)
            
            # Build dependency graph
            depends_on = step.get("depends_on", [])
            if isinstance(depends_on, str):
                depends_on = [depends_on]
            
            self.dependency_graph[step_id] = depends_on
        
        # Calculate execution order (topological sort)
        self.execution_order = self._topological_sort()
    
    def _topological_sort(self) -> List[str]:
        """Topologically sort steps based on dependencies"""
        
        in_degree = {step_id: 0 for step_id in self.step_contexts}
        
        # Calculate in-degrees
        for step_id, dependencies in self.dependency_graph.items():
            for dep in dependencies:
                if dep in in_degree:
                    in_degree[step_id] += 1
        
        # Queue for steps with no dependencies
        queue = [step_id for step_id, degree in in_degree.items() if degree == 0]
        result = []
        
        while queue:
            current = queue.pop(0)
            result.append(current)
            
            # Update in-degrees for dependent steps
            for step_id, dependencies in self.dependency_graph.items():
                if current in dependencies:
                    in_degree[step_id] -= 1
                    if in_degree[step_id] == 0:
                        queue.append(step_id)
        
        return result
    
    def get_ready_steps(self) -> List[str]:
        """Get steps that are ready to execute"""
        ready_steps = []
        
        for step_id in self.execution_order:
            context = self.step_contexts[step_id]
            
            if context.status != "pending":
                continue
                
            # Check if dependencies are met
            dependencies = self.dependency_graph[step_id]
            if all(dep in self.completed_steps for dep in dependencies):
                ready_steps.append(step_id)
        
        return ready_steps

class EnhancedExecutionCoordinator:
    """
    Enhanced coordinator for multi-step execution with dependency management
    """
    
    def __init__(self):
        self.asyncio_manager = AsyncIOManager()
        self.serialization_helper = SerializationHelper()
        self.active_workflows = {}
        self.execution_history = []
        
        # Performance tracking
        self.execution_stats = {
            "total_workflows": 0,
            "successful_workflows": 0,
            "failed_workflows": 0,
            "total_execution_time": 0,
            "average_steps_per_workflow": 0
        }
        
        logger.info("Enhanced Execution Coordinator initialized")
    
    @monitor_performance
    async def execute_workflow(self, workflow_id: str, steps: List[Dict[str, Any]], 
                             context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Execute a multi-step workflow with dependency coordination
        
        Args:
            workflow_id: Unique identifier for the workflow
            steps: List of steps to execute
            context: Optional execution context
            
        Returns:
            Dict containing execution results
        """
        start_time = time.time()
        
        try:
            logger.info(f"Starting workflow execution: {workflow_id}")
            
            # Create execution plan
            execution_plan = WorkflowExecutionPlan(workflow_id, steps)
            self.active_workflows[workflow_id] = execution_plan
            
            # Initialize workflow context
            workflow_context = {
                "workflow_id": workflow_id,
                "start_time": start_time,
                "user_context": context or {},
                "step_results": {},
                "global_variables": {}
            }
            
            # Execute steps according to plan
            result = await self._execute_workflow_steps(execution_plan, workflow_context)
            
            # Update statistics
            execution_time = time.time() - start_time
            self.execution_stats["total_workflows"] += 1
            self.execution_stats["total_execution_time"] += execution_time
            
            if result["status"] == "success":
                self.execution_stats["successful_workflows"] += 1
            else:
                self.execution_stats["failed_workflows"] += 1
            
            # Calculate average steps
            total_steps = sum(len(plan.steps) for plan in self.active_workflows.values())
            self.execution_stats["average_steps_per_workflow"] = total_steps / max(len(self.active_workflows), 1)
            
            # Clean up
            if workflow_id in self.active_workflows:
                del self.active_workflows[workflow_id]
            
            # Add to history
            execution_record = {
                "workflow_id": workflow_id,
                "execution_time": execution_time,
                "status": result["status"],
                "step_count": len(steps),
                "timestamp": datetime.now().isoformat()
            }
            self.execution_history.append(execution_record)
            
            # Keep only last 100 records
            if len(self.execution_history) > 100:
                self.execution_history = self.execution_history[-100:]
            
            return result
            
        except Exception as e:
            logger.error(f"Workflow execution failed for {workflow_id}: {e}")
            
            # Update failure statistics
            self.execution_stats["total_workflows"] += 1
            self.execution_stats["failed_workflows"] += 1
            
            error_context = {
                "component": "execution_coordinator",
                "workflow_id": workflow_id,
                "operation": "execute_workflow"
            }
            await error_handler.handle_error(e, error_context)
            
            return {
                "status": "failed",
                "workflow_id": workflow_id,
                "error": str(e),
                "execution_time": time.time() - start_time
            }
    
    async def _execute_workflow_steps(self, plan: WorkflowExecutionPlan, 
                                    context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute workflow steps according to the execution plan"""
        
        plan.status = "executing"
        results = []
        
        try:
            # Execute steps in dependency order
            while len(plan.completed_steps) < len(plan.steps):
                ready_steps = plan.get_ready_steps()
                
                if not ready_steps:
                    # Check for circular dependencies or errors
                    remaining_steps = set(plan.step_contexts.keys()) - plan.completed_steps - plan.failed_steps
                    if remaining_steps:
                        logger.error(f"Workflow {plan.workflow_id} has unresolvable dependencies: {remaining_steps}")
                        break
                    else:
                        break  # All steps completed
                
                # Execute ready steps in parallel
                step_tasks = []
                for step_id in ready_steps:
                    task = self._execute_single_step(step_id, plan, context)
                    step_tasks.append((step_id, task))
                
                # Wait for step completion
                for step_id, task in step_tasks:
                    try:
                        step_result = await self.asyncio_manager.safe_execute(task, timeout=300)  # 5 minutes per step
                        step_context = plan.step_contexts[step_id]
                        
                        if step_result and step_result.get("status") == "success":
                            step_context.status = "completed"
                            step_context.result = step_result
                            plan.completed_steps.add(step_id)
                            
                            # Store result for use by dependent steps
                            context["step_results"][step_id] = step_result
                            
                            logger.info(f"Step {step_id} completed successfully")
                        else:
                            step_context.status = "failed"
                            step_context.error = step_result.get("error", "Unknown error")
                            plan.failed_steps.add(step_id)
                            
                            # Check if step is critical
                            if step_context.step_data.get("critical", False):
                                logger.error(f"Critical step {step_id} failed, aborting workflow")
                                plan.status = "failed"
                                break
                            else:
                                logger.warning(f"Non-critical step {step_id} failed, continuing")
                        
                        results.append({
                            "step_id": step_id,
                            "status": step_context.status,
                            "result": step_context.result,
                            "error": step_context.error
                        })
                        
                    except Exception as e:
                        logger.error(f"Error executing step {step_id}: {e}")
                        step_context = plan.step_contexts[step_id]
                        step_context.status = "failed"
                        step_context.error = str(e)
                        plan.failed_steps.add(step_id)
                        
                        results.append({
                            "step_id": step_id,
                            "status": "failed",
                            "error": str(e)
                        })
                
                # Break if workflow failed
                if plan.status == "failed":
                    break
            
            # Determine final workflow status
            if plan.failed_steps:
                if any(plan.step_contexts[step_id].step_data.get("critical", False) 
                       for step_id in plan.failed_steps):
                    final_status = "failed"
                else:
                    final_status = "completed_with_warnings"
            else:
                final_status = "success"
            
            plan.status = final_status
            
            return {
                "status": final_status,
                "workflow_id": plan.workflow_id,
                "results": results,
                "completed_steps": len(plan.completed_steps),
                "failed_steps": len(plan.failed_steps),
                "total_steps": len(plan.steps)
            }
            
        except Exception as e:
            logger.error(f"Workflow execution error: {e}")
            plan.status = "failed"
            return {
                "status": "failed",
                "workflow_id": plan.workflow_id,
                "error": str(e),
                "results": results
            }
    
    async def _execute_single_step(self, step_id: str, plan: WorkflowExecutionPlan, 
                                 context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a single step"""
        
        step_context = plan.step_contexts[step_id]
        step_data = step_context.step_data
        
        logger.info(f"Executing step {step_id}: {step_data.get('description', 'No description')}")
        
        step_context.start_time = time.time()
        step_context.status = "executing"
        
        try:
            # Prepare step command
            command = self._prepare_step_command(step_data, context)
            
            # Execute through command router
            from core.command_router import router
            result = await router.route_command(command)
            
            step_context.end_time = time.time()
            
            # Process result variables
            self._process_step_variables(step_data, result, context)
            
            return {
                "status": "success",
                "result": result,
                "execution_time": step_context.end_time - step_context.start_time
            }
            
        except Exception as e:
            step_context.end_time = time.time()
            step_context.error = str(e)
            
            # Retry logic for non-critical steps
            if step_context.retry_count < step_context.max_retries and not step_data.get("critical", False):
                step_context.retry_count += 1
                logger.warning(f"Step {step_id} failed, retrying ({step_context.retry_count}/{step_context.max_retries})")
                await asyncio.sleep(1 * step_context.retry_count)  # Exponential backoff
                return await self._execute_single_step(step_id, plan, context)
            
            return {
                "status": "failed",
                "error": str(e),
                "execution_time": step_context.end_time - step_context.start_time if step_context.end_time else 0
            }
    
    def _prepare_step_command(self, step_data: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare command from step data with variable substitution"""
        
        command = dict(step_data)  # Copy step data
        
        # Remove coordinator-specific fields
        coordinator_fields = ["depends_on", "critical", "description", "variables", "step_id"]
        for field in coordinator_fields:
            command.pop(field, None)
        
        # Substitute variables in command
        command = self._substitute_variables(command, context)
        
        return command
    
    def _substitute_variables(self, obj: Any, context: Dict[str, Any]) -> Any:
        """Substitute variables in command data"""
        
        if isinstance(obj, str):
            # Simple variable substitution
            if obj.startswith("${") and obj.endswith("}"):
                var_name = obj[2:-1]
                return self._resolve_variable(var_name, context)
            return obj
        
        elif isinstance(obj, dict):
            return {k: self._substitute_variables(v, context) for k, v in obj.items()}
        
        elif isinstance(obj, list):
            return [self._substitute_variables(item, context) for item in obj]
        
        return obj
    
    def _resolve_variable(self, var_name: str, context: Dict[str, Any]) -> Any:
        """Resolve variable value from context"""
        
        # Check global variables first
        if var_name in context.get("global_variables", {}):
            return context["global_variables"][var_name]
        
        # Check step results
        if "." in var_name:
            step_id, field = var_name.split(".", 1)
            step_results = context.get("step_results", {})
            if step_id in step_results:
                return step_results[step_id].get(field, f"${{{var_name}}}")
        
        # Check user context
        if var_name in context.get("user_context", {}):
            return context["user_context"][var_name]
        
        # Return original if not found
        logger.warning(f"Variable {var_name} not found in context")
        return f"${{{var_name}}}"
    
    def _process_step_variables(self, step_data: Dict[str, Any], result: Dict[str, Any], 
                               context: Dict[str, Any]):
        """Process variables defined in step output"""
        
        variables = step_data.get("variables", {})
        if not variables:
            return
        
        global_vars = context.setdefault("global_variables", {})
        
        for var_name, var_expression in variables.items():
            try:
                # Simple variable extraction from result
                if var_expression.startswith("result."):
                    field_path = var_expression[7:]  # Remove "result."
                    value = self._extract_field_from_result(result, field_path)
                    global_vars[var_name] = value
                    logger.debug(f"Set variable {var_name} = {value}")
                
            except Exception as e:
                logger.warning(f"Failed to process variable {var_name}: {e}")
    
    def _extract_field_from_result(self, result: Dict[str, Any], field_path: str) -> Any:
        """Extract field value from result using dot notation"""
        
        fields = field_path.split(".")
        current = result
        
        for field in fields:
            if isinstance(current, dict) and field in current:
                current = current[field]
            else:
                return None
        
        return current
    
    def get_workflow_status(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        """Get current status of a workflow"""
        
        if workflow_id not in self.active_workflows:
            return None
        
        plan = self.active_workflows[workflow_id]
        
        return {
            "workflow_id": workflow_id,
            "status": plan.status,
            "total_steps": len(plan.steps),
            "completed_steps": len(plan.completed_steps),
            "failed_steps": len(plan.failed_steps),
            "step_details": [
                {
                    "step_id": step_id,
                    "status": context.status,
                    "retry_count": context.retry_count
                }
                for step_id, context in plan.step_contexts.items()
            ]
        }
    
    def get_execution_statistics(self) -> Dict[str, Any]:
        """Get execution statistics"""
        
        stats = dict(self.execution_stats)
        
        if stats["total_workflows"] > 0:
            stats["success_rate"] = stats["successful_workflows"] / stats["total_workflows"]
            stats["average_execution_time"] = stats["total_execution_time"] / stats["total_workflows"]
        else:
            stats["success_rate"] = 0
            stats["average_execution_time"] = 0
        
        stats["active_workflows"] = len(self.active_workflows)
        stats["recent_executions"] = self.execution_history[-10:]  # Last 10 executions
        
        return stats
    
    async def shutdown(self):
        """Clean shutdown"""
        logger.info("Shutting down Enhanced Execution Coordinator")
        await self.asyncio_manager.cleanup()

# Create singleton instance
execution_coordinator = EnhancedExecutionCoordinator()
