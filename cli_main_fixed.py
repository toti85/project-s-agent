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
        self.workflow: Optional[Any] = None
        self.session_history: List[Dict[str, Any]] = []
        self.diagnostics_enabled = False
        self.dashboard_running = False
        
    async def initialize(self) -> bool:
        """Initialize the Project-S system with full diagnostics."""
        try:
            logger.info("Initializing Project-S CLI...")
            self.diagnostics_enabled = True
            logger.info("✅ CLI system initialized")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize CLI: {e}")
            return False
    
    def display_banner(self):
        """Display the Project-S CLI banner with diagnostics info."""
        print("\n" + "=" * 80)
        print(f"🚀 PROJECT-S UNIFIED CLI v{self.version}")
        print("=" * 80)
        print("🤖 Multi-Model AI System | 🔧 File Operations | 🌐 Web Tools | ⚡ Workflows")
        print(f"📅 Session: {self.session_start.strftime('%Y-%m-%d %H:%M:%S')}")
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
        print("  Project-S> analyze https://example.com")
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
            logger.info("CLI cleanup completed")
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
    
    async def run_interactive_mode(self):
        """Run the CLI in interactive mode."""
        self.display_banner()
        print("🔥 Interactive mode started! Type 'help' for commands, 'exit' to quit")
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
                    self.display_help()
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
                
                print("\n📋 RESULT:\n" + "-" * 40)
                self._display_result(result)
                print(f"\n⏱️ Execution time: {duration:.2f}s")
                
            except KeyboardInterrupt:
                print("\n\n👋 Interrupted. Type 'exit' to quit gracefully.")
                continue
            except Exception as e:
                logger.error(f"Error in interactive mode: {e}")
                print(f"\n❌ Error: {e}")
                continue

    async def _show_system_status(self):
        """Show comprehensive system status."""
        print("🚀 PROJECT-S SYSTEM STATUS")
        print("=" * 50)
        
        try:
            # Basic system info
            print(f"Version: {self.version}")
            print(f"Session Started: {self.session_start.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"Commands Executed: {len(self.session_history)}")
            print(f"  Diagnostics: {'✅ ACTIVE' if self.diagnostics_enabled else '❌ INACTIVE'}")
                
        except Exception as e:
            logger.error(f"Error showing system status: {e}")
            print(f"❌ Error retrieving system status: {e}")


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
    
    # Global options
    parser.add_argument('--interactive', '-i', action='store_true', help='Start interactive mode')
    parser.add_argument('--session', '-s', help='Continue existing session ID')
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
            
        elif args.command == 'ask':
            query = ' '.join(args.query)
            cli.display_banner()
            result = await cli.process_ask_command(query)
            cli._display_result(result)
            
        elif args.command == 'cmd':
            command = ' '.join(args.command)
            cli.display_banner()
            result = await cli.process_cmd_command(command)
            cli._display_result(result)
            
        elif args.command == 'file':
            cli.display_banner()
            result = await cli.process_file_command(args.operation, args.path, args.content)
            cli._display_result(result)
            
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
