#!/usr/bin/env python3
"""
Project-S Unified CLI Interface - PHASE 2 ENHANCED [DEPRECATED]
============================================================
⚠️  DEPRECATION NOTICE: This entry point is now DEPRECATED! ⚠️

🚀 USE INSTEAD: python main.py
   
   The new unified main.py includes ALL CLI functionality from this file
   plus smart mode detection, seamless AI chat integration, and unified UX.

LEGACY SUPPORT: This file is preserved for reference but is no longer
the recommended entry point. All users should migrate to main.py.

ORIGINAL DESCRIPTION:
Unified command-line interface that integrates all Project-S functionality
into a single, modern, user-friendly CLI with full diagnostics and tool discovery.

Features:
- Interactive and batch modes
- Multi-model AI support with comparison
- File operations and workflow management
- Professional CLI with comprehensive help
- Full diagnostics integration
- Tool discovery and browsing
- Real-time system monitoring
- Cross-interface navigation

Author: Project-S Team
Version: 2.0 - Phase 2 Integration Complete [DEPRECATED]
"""

import argparse
import asyncio
import logging
import os
import sys
import webbrowser
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

# Diagnostics Integration
try:
    from core.diagnostics import diagnostics_manager, AlertLevel
    from integrations.langgraph_diagnostics_bridge import langgraph_diagnostics_bridge
    from integrations.workflow_visualizer import workflow_visualizer
    from integrations.diagnostics_dashboard import dashboard, start_dashboard, stop_dashboard
    from core.diagnostics_initializer import initialize_diagnostics
    DIAGNOSTICS_AVAILABLE = True
    logger.info("✅ Diagnostics system loaded")
except ImportError as e:
    DIAGNOSTICS_AVAILABLE = False
    logger.warning(f"⚠️ Diagnostics not available: {e}")

# Tool Registry Integration
try:
    from tools.tool_registry import tool_registry
    TOOL_REGISTRY_AVAILABLE = True
    logger.info("✅ Tool registry loaded")
except ImportError as e:
    TOOL_REGISTRY_AVAILABLE = False
    logger.warning(f"⚠️ Tool registry not available: {e}")

# Session and Model Management
from integrations.session_manager import session_manager
from integrations.model_manager import model_manager
from integrations.multi_model_ai_client import multi_model_ai_client
from integrations.advanced_langgraph_workflow import AdvancedLangGraphWorkflow
from integrations.persistent_state_manager import persistent_state_manager

# Initialize error handler
error_handler = ErrorHandler()


class ProjectSCLI:
    """
    Unified Project-S Command Line Interface with Full Diagnostics Integration
    """
    
    def __init__(self):
        self.version = "2.0"
        self.session_start = datetime.now()
        self.current_session_id: Optional[str] = None
        self.workflow: Optional[AdvancedLangGraphWorkflow] = None
        self.session_history: List[Dict[str, Any]] = []
        self.diagnostics_enabled = False
        self.dashboard_running = False
        
    async def initialize(self) -> bool:
        """Initialize the Project-S system with full diagnostics."""
        try:
            logger.info("Initializing Project-S CLI with Phase 2 enhancements...")
            
            # Initialize diagnostics first
            if DIAGNOSTICS_AVAILABLE:
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
            logger.info("✅ LangGraph diagnostics bridge initialized")
            
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
        """Display the Project-S CLI banner with Phase 2 enhancements."""
        print("\n" + "=" * 80)
        print(f"🚀 PROJECT-S UNIFIED CLI v{self.version} - PHASE 2 ENHANCED")
        print("=" * 80)
        print("🤖 Multi-Model AI System | 🔧 13+ Tools | 🌐 Web Tools | ⚡ Workflows")
        print("🏥 Full Diagnostics | 📊 Real-time Dashboard | 🔍 Smart Discovery")
        print(f"📅 Session: {self.session_start.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Diagnostics status
        if self.diagnostics_enabled:
            print("🏥 Diagnostics: ENABLED")
            if self.dashboard_running:
                print("📊 Dashboard: http://localhost:7777")
            else:
                print("📊 Dashboard: OFFLINE (use 'diag dashboard start')")
        else:
            print("🏥 Diagnostics: DISABLED")
        
        # Tool status
        if TOOL_REGISTRY_AVAILABLE:
            try:
                tools = tool_registry.get_available_tools()
                print(f"🔧 Tools: {len(tools)} available (use 'tools' to explore)")
            except:
                print("🔧 Tools: Loading...")
        else:
            print("🔧 Tools: Not available")
            
        print("-" * 80)
        print("💡 NEW: Type 'multimodel' for AI comparison interface")
        print("💡 NEW: Type 'tools' to explore available tools")
        print("💡 PRO TIP: 'diag dashboard start' for web interface")
        print("-" * 80)
    
    def display_help(self):
        """Display comprehensive help information."""
        print("\n🆘 PROJECT-S CLI HELP - PHASE 2 ENHANCED")
        print("=" * 60)
        print("💬 Basic Commands:")
        print("  <question>           - Ask AI a question")
        print("  help                 - Show this help")
        print("  status               - Show system status")
        print("  exit/quit/bye        - Exit CLI")
        
        print("\n🤖 Multi-Model AI Commands:")
        print("  models               - Show available AI models")
        print("  compare <question>   - Compare multiple AI models")
        print("  multimodel           - Switch to multi-model interface")
        
        print("\n🔧 Tool Commands:")
        if TOOL_REGISTRY_AVAILABLE:
            print("  tools                - Show available tools")
            print("  tools <category>     - Show tools by category")
            print("  tool <name>          - Get tool information")
        else:
            print("  tools                - (Tool registry not available)")
        
        print("\n🏥 Diagnostics Commands:")
        if self.diagnostics_enabled:
            print("  diag status          - Show diagnostics status")
            print("  diag dashboard       - Manage web dashboard")
            print("  diag dashboard start - Start dashboard")
            print("  diag dashboard stop  - Stop dashboard")
            print("  diag dashboard open  - Open dashboard in browser")
            print("  diag errors          - Show error statistics")
            print("  diag performance     - Show performance report")
        else:
            print("  diag                 - (Diagnostics not available)")
        
        print("\n📂 File Commands:")
        print("  create file <name>   - Create a file")
        print("  read file <name>     - Read a file")
        print("  list files           - List files")
        
        print("\n🌐 Web Commands:")
        print("  analyze <url>        - Analyze website")
        print("  fetch <url>          - Fetch webpage content")
        
        print("\n🚀 Interface Commands:")
        print("  multimodel           - Launch multi-model interface")
        print("  dashboard            - Open diagnostics dashboard")
        
        print("\n💡 Examples:")
        print("  Project-S> Hello, how are you?")
        print("  Project-S> compare Explain machine learning")
        print("  Project-S> tools file")
        print("  Project-S> diag status")
        print("  Project-S> multimodel")
        print()
    
    async def show_available_tools(self):
        """Show available tools with descriptions."""
        if not TOOL_REGISTRY_AVAILABLE:
            print("❌ Tool registry not available")
            return
            
        try:
            tools = tool_registry.get_available_tools()
            
            print("\n🔧 AVAILABLE TOOLS")
            print("=" * 50)
            
            categories = {}
            for name, tool_class in tools.items():
                category = getattr(tool_class, 'category', 'General')
                if category not in categories:
                    categories[category] = []
                categories[category].append((name, tool_class))
            
            for category, tool_list in categories.items():
                print(f"\n📁 {category.upper()}:")
                for name, tool_class in tool_list:
                    description = getattr(tool_class, 'description', 'No description')
                    print(f"  • {name}: {description}")
            
            print(f"\n📊 Total: {len(tools)} tools available")
            print("💡 Use 'tool <name>' for detailed information")
            
        except Exception as e:
            print(f"❌ Error loading tools: {e}")
    
    async def show_available_models(self):
        """Show available AI models."""
        try:
            models = multi_model_ai_client.list_available_models()
            
            print("\n🤖 AVAILABLE AI MODELS")
            print("=" * 50)
            
            by_provider = {}
            for model in models:
                provider = model["provider"]
                if provider not in by_provider:
                    by_provider[provider] = []
                by_provider[provider].append(model)
            
            for provider, provider_models in by_provider.items():
                print(f"\n🏢 {provider.upper()}:")
                for model in provider_models:
                    print(f"  • {model['name']} ({model['model_id']})")
                    print(f"    {model['description']}")
                    print(f"    Strengths: {', '.join(model['strengths'])}")
            
            print(f"\n📊 Total: {len(models)} models available")
            
        except Exception as e:
            print(f"❌ Error loading models: {e}")
    
    async def run_model_comparison(self, query: str):
        """Run a multi-model comparison."""
        try:
            print(f"🤖 Running multi-model comparison: {query}")
            print("⏳ Processing with multiple models...")
            
            session_id = await session_manager.create_session({
                "type": "cli_comparison",
                "query": query,
                "created_at": datetime.now().isoformat()
            })
            
            result = await session_manager.process_with_multiple_models(
                session_id=session_id,
                query=query,
                models=["gpt-3.5-turbo", "claude-3-sonnet"]
            )
            
            print("\n📊 COMPARISON RESULTS:")
            print("=" * 60)
            
            for model, response in result["responses"].items():
                print(f"\n🤖 {model.upper()}:")
                print("-" * 40)
                if "error" in response:
                    print(f"❌ Error: {response.get('message', 'Unknown error')}")
                else:
                    content = response.get("content", "No content")
                    print(content[:400] + ("..." if len(content) > 400 else ""))
                print("-" * 40)
            
            print(f"\n💾 Session saved: {session_id}")
            
        except Exception as e:
            logger.error(f"Model comparison error: {e}")
            print(f"❌ Comparison failed: {e}")
    
    async def launch_multimodel_interface(self):
        """Launch the multi-model interface."""
        print("🚀 Launching Multi-Model Interface...")
        print("💡 Starting enhanced multi-model interface with Phase 2 features...")
        
        try:
            # Import and run the enhanced interface
            from main_multi_model import main as multimodel_main
            print("✅ Multi-model interface loaded")
            await multimodel_main()
            
        except Exception as e:
            print(f"❌ Could not launch multi-model interface: {e}")
            print("💡 Try running: python main_multi_model.py")
    
    async def quick_dashboard_launch(self):
        """Quick dashboard launch."""
        if not self.diagnostics_enabled:
            print("❌ Diagnostics not available. Cannot launch dashboard.")
            return
        
        try:
            if not self.dashboard_running:
                print("🚀 Starting diagnostics dashboard...")
                await start_dashboard()
                self.dashboard_running = True
                print("✅ Dashboard started at http://localhost:7777")
                
                webbrowser.open("http://localhost:7777")
                print("🌐 Dashboard opened in browser")
            else:
                print("📊 Dashboard already running at http://localhost:7777")
                webbrowser.open("http://localhost:7777")
                
        except Exception as e:
            print(f"❌ Dashboard error: {e}")
    
    async def show_system_status(self):
        """Show comprehensive system status."""
        print("\n📊 SYSTEM STATUS")
        print("=" * 50)
        
        # Basic info
        uptime = datetime.now() - self.session_start
        print(f"⏱️  Uptime: {uptime}")
        print(f"🤖 AI Models: Available")
        
        if TOOL_REGISTRY_AVAILABLE:
            try:
                tools = tool_registry.get_available_tools()
                print(f"🔧 Tools: {len(tools)} loaded")
            except:
                print("🔧 Tools: Loading...")
        else:
            print("🔧 Tools: Not available")
        
        # Diagnostics status
        if self.diagnostics_enabled:
            print(f"🏥 Diagnostics: ENABLED")
            print(f"📊 Dashboard: {'RUNNING' if self.dashboard_running else 'STOPPED'}")
            
            try:
                current_metrics = diagnostics_manager.get_current_metrics()
                if current_metrics:
                    print(f"🖥️  CPU: {current_metrics.cpu_percent:.1f}%")
                    print(f"💾 Memory: {current_metrics.memory_used_mb:.1f}MB ({current_metrics.memory_percent:.1f}%)")
            except:
                pass
        else:
            print(f"🏥 Diagnostics: DISABLED")
        
        print(f"⚡ Workflows: AVAILABLE")
        print("\n💡 Use 'help' for available commands")
    
    async def process_command(self, user_input: str) -> Any:
        """Process a user command using the Project-S system."""
        try:
            # Process the command through the model manager
            result = await model_manager.process_user_command(user_input)
            return result
            
        except Exception as e:
            logger.error(f"Command processing failed: {e}")
            return {"status": "error", "message": str(e)}
    
    async def run_interactive_mode(self):
        """Run the CLI in interactive mode with Phase 2 enhancements."""
        self.display_banner()
        print("🔥 Enhanced Interactive Mode Started!")
        print("💡 Type 'help' for commands, 'exit' to quit")
        print("💡 NEW: Use 'tools', 'models', 'multimodel', 'dashboard'")
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
                    await self.show_system_status()
                    continue
                elif user_input.lower() == 'tools':
                    await self.show_available_tools()
                    continue
                elif user_input.lower() == 'models':
                    await self.show_available_models()
                    continue
                elif user_input.lower().startswith('compare '):
                    query = user_input[8:].strip()
                    await self.run_model_comparison(query)
                    continue
                elif user_input.lower() == 'multimodel':
                    await self.launch_multimodel_interface()
                    continue
                elif user_input.lower() == 'dashboard':
                    await self.quick_dashboard_launch()
                    continue
                
                # Process regular command
                print(f"\n⚡ Processing: {user_input}")
                start_time = datetime.now()
                
                result = await self.process_command(user_input)
                
                end_time = datetime.now()
                duration = (end_time - start_time).total_seconds()
                
                print("\n📋 RESULT:")
                print("-" * 40)
                if isinstance(result, dict) and "error" in result:
                    print(f"❌ Error: {result['error']}")
                else:
                    print(f"✅ {result}")
                print(f"\n⏱️ Execution time: {duration:.2f}s")
                
            except KeyboardInterrupt:
                print("\n\n👋 Interrupted. Type 'exit' to quit gracefully.")
                continue
            except Exception as e:
                logger.error(f"Error in interactive mode: {e}")
                print(f"\n❌ Error: {e}")
                continue
    
    async def cleanup(self):
        """Cleanup resources before exit."""
        try:
            if self.dashboard_running:
                logger.info("Stopping diagnostics dashboard...")
                await stop_dashboard()
                
            logger.info("CLI cleanup completed")
            
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")


async def main():
    """Main entry point for the CLI."""
    cli = ProjectSCLI()
    
    try:
        # Initialize the system
        if not await cli.initialize():
            print("❌ Failed to initialize Project-S CLI")
            return
        
        # Run interactive mode
        await cli.run_interactive_mode()
        
    except KeyboardInterrupt:
        print("\n👋 Interrupted by user")
    except Exception as e:
        logger.error(f"Unhandled error: {e}")
        print(f"❌ Error: {e}")
    finally:
        await cli.cleanup()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"❌ Critical error: {e}")
        sys.exit(1)
