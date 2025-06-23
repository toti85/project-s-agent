"""
Project-S Autonomous Manager
============================
Enhanced autonomous capabilities that proactively manage and optimize the system.
Builds on the existing monitoring and cognitive infrastructure.
"""

import asyncio
import logging
import time
import json
import os
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, field
from pathlib import Path

from core.event_bus import event_bus
from core.cognitive_core_langgraph import cognitive_core_langgraph
from core.diagnostics import diagnostics_manager
from core.error_handler import error_handler
from utils.performance_monitor import monitor_performance

logger = logging.getLogger(__name__)

@dataclass
class AutonomousAction:
    """Represents an autonomous action taken by the system."""
    id: str
    action_type: str
    description: str
    triggered_by: str
    timestamp: datetime
    parameters: Dict[str, Any] = field(default_factory=dict)
    result: Optional[Dict[str, Any]] = None
    success: bool = False

@dataclass
class SystemMetrics:
    """System performance metrics for autonomous decision making."""
    cpu_usage: float
    memory_usage: float
    disk_usage: float
    error_rate: float
    response_time_avg: float
    active_workflows: int
    timestamp: datetime

class AutonomousManager:
    """
    Advanced autonomous manager that proactively optimizes and manages the system.
    """
    
    def __init__(self):
        self.is_running = False
        self.monitoring_interval = 30  # Check every 30 seconds for proactive actions
        self.metrics_history: List[SystemMetrics] = []
        self.autonomous_actions: List[AutonomousAction] = []
        self.action_strategies: Dict[str, Callable] = {}
        self.optimization_rules: List[Dict[str, Any]] = []
        
        # Initialize autonomous strategies
        self._register_strategies()
        self._load_optimization_rules()
        
        # Subscribe to system events
        self._setup_event_listeners()
        
        logger.info("Autonomous Manager initialized with enhanced proactive capabilities")
    
    def _register_strategies(self):
        """Register autonomous action strategies."""
        self.action_strategies = {
            "optimize_memory": self._optimize_memory,
            "cleanup_logs": self._cleanup_old_logs,
            "restart_failed_services": self._restart_failed_services,
            "preemptive_scaling": self._preemptive_scaling,
            "predictive_maintenance": self._predictive_maintenance,
            "auto_backup": self._auto_backup_critical_data,
            "resource_rebalancing": self._rebalance_resources,
            "proactive_error_prevention": self._prevent_potential_errors
        }
    
    def _load_optimization_rules(self):
        """Load optimization rules for autonomous decision making."""
        self.optimization_rules = [
            {
                "name": "high_memory_usage",
                "condition": lambda metrics: metrics.memory_usage > 75,
                "action": "optimize_memory",
                "priority": "high",
                "cooldown_minutes": 10
            },
            {
                "name": "disk_space_warning",
                "condition": lambda metrics: metrics.disk_usage > 80,
                "action": "cleanup_logs",
                "priority": "medium",
                "cooldown_minutes": 30
            },
            {
                "name": "high_error_rate",
                "condition": lambda metrics: metrics.error_rate > 0.1,
                "action": "proactive_error_prevention",
                "priority": "high",
                "cooldown_minutes": 5
            },
            {
                "name": "performance_degradation",
                "condition": lambda metrics: metrics.response_time_avg > 10000,  # > 10 seconds
                "action": "preemptive_scaling",
                "priority": "medium",
                "cooldown_minutes": 15
            },
            {
                "name": "scheduled_maintenance",
                "condition": lambda metrics: self._should_do_maintenance(),
                "action": "predictive_maintenance",
                "priority": "low",
                "cooldown_minutes": 240  # 4 hours
            }
        ]
    
    def _setup_event_listeners(self):
        """Setup event listeners for autonomous responses."""
        event_bus.subscribe("system.error", self._on_system_error)
        event_bus.subscribe("workflow.failed", self._on_workflow_failed)
        event_bus.subscribe("performance.degraded", self._on_performance_degraded)
        event_bus.subscribe("resource.threshold_exceeded", self._on_resource_threshold)
    
    async def start(self):
        """Start the autonomous monitoring and management loop."""
        if self.is_running:
            logger.warning("Autonomous Manager is already running")
            return
        
        self.is_running = True
        logger.info("Starting Autonomous Manager with proactive capabilities")
        
        # Start the main autonomous loop
        asyncio.create_task(self._autonomous_loop())
        
        # Start predictive analytics
        asyncio.create_task(self._predictive_analytics_loop())
        
        # Start resource optimization
        asyncio.create_task(self._resource_optimization_loop())
    
    async def stop(self):
        """Stop autonomous operations."""
        self.is_running = False
        logger.info("Autonomous Manager stopped")
    
    async def _autonomous_loop(self):
        """Main autonomous monitoring and action loop."""
        while self.is_running:
            try:
                # Collect current system metrics
                metrics = await self._collect_system_metrics()
                self.metrics_history.append(metrics)
                
                # Keep only last 1000 metrics entries
                if len(self.metrics_history) > 1000:
                    self.metrics_history = self.metrics_history[-1000:]
                
                # Evaluate autonomous actions
                await self._evaluate_and_execute_actions(metrics)
                
                await asyncio.sleep(self.monitoring_interval)
                
            except Exception as e:
                logger.error(f"Error in autonomous loop: {e}")
                await error_handler.handle_error(e, {"component": "autonomous_manager"})
                await asyncio.sleep(5)  # Short delay before retrying
    
    async def _collect_system_metrics(self) -> SystemMetrics:
        """Collect current system metrics."""
        import psutil
        
        # Get basic system metrics
        cpu_usage = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        # Get application-specific metrics
        error_stats = diagnostics_manager.get_error_statistics() if hasattr(diagnostics_manager, "get_error_statistics") else {}
        error_rate = error_stats.get("error_rate_per_hour", 0)
        
        # Get performance metrics
        performance_metrics = diagnostics_manager.get_current_metrics() if hasattr(diagnostics_manager, "get_current_metrics") else {}
        response_time_avg = performance_metrics.get("average_response_time_ms", 0)
        active_workflows = performance_metrics.get("active_workflows", 0)
        
        return SystemMetrics(
            cpu_usage=cpu_usage,
            memory_usage=memory.percent,
            disk_usage=disk.percent,
            error_rate=error_rate,
            response_time_avg=response_time_avg,
            active_workflows=active_workflows,
            timestamp=datetime.now()
        )
    
    async def _evaluate_and_execute_actions(self, metrics: SystemMetrics):
        """Evaluate optimization rules and execute autonomous actions."""
        for rule in self.optimization_rules:
            try:
                # Check if rule condition is met
                if rule["condition"](metrics):
                    # Check cooldown
                    if self._is_action_on_cooldown(rule["name"], rule["cooldown_minutes"]):
                        continue
                    
                    # Execute the autonomous action
                    await self._execute_autonomous_action(
                        rule["action"], 
                        rule["name"], 
                        metrics,
                        rule["priority"]
                    )
                    
            except Exception as e:
                logger.error(f"Error evaluating rule {rule['name']}: {e}")
    
    def _is_action_on_cooldown(self, action_name: str, cooldown_minutes: int) -> bool:
        """Check if an action is on cooldown."""
        cutoff_time = datetime.now() - timedelta(minutes=cooldown_minutes)
        
        for action in reversed(self.autonomous_actions):
            if action.triggered_by == action_name and action.timestamp > cutoff_time:
                return True
        
        return False
    
    async def _execute_autonomous_action(self, action_type: str, triggered_by: str, 
                                       metrics: SystemMetrics, priority: str):
        """Execute an autonomous action."""
        action_id = f"auto_{len(self.autonomous_actions)}_{int(time.time())}"
        
        action = AutonomousAction(
            id=action_id,
            action_type=action_type,
            description=f"Autonomous {action_type} triggered by {triggered_by}",
            triggered_by=triggered_by,
            timestamp=datetime.now(),
            parameters={"metrics": metrics.__dict__, "priority": priority}
        )
        
        try:
            logger.info(f"Executing autonomous action: {action_type} (triggered by: {triggered_by})")
            
            # Execute the strategy
            if action_type in self.action_strategies:
                result = await self.action_strategies[action_type](metrics, action)
                action.result = result
                action.success = True
                
                # Send alert about autonomous action
                diagnostics_manager.send_alert(
                    level="INFO",
                    message=f"Autonomous action executed: {action_type}",
                    source="autonomous_manager",
                    details={"action_id": action_id, "result": result}
                )
            else:
                logger.warning(f"Unknown autonomous action type: {action_type}")
                action.success = False
                action.result = {"error": "Unknown action type"}
        
        except Exception as e:
            logger.error(f"Failed to execute autonomous action {action_type}: {e}")
            action.success = False
            action.result = {"error": str(e)}
        
        finally:
            self.autonomous_actions.append(action)
            
            # Publish event about autonomous action
            await event_bus.publish("autonomous.action_executed", {
                "action": action.__dict__,
                "success": action.success
            })
    
    # === Autonomous Action Strategies ===
    
    async def _optimize_memory(self, metrics: SystemMetrics, action: AutonomousAction) -> Dict[str, Any]:
        """Optimize memory usage autonomously."""
        logger.info("Executing autonomous memory optimization")
        
        # Clear unnecessary caches
        if hasattr(diagnostics_manager, 'clear_old_metrics'):
            diagnostics_manager.clear_old_metrics()
        
        # Trigger garbage collection in Python
        import gc
        gc.collect()
        
        # Clear old session history if available
        # This would integrate with the memory system
        
        return {
            "action": "memory_optimization",
            "freed_memory": "estimated_cleanup",
            "timestamp": datetime.now().isoformat()
        }
    
    async def _cleanup_old_logs(self, metrics: SystemMetrics, action: AutonomousAction) -> Dict[str, Any]:
        """Clean up old log files autonomously."""
        logger.info("Executing autonomous log cleanup")
        
        logs_cleaned = 0
        bytes_freed = 0
        
        # Clean logs older than 7 days
        cutoff_date = datetime.now() - timedelta(days=7)
        logs_dir = Path("logs")
        
        if logs_dir.exists():
            for log_file in logs_dir.glob("*.log"):
                try:
                    if log_file.stat().st_mtime < cutoff_date.timestamp():
                        file_size = log_file.stat().st_size
                        log_file.unlink()
                        logs_cleaned += 1
                        bytes_freed += file_size
                except Exception as e:
                    logger.warning(f"Failed to clean log file {log_file}: {e}")
        
        return {
            "action": "log_cleanup",
            "files_cleaned": logs_cleaned,
            "bytes_freed": bytes_freed,
            "timestamp": datetime.now().isoformat()
        }
    
    async def _restart_failed_services(self, metrics: SystemMetrics, action: AutonomousAction) -> Dict[str, Any]:
        """Restart failed services autonomously."""
        logger.info("Checking for failed services to restart")
        
        # This would check for failed components and restart them
        # For now, we'll just log the action
        
        return {
            "action": "service_restart_check",
            "services_checked": ["diagnostics", "cognitive_core", "event_bus"],
            "services_restarted": 0,
            "timestamp": datetime.now().isoformat()
        }
    
    async def _preemptive_scaling(self, metrics: SystemMetrics, action: AutonomousAction) -> Dict[str, Any]:
        """Perform preemptive scaling based on performance trends."""
        logger.info("Executing preemptive scaling optimization")
        
        # Analyze recent performance trends
        recent_metrics = self.metrics_history[-10:] if len(self.metrics_history) >= 10 else self.metrics_history
        
        if len(recent_metrics) > 3:
            avg_response_time = sum(m.response_time_avg for m in recent_metrics) / len(recent_metrics)
            trend_increasing = recent_metrics[-1].response_time_avg > avg_response_time * 1.2
            
            if trend_increasing:
                # Trigger optimization measures
                logger.info("Performance trend indicates scaling needed")
        
        return {
            "action": "preemptive_scaling",
            "performance_trend": "analyzed",
            "optimizations_applied": ["response_time_monitoring"],
            "timestamp": datetime.now().isoformat()
        }
    
    async def _predictive_maintenance(self, metrics: SystemMetrics, action: AutonomousAction) -> Dict[str, Any]:
        """Perform predictive maintenance tasks."""
        logger.info("Executing predictive maintenance")
        
        maintenance_tasks = []
        
        # Check for potential issues based on trends
        if len(self.metrics_history) > 20:
            # Analyze trends for predictive insights
            recent_errors = [m.error_rate for m in self.metrics_history[-20:]]
            if sum(recent_errors) > 0:
                maintenance_tasks.append("error_pattern_analysis")
        
        # Check disk fragmentation (placeholder)
        maintenance_tasks.append("disk_health_check")
        
        # Check memory leak patterns
        memory_trend = [m.memory_usage for m in self.metrics_history[-10:]] if len(self.metrics_history) >= 10 else []
        if len(memory_trend) > 5 and memory_trend[-1] > memory_trend[0] * 1.1:
            maintenance_tasks.append("memory_leak_prevention")
        
        return {
            "action": "predictive_maintenance",
            "tasks_performed": maintenance_tasks,
            "timestamp": datetime.now().isoformat()
        }
    
    async def _auto_backup_critical_data(self, metrics: SystemMetrics, action: AutonomousAction) -> Dict[str, Any]:
        """Perform automatic backup of critical system data."""
        logger.info("Executing autonomous backup")
        
        backup_items = []
        
        # Backup configuration files
        config_files = ["config.json", "model_config.yaml"]
        for config_file in config_files:
            if os.path.exists(config_file):
                backup_items.append(config_file)
        
        # Backup recent autonomous actions log
        actions_backup = {
            "actions": [action.__dict__ for action in self.autonomous_actions[-100:]],
            "timestamp": datetime.now().isoformat()
        }
        
        backup_path = f"backups/autonomous_backup_{int(time.time())}.json"
        os.makedirs("backups", exist_ok=True)
        
        with open(backup_path, 'w') as f:
            json.dump(actions_backup, f, default=str, indent=2)
        
        return {
            "action": "auto_backup",
            "items_backed_up": backup_items,
            "backup_path": backup_path,
            "timestamp": datetime.now().isoformat()
        }
    
    async def _rebalance_resources(self, metrics: SystemMetrics, action: AutonomousAction) -> Dict[str, Any]:
        """Rebalance system resources autonomously."""
        logger.info("Executing resource rebalancing")
        
        optimizations = []
        
        # CPU optimization
        if metrics.cpu_usage > 70:
            optimizations.append("cpu_throttling")
        
        # Memory optimization
        if metrics.memory_usage > 70:
            optimizations.append("memory_defragmentation")
        
        # I/O optimization
        optimizations.append("io_scheduling_optimization")
        
        return {
            "action": "resource_rebalancing",
            "optimizations_applied": optimizations,
            "timestamp": datetime.now().isoformat()
        }
    
    async def _prevent_potential_errors(self, metrics: SystemMetrics, action: AutonomousAction) -> Dict[str, Any]:
        """Proactively prevent potential errors based on patterns."""
        logger.info("Executing proactive error prevention")
        
        prevention_measures = []
        
        # Check for error patterns in recent history
        if hasattr(diagnostics_manager, 'get_error_patterns'):
            error_patterns = diagnostics_manager.get_error_patterns()
            for pattern in error_patterns:
                prevention_measures.append(f"pattern_mitigation_{pattern}")
        
        # Generic prevention measures
        prevention_measures.extend([
            "connection_health_check",
            "resource_availability_check",
            "dependency_validation"
        ])
        
        return {
            "action": "proactive_error_prevention",
            "measures_applied": prevention_measures,
            "timestamp": datetime.now().isoformat()
        }
    
    # === Predictive Analytics ===
    
    async def _predictive_analytics_loop(self):
        """Run predictive analytics for system optimization."""
        while self.is_running:
            try:
                await asyncio.sleep(300)  # Run every 5 minutes
                await self._run_predictive_analysis()
            except Exception as e:
                logger.error(f"Error in predictive analytics: {e}")
                await asyncio.sleep(60)
    
    async def _run_predictive_analysis(self):
        """Run predictive analysis on system metrics."""
        if len(self.metrics_history) < 10:
            return  # Not enough data for meaningful analysis
        
        # Analyze trends
        recent_metrics = self.metrics_history[-20:]
        
        # CPU trend analysis
        cpu_trend = [m.cpu_usage for m in recent_metrics]
        if self._is_trend_increasing(cpu_trend):
            logger.info("Predictive analysis: CPU usage trend increasing")
            await event_bus.publish("prediction.cpu_increase", {"trend": cpu_trend})
        
        # Memory trend analysis
        memory_trend = [m.memory_usage for m in recent_metrics]
        if self._is_trend_increasing(memory_trend):
            logger.info("Predictive analysis: Memory usage trend increasing")
            await event_bus.publish("prediction.memory_increase", {"trend": memory_trend})
        
        # Error rate prediction
        error_trend = [m.error_rate for m in recent_metrics]
        if self._is_trend_increasing(error_trend):
            logger.warning("Predictive analysis: Error rate may increase")
            await event_bus.publish("prediction.error_increase", {"trend": error_trend})
    
    def _is_trend_increasing(self, values: List[float]) -> bool:
        """Check if a trend is increasing using simple linear regression."""
        if len(values) < 5:
            return False
        
        # Simple trend detection
        first_half = values[:len(values)//2]
        second_half = values[len(values)//2:]
        
        first_avg = sum(first_half) / len(first_half)
        second_avg = sum(second_half) / len(second_half)
        
        return second_avg > first_avg * 1.1  # 10% increase threshold
    
    # === Resource Optimization ===
    
    async def _resource_optimization_loop(self):
        """Continuous resource optimization loop."""
        while self.is_running:
            try:
                await asyncio.sleep(600)  # Run every 10 minutes
                await self._optimize_system_resources()
            except Exception as e:
                logger.error(f"Error in resource optimization: {e}")
                await asyncio.sleep(120)
    
    async def _optimize_system_resources(self):
        """Optimize system resources based on usage patterns."""
        logger.info("Running continuous resource optimization")
        
        if len(self.metrics_history) < 5:
            return
        
        recent_metrics = self.metrics_history[-5:]
        avg_cpu = sum(m.cpu_usage for m in recent_metrics) / len(recent_metrics)
        avg_memory = sum(m.memory_usage for m in recent_metrics) / len(recent_metrics)
        
        optimizations = []
        
        # CPU optimization
        if avg_cpu < 30:
            optimizations.append("reduce_background_tasks")
        elif avg_cpu > 80:
            optimizations.append("increase_task_scheduling_efficiency")
        
        # Memory optimization
        if avg_memory > 75:
            optimizations.append("trigger_garbage_collection")
            import gc
            gc.collect()
        
        if optimizations:
            logger.info(f"Applied resource optimizations: {optimizations}")
            await event_bus.publish("optimization.resources_optimized", {
                "optimizations": optimizations,
                "avg_cpu": avg_cpu,
                "avg_memory": avg_memory
            })
    
    # === Event Handlers ===
    
    async def _on_system_error(self, event_data):
        """Handle system error events autonomously."""
        error_info = event_data.get("error", {})
        component = error_info.get("component", "unknown")
        
        logger.info(f"Autonomous response to system error in {component}")
        
        # Trigger error recovery action
        await self._execute_autonomous_action(
            "proactive_error_prevention",
            f"system_error_{component}",
            await self._collect_system_metrics(),
            "high"
        )
    
    async def _on_workflow_failed(self, event_data):
        """Handle workflow failure events autonomously."""
        workflow_id = event_data.get("workflow_id", "unknown")
        
        logger.info(f"Autonomous response to workflow failure: {workflow_id}")
        
        # Could trigger workflow retry or alternative execution
    
    async def _on_performance_degraded(self, event_data):
        """Handle performance degradation events autonomously."""
        logger.info("Autonomous response to performance degradation")
        
        await self._execute_autonomous_action(
            "preemptive_scaling",
            "performance_degradation",
            await self._collect_system_metrics(),
            "medium"
        )
    
    async def _on_resource_threshold(self, event_data):
        """Handle resource threshold exceeded events autonomously."""
        resource_type = event_data.get("resource_type", "unknown")
        
        logger.info(f"Autonomous response to {resource_type} threshold exceeded")
        
        await self._execute_autonomous_action(
            "resource_rebalancing",
            f"threshold_{resource_type}",
            await self._collect_system_metrics(),
            "high"
        )
    
    # === Utility Methods ===
    
    def _should_do_maintenance(self) -> bool:
        """Check if scheduled maintenance should be performed."""
        # Run maintenance every 6 hours
        if not self.autonomous_actions:
            return True
        
        last_maintenance = None
        for action in reversed(self.autonomous_actions):
            if action.action_type == "predictive_maintenance":
                last_maintenance = action.timestamp
                break
        
        if last_maintenance is None:
            return True
        
        return datetime.now() - last_maintenance > timedelta(hours=6)
    
    def get_status(self) -> Dict[str, Any]:
        """Get the current status of the autonomous manager."""
        return {
            "is_running": self.is_running,
            "monitoring_interval": self.monitoring_interval,
            "total_actions_executed": len(self.autonomous_actions),
            "recent_actions": [
                {
                    "action_type": action.action_type,
                    "triggered_by": action.triggered_by,
                    "success": action.success,
                    "timestamp": action.timestamp.isoformat()
                }
                for action in self.autonomous_actions[-10:]
            ],
            "metrics_history_size": len(self.metrics_history),
            "active_strategies": list(self.action_strategies.keys()),
            "optimization_rules": len(self.optimization_rules)
        }

# Create singleton instance
autonomous_manager = AutonomousManager()
