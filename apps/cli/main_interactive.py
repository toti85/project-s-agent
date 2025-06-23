#!/usr/bin/env python3
"""
Project-S Agent - Stable Production Main Entry Point
===================================================
Enterprise multi-model AI agent with direct model orchestration, professional tool ecosystem, and event-driven architecture.

Features:
- Fast startup (<5s typical)
- Clean, professional welcome interface
- Multi-model routing (Qwen3-235B, GPT-3.5, etc)
- 13+ tools registered and available
- Event-driven, memory-efficient, robust
- No VSCode dependencies
- Graceful error handling and shutdown

Author: Project-S Team
Version: 3.0 - Stable Production
"""

import asyncio
import logging
import os
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Any

# --- Logging and Environment ---
if os.name == 'nt':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer)
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer)

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(name)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('logs/project_s.log', mode='w', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)
os.makedirs('logs', exist_ok=True)

# --- Core Imports ---
from core.event_bus import event_bus
from core.error_handler import ErrorHandler
from core.memory_system import MemorySystem
from core.ai_command_handler import ai_handler
from project_s_agent_old.integrations.model_manager import model_manager
from integrations.multi_model_ai_client import multi_model_ai_client
from tools.tool_registry import tool_registry

# --- Tool Registration ---
async def register_all_tools():
    tool_count = await tool_registry.load_tools()
    logger.info(f"Registered {tool_count} tools.")
    return tool_count

# --- System Status ---
def get_system_status(agent) -> Dict[str, Any]:
    return {
        "version": agent.version,
        "uptime": str(datetime.now() - agent.session_start),
        "models": agent.ai_client.list_available_models() if agent.ai_client else [],
        "tools": tool_registry.list_tools(),
        "memory_entries": len(agent.session_history),
        "mode": agent.mode,
        "startup_time": f"{time.time() - agent.start_time:.2f}s"
    }

# --- Main Agent Class ---
class ProjectSAgent:
    def __init__(self):
        self.start_time = time.time()
        self.version = "3.0.0"
        self.session_history = []
        self.session_start = datetime.now()
        self.model_manager = model_manager
        self.ai_client = multi_model_ai_client
        self.ai_handler = ai_handler
        self.memory_system = MemorySystem()
        self.tool_registry = tool_registry
        self.error_handler = ErrorHandler()
        self.mode = "Production"
        logger.info(f"Project-S Agent v{self.version} initialized.")

    async def initialize(self):
        await register_all_tools()
        event_bus.register_default_handlers()
        logger.info("All tools and event handlers registered.")

    def display_welcome(self):
        status = get_system_status(self)
        print("\n" + "=" * 80)
        print(f"🚀 PROJECT-S AGENT v{self.version} - ENTERPRISE MULTI-MODEL AI SYSTEM")
        print("=" * 80)
        print(f"⚡ Startup time: {status['startup_time']} | Build: {self.session_start.strftime('%Y-%m-%d')}")
        print(f"🤖 Models loaded: {len(status['models'])} | Tools: {len(status['tools'])}")
        print(f"🎯 Capabilities: File Ops | Code Gen | Web | System | Workflows")
        print("-" * 80)
        print("💡 QUICK START:")
        print("  • Create file: 'create hello.txt with content Hello World'")
        print("  • Generate code: 'write a Python function to sort lists'")
        print("  • Analyze web: 'analyze this website: https://python.org'")
        print("  • Get help: 'help' | Demo: 'demo' | Exit: 'exit'")
        print("-" * 80)
        print("Project-S> ", end="", flush=True)

    def display_help(self):
        print("\n🆘 PROJECT-S HELP\n" + "=" * 50)
        print("\n📁 FILE OPERATIONS:")
        print("  • create <filename> [with content <text>]")
        print("  • read <filename>")
        print("  • delete <filename>")
        print("  • list files")
        print("\n💻 CODE GENERATION:")
        print("  • write/generate a Python function...")
        print("  • create a script that...")
        print("\n🌐 WEB & ANALYSIS:")
        print("  • analyze website: <url>")
        print("  • scrape data from: <url>")
        print("\n🔧 SYSTEM COMMANDS:")
        print("  • run command: <shell_command>")
        print("\n🎮 SPECIAL MODES:")
        print("  • demo - Run demonstration")
        print("  • models - Show available models")
        print("  • history - Show session history")
        print("  • clear - Clear screen")
        print("  • status - System status")
        print("  • exit/quit - Exit agent")
        print("=" * 50)

    def display_models(self):
        print("\n🤖 AVAILABLE MODELS\n" + "=" * 50)
        models = self.ai_client.list_available_models() if self.ai_client else []
        if not models:
            print("❌ No models available.")
            return
        for m in models:
            print(f"  • {m['name']} ({m['provider']}) - {', '.join(m.get('strengths', []))}")
        print(f"\nTotal: {len(models)} models")

    def display_tools(self):
        print("\n🛠️  AVAILABLE TOOLS\n" + "=" * 50)
        tools = self.tool_registry.list_tools()
        for t in tools:
            print(f"  • {t['name']} ({t['category']}) - {t.get('description', '')}")
        print(f"\nTotal: {len(tools)} tools")

    def display_status(self):
        status = get_system_status(self)
        print("\n📊 SYSTEM STATUS\n" + "=" * 40)
        print(f"Version: {status['version']}")
        print(f"Uptime: {status['uptime']}")
        print(f"Models: {len(status['models'])}")
        print(f"Tools: {len(status['tools'])}")
        print(f"Session history: {status['memory_entries']} entries")
        print(f"Mode: {status['mode']}")
        print(f"Startup time: {status['startup_time']}")
        print("=" * 40)

    def display_history(self):
        print("\n📜 SESSION HISTORY\n" + "=" * 50)
        if not self.session_history:
            print("No commands executed yet.")
            return
        for i, entry in enumerate(self.session_history[-10:], 1):
            print(f"{i:2d}. [{entry.get('timestamp', 'unknown')}] {entry.get('command', '')[:60]}")
            print(f"     Status: {entry.get('status', 'unknown')}")
        if len(self.session_history) > 10:
            print(f"... and {len(self.session_history) - 10} more entries")
        print("=" * 50)

    async def display_demo(self):
        print("\n🎮 PROJECT-S DEMONSTRATION MODE\n" + "=" * 60)
        demos = [
            ("📁 File Operations", "create demo.txt with content 'Demo file created by Project-S'"),
            ("💻 Code Generation", "write a Python function to calculate factorial"),
            ("🤖 AI Analysis", "explain quantum computing in simple terms"),
            ("🛠️  Tool List", "tools"),
            ("📊 System Info", "status")
        ]
        for demo_name, demo_command in demos:
            print(f"\n{demo_name}\n{'-' * 40}\nCommand: {demo_command}\nExecuting...")
            try:
                result = await self.process_command(demo_command)
                print(f"Result: {str(result)[:200]}{'...' if len(str(result)) > 200 else ''}")
            except Exception as e:
                print(f"Error: {e}")
            print("✅ Demo step completed")
            await asyncio.sleep(1)
        print("\n🎉 Demonstration completed! All features working correctly.")

    async def process_command(self, user_input: str) -> Any:
        start_time = time.time()
        self.session_history.append({
            "timestamp": datetime.now().strftime("%H:%M:%S"),
            "command": user_input,
            "status": "processing"
        })
        try:
            await event_bus.default_event_handler({"event": "command.received", "command": user_input})
            result = await self.model_manager.process_user_command(user_input)
            self.session_history[-1]["status"] = "completed"
            self.session_history[-1]["duration"] = f"{time.time() - start_time:.2f}s"
            await event_bus.default_event_handler({"event": "command.processed", "command": user_input, "result": result})
            return result
        except Exception as e:
            self.session_history[-1]["status"] = "error"
            self.session_history[-1]["error"] = str(e)
            logger.error(f"Command execution failed: {e}")
            await event_bus.default_event_handler({"event": "command.error", "command": user_input, "error": str(e)})
            return {"status": "error", "message": str(e)}

    async def run_interactive_mode(self):
        self.display_welcome()
        while True:
            try:
                user_input = input().strip()
                if not user_input:
                    print("Project-S> ", end="", flush=True)
                    continue
                if user_input.lower() in ('exit', 'quit', 'q'):
                    print("\n👋 Goodbye! Project-S session ended.")
                    break
                elif user_input.lower() == 'help':
                    self.display_help()
                elif user_input.lower() == 'demo':
                    await self.display_demo()
                elif user_input.lower() == 'models':
                    self.display_models()
                elif user_input.lower() == 'tools':
                    self.display_tools()
                elif user_input.lower() == 'status':
                    self.display_status()
                elif user_input.lower() == 'history':
                    self.display_history()
                elif user_input.lower() == 'clear':
                    os.system('cls' if os.name == 'nt' else 'clear')
                    self.display_welcome()
                    continue
                else:
                    print("⏳ Processing...")
                    result = await self.process_command(user_input)
                    print("\n📋 RESULT:\n" + "-" * 40)
                    # --- Enhanced result display (from main_multi_model.py) ---
                    error_displayed = False
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
                            ai_insights = workflow_result.get('ai_insights')
                            if ai_insights:
                                print(f"\n🤖 AI Insights:\n{ai_insights}")
                        elif result.get("command_type", "").upper() == "FILE":
                            path = result.get("execution_result", {}).get("path")
                            if path and Path(path).exists():
                                print(f"✅ File operation successful: {path}")
                            else:
                                print("❌ File operation failed")
                                error_displayed = True
                        elif result.get("command_type", "").upper() == "AI_RESPONSE":
                            content = result.get("execution_result", {}).get("content")
                            if content:
                                print(content)
                            else:
                                print(result)
                        else:
                            print(result)
                            # If result contains error, set flag
                            if isinstance(result, dict) and (result.get("status") == "error" or result.get("error")):
                                error_displayed = True
                    else:
                        print(result)
                print("-" * 40)
                # Only print error prompt if not already displayed
                if not error_displayed and isinstance(result, dict) and (result.get("status") == "error" or result.get("error")):
                    print(f"❌ Error: {result.get('error', '')}")
                print("\nProject-S> ", end="", flush=True)
            except KeyboardInterrupt:
                print("\n👋 Goodbye! Project-S session ended.")
                break
            except Exception as e:
                print(f"\n❌ Error: {e}")
                print("Project-S> ", end="", flush=True)

async def main():
    agent = ProjectSAgent()
    await agent.initialize()
    await agent.run_interactive_mode()

if __name__ == "__main__":
    asyncio.run(main())