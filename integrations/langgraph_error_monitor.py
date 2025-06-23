"""
Enhanced Error Monitoring and Reporting for LangGraph Workflows
--------------------------------------------------------------
This module provides advanced error monitoring and reporting capabilities
for LangGraph workflows in Project-S.
"""
import asyncio
import logging
import traceback
import json
import os
import time
from typing import Dict, Any, List, Optional, Tuple, Callable
from datetime import datetime
from core.event_bus import event_bus
from core.error_handler import error_handler

logger = logging.getLogger(__name__)

class LangGraphErrorMonitor:
    """
    Enhanced error monitoring for LangGraph workflows.
    Provides detailed tracking, reporting, and recovery recommendations.
    """
    
    def __init__(self):
        """Initialize the error monitor"""
        self.errors = {}  # graph_id -> list of errors
        self.error_trends = {}  # error_type -> count
        self.recovery_actions = {}  # error_type -> recommended action
        self.error_locations = {}  # location -> count
        self.runtime_errors = {}  # graph_id -> runtime stats with errors
        
        # Setup recovery actions for common errors
        self._setup_recovery_actions()
        
        # Register for relevant events
        self._register_event_handlers()
        
        # Setup logging
        self._setup_logging()
        
        logger.info("LangGraph Error Monitor initialized")
    
    def _setup_recovery_actions(self):
        """Set up recovery actions for common error types"""
        self.recovery_actions = {
            "CommandExecutionError": "Verify command syntax and try again with correct parameters",
            "AsyncTimeoutError": "Increase timeout settings or break operation into smaller chunks",
            "StateAccessError": "Ensure all required state fields are properly defined",
            "NodeNotFoundError": "Verify node names in workflow definition",
            "EdgeConditionError": "Check condition functions for logical errors",
            "GraphCycleError": "Remove cycles in graph definition",
            "GraphExecutionTimeout": "Simplify workflow or increase execution timeout"
        }
    
    def _register_event_handlers(self):
        """Register for relevant error events"""
        event_bus.subscribe("workflow.error", self._on_workflow_error)
        event_bus.subscribe("workflow.retry", self._on_workflow_retry)
        event_bus.subscribe("command.error", self._on_command_error)
    
    def _setup_logging(self):
        """Set up logging for errors"""
        log_dir = os.path.join(os.getcwd(), "logs")
        os.makedirs(log_dir, exist_ok=True)
        
        # Create file handler for error logs
        error_log_path = os.path.join(log_dir, "langgraph_errors.log")
        file_handler = logging.FileHandler(error_log_path)
        file_handler.setLevel(logging.ERROR)
        
        # Create formatter
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        
        # Add handler to logger
        logger.addHandler(file_handler)
    
    async def _on_workflow_error(self, event_data: Dict[str, Any]):
        """Handler for workflow error events"""
        graph_id = event_data.get("graph_id")
        error = event_data.get("error")
        state = event_data.get("state", {})
        traceback_str = event_data.get("traceback", "")
        
        if not graph_id:
            logger.error("Received workflow error event without graph_id")
            return
        
        # Record the error
        if graph_id not in self.errors:
            self.errors[graph_id] = []
        
        error_record = {
            "timestamp": datetime.now().isoformat(),
            "error_message": str(error),
            "traceback": traceback_str,
            "state_summary": self._create_state_summary(state),
            "context": state.get("context", {}),
            "current_task": state.get("current_task")
        }
        
        self.errors[graph_id].append(error_record)
        
        # Update trend analysis
        error_type = self._classify_error(error, traceback_str)
        self.error_trends[error_type] = self.error_trends.get(error_type, 0) + 1
        
        # Extract error location
        error_location = self._extract_error_location(traceback_str)
        if error_location:
            self.error_locations[error_location] = self.error_locations.get(error_location, 0) + 1
        
        # Log detailed error information
        logger.error(f"Workflow error in graph {graph_id}: {error}")
        logger.error(f"Error type: {error_type}")
        logger.error(f"Error location: {error_location}")
        
        # Generate recovery recommendation
        recovery = self.recovery_actions.get(error_type, "Review workflow definition and input parameters")
        logger.info(f"Recovery recommendation: {recovery}")
        
        # Publish detailed error analysis
        await event_bus.publish("workflow.error.analysis", {
            "graph_id": graph_id,
            "error_type": error_type,
            "error_location": error_location,
            "recovery_recommendation": recovery,
            "error_count": len(self.errors[graph_id])
        })
    
    async def _on_workflow_retry(self, event_data: Dict[str, Any]):
        """Handler for workflow retry events"""
        graph_id = event_data.get("graph_id")
        retry_count = event_data.get("retry_count", 0)
        error = event_data.get("error")
        
        # Record retry statistics
        if graph_id not in self.runtime_errors:
            self.runtime_errors[graph_id] = {
                "retry_count": 0,
                "retry_timestamps": [],
                "errors": []
            }
        
        self.runtime_errors[graph_id]["retry_count"] = retry_count
        self.runtime_errors[graph_id]["retry_timestamps"].append(datetime.now().isoformat())
        self.runtime_errors[graph_id]["errors"].append(str(error))
        
        logger.info(f"Workflow {graph_id} retrying (attempt {retry_count})")
    
    async def _on_command_error(self, event_data: Dict[str, Any]):
        """Handler for command error events that are part of a workflow"""
        command = event_data.get("command", {})
        error = event_data.get("error")
        
        # Only process if part of a workflow
        graph_id = command.get("graph_id")
        if not graph_id:
            return
        
        # Log the command error
        logger.error(f"Command error in workflow {graph_id}: {error}")
        
        # Track command errors by type
        command_type = command.get("type", "UNKNOWN")
        error_key = f"COMMAND_{command_type}"
        self.error_trends[error_key] = self.error_trends.get(error_key, 0) + 1
    
    def _create_state_summary(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Create a concise summary of the state for error reporting"""
        if not state:
            return {"state": "empty"}
        
        # Create a filtered version of state to avoid huge logs
        summary = {
            "status": state.get("status"),
            "command_history_count": len(state.get("command_history", [])),
            "message_count": len(state.get("messages", [])),
            "retry_count": state.get("retry_count", 0),
            "branch": state.get("branch"),
            "context_keys": list(state.get("context", {}).keys()),
            "has_error_info": "error_info" in state and state["error_info"] is not None
        }
        
        # Include last command if available
        if state.get("command_history") and len(state["command_history"]) > 0:
            summary["last_command_type"] = state["command_history"][-1].get("type")
        
        return summary
    
    def _classify_error(self, error: str, traceback_str: str) -> str:
        """Classify the error into a type"""
        error_str = str(error).lower()
        
        # Check for common error patterns
        if "timeout" in error_str:
            return "AsyncTimeoutError"
        elif "command" in error_str and ("execution" in error_str or "failed" in error_str):
            return "CommandExecutionError"
        elif "state" in error_str and "access" in error_str:
            return "StateAccessError"
        elif "node" in error_str and "not found" in error_str:
            return "NodeNotFoundError"
        elif "condition" in error_str:
            return "EdgeConditionError"
        elif "cycle" in error_str:
            return "GraphCycleError"
        
        # Check traceback for more context
        if traceback_str:
            if "KeyError" in traceback_str:
                return "StateKeyError"
            elif "IndexError" in traceback_str:
                return "StateIndexError"
            elif "AttributeError" in traceback_str:
                return "StateAttributeError"
            elif "TypeError" in traceback_str:
                return "TypeMismatchError"
        
        # Default classification
        return "UnknownError"
    
    def _extract_error_location(self, traceback_str: str) -> Optional[str]:
        """Extract the location (file:line) of the error from traceback"""
        if not traceback_str:
            return None
            
        try:
            # Look for the most relevant line in the traceback
            lines = traceback_str.split("\n")
            for line in lines:
                if "File" in line and "line" in line and "langgraph" in line:
                    parts = line.split(", ")
                    if len(parts) >= 2:
                        file_part = parts[0].strip()
                        line_part = parts[1].strip()
                        return f"{file_part.split('File')[-1].strip()}, {line_part}"
            
            # If no langgraph-specific line found, return the last file reference
            for line in reversed(lines):
                if "File" in line and "line" in line:
                    parts = line.split(", ")
                    if len(parts) >= 2:
                        file_part = parts[0].strip()
                        line_part = parts[1].strip()
                        return f"{file_part.split('File')[-1].strip()}, {line_part}"
        
        except Exception as e:
            logger.error(f"Error extracting location from traceback: {e}")
        
        return None
    
    def get_error_report(self, graph_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate an error report for a specific workflow or all workflows.
        
        Args:
            graph_id: Optional graph ID to filter for
            
        Returns:
            Dict with error statistics and details
        """
        # Specific workflow report
        if graph_id:
            if graph_id not in self.errors:
                return {"graph_id": graph_id, "errors": [], "total_errors": 0}
            
            return {
                "graph_id": graph_id,
                "errors": self.errors[graph_id],
                "total_errors": len(self.errors[graph_id]),
                "runtime_stats": self.runtime_errors.get(graph_id, {}),
                "error_types": self._count_error_types_for_graph(graph_id)
            }
        
        # Overall error report
        total_errors = sum(len(errs) for errs in self.errors.values())
        total_retries = sum(stats.get("retry_count", 0) for stats in self.runtime_errors.values())
        
        return {
            "total_errors": total_errors,
            "total_retries": total_retries,
            "error_trends": self.error_trends,
            "error_locations": self.error_locations,
            "workflow_error_counts": {gid: len(errs) for gid, errs in self.errors.items()},
            "most_common_error": self._get_most_common_error(),
            "most_common_location": self._get_most_common_location()
        }
    
    def _count_error_types_for_graph(self, graph_id: str) -> Dict[str, int]:
        """Count the types of errors for a specific graph"""
        error_types = {}
        
        if graph_id not in self.errors:
            return error_types
            
        for error in self.errors[graph_id]:
            error_msg = error.get("error_message", "")
            error_type = self._classify_error(error_msg, error.get("traceback", ""))
            error_types[error_type] = error_types.get(error_type, 0) + 1
            
        return error_types
    
    def _get_most_common_error(self) -> Tuple[str, int]:
        """Get the most common error type and its count"""
        if not self.error_trends:
            return ("None", 0)
            
        return max(self.error_trends.items(), key=lambda x: x[1])
    
    def _get_most_common_location(self) -> Tuple[str, int]:
        """Get the most common error location and its count"""
        if not self.error_locations:
            return ("None", 0)
            
        return max(self.error_locations.items(), key=lambda x: x[1])
    
    def get_recovery_recommendation(self, error_type: str) -> str:
        """
        Get a recovery recommendation for a specific error type.
        
        Args:
            error_type: The type of error
            
        Returns:
            Recommendation string
        """
        return self.recovery_actions.get(error_type, "Review workflow definition and input parameters")
    
    def export_error_data(self, filepath: str) -> bool:
        """
        Export error data to a JSON file.
        
        Args:
            filepath: Path to save the JSON file
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            report = {
                "export_time": datetime.now().isoformat(),
                "error_report": self.get_error_report(),
                "per_workflow_reports": {
                    graph_id: self.get_error_report(graph_id)
                    for graph_id in self.errors.keys()
                }
            }
            
            with open(filepath, 'w') as f:
                json.dump(report, f, indent=2)
                
            logger.info(f"Error data exported to {filepath}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to export error data: {e}")
            return False
    
    async def monitor_workflow_execution(self, graph_id: str) -> Dict[str, Any]:
        """
        Actively monitor a workflow execution and report on errors.
        
        Args:
            graph_id: ID of the workflow graph to monitor
            
        Returns:
            Dict with monitoring results
        """
        from integrations.langgraph_integration import langgraph_integrator
        
        start_time = time.time()
        error_count_start = len(self.errors.get(graph_id, []))
        
        while True:
            # Get current state
            state = langgraph_integrator.get_workflow_state(graph_id)
            
            # Exit if workflow completed or errored
            if not state or state["status"] in ["completed", "error", "cancelled"]:
                break
                
            # Wait a bit before checking again
            await asyncio.sleep(1)
            
            # Timeout after 5 minutes to prevent infinite monitoring
            if time.time() - start_time > 300:  # 5 minutes
                logger.warning(f"Monitoring timeout for workflow {graph_id}")
                break
        
        # Calculate monitoring results
        duration = time.time() - start_time
        end_state = langgraph_integrator.get_workflow_state(graph_id)
        error_count_end = len(self.errors.get(graph_id, []))
        new_errors = error_count_end - error_count_start
        
        result = {
            "graph_id": graph_id,
            "duration_seconds": duration,
            "final_status": end_state["status"] if end_state else "unknown",
            "new_errors": new_errors,
            "retry_count": end_state.get("retry_count", 0) if end_state else 0
        }
        
        # Add error details if there were new errors
        if new_errors > 0:
            result["errors"] = self.errors.get(graph_id, [])[error_count_start:]
            
        return result

# Create a singleton instance
error_monitor = LangGraphErrorMonitor()

async def register_error_monitoring_handlers():
    """Register the error monitoring command handler"""
    from core.command_router import router
    
    # Register a handler for the ERROR_REPORT command
    async def handle_error_report_command(command: Dict[str, Any]) -> Dict[str, Any]:
        operation = command.get("operation", "summary")
        graph_id = command.get("graph_id")
        export_path = command.get("export_path")
        
        if operation == "summary":
            return {
                "status": "success",
                "report": error_monitor.get_error_report(graph_id)
            }
        elif operation == "export" and export_path:
            success = error_monitor.export_error_data(export_path)
            return {
                "status": "success" if success else "error",
                "message": f"Error data {'exported successfully' if success else 'export failed'}"
            }
        elif operation == "monitor" and graph_id:
            report = await error_monitor.monitor_workflow_execution(graph_id)
            return {
                "status": "success",
                "monitoring_report": report
            }
        else:
            return {
                "status": "error",
                "message": "Invalid operation or missing required parameters"
            }
    
    # Register the command handler
    router.register("ERROR_REPORT", handle_error_report_command)
    logger.info("Error monitoring command handler registered")
    
    # Listen for specific events from LangGraph
    async def on_state_transition(event_data):
        """Track state transitions for error analysis"""
        graph_id = event_data.get("graph_id")
        if not graph_id:
            return
            
        # We don't need to do anything here, just tracking for awareness
        logger.debug(f"State transition in graph {graph_id}: {event_data.get('from_state')} -> {event_data.get('to_state')}")
    
    # Subscribe to state transition events
    event_bus.subscribe("workflow.state.transition", on_state_transition)
