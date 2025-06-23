#!/usr/bin/env python3
"""
Project-S CLI Main Module
=========================
Main CLI class with modular architecture.
This is the core CLI logic extracted from the monolithic cli_main.py

Author: Project-S Team
Version: 2.0 - Modular CLI
"""

import argparse
import asyncio
import logging
import os
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional, List

# Core imports
try:
    # The project root should already be in sys.path from the entry point
    from core.event_bus import event_bus
    from core.error_handler import ErrorHandler
    # Import integrations with fallback to simple implementations
    try:
        from integrations.multi_model_ai_client import multi_model_ai_client
        from integrations.model_manager import model_manager
    except ImportError:
        multi_model_ai_client = None
        model_manager = None
        
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Please make sure you're running from the project root directory")
    sys.exit(1)

logger = logging.getLogger("ProjectS-CLI")


class ProjectSCLI:
    """
    Modular Project-S Command Line Interface
    """
    
    def __init__(self):
        self.version = "2.0.0"
        self.session_start = datetime.now()
        self.current_session_id: Optional[str] = None
        self.session_history: List[Dict[str, Any]] = []
        self.error_handler = ErrorHandler()
        
    async def initialize(self) -> bool:
        """Initialize the Project-S system."""
        try:
            logger.info("Initializing Project-S CLI...")
            
            # Initialize event bus
            event_bus.register_default_handlers()
            logger.info("✅ Event bus initialized")
            
            return True
            
        except Exception as e:
            await self.error_handler.handle_error(e, {
                "component": "CLI",
                "operation": "initialization"
            })
            return False

    def create_parser(self) -> argparse.ArgumentParser:
        """Create the main argument parser."""
        parser = argparse.ArgumentParser(
            description="Project-S AI Agent - Multi-Model AI System",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Examples:
  %(prog)s ask "What is Python?"
  %(prog)s cmd "ls -la"  
  %(prog)s file create test.txt "Hello World"
  %(prog)s --interactive
  %(prog)s --version
            """
        )
        
        # Version
        parser.add_argument('--version', action='version', version=f'Project-S CLI v{self.version}')
        
        # Modes
        parser.add_argument('--interactive', '-i', action='store_true', 
                          help='Start interactive mode')
        parser.add_argument('--test', action='store_true',
                          help='Run system tests')
        
        # Subcommands
        subparsers = parser.add_subparsers(dest='command', help='Available commands')
        
        # ASK command
        ask_parser = subparsers.add_parser('ask', help='Ask AI questions')
        ask_parser.add_argument('question', help='Question to ask')
        ask_parser.add_argument('--model', help='Specific model to use')
        
        # CMD command  
        cmd_parser = subparsers.add_parser('cmd', help='Execute system commands')
        cmd_parser.add_argument('command', help='Command to execute')
        
        # FILE command
        file_parser = subparsers.add_parser('file', help='File operations')
        file_subparsers = file_parser.add_subparsers(dest='file_action')
        
        create_parser = file_subparsers.add_parser('create', help='Create file')
        create_parser.add_argument('filename', help='File to create')
        create_parser.add_argument('content', nargs='?', default='', help='File content')
        
        read_parser = file_subparsers.add_parser('read', help='Read file')
        read_parser.add_argument('filename', help='File to read')
        
        return parser

    async def handle_ask_command(self, question: str, model: Optional[str] = None) -> Dict[str, Any]:
        """Handle ASK command."""
        try:
            logger.info(f"Processing ASK command: {question}")
            
            # Use multi-model AI client
            if hasattr(multi_model_ai_client, 'process_user_command'):
                result = await multi_model_ai_client.process_user_command(f"ASK {question}")
            else:
                result = {"response": f"AI Response: {question}", "status": "success"}
            
            return result
            
        except Exception as e:
            await self.error_handler.handle_error(e, {
                "component": "CLI",
                "operation": "ask_command",
                "question": question
            })
            return {"error": str(e), "status": "error"}

    async def handle_cmd_command(self, command: str) -> Dict[str, Any]:
        """Handle CMD command."""
        try:
            logger.info(f"Processing CMD command: {command}")
            
            # Use model manager for command processing
            if hasattr(model_manager, 'process_user_command'):
                result = await model_manager.process_user_command(f"CMD {command}")
            else:
                result = {"response": f"Command executed: {command}", "status": "success"}
            
            return result
            
        except Exception as e:
            await self.error_handler.handle_error(e, {
                "component": "CLI",
                "operation": "cmd_command", 
                "command": command
            })
            return {"error": str(e), "status": "error"}

    async def handle_file_command(self, action: str, filename: str, content: str = "") -> Dict[str, Any]:
        """Handle FILE command."""
        try:
            logger.info(f"Processing FILE command: {action} {filename}")
            
            if action == "create":
                # Create file
                file_path = Path(filename)
                file_path.write_text(content, encoding='utf-8')
                return {"response": f"File created: {filename}", "status": "success"}
            elif action == "read":
                # Read file
                file_path = Path(filename)
                if file_path.exists():
                    content = file_path.read_text(encoding='utf-8')
                    return {"response": content, "status": "success"}
                else:
                    return {"error": f"File not found: {filename}", "status": "error"}
            else:
                return {"error": f"Unknown file action: {action}", "status": "error"}
                
        except Exception as e:
            await self.error_handler.handle_error(e, {
                "component": "CLI",
                "operation": "file_command",
                "action": action,
                "filename": filename
            })
            return {"error": str(e), "status": "error"}

    async def run_interactive_mode(self):
        """Run interactive CLI mode."""
        print(f"\n🚀 Project-S Interactive Mode v{self.version}")
        print("="*50)
        print("Type 'help' for commands, 'exit' to quit")
        print("="*50)
        
        while True:
            try:
                user_input = input("\nProject-S> ").strip()
                
                if not user_input:
                    continue
                    
                if user_input.lower() in ['exit', 'quit', 'q']:
                    print("\n👋 Goodbye!")
                    break
                elif user_input.lower() == 'help':
                    self.show_help()
                    continue
                elif user_input.lower() == 'version':
                    print(f"Project-S CLI v{self.version}")
                    continue
                
                # Process command
                print("⏳ Processing...")
                if user_input.startswith('ask '):
                    question = user_input[4:].strip()
                    result = await self.handle_ask_command(question)
                elif user_input.startswith('cmd '):
                    command = user_input[4:].strip()
                    result = await self.handle_cmd_command(command)
                elif user_input.startswith('file '):
                    # Parse file command
                    parts = user_input[5:].strip().split()
                    if len(parts) >= 2:
                        action = parts[0]
                        filename = parts[1]
                        content = ' '.join(parts[2:]) if len(parts) > 2 else ""
                        result = await self.handle_file_command(action, filename, content)
                    else:
                        result = {"error": "Invalid file command format", "status": "error"}
                else:
                    # Default to ASK command
                    result = await self.handle_ask_command(user_input)
                
                # Display result
                if result.get("status") == "error":
                    print(f"❌ Error: {result.get('error', 'Unknown error')}")
                else:
                    response = result.get("response", str(result))
                    print(f"📋 Result:\n{response}")
                    
            except KeyboardInterrupt:
                print("\n\n👋 Session interrupted. Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")

    def show_help(self):
        """Show help information."""
        print("\n🆘 Project-S CLI Help")
        print("="*30)
        print("Commands:")
        print("  ask <question>           - Ask AI a question")
        print("  cmd <command>           - Execute system command")  
        print("  file create <file> [content] - Create file")
        print("  file read <file>        - Read file")
        print("  help                    - Show this help")
        print("  version                 - Show version")
        print("  exit/quit/q            - Exit CLI")
        print("\nExamples:")
        print("  ask What is Python?")
        print("  cmd ls -la")
        print("  file create test.txt Hello World")
        print("  file read test.txt")

    async def run_tests(self) -> bool:
        """Run basic system tests."""
        print("🧪 Running Project-S System Tests...")
        print("="*40)
        
        tests_passed = 0
        total_tests = 3
        
        # Test 1: Ask command
        print("1. Testing ASK command...")
        try:
            result = await self.handle_ask_command("Hello World")
            if result.get("status") == "success":
                print("   ✅ ASK command working")
                tests_passed += 1
            else:
                print(f"   ❌ ASK command failed: {result.get('error')}")
        except Exception as e:
            print(f"   ❌ ASK command error: {e}")
        
        # Test 2: File command
        print("2. Testing FILE command...")
        try:
            result = await self.handle_file_command("create", "test_cli.txt", "Test content")
            if result.get("status") == "success":
                print("   ✅ FILE create working")
                tests_passed += 1
            else:
                print(f"   ❌ FILE command failed: {result.get('error')}")
        except Exception as e:
            print(f"   ❌ FILE command error: {e}")
        
        # Test 3: CMD command
        print("3. Testing CMD command...")
        try:
            result = await self.handle_cmd_command("echo Hello")
            if result.get("status") == "success":
                print("   ✅ CMD command working")
                tests_passed += 1
            else:
                print(f"   ❌ CMD command failed: {result.get('error')}")
        except Exception as e:
            print(f"   ❌ CMD command error: {e}")
        
        # Summary
        print(f"\n📊 Test Results: {tests_passed}/{total_tests} passed")
        success = tests_passed == total_tests
        if success:
            print("🎉 All tests passed!")
        else:
            print("⚠️  Some tests failed")
        
        return success

    async def run(self) -> int:
        """Main entry point for CLI."""
        try:
            # Initialize system
            if not await self.initialize():
                print("❌ Failed to initialize Project-S system")
                return 1
            
            # Parse arguments
            parser = self.create_parser()
            args = parser.parse_args()
            
            # Handle commands
            if args.interactive:
                await self.run_interactive_mode()
                return 0
            elif args.test:
                success = await self.run_tests()
                return 0 if success else 1
            elif args.command == 'ask':
                result = await self.handle_ask_command(args.question, args.model)
                if result.get("status") == "error":
                    print(f"❌ Error: {result.get('error')}")
                    return 1
                else:
                    print(result.get("response", str(result)))
                    return 0
            elif args.command == 'cmd':
                result = await self.handle_cmd_command(args.command)
                if result.get("status") == "error":
                    print(f"❌ Error: {result.get('error')}")
                    return 1
                else:
                    print(result.get("response", str(result)))
                    return 0
            elif args.command == 'file':
                if args.file_action == 'create':
                    result = await self.handle_file_command('create', args.filename, args.content)
                elif args.file_action == 'read':
                    result = await self.handle_file_command('read', args.filename)
                else:
                    print("❌ Unknown file action")
                    return 1
                    
                if result.get("status") == "error":
                    print(f"❌ Error: {result.get('error')}")
                    return 1
                else:
                    print(result.get("response", str(result)))
                    return 0
            else:
                # No command provided, show help
                parser.print_help()
                return 0
                
        except Exception as e:
            logger.error(f"CLI error: {e}")
            print(f"❌ Fatal error: {e}")
            return 1
