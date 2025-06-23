#!/usr/bin/env python3
"""
Project-S Unified CLI Interface
==============================
Unified command-line interface that integrates all Project-S functionality
into a single, modern, user-friendly CLI.

Features:
- Interactive and batch modes
- Multi-model AI support
- File operations and workflow management
- Professional CLI with argparse
- Clean error handling
- Session management
- Export capabilities

Author: Project-S Team
Version: 1.0 - Unified CLI Integration
"""

import argparse
import asyncio
import logging
import os
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional, List

# Fix Unicode encoding issues FIRST
import fix_unicode_encoding

# Configure professional logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('logs/cli_main.log', mode='w', encoding='utf-8')
    ]
)

logger = logging.getLogger("ProjectS-CLI")

# Ensure logs directory exists
os.makedirs('logs', exist_ok=True)

# Core imports
from core.event_bus import event_bus
from core.error_handler import ErrorHandler
# LangGraph Diagnostics Integration
from core.diagnostics import diagnostics_manager, AlertLevel
from integrations.langgraph_diagnostics_bridge import langgraph_diagnostics_bridge
from integrations.workflow_visualizer import workflow_visualizer
from integrations.diagnostics_dashboard import dashboard, start_dashboard, stop_dashboard
from core.diagnostics_initializer import initialize_diagnostics
# Session and Model Management
from integrations.session_manager import session_manager
from integrations.model_manager import model_manager
from integrations.multi_model_ai_client import multi_model_ai_client
from integrations.advanced_langgraph_workflow import AdvancedLangGraphWorkflow
from integrations.persistent_state_manager import persistent_state_manager
# Advanced integrations
from integrations.vscode_interface import VSCodeInterface  
from integrations.intelligent_workflow_integration import intelligent_workflow_orchestrator
from integrations.core_execution_bridge import CoreExecutionBridge

# Initialize error handler
error_handler = ErrorHandler()


class ProjectSCLI:
    """
    Unified Project-S Command Line Interface with Full Diagnostics Integration
    """
    
    def __init__(self):
        self.version = "1.0.0"
        self.session_start = datetime.now()
        self.current_session_id: Optional[str] = None
        self.workflow: Optional[AdvancedLangGraphWorkflow] = None
        self.session_history: List[Dict[str, Any]] = []
        self.diagnostics_enabled = False
        self.dashboard_running = False
        
        # Initialize advanced components
        self.vscode_interface: Optional[VSCodeInterface] = None
        self.core_execution_bridge: Optional[CoreExecutionBridge] = None
        self.performance_start_time = None
        
    async def initialize(self) -> bool:
        """Initialize the Project-S system with full diagnostics."""
        try:
            logger.info("Initializing Project-S CLI with LangGraph Diagnostics...")
            
            # Initialize diagnostics first
            await initialize_diagnostics({
                "enable_dashboard": True,
                "dashboard_port": 7777,
                "enable_performance_monitoring": True,
                "monitoring_interval_seconds": 30
            })
            self.diagnostics_enabled = True
            logger.info("✅ Diagnostics system initialized")
            
            # Initialize event bus
            event_bus.register_default_handlers()
            logger.info("✅ Event bus initialized")
            
            # Initialize LangGraph diagnostics bridge
            # Bridge is automatically initialized when imported
            logger.info("✅ LangGraph diagnostics bridge initialized")
            
            # Initialize VSCode interface
            try:
                self.vscode_interface = VSCodeInterface()
                logger.info("✅ VSCode interface initialized")
            except Exception as e:
                logger.warning(f"⚠️ VSCode interface failed to initialize: {e}")
                
            # Initialize Core Execution Bridge
            try:
                self.core_execution_bridge = CoreExecutionBridge()
                logger.info("✅ Core execution bridge initialized")
            except Exception as e:
                logger.warning(f"⚠️ Core execution bridge failed to initialize: {e}")
                
            # Initialize intelligent workflow orchestrator
            try:
                # Orchestrator is automatically initialized when imported
                logger.info("✅ Intelligent workflow orchestrator initialized")
            except Exception as e:
                logger.warning(f"⚠️ Intelligent workflow failed to initialize: {e}")
            
            # Initialize workflow
            self.workflow = AdvancedLangGraphWorkflow()
            logger.info("✅ LangGraph workflow initialized")
              # Dashboard will be started on-demand when needed
            self.dashboard_running = False
            logger.info("📊 Dashboard available (use 'diag dashboard start' to launch)")
            
            logger.info("🚀 Project-S CLI initialization complete")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize CLI: {e}")
            await error_handler.handle_error(e, {"component": "cli", "operation": "initialization"})
            return False
    
    def display_banner(self):
        """Display the Project-S CLI banner with diagnostics info."""
        print("\n" + "=" * 80)
        print(f"🚀 PROJECT-S UNIFIED CLI v{self.version}")
        print("=" * 80)
        print("🤖 Multi-Model AI System | 🔧 File Operations | 🌐 Web Tools | ⚡ Workflows")
        print(f"📅 Session: {self.session_start.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Performance status
        if self.performance_start_time:
            core_performance = (self.performance_start_time * 1000)  # Convert to ms
            print(f"⚡ Fast Execution: ENABLED ({core_performance:.1f}ms core performance)")
        else:
            print("⚡ Fast Execution: ENABLED")
        
        # Diagnostics status
        if self.diagnostics_enabled:
            print("🏥 Diagnostics: ENABLED")
            if self.dashboard_running:
                print("📊 Dashboard: http://localhost:7777")
            else:
                print("📊 Dashboard: OFFLINE")
        else:
            print("🏥 Diagnostics: DISABLED")
            
        print("-" * 80)
    
    def display_help(self):
        """Display comprehensive help information."""
        print("\n🆘 PROJECT-S CLI HELP")
        print("=" * 50)
        print("💬 Basic Commands:")
        print("  <question>           - Ask AI a question")
        print("  help                 - Show this help")
        print("  status               - Show system status")
        print("  exit/quit/bye        - Exit CLI")
        
        print("\n🏥 Diagnostics Commands:")
        print("  diag status          - Show diagnostics status")
        print("  diag dashboard       - Manage web dashboard")
        print("  diag dashboard start - Start dashboard")
        print("  diag dashboard stop  - Stop dashboard")
        print("  diag dashboard open  - Open dashboard in browser")
        print("  diag errors          - Show error statistics")
        print("  diag performance     - Show performance report")
        print("  diag workflow <id>   - Show workflow diagnostics")
        print("  diag visualize <id>  - Visualize workflow")
        
        print("\n📂 File Commands:")
        print("  create file <name>   - Create a file")
        print("  read file <name>     - Read a file")
        print("  list files           - List files")
        
        print("\n🌐 Web Commands:")
        print("  analyze <url>        - Analyze website")
        print("  fetch <url>          - Fetch webpage content")
        
        print("\n💡 Examples:")
        print("  Project-S> Hello, how are you?")
        print("  Project-S> create file hello.py")
        print("  Project-S> diag status")
        print("  Project-S> analyze https://example.com")
        print("  Project-S> diag dashboard start")
        print()

    def _display_result(self, result):
        """Display command result with enhanced formatting."""
        if isinstance(result, dict):
            if result.get("command_type") == "INTELLIGENT_WORKFLOW":
                workflow_result = result.get("execution_result", {})
                if workflow_result.get("success"):
                    print(f"✅ Workflow: {workflow_result.get('workflow_type', 'unknown')}")
                    output_paths = workflow_result.get('output_paths', {})
                    if output_paths:
                        print("📁 Created files:")
                        for name, path in output_paths.items():
                            print(f"  • {name}: {path}")
                else:
                    print(f"❌ Workflow failed: {workflow_result.get('error', 'Unknown error')}")
                    
                ai_insights = workflow_result.get('ai_insights')
                if ai_insights:
                    print(f"\n🤖 AI Insights:\n{ai_insights}")
                    
            elif result.get("command_type", "").upper() == "FILE":
                if result.get("success"):
                    print(f"✅ File operation successful")
                    if "content" in result:
                        print(f"📄 Content:\n{result['content']}")
                    if "path" in result:
                        print(f"📁 Path: {result['path']}")
                else:
                    print(f"❌ File operation failed: {result.get('error', 'Unknown error')}")
                    
            elif "error" in result:
                print(f"❌ Error: {result['error']}")
            else:
                print(f"✅ Result: {result}")
        else:
            print(f"✅ {result}")
    
    async def process_command(self, user_input: str) -> Any:
        """Process a user command using the Project-S system."""
        try:
            # Import the model manager
            from integrations.model_manager import model_manager
            
            # Process the command through the model manager
            result = await model_manager.process_user_command(user_input)
            return result
            
        except Exception as e:
            logger.error(f"Command processing failed: {e}")
            return {"status": "error", "message": str(e)}
    
    async def process_ask_command(self, query: str) -> Any:
        """Process an ASK command."""
        try:
            # Import the model manager
            from integrations.model_manager import model_manager
            
            # Process as a regular user command
            result = await model_manager.process_user_command(query)
            return result
            
        except Exception as e:
            logger.error(f"ASK command processing failed: {e}")
            return {"status": "error", "message": str(e)}
    
    async def process_file_command(self, operation: str, path: str = None, content: str = None) -> Any:
        """Process a FILE command."""
        try:
            # Import the core execution bridge
            from integrations.core_execution_bridge import core_execution_bridge
            
            # Build file command
            file_command = {"action": operation}
            if path:
                file_command["path"] = path
            if content:
                file_command["content"] = content
                
            # Execute through core bridge
            result = await core_execution_bridge.execute_file_operation(file_command)
            return result
            
        except Exception as e:
            logger.error(f"FILE command processing failed: {e}")
            return {"status": "error", "message": str(e)}
    
    async def process_cmd_command(self, shell_cmd: str) -> Any:
        """Process a CMD command."""
        try:
            # Import the core execution bridge
            from integrations.core_execution_bridge import core_execution_bridge
            
            # Execute shell command
            result = await core_execution_bridge.execute_shell_command({"command": shell_cmd})
            return result
            
        except Exception as e:
            logger.error(f"CMD command processing failed: {e}")
            return {"status": "error", "message": str(e)}
    
    async def process_workflow_command(self, workflow_type: str, prompt: str = None) -> Any:
        """Process a WORKFLOW command."""
        try:
            # Import the workflow system
            from integrations.intelligent_workflow_integration import workflow_orchestrator
            
            # Execute workflow
            result = await workflow_orchestrator.execute_workflow(
                workflow_type=workflow_type,
                prompt=prompt or f"Execute {workflow_type} workflow"
            )
            return result
            
        except Exception as e:
            logger.error(f"WORKFLOW command processing failed: {e}")
            return {"status": "error", "message": str(e)}

    async def cleanup(self):
        """Cleanup resources before exit."""
        try:
            if self.dashboard_running:
                logger.info("Stopping diagnostics dashboard...")
                await stop_dashboard()
                
            if self.diagnostics_enabled:
                logger.info("Saving diagnostics data...")
                # Diagnostics cleanup if needed
                
            logger.info("CLI cleanup completed")
            
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
    
    async def run_interactive_mode(self):
        """Run the CLI in interactive mode with diagnostics support."""
        self.display_banner()
        print("🔥 Interactive mode started! Type 'help' for commands, 'exit' to quit")
        print("💡 Use 'diag status' for system diagnostics, 'diag dashboard' for web interface")
        print()
        
        while True:
            try:
                # Get user input
                user_input = input("Project-S> ").strip()
                
                if not user_input:
                    continue
                    
                if user_input.lower() in ['exit', 'quit', 'bye']:
                    print("👋 Goodbye!")
                    break
                elif user_input.lower() == 'help':
                    self._show_help()
                    continue
                elif user_input.lower().startswith('diag'):
                    await self._handle_diagnostics_command(user_input)
                    continue
                elif user_input.lower() == 'status':
                    await self._show_system_status()
                    continue
                
                # Record session history
                command_entry = {
                    "timestamp": datetime.now().isoformat(),
                    "command": user_input,
                    "session_id": self.current_session_id
                }
                self.session_history.append(command_entry)
                
                # Process command
                print(f"\n⚡ Processing: {user_input}")
                start_time = datetime.now()
                
                result = await self.process_command(user_input)
                
                end_time = datetime.now()
                duration = (end_time - start_time).total_seconds()
                
                # Update diagnostics
                if self.diagnostics_enabled:
                    diagnostics_manager.update_response_time("cli_command", duration * 1000)
                
                print("\n📋 RESULT:\n" + "-" * 40)
                self._display_result(result)
                print(f"\n⏱️ Execution time: {duration:.2f}s")
                
            except KeyboardInterrupt:
                print("\n\n👋 Interrupted. Type 'exit' to quit gracefully.")
                continue
            except Exception as e:
                logger.error(f"Error in interactive mode: {e}")
                if self.diagnostics_enabled:
                    diagnostics_manager.register_error(
                        error=e,
                        component="cli_interactive",
                        alert_level=AlertLevel.WARNING
                    )
                print(f"\n❌ Error: {e}")
                continue
    
    async def execute_interactive_command(self, command: str):
        """Execute a command in interactive mode."""
        try:
            print("⏳ Processing...")
            
            # Simple command parsing
            parts = command.split()
            if not parts:
                return
            
            cmd_type = parts[0].lower()
            
            if cmd_type == "ask":
                query = " ".join(parts[1:]) if len(parts) > 1 else ""
                if not query:
                    print("❌ Please provide a question to ask")
                    return
                result = await self.process_ask_command(query)
                self.display_result(result)
                
            elif cmd_type == "cmd":
                shell_cmd = " ".join(parts[1:]) if len(parts) > 1 else ""
                if not shell_cmd:
                    print("❌ Please provide a command to execute")
                    return
                result = await self.process_cmd_command(shell_cmd)
                self.display_result(result)
                
            elif cmd_type == "file":
                if len(parts) < 2:
                    print("❌ Usage: file <read|write|list> [path] [content]")
                    return
                
                operation = parts[1]
                path = parts[2] if len(parts) > 2 else None
                content = " ".join(parts[3:]) if len(parts) > 3 else None
                
                result = await self.process_file_command(operation, path, content)
                self.display_result(result)
                
            elif cmd_type == "workflow":
                workflow_type = parts[1] if len(parts) > 1 else "general"
                prompt = " ".join(parts[2:]) if len(parts) > 2 else None
                
                result = await self.process_workflow_command(workflow_type, prompt)
                self.display_result(result)
                
            else:
                # Treat as general AI query
                result = await self.process_ask_command(command)
                self.display_result(result)
                
        except Exception as e:
            logger.error(f"Error executing command: {e}")
            print(f"❌ Error executing command: {e}")
    
    def display_history(self):
        """Display session command history."""
        print("\n📜 SESSION HISTORY")
        print("=" * 50)
        
        if not self.session_history:
            print("No commands executed yet.")
            return
        
        for i, entry in enumerate(self.session_history[-10:], 1):
            print(f"{i:2d}. [{entry.get('timestamp', 'unknown')}] {entry.get('command', '')[:60]}")
            print(f"     Status: {entry.get('status', 'unknown')}")
        
        if len(self.session_history) > 10:
            print(f"... and {len(self.session_history) - 10} more entries")
        
        print("=" * 50)
    
    def export_cli_config(self):
        """Export CLI configuration for external use."""
        print("\n📦 EXPORTING CLI CONFIGURATION")
        print("=" * 50)
        
        export_dir = Path("CLI_EXPORT")
        export_dir.mkdir(exist_ok=True)
        
        # CLI entry point
        cli_entry_content = '''#!/usr/bin/env python3
"""
Project-S CLI Entry Point
Exported CLI configuration for external use.
"""
import sys
from pathlib import Path

# Add the parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from cli_main import ProjectSCLI, main

if __name__ == "__main__":
    sys.exit(main())
'''
        
        (export_dir / "cli_entry.py").write_text(cli_entry_content, encoding='utf-8')
        
        # Configuration file
        config_content = '''# Project-S CLI Configuration
# Copy this file to your target system along with the CLI files

[system]
name = "Project-S CLI"
version = "1.0.0"

[models]
default_provider = "openrouter"
default_model = "qwen/qwen-72b"

[workflows]
enabled = true
default_timeout = 300

[cli]
interactive_mode = true
auto_save_session = true
max_history = 100
'''
        
        (export_dir / "config.ini").write_text(config_content, encoding='utf-8')
        
        # README
        readme_content = '''# Project-S CLI Export

This directory contains the exported CLI configuration for Project-S.

## Files:
- `cli_entry.py` - Main CLI entry point
- `config.ini` - Configuration file
- `README.md` - This file

## Usage:
1. Copy this directory to your target system
2. Ensure Project-S dependencies are installed
3. Run: `python cli_entry.py --help`

## Interactive Mode:
```bash
python cli_entry.py --interactive
```

## Direct Commands:
```bash
python cli_entry.py ask "What is Python?"
python cli_entry.py workflow code-generator "Create a FastAPI server"
```
'''
        
        (export_dir / "README.md").write_text(readme_content, encoding='utf-8')
        
        print(f"✅ CLI configuration exported to: {export_dir.absolute()}")
        print("📁 Files created:")
        print("  • cli_entry.py - Main entry point")
        print("  • config.ini - Configuration")
        print("  • README.md - Documentation")
        print("=" * 50)
    
    async def _handle_diagnostics_command(self, operation: str, target: str = None, action: str = None):
        """Handle diagnostics-related commands."""
        try:
            if operation == 'status':
                await self._show_diagnostics_status()
            elif operation == 'dashboard':
                await self._manage_dashboard(action)
            elif operation == 'errors':
                await self._show_error_statistics()
            elif operation == 'performance':
                await self._show_performance_report()
            elif operation == 'workflow':
                await self._handle_workflow_diagnostics(target)
            elif operation == 'visualize':
                await self._handle_workflow_visualization(target)
            else:
                print(f"Unknown diagnostics operation: {operation}")
                print("Available operations: status, dashboard, errors, performance, workflow, visualize")
                
        except Exception as e:
            logger.error(f"Error in diagnostics command: {e}")
            print(f"❌ Diagnostics error: {e}")

    async def _show_diagnostics_status(self):
        """Show comprehensive diagnostics status."""
        if not self.diagnostics_enabled:
            print("❌ Diagnostics system is not enabled")
            return
            
        print("🏥 DIAGNOSTICS STATUS")
        print("=" * 50)
        
        try:
            # System metrics
            current_metrics = diagnostics_manager.get_current_metrics()
            if current_metrics:
                print(f"🖥️  CPU Usage: {current_metrics.cpu_percent:.1f}%")
                print(f"💾 Memory Usage: {current_metrics.memory_used_mb:.1f}MB ({current_metrics.memory_percent:.1f}%)")
                print(f"🧵 Threads: {current_metrics.threads_count}")
                print(f"📂 Open Files: {current_metrics.open_file_descriptors}")
                
            # Error statistics
            error_stats = diagnostics_manager.get_error_statistics()
            print(f"\n🚨 Error Statistics:")
            print(f"   Total Errors: {error_stats.get('total_errors', 0)}")
            print(f"   Recent Errors (24h): {error_stats.get('recent_errors', 0)}")
            
            # Workflow statistics
            print(f"\n⚡ Workflow Statistics:")
            completed = sum(m.completed_workflows for m in diagnostics_manager.performance_history[-10:])
            failed = sum(m.failed_workflows for m in diagnostics_manager.performance_history[-10:])
            total = completed + failed
            success_rate = (completed / total * 100) if total > 0 else 0
            print(f"   Completed: {completed}")
            print(f"   Failed: {failed}")
            print(f"   Success Rate: {success_rate:.1f}%")
            
            # Dashboard status
            print(f"\n📊 Dashboard: {'RUNNING' if self.dashboard_running else 'STOPPED'}")
            if self.dashboard_running:
                print("   URL: http://localhost:7777")
                
        except Exception as e:
            logger.error(f"Error getting diagnostics status: {e}")
            print(f"❌ Error retrieving diagnostics: {e}")

    async def _manage_dashboard(self, args: List[str]):
        """Manage the diagnostics dashboard."""
        if not args:
            print("Dashboard status:", "RUNNING" if self.dashboard_running else "STOPPED")
            if self.dashboard_running:
                print("URL: http://localhost:7777")
            return
            
        action = args[0].lower()
        
        if action == 'start':
            if self.dashboard_running:
                print("Dashboard is already running at http://localhost:7777")
                return
                
            try:
                dashboard_started = await start_dashboard()
                if dashboard_started:
                    self.dashboard_running = True
                    print("✅ Dashboard started at http://localhost:7777")
                else:
                    print("❌ Failed to start dashboard")
            except Exception as e:
                print(f"❌ Dashboard startup error: {e}")
                
        elif action == 'stop':
            if not self.dashboard_running:
                print("Dashboard is not running")
                return
                
            try:
                await stop_dashboard()
                self.dashboard_running = False
                print("✅ Dashboard stopped")
            except Exception as e:
                print(f"❌ Dashboard stop error: {e}")
                
        elif action == 'open':
            if self.dashboard_running:
                import webbrowser
                webbrowser.open('http://localhost:7777')
                print("🌐 Opening dashboard in browser...")
            else:
                print("❌ Dashboard is not running. Use 'diag dashboard start' first.")
        else:
            print("Usage: diag dashboard [start|stop|open]")

    async def _show_error_statistics(self):
        """Show error statistics and recent errors."""
        if not self.diagnostics_enabled:
            print("❌ Diagnostics system is not enabled")
            return
            
        print("🚨 ERROR STATISTICS")
        print("=" * 50)
        
        try:
            stats = diagnostics_manager.get_error_statistics()
            print(f"Total Errors: {stats.get('total_errors', 0)}")
            print(f"Recent Errors (24h): {stats.get('recent_errors', 0)}")
            print(f"Error Rate: {stats.get('error_rate', 0):.2f} errors/hour")
            
            # Show recent errors
            recent_errors = diagnostics_manager.error_history[-5:]  # Last 5 errors
            if recent_errors:
                print("\n📋 Recent Errors:")
                for i, error_ctx in enumerate(recent_errors, 1):
                    print(f"  {i}. [{error_ctx.timestamp.strftime('%H:%M:%S')}] {error_ctx.component}: {error_ctx.error_message}")
            else:
                print("\n✅ No recent errors")
                
        except Exception as e:
            logger.error(f"Error getting error statistics: {e}")
            print(f"❌ Error retrieving error statistics: {e}")

    async def _show_performance_report(self):
        """Show performance report."""
        if not self.diagnostics_enabled:
            print("❌ Diagnostics system is not enabled")
            return
            
        print("📊 PERFORMANCE REPORT")
        print("=" * 50)
        
        try:
            report = diagnostics_manager.generate_performance_report(include_graphs=False)
            
            print(f"Uptime: {report['uptime_human']}")
            print(f"\nCurrent Metrics:")
            current = report['current_metrics']
            print(f"  CPU: {current['cpu_percent']:.1f}%")
            print(f"  Memory: {current['memory_used_mb']:.1f}MB ({current['memory_percent']:.1f}%)")
            print(f"  Threads: {current['threads_count']}")
            
            print(f"\nAverages:")
            averages = report['averages']
            print(f"  CPU: {averages['cpu_percent']:.1f}%")
            print(f"  Memory: {averages['memory_used_mb']:.1f}MB ({averages['memory_percent']:.1f}%)")
            
            print(f"\nWorkflows:")
            workflows = report['workflows']
            print(f"  Completed: {workflows['completed']}")
            print(f"  Failed: {workflows['failed']}")
            print(f"  Success Rate: {workflows['success_rate_percent']:.1f}%")
            
        except Exception as e:
            logger.error(f"Error generating performance report: {e}")
            print(f"❌ Error generating performance report: {e}")

    async def _handle_workflow_diagnostics(self, args: List[str]):
        """Handle workflow diagnostics commands."""
        if not args:
            print("Usage: diag workflow <workflow_id> [action]")
            print("Actions: info, export")
            return
            
        workflow_id = args[0]
        action = args[1] if len(args) > 1 else 'info'
        
        # This would need to be implemented based on your workflow storage
        print(f"Workflow diagnostics for {workflow_id} (action: {action})")
        print("Note: Full workflow diagnostics integration pending")

    async def _handle_workflow_visualization(self, args: List[str]):
        """Handle workflow visualization commands."""
        if not args:
            print("Usage: diag visualize <workflow_id>")
            return
            
        workflow_id = args[0]
        
        try:
            # This would need actual workflow data
            print(f"🎨 Generating visualization for workflow: {workflow_id}")
            print("Note: Connect to actual workflow data for full visualization")
            
        except Exception as e:
            logger.error(f"Error in workflow visualization: {e}")
            print(f"❌ Visualization error: {e}")

    async def _show_system_status(self):
        """Show comprehensive system status."""
        print("🚀 PROJECT-S SYSTEM STATUS")
        print("=" * 50)
        
        try:
            # Basic system info
            print(f"Version: {self.version}")
            print(f"Session Started: {self.session_start.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"Commands Executed: {len(self.session_history)}")
            
            # Component status
            print(f"\n🔧 Components:")
            print(f"  Event Bus: {'✅ ACTIVE' if event_bus else '❌ INACTIVE'}")
            print(f"  Workflow System: {'✅ ACTIVE' if self.workflow else '❌ INACTIVE'}")
            print(f"  Diagnostics: {'✅ ACTIVE' if self.diagnostics_enabled else '❌ INACTIVE'}")
            print(f"  Dashboard: {'✅ RUNNING' if self.dashboard_running else '❌ STOPPED'}")
              # Show diagnostics if available
            if self.diagnostics_enabled:
                await self._show_diagnostics_status()
                
        except Exception as e:
            logger.error(f"Error showing system status: {e}")
            print(f"❌ Error retrieving system status: {e}")
    
    async def process_command(self, user_input: str) -> Any:
        """Process a user command using the Project-S system."""
        try:
            # Import the model manager
            from integrations.model_manager import model_manager
            
            # Process the command through the model manager
            result = await model_manager.process_user_command(user_input)
            return result
            
        except Exception as e:
            logger.error(f"Command processing failed: {e}")
            return {"status": "error", "message": str(e)}
    
    async def process_ask_command(self, query: str) -> Any:
        """Process an ASK command."""
        try:
            # Import the model manager
            from integrations.model_manager import model_manager
            
            # Process as a regular user command
            result = await model_manager.process_user_command(query)
            return result
            
        except Exception as e:
            logger.error(f"ASK command processing failed: {e}")
            return {"status": "error", "message": str(e)}
    
    async def process_file_command(self, operation: str, path: str = None, content: str = None) -> Any:
        """Process a FILE command."""
        try:
            # Import the core execution bridge
            from integrations.core_execution_bridge import core_execution_bridge
            
            # Build file command
            file_command = {"action": operation}
            if path:
                file_command["path"] = path
            if content:
                file_command["content"] = content
                
            # Execute through core bridge
            result = await core_execution_bridge.execute_file_operation(file_command)
            return result
            
        except Exception as e:
            logger.error(f"FILE command processing failed: {e}")
            return {"status": "error", "message": str(e)}
    
    async def process_cmd_command(self, shell_cmd: str) -> Any:
        """Process a CMD command."""
        try:
            # Import the core execution bridge
            from integrations.core_execution_bridge import core_execution_bridge
            
            # Execute shell command
            result = await core_execution_bridge.execute_shell_command({"command": shell_cmd})
            return result
            
        except Exception as e:
            logger.error(f"CMD command processing failed: {e}")
            return {"status": "error", "message": str(e)}
    
    async def process_workflow_command(self, workflow_type: str, prompt: str = None) -> Any:
        """Process a WORKFLOW command."""
        try:
            # Import the workflow system
            from integrations.intelligent_workflow_integration import workflow_orchestrator
            
            # Execute workflow
            result = await workflow_orchestrator.execute_workflow(
                workflow_type=workflow_type,
                prompt=prompt or f"Execute {workflow_type} workflow"
            )
            return result
            
        except Exception as e:
            logger.error(f"WORKFLOW command processing failed: {e}")
            return {"status": "error", "message": str(e)}

    def display_result(self, result):
        """Public method to display command results."""
        self._display_result(result)

def create_argument_parser() -> argparse.ArgumentParser:
    """Create and configure the argument parser."""
    parser = argparse.ArgumentParser(
        description="Project-S Unified CLI - Multi-Model AI System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s ask "What is quantum computing?"
  %(prog)s --interactive
  %(prog)s cmd "dir"
  %(prog)s file read README.md
  %(prog)s workflow code-generator "Create a FastAPI server"
  %(prog)s --list-models
  %(prog)s --export
        """
    )
    
    # Main command groups
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # ASK command
    ask_parser = subparsers.add_parser('ask', help='Ask AI a question')
    ask_parser.add_argument('query', nargs='+', help='Question to ask')
    
    # CMD command
    cmd_parser = subparsers.add_parser('cmd', help='Execute system command')
    cmd_parser.add_argument('command', nargs='+', help='Command to execute')
    
    # FILE command
    file_parser = subparsers.add_parser('file', help='File operations')
    file_parser.add_argument('operation', choices=['read', 'write', 'list'], help='File operation')
    file_parser.add_argument('path', nargs='?', help='File path')
    file_parser.add_argument('--content', help='Content for write operation')
      # WORKFLOW command
    workflow_parser = subparsers.add_parser('workflow', help='Run intelligent workflows')
    workflow_parser.add_argument('type', help='Workflow type')
    workflow_parser.add_argument('prompt', nargs='*', help='Additional prompt for workflow')
    
    # DIAGNOSTICS command
    diag_parser = subparsers.add_parser('diag', help='Diagnostics and monitoring')
    diag_parser.add_argument('operation', choices=['status', 'dashboard', 'errors', 'performance', 'workflow', 'visualize'], help='Diagnostic operation')
    diag_parser.add_argument('target', nargs='?', help='Target (e.g., workflow ID for workflow/visualize operations)')
    diag_parser.add_argument('action', nargs='?', help='Action (e.g., start/stop/open for dashboard)')
    
    # Global options
    parser.add_argument('--interactive', '-i', action='store_true', help='Start interactive mode')
    parser.add_argument('--session', '-s', help='Continue existing session ID')
    parser.add_argument('--list-models', action='store_true', help='List available AI models')
    parser.add_argument('--list-workflows', action='store_true', help='List available workflows')
    parser.add_argument('--export', action='store_true', help='Export CLI configuration')
    parser.add_argument('--version', action='version', version='Project-S CLI 1.0.0')
    parser.add_argument('--verbose', '-v', action='store_true', help='Enable verbose logging')
    
    return parser


async def main():
    """Main CLI entry point."""
    parser = create_argument_parser()
    args = parser.parse_args()
    
    # Configure verbose logging if requested
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
      # Initialize CLI
    cli = ProjectSCLI()
    
    # Initialize system
    if not await cli.initialize():
        print("❌ Failed to initialize Project-S CLI")
        return 1
    
    try:
        # Handle specific commands
        if args.interactive:
            await cli.run_interactive_mode()
            
        elif args.list_models:
            await cli.display_models()
            
        elif args.list_workflows:
            cli.display_workflows()
            
        elif args.export:
            cli.export_cli_config()
            
        elif args.command == 'ask':
            query = ' '.join(args.query)
            cli.display_banner()
            result = await cli.process_ask_command(query)
            cli.display_result(result)
            
        elif args.command == 'cmd':
            command = ' '.join(args.command)
            cli.display_banner()
            result = await cli.process_cmd_command(command)
            cli.display_result(result)
            
        elif args.command == 'file':
            cli.display_banner()
            result = await cli.process_file_command(args.operation, args.path, args.content)
            cli.display_result(result)
            
        elif args.command == 'workflow':
            prompt = ' '.join(args.prompt) if args.prompt else None
            cli.display_banner()
            result = await cli.process_workflow_command(args.type, prompt)
            cli.display_result(result)
            
        elif args.command == 'diag':
            cli.display_banner()
            await cli._handle_diagnostics_command(args.operation, args.target, args.action)
            
        else:
            # No specific command, show help or start interactive
            if len(sys.argv) == 1:
                cli.display_banner()
                print("\n💡 No command specified. Use --help for options or --interactive for interactive mode.")
                cli.display_help()
            else:
                parser.print_help()
        
        return 0
        
    except KeyboardInterrupt:
        print("\n👋 CLI session interrupted.")
        return 0
    except Exception as e:
        logger.critical(f"Critical CLI error: {e}")
        print(f"❌ Critical error: {e}")
        return 1


if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except Exception as e:
        print(f"Fatal error: {e}")
        sys.exit(1)
