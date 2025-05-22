"""
LangGraph Diagnostics Bridge
---------------------------
This module provides integration between LangGraph and the Project-S diagnostics system.
It captures LangGraph events and reports them to the diagnostics manager for unified monitoring.
"""

import asyncio
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime

from core.event_bus import event_bus
from core.diagnostics import diagnostics_manager, AlertLevel, LogLevel
from integrations.langgraph_error_monitor import error_monitor
from integrations.workflow_visualizer import workflow_visualizer

logger = logging.getLogger(__name__)

class LangGraphDiagnosticsBridge:
    """
    Bridge between LangGraph events and the Project-S diagnostics system.
    
    Subscribes to LangGraph events and forwards relevant information to the 
    diagnostics manager to provide a unified view of system diagnostics.
    """
    
    def __init__(self):
        """Initialize the diagnostics bridge"""
        self._register_event_handlers()
        logger.info("LangGraph Diagnostics Bridge initialized")
    
    def _register_event_handlers(self):
        """Register event handlers for LangGraph events"""
        # Error-related events
        event_bus.subscribe("workflow.error", self._on_workflow_error)
        event_bus.subscribe("workflow.retry", self._on_workflow_retry)
        event_bus.subscribe("command.error", self._on_command_error)
        
        # Workflow state events
        event_bus.subscribe("workflow.start", self._on_workflow_start)
        event_bus.subscribe("workflow.complete", self._on_workflow_complete)
        event_bus.subscribe("workflow.state.transition", self._on_state_transition)
        
        # Performance events
        event_bus.subscribe("command.start", self._on_command_start)
        event_bus.subscribe("command.complete", self._on_command_complete)
    
    async def _on_workflow_error(self, event_data: Dict[str, Any]):
        """Handle workflow error events and forward to diagnostics"""
        graph_id = event_data.get("graph_id", "unknown")
        error = event_data.get("error")
        state = event_data.get("state", {})
        
        # Register the error with the diagnostics system
        if error:
            diagnostics_manager.register_error(
                error=error,
                component="langgraph_workflow",
                workflow_id=graph_id,
                additional_info={
                    "current_task": state.get("current_task"),
                    "context": state.get("context", {})
                },
                alert_level=AlertLevel.WARNING
            )
        
        # If we have state data, visualize the workflow at the error point
        if state:
            try:
                await workflow_visualizer.visualize_workflow(graph_id, state)
            except Exception as viz_error:
                logger.error(f"Failed to visualize workflow at error point: {viz_error}")
    
    async def _on_workflow_retry(self, event_data: Dict[str, Any]):
        """Handle workflow retry events"""
        graph_id = event_data.get("graph_id", "unknown")
        retry_count = event_data.get("retry_count", 0)
        state = event_data.get("state", {})
        
        # Log retry attempt
        logger.warning(f"Workflow {graph_id} retry #{retry_count}")
        
        # Send an alert if retry count is high
        if retry_count >= 3:
            diagnostics_manager.send_alert(
                level=AlertLevel.WARNING,
                message=f"High retry count ({retry_count}) for workflow {graph_id}",
                source="langgraph_workflow",
                details={"retry_count": retry_count, "workflow_id": graph_id}
            )
    
    async def _on_command_error(self, event_data: Dict[str, Any]):
        """Handle command error events"""
        command = event_data.get("command", {})
        error = event_data.get("error")
        
        if error:
            diagnostics_manager.register_error(
                error=error,
                component="langgraph_command",
                additional_info={"command": command},
                alert_level=AlertLevel.INFO
            )
    
    async def _on_workflow_start(self, event_data: Dict[str, Any]):
        """Handle workflow start events"""
        graph_id = event_data.get("graph_id", "unknown")
        state = event_data.get("state", {})
        
        logger.info(f"Workflow started: {graph_id}")
        
        # Store initial state for performance tracking
        self._store_workflow_start_time(graph_id)
        
        # Visualize initial workflow state
        if state:
            try:
                await workflow_visualizer.visualize_workflow(graph_id, state)
            except Exception as viz_error:
                logger.error(f"Failed to visualize initial workflow state: {viz_error}")
    
    async def _on_workflow_complete(self, event_data: Dict[str, Any]):
        """Handle workflow completion events"""
        graph_id = event_data.get("graph_id", "unknown")
        state = event_data.get("state", {})
        
        # Calculate execution time and update metrics
        execution_time_ms = self._calculate_execution_time(graph_id)
        status = state.get("status", "completed")
        
        # Update workflow metrics
        if execution_time_ms:
            diagnostics_manager.update_workflow_metrics(
                workflow_id=graph_id,
                execution_time_ms=execution_time_ms,
                status=status,
                context={"state": state}
            )
        
        # Visualize final workflow state
        if state:
            try:
                await workflow_visualizer.visualize_workflow(graph_id, state)
                
                # Export workflow data for future reference
                workflow_visualizer.export_workflow_data(graph_id, state)
            except Exception as viz_error:
                logger.error(f"Failed to visualize final workflow state: {viz_error}")
    
    async def _on_state_transition(self, event_data: Dict[str, Any]):
        """Handle workflow state transition events"""
        # Primarily used for logging and advanced debugging
        graph_id = event_data.get("graph_id", "unknown")
        from_state = event_data.get("from_state", "")
        to_state = event_data.get("to_state", "")
        
        logger.debug(f"Workflow {graph_id} state transition: {from_state} -> {to_state}")
    
    async def _on_command_start(self, event_data: Dict[str, Any]):
        """Handle command start events for performance tracking"""
        command = event_data.get("command", {})
        command_id = command.get("id", "unknown")
        
        # Store start time for command execution time tracking
        self._store_command_start_time(command_id)
        
        logger.debug(f"Command started: {command_id}")
    
    async def _on_command_complete(self, event_data: Dict[str, Any]):
        """Handle command completion events for performance tracking"""
        command = event_data.get("command", {})
        command_id = command.get("id", "unknown")
        command_type = command.get("type", "unknown")
        
        # Calculate execution time
        execution_time_ms = self._calculate_command_execution_time(command_id)
        
        if execution_time_ms:
            # Update API response time metrics
            diagnostics_manager.update_response_time(
                endpoint=command_type,
                response_time_ms=execution_time_ms
            )
            
            # Alert on slow commands
            if execution_time_ms > 10000:  # More than 10 seconds
                diagnostics_manager.send_alert(
                    level=AlertLevel.INFO,
                    message=f"Slow command execution: {command_type} took {execution_time_ms:.1f}ms",
                    source="command_performance",
                    details={"command_id": command_id, "execution_time_ms": execution_time_ms}
                )
    
    # Utility methods for time tracking
    _workflow_start_times = {}
    _command_start_times = {}
    
    def _store_workflow_start_time(self, workflow_id: str):
        """Store the start time for a workflow"""
        self._workflow_start_times[workflow_id] = datetime.now().timestamp()
    
    def _calculate_execution_time(self, workflow_id: str) -> Optional[float]:
        """Calculate the execution time for a workflow in milliseconds"""
        start_time = self._workflow_start_times.pop(workflow_id, None)
        if start_time:
            execution_time = (datetime.now().timestamp() - start_time) * 1000
            return execution_time
        return None
    
    def _store_command_start_time(self, command_id: str):
        """Store the start time for a command"""
        self._command_start_times[command_id] = datetime.now().timestamp()
    
    def _calculate_command_execution_time(self, command_id: str) -> Optional[float]:
        """Calculate the execution time for a command in milliseconds"""
        start_time = self._command_start_times.pop(command_id, None)
        if start_time:
            execution_time = (datetime.now().timestamp() - start_time) * 1000
            return execution_time
        return None
    
    async def visualize_workflow_history(self, graph_id: str, states_history: List[Dict[str, Any]]):
        """Visualize the history of a workflow's states"""
        try:
            await workflow_visualizer.visualize_workflow_history(graph_id, states_history)
        except Exception as e:
            logger.error(f"Failed to visualize workflow history: {e}")


# Create singleton instance
langgraph_diagnostics_bridge = LangGraphDiagnosticsBridge()


async def register_diagnostic_commands():
    """Register diagnostic commands with the command router"""
    from core.command_router import router
    
    # Handler for diagnostic commands
    async def handle_diagnostic_command(command: Dict[str, Any]) -> Dict[str, Any]:
        operation = command.get("operation", "status")
        
        if operation == "status":
            # Generate current system status report
            return {
                "status": "success",
                "diagnostics": {
                    "uptime": diagnostics_manager.get_uptime_seconds(),
                    "error_count": len(diagnostics_manager.error_history),
                    "system_metrics": diagnostics_manager.get_current_metrics(),
                    "alert_count": len(diagnostics_manager.alert_history)
                }
            }
        elif operation == "performance_report":
            # Generate performance report
            output_path = command.get("output_path")
            report = diagnostics_manager.generate_performance_report(output_path)
            return {
                "status": "success",
                "report": report
            }
        elif operation == "errors":
            # Get error statistics
            stats = diagnostics_manager.get_error_statistics()
            return {
                "status": "success",
                "error_statistics": stats
            }
        elif operation == "visualize_workflow":
            # Visualize a specific workflow
            workflow_id = command.get("workflow_id")
            if not workflow_id:
                return {"status": "error", "message": "Missing workflow_id"}
                
            # Get workflow state from error monitor
            data = error_monitor.get_workflow_state(workflow_id)
            if not data:
                return {"status": "error", "message": f"No data found for workflow {workflow_id}"}
            
            # Visualize the workflow
            result = await workflow_visualizer.visualize_workflow(workflow_id, data)
            return {
                "status": "success",
                "visualization_path": result
            }
        else:
            return {
                "status": "error",
                "message": f"Unknown operation: {operation}"
            }
    
    # Register the handler
    router.register("DIAGNOSTICS", handle_diagnostic_command)
    logger.info("Diagnostic commands registered")
"""
