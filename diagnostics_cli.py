"""
Diagnostics Command Line Interface
---------------------------------
This module provides a command-line interface for accessing the Project-S
diagnostic capabilities and tools.
"""

import argparse
import asyncio
import json
import logging
import os
import sys
from datetime import datetime
from typing import Dict, Any, List, Optional, Union

# Add the project root to the path for imports
import sys
from pathlib import Path
project_root = Path(__file__).parent.parent.resolve()
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from core.diagnostics import diagnostics_manager
from integrations.workflow_visualizer import workflow_visualizer
from integrations.langgraph_error_monitor import error_monitor
from integrations.diagnostics_dashboard import dashboard

logger = logging.getLogger(__name__)

class DiagnosticsCLI:
    """
    Command-line interface for diagnostic operations and tools.
    """
    
    def __init__(self):
        """Initialize the diagnostics CLI"""
        self.parser = argparse.ArgumentParser(
            description="Project-S Diagnostics CLI",
            formatter_class=argparse.RawDescriptionHelpFormatter
        )
        self._setup_commands()
    
    def _setup_commands(self):
        """Set up the command-line commands and arguments"""
        subparsers = self.parser.add_subparsers(dest="command", help="Command to execute")
        
        # Status command
        status_parser = subparsers.add_parser("status", help="Show system status")
        status_parser.add_argument("--verbose", "-v", action="store_true", help="Show detailed status")
        
        # Performance command
        perf_parser = subparsers.add_parser("performance", help="Show performance metrics")
        perf_parser.add_argument("--report", "-r", action="store_true", help="Generate a full report")
        perf_parser.add_argument("--output", "-o", help="Output file path")
        
        # Errors command
        error_parser = subparsers.add_parser("errors", help="Show error information")
        error_parser.add_argument("--stats", "-s", action="store_true", help="Show error statistics")
        error_parser.add_argument("--list", "-l", action="store_true", help="List recent errors")
        error_parser.add_argument("--count", "-c", type=int, default=10, help="Number of errors to show")
        error_parser.add_argument("--output", "-o", help="Export error data to file")
        
        # Workflow command
        workflow_parser = subparsers.add_parser("workflow", help="Workflow diagnostics")
        workflow_parser.add_argument("--id", required=True, help="Workflow ID")
        workflow_parser.add_argument("--visualize", "-v", action="store_true", help="Visualize workflow")
        workflow_parser.add_argument("--export", "-e", help="Export workflow data format (json or yaml)")
        workflow_parser.add_argument("--output", "-o", help="Output file path")
        
        # Dashboard command
        dashboard_parser = subparsers.add_parser("dashboard", help="Control the diagnostics dashboard")
        dashboard_parser.add_argument("--start", action="store_true", help="Start the dashboard")
        dashboard_parser.add_argument("--stop", action="store_true", help="Stop the dashboard")
        dashboard_parser.add_argument("--port", type=int, default=7777, help="Dashboard port")
        
        # Logs command
        logs_parser = subparsers.add_parser("logs", help="View and manage logs")
        logs_parser.add_argument("--tail", "-t", type=int, default=20, help="Show last N log lines")
        logs_parser.add_argument("--level", "-l", choices=["debug", "info", "warning", "error", "critical"], 
                                 default="info", help="Minimum log level to show")
        logs_parser.add_argument("--follow", "-f", action="store_true", help="Follow log output")
        logs_parser.add_argument("--errors-only", "-e", action="store_true", help="Show only error logs")
        
        # Monitor command
        monitor_parser = subparsers.add_parser("monitor", help="Real-time monitoring")
        monitor_parser.add_argument("--interval", "-i", type=int, default=2, help="Update interval in seconds")
        monitor_parser.add_argument("--metrics", "-m", choices=["cpu", "memory", "all"], default="all", 
                                    help="Metrics to monitor")
        
        # Alerts command
        alerts_parser = subparsers.add_parser("alerts", help="View system alerts")
        alerts_parser.add_argument("--count", "-c", type=int, default=10, help="Number of alerts to show")
        alerts_parser.add_argument("--level", "-l", choices=["info", "warning", "critical"], 
                                   help="Filter by alert level")
        
    async def run(self, args=None):
        """Run the CLI with the provided arguments"""
        parsed_args = self.parser.parse_args(args)
        
        if not parsed_args.command:
            self.parser.print_help()
            return 1
        
        try:
            command_method = getattr(self, f"_handle_{parsed_args.command}", None)
            if command_method:
                return await command_method(parsed_args)
            else:
                print(f"Unknown command: {parsed_args.command}")
                return 1
        except Exception as e:
            print(f"Error: {e}")
            logger.exception(f"CLI error when executing {parsed_args.command}")
            return 1
    
    async def _handle_status(self, args):
        """Handle the 'status' command"""
        print("Project-S System Status")
        print("=" * 50)
        
        # Basic metrics
        metrics = diagnostics_manager.get_current_metrics() if hasattr(diagnostics_manager, "get_current_metrics") else {}
        
        uptime_seconds = metrics.get("process_uptime_seconds", 0)
        uptime_str = self._format_duration(uptime_seconds)
        
        print(f"Uptime: {uptime_str}")
        print(f"CPU Usage: {metrics.get('cpu_percent', 0):.1f}%")
        print(f"Memory Usage: {metrics.get('memory_percent', 0):.1f}% ({metrics.get('memory_used_mb', 0):.1f} MB)")
        print(f"Threads: {metrics.get('threads_count', 0)}")
        
        # Error and workflow stats
        error_stats = diagnostics_manager.get_error_statistics() if hasattr(diagnostics_manager, "get_error_statistics") else {}
        total_errors = error_stats.get("total_errors", 0)
        
        print(f"Total Errors: {total_errors}")
        
        # Workflow stats from performance report
        report = diagnostics_manager.generate_performance_report(output_path=None, include_graphs=False) or {}
        workflow_stats = report.get("workflows", {})
        
        print(f"Workflows: {workflow_stats.get('completed', 0)} completed, {workflow_stats.get('failed', 0)} failed")
        
        # Alert count
        alert_count = len(diagnostics_manager.alert_history) if hasattr(diagnostics_manager, "alert_history") else 0
        print(f"Active Alerts: {alert_count}")
        
        # Detailed status
        if args.verbose:
            print("\nDetailed Status")
            print("-" * 50)
            
            # System information
            print("\nSystem Information:")
            import platform
            print(f"  Platform: {platform.system()} {platform.release()}")
            print(f"  Python: {platform.python_version()}")
            
            # Network status
            print("\nNetwork Status:")
            import socket
            hostname = socket.gethostname()
            try:
                local_ip = socket.gethostbyname(hostname)
                print(f"  Hostname: {hostname}")
                print(f"  Local IP: {local_ip}")
            except socket.error:
                print("  Network information unavailable")
            
            # Top error types
            if error_stats.get("top_error_types"):
                print("\nTop Error Types:")
                for error_type, count in error_stats.get("top_error_types", {}).items():
                    print(f"  {error_type}: {count}")
            
            # Recent alerts
            if alert_count > 0 and hasattr(diagnostics_manager, "alert_history"):
                print("\nRecent Alerts:")
                for alert in diagnostics_manager.alert_history[-5:]:
                    timestamp = alert.timestamp.strftime("%Y-%m-%d %H:%M:%S") if hasattr(alert, "timestamp") else "unknown"
                    level = alert.level.name if hasattr(alert.level, "name") else alert.level
                    message = alert.message if hasattr(alert, "message") else str(alert)
                    print(f"  [{timestamp}] {level}: {message}")
        
        return 0
    
    async def _handle_performance(self, args):
        """Handle the 'performance' command"""
        if args.report:
            # Generate a full performance report
            output_path = args.output
            if not output_path:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_path = f"diagnostics/reports/performance_{timestamp}.json"
            
            report = diagnostics_manager.generate_performance_report(output_path=output_path)
            
            print(f"Performance report generated at: {output_path}")
            
            # Display report summary
            print("\nPerformance Report Summary")
            print("=" * 50)
            
            print(f"CPU Average: {report.get('averages', {}).get('cpu_percent', 0):.1f}%")
            print(f"Memory Average: {report.get('averages', {}).get('memory_percent', 0):.1f}%")
            
            workflows = report.get("workflows", {})
            completed = workflows.get("completed", 0)
            failed = workflows.get("failed", 0)
            total = workflows.get("total", 0)
            
            print(f"Workflow Success Rate: {workflows.get('success_rate_percent', 0):.1f}%")
            print(f"Total Workflows: {total} ({completed} completed, {failed} failed)")
            
            # Show graph paths if available
            graph_paths = report.get("graph_paths", {})
            if graph_paths:
                print("\nGenerated Graphs:")
                for graph_type, path in graph_paths.items():
                    print(f"  {graph_type}: {path}")
        else:
            # Show current performance metrics
            metrics = diagnostics_manager.get_current_metrics() if hasattr(diagnostics_manager, "get_current_metrics") else {}
            
            print("Current Performance Metrics")
            print("=" * 50)
            
            print(f"CPU Usage: {metrics.get('cpu_percent', 0):.1f}%")
            print(f"Memory Usage: {metrics.get('memory_percent', 0):.1f}% ({metrics.get('memory_used_mb', 0):.1f} MB)")
            print(f"Threads: {metrics.get('threads_count', 0)}")
            print(f"Open Files: {metrics.get('open_file_descriptors', 0)}")
            
            # Display API response times
            response_times = metrics.get("response_times_ms", {})
            if response_times:
                print("\nAPI Response Times (ms):")
                for endpoint, time_ms in response_times.items():
                    print(f"  {endpoint}: {time_ms:.1f} ms")
        
        return 0
    
    async def _handle_errors(self, args):
        """Handle the 'errors' command"""
        if args.stats:
            # Show error statistics
            error_stats = diagnostics_manager.get_error_statistics() if hasattr(diagnostics_manager, "get_error_statistics") else {}
            
            print("Error Statistics")
            print("=" * 50)
            
            total_errors = error_stats.get("total_errors", 0)
            print(f"Total Errors: {total_errors}")
            
            # Top error types
            if error_stats.get("top_error_types"):
                print("\nTop Error Types:")
                for error_type, count in error_stats.get("top_error_types", {}).items():
                    print(f"  {error_type}: {count}")
            
            # Top error components
            if error_stats.get("top_error_components"):
                print("\nTop Error Components:")
                for component, count in error_stats.get("top_error_components", {}).items():
                    print(f"  {component}: {count}")
            
            # Error timeline
            if error_stats.get("error_timeline"):
                print("\nError Timeline:")
                for hour, count in error_stats.get("error_timeline", {}).items():
                    print(f"  {hour}: {count} errors")
        
        elif args.list:
            # List recent errors
            errors = diagnostics_manager.error_history if hasattr(diagnostics_manager, "error_history") else []
            count = min(args.count, len(errors))
            
            if count == 0:
                print("No errors found")
                return 0
                
            print(f"Recent Errors (showing {count} of {len(errors)})")
            print("=" * 50)
            
            for i, error in enumerate(errors[-count:]):
                timestamp = error.timestamp.strftime("%Y-%m-%d %H:%M:%S") if hasattr(error, "timestamp") else "unknown"
                print(f"\nError #{i+1} - {timestamp}")
                print(f"Type: {error.error_type if hasattr(error, 'error_type') else 'Unknown'}")
                print(f"Message: {error.message if hasattr(error, 'message') else str(error)}")
                
                if hasattr(error, "component") and error.component:
                    print(f"Component: {error.component}")
                    
                if hasattr(error, "workflow_id") and error.workflow_id:
                    print(f"Workflow ID: {error.workflow_id}")
                    
                print("-" * 30)
        
        elif args.output:
            # Export error data
            if not hasattr(error_monitor, "export_error_data"):
                print("Error export functionality not available")
                return 1
                
            success = error_monitor.export_error_data(args.output)
            if success:
                print(f"Error data exported to {args.output}")
            else:
                print("Failed to export error data")
                return 1
        
        else:
            # Default error summary
            error_stats = diagnostics_manager.get_error_statistics() if hasattr(diagnostics_manager, "get_error_statistics") else {}
            total_errors = error_stats.get("total_errors", 0)
            
            print("Error Summary")
            print("=" * 50)
            print(f"Total Errors: {total_errors}")
            
            if total_errors > 0:
                print("\nUse '--stats' for detailed statistics")
                print("Use '--list' to show recent errors")
        
        return 0
    
    async def _handle_workflow(self, args):
        """Handle the 'workflow' command"""
        workflow_id = args.id
        
        # Get workflow data from error monitor
        workflow_data = error_monitor.get_workflow_state(workflow_id) if hasattr(error_monitor, "get_workflow_state") else None
        
        if not workflow_data:
            print(f"No data found for workflow: {workflow_id}")
            return 1
        
        # Visualize workflow
        if args.visualize:
            try:
                output_path = await workflow_visualizer.visualize_workflow(workflow_id, workflow_data)
                if output_path:
                    print(f"Workflow visualization saved to: {output_path}")
                else:
                    print("Failed to visualize workflow")
                    return 1
            except Exception as e:
                print(f"Error visualizing workflow: {e}")
                return 1
        
        # Export workflow data
        if args.export:
            try:
                output_path = args.output
                export_format = args.export.lower()
                if export_format not in ["json", "yaml", "yml"]:
                    print(f"Unsupported export format: {export_format}")
                    print("Supported formats: json, yaml")
                    return 1
                
                result = workflow_visualizer.export_workflow_data(
                    workflow_id, 
                    workflow_data,
                    output_path=output_path,
                    format=export_format
                )
                
                if result:
                    print(f"Workflow data exported to: {result}")
                else:
                    print("Failed to export workflow data")
                    return 1
            except Exception as e:
                print(f"Error exporting workflow data: {e}")
                return 1
        
        # If no action specified, show workflow summary
        if not args.visualize and not args.export:
            print(f"Workflow Summary: {workflow_id}")
            print("=" * 50)
            
            print(f"Status: {workflow_data.get('status', 'unknown')}")
            
            if 'current_task' in workflow_data and workflow_data['current_task']:
                task = workflow_data['current_task']
                print(f"Current Task: {task.get('name', 'unknown')}")
            
            if 'retry_count' in workflow_data:
                print(f"Retry Count: {workflow_data['retry_count']}")
                
            if 'error_info' in workflow_data and workflow_data['error_info']:
                print(f"\nError: {workflow_data['error_info'].get('error_type', 'unknown')}")
                print(f"Message: {workflow_data['error_info'].get('error_message', 'unknown')}")
                
            # Workflow steps summary
            steps = workflow_data.get('context', {}).get('workflow_steps', [])
            if steps:
                print(f"\nWorkflow Steps: {len(steps)}")
                for i, step in enumerate(steps):
                    status = "✓" if step.get('status') == 'completed' else "○"
                    print(f"  {status} {i+1}. {step.get('name', f'Step {i+1}')}")
                    
            print("\nUse '--visualize' to generate a graph visualization")
            print("Use '--export json' or '--export yaml' to export workflow data")
        
        return 0
    
    async def _handle_dashboard(self, args):
        """Handle the 'dashboard' command"""
        if args.start:
            dashboard.port = args.port
            success = await dashboard.start()
            if success:
                print(f"Diagnostic dashboard started at http://127.0.0.1:{args.port}")
                print("Press Ctrl+C to exit")
                
                # Keep the dashboard running
                try:
                    while True:
                        await asyncio.sleep(1)
                except KeyboardInterrupt:
                    print("\nStopping dashboard...")
                    await dashboard.stop()
            else:
                print("Failed to start diagnostic dashboard")
                return 1
        
        elif args.stop:
            await dashboard.stop()
            print("Diagnostic dashboard stopped")
        
        else:
            print("Please specify an action: --start or --stop")
            return 1
            
        return 0
    
    async def _handle_logs(self, args):
        """Handle the 'logs' command"""
        log_file = "logs/project_s_errors.log" if args.errors_only else "logs/project_s_full.log"
        
        if not os.path.exists(log_file):
            print(f"Log file not found: {log_file}")
            return 1
        
        # Set level filter based on argument
        level_map = {
            "debug": 10,
            "info": 20,
            "warning": 30,
            "error": 40,
            "critical": 50
        }
        min_level = level_map.get(args.level.lower(), 20)
        
        # Read and display logs
        if args.follow:
            import subprocess
            import shutil
            
            # Use 'tail -f' if available, otherwise fallback to Python
            tail_cmd = shutil.which("tail")
            if tail_cmd:
                cmd = [tail_cmd, "-f", "-n", str(args.tail), log_file]
                try:
                    subprocess.run(cmd)
                except KeyboardInterrupt:
                    print("\nStopped following logs")
            else:
                # Python fallback
                print(f"Following {log_file} (press Ctrl+C to stop)...")
                try:
                    with open(log_file, "r") as f:
                        # Go to the end of file
                        f.seek(0, 2)
                        
                        while True:
                            line = f.readline()
                            if line:
                                # Simple level filtering
                                if min_level <= 20 or "[WARNING]" in line or "[ERROR]" in line or "[CRITICAL]" in line:
                                    print(line, end="")
                            else:
                                await asyncio.sleep(0.1)
                except KeyboardInterrupt:
                    print("\nStopped following logs")
        else:
            # Display last N lines
            try:
                import subprocess
                import shutil
                
                tail_cmd = shutil.which("tail")
                if tail_cmd:
                    subprocess.run([tail_cmd, "-n", str(args.tail), log_file])
                else:
                    # Python fallback
                    from collections import deque
                    with open(log_file, "r") as f:
                        last_lines = deque(f, args.tail)
                    
                    for line in last_lines:
                        # Simple level filtering
                        if min_level <= 20 or "[WARNING]" in line or "[ERROR]" in line or "[CRITICAL]" in line:
                            print(line, end="")
            except Exception as e:
                print(f"Error reading log file: {e}")
                return 1
        
        return 0
    
    async def _handle_monitor(self, args):
        """Handle the 'monitor' command"""
        try:
            import psutil
            import time
            from datetime import datetime
            import shutil
            
            # Get terminal dimensions for display formatting
            terminal_width, _ = shutil.get_terminal_size((80, 24))
            
            print("Project-S Real-time Monitoring")
            print("=" * terminal_width)
            print("Press Ctrl+C to exit")
            print("-" * terminal_width)
            
            # Metrics to monitor based on args
            show_cpu = args.metrics in ["cpu", "all"]
            show_memory = args.metrics in ["memory", "all"]
            
            # Get the current process
            process = psutil.Process()
            
            try:
                while True:
                    # Clear previous output
                    if os.name == 'nt':
                        os.system('cls')
                    else:
                        os.system('clear')
                    
                    # Get updated metrics
                    cpu_percent = process.cpu_percent()
                    memory_info = process.memory_info()
                    memory_percent = process.memory_percent()
                    
                    # Get system-wide info
                    system_cpu = psutil.cpu_percent()
                    system_memory = psutil.virtual_memory()
                    
                    # Current time
                    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    print(f"Project-S Monitoring - {now}")
                    print("=" * terminal_width)
                    
                    # Display CPU usage
                    if show_cpu:
                        print("\nCPU Usage:")
                        process_bar = self._create_progress_bar(cpu_percent, terminal_width - 20)
                        system_bar = self._create_progress_bar(system_cpu, terminal_width - 20)
                        print(f"  Process: {cpu_percent:5.1f}% {process_bar}")
                        print(f"  System:  {system_cpu:5.1f}% {system_bar}")
                    
                    # Display memory usage
                    if show_memory:
                        print("\nMemory Usage:")
                        memory_mb = memory_info.rss / (1024 * 1024)
                        process_bar = self._create_progress_bar(memory_percent, terminal_width - 30)
                        system_bar = self._create_progress_bar(system_memory.percent, terminal_width - 30)
                        print(f"  Process: {memory_percent:5.1f}% ({memory_mb:.1f} MB) {process_bar}")
                        system_mem_gb = system_memory.used / (1024 * 1024 * 1024)
                        system_total_gb = system_memory.total / (1024 * 1024 * 1024)
                        print(f"  System:  {system_memory.percent:5.1f}% ({system_mem_gb:.1f}/{system_total_gb:.1f} GB) {system_bar}")
                    
                    # Display other metrics
                    print(f"\nThreads: {process.num_threads()}")
                    print(f"Open Files: {len(process.open_files())}")
                    print(f"Connections: {len(process.connections())}")
                    
                    # Error count
                    error_count = len(diagnostics_manager.error_history) if hasattr(diagnostics_manager, "error_history") else 0
                    print(f"Total Errors: {error_count}")
                    
                    print("\nPress Ctrl+C to exit")
                    
                    # Wait before next update
                    time.sleep(args.interval)
                    
            except KeyboardInterrupt:
                print("\nMonitoring stopped")
        except ImportError:
            print("Error: psutil module is required for monitoring")
            return 1
        
        return 0
    
    async def _handle_alerts(self, args):
        """Handle the 'alerts' command"""
        alerts = diagnostics_manager.alert_history if hasattr(diagnostics_manager, "alert_history") else []
        
        # Filter by level if specified
        if args.level:
            alerts = [a for a in alerts if hasattr(a, "level") and a.level.lower() == args.level.lower()]
        
        # Limit to requested count
        count = min(args.count, len(alerts))
        
        if not alerts:
            print("No alerts found")
            return 0
        
        print(f"System Alerts (showing {count} of {len(alerts)})")
        print("=" * 50)
        
        for i, alert in enumerate(alerts[-count:]):
            timestamp = alert.timestamp.strftime("%Y-%m-%d %H:%M:%S") if hasattr(alert, "timestamp") else "unknown"
            level = alert.level.name if hasattr(alert.level, "name") else alert.level
            source = alert.source if hasattr(alert, "source") else "unknown"
            message = alert.message if hasattr(alert, "message") else str(alert)
            
            print(f"\nAlert #{i+1} - {timestamp}")
            print(f"Level: {level}")
            print(f"Source: {source}")
            print(f"Message: {message}")
            
            # Show details if available
            if hasattr(alert, "details") and alert.details:
                print("Details:")
                for key, value in alert.details.items():
                    if isinstance(value, dict):
                        print(f"  {key}: {json.dumps(value, default=str)[:80]}...")
                    else:
                        print(f"  {key}: {value}")
            
            print("-" * 30)
        
        return 0
    
    def _format_duration(self, seconds: float) -> str:
        """Format seconds into a readable duration string"""
        days, remainder = divmod(int(seconds), 86400)
        hours, remainder = divmod(remainder, 3600)
        minutes, seconds = divmod(remainder, 60)
        
        parts = []
        if days > 0:
            parts.append(f"{days}d")
        if hours > 0 or days > 0:
            parts.append(f"{hours}h")
        if minutes > 0 or hours > 0 or days > 0:
            parts.append(f"{minutes}m")
        parts.append(f"{seconds}s")
        
        return " ".join(parts)
    
    def _create_progress_bar(self, percentage: float, width: int = 40) -> str:
        """Create a text-based progress bar"""
        filled_width = int(percentage / 100 * width)
        bar = '█' * filled_width + '░' * (width - filled_width)
        return bar


async def main():
    """Main entry point for the diagnostics CLI"""
    cli = DiagnosticsCLI()
    exit_code = await cli.run()
    sys.exit(exit_code)


if __name__ == "__main__":
    asyncio.run(main())
"""
