"""
Project-S Multi-Model Main Entry Point [DEPRECATED]
-------------------------------------------------
⚠️  DEPRECATION NOTICE: This entry point is now DEPRECATED! ⚠️

🚀 USE INSTEAD: python main.py
   
   The new unified main.py provides ALL the functionality from this file
   plus intelligent mode detection, seamless switching, and better UX.

LEGACY SUPPORT: This file is preserved for reference but is no longer
the recommended entry point. All users should migrate to main.py.

ORIGINAL DESCRIPTION:
This was the main entry point for the Project-S Multi-Model system.
It combines LangGraph workflows with persistent state and multiple AI models.

PHASE 2 INTEGRATION:
- Enhanced with diagnostics and tool discoverability
- Unified with CLI interface capabilities
- Real-time system monitoring
- Comprehensive help system
"""

# Fix Unicode encoding issues FIRST before any other imports
import fix_unicode_encoding  # This automatically applies fixes

import asyncio
import logging
import os
import json
from pathlib import Path
import sys
from datetime import datetime
import webbrowser

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='[%(asctime)s] [%(levelname)s] %(name)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('logs/multi_model_system.log', mode='w')
    ]
)

logger = logging.getLogger(__name__)

# Ensure logs directory exists
os.makedirs('logs', exist_ok=True)

# Core components imports
from core.event_bus import event_bus
from core.error_handler import ErrorHandler

# PHASE 2: Diagnostic Integration
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

# PHASE 2: Tool Registry Integration
try:
    from tools.tool_registry import tool_registry
    TOOL_REGISTRY_AVAILABLE = True
    logger.info("✅ Tool registry loaded")
except ImportError as e:
    TOOL_REGISTRY_AVAILABLE = False
    logger.warning(f"⚠️ Tool registry not available: {e}")

from integrations.session_manager import session_manager
from integrations.model_manager import model_manager
from integrations.multi_model_ai_client import multi_model_ai_client
from integrations.advanced_langgraph_workflow import AdvancedLangGraphWorkflow
from integrations.persistent_state_manager import persistent_state_manager

# Intelligent workflow integration
try:
    from integrations.intelligent_workflow_integration import intelligent_workflow_orchestrator
    INTELLIGENT_WORKFLOWS_AVAILABLE = True
    logger.info("✅ Intelligent workflow integration loaded in main")
except ImportError as e:
    INTELLIGENT_WORKFLOWS_AVAILABLE = False
    logger.warning(f"⚠️ Intelligent workflow integration not available in main: {e}")

# Initialize error handler
error_handler = ErrorHandler()

# PHASE 2: Global state for enhanced features
class SystemState:
    def __init__(self):
        self.diagnostics_enabled = False
        self.dashboard_running = False
        self.session_start = datetime.now()
        self.tools_loaded = False
        self.available_tools = []
        
system_state = SystemState()

async def initialize_enhanced_system():
    """Initialize the enhanced multi-model system with diagnostics and tools."""
    print("🚀 Initializing Enhanced Project-S Multi-Model System...")
    
    try:
        # Initialize diagnostics if available
        if DIAGNOSTICS_AVAILABLE:
            await initialize_diagnostics({
                "enable_dashboard": True,
                "dashboard_port": 7777,
                "enable_performance_monitoring": True,
                "monitoring_interval_seconds": 30
            })
            system_state.diagnostics_enabled = True
            logger.info("✅ Diagnostics system initialized")
        
        # Initialize tool registry if available
        if TOOL_REGISTRY_AVAILABLE:
            await tool_registry.load_tools()
            system_state.tools_loaded = True
            system_state.available_tools = list(tool_registry.get_available_tools().keys())
            logger.info(f"✅ Tools loaded: {len(system_state.available_tools)} available")
        
        # Initialize event bus
        event_bus.register_default_handlers()
        logger.info("✅ Event bus initialized")
        
        print("✅ Enhanced system initialization complete!")
        return True
        
    except Exception as e:
        logger.error(f"Failed to initialize enhanced system: {e}")
        print(f"❌ Initialization failed: {e}")
        return False

def display_enhanced_banner():
    """Display enhanced banner with system status."""
    print("\n" + "=" * 80)
    print("🚀 PROJECT-S MULTI-MODEL AI SYSTEM v2.0 - ENHANCED")
    print("=" * 80)
    print("🤖 Multi-Model AI | 🔧 13+ Tools | 🏥 Diagnostics | 📊 Dashboard")
    print(f"📅 Session: {system_state.session_start.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🔧 Tools: {len(system_state.available_tools)} available" if system_state.tools_loaded else "🔧 Tools: Not loaded")
    print(f"🏥 Diagnostics: {'ENABLED' if system_state.diagnostics_enabled else 'DISABLED'}")
    print(f"📊 Dashboard: {'http://localhost:7777' if system_state.dashboard_running else 'OFFLINE'}")
    print("-" * 80)
    print("💡 NEW COMMANDS: 'help', 'tools', 'diag', 'dashboard', 'status'")
    print("💡 LEGACY: Multi-model demos and comparisons available")
    print("💡 CLI MODE: Type 'cli' to switch to full CLI interface")
    print("-" * 80)

def display_comprehensive_help():
    """Display comprehensive help with Phase 2 enhancements."""
    print("\n🆘 PROJECT-S MULTI-MODEL HELP SYSTEM")
    print("=" * 60)
    
    print("\n🤖 AI & MODEL COMMANDS:")
    print("  <question>           - Ask AI a question")
    print("  compare <question>   - Compare multiple AI models")
    print("  models               - Show available AI models")
    print("  demo                 - Run multi-model demonstration")
    print("  workflow <type>      - Run intelligent workflow")
    
    print("\n🔧 TOOL COMMANDS:")
    if system_state.tools_loaded:
        print("  tools                - Show all available tools")
        print("  tools <category>     - Show tools by category")
        print("  tool <name>          - Get tool information")
        print("  use <tool> <args>    - Execute a specific tool")
    else:
        print("  tools                - (Tools not loaded)")
    
    print("\n🏥 DIAGNOSTIC COMMANDS:")
    if system_state.diagnostics_enabled:
        print("  diag                 - Show diagnostics status")
        print("  dashboard            - Open diagnostics dashboard")
        print("  dashboard start      - Start web dashboard")
        print("  dashboard stop       - Stop web dashboard")
        print("  performance          - Show performance metrics")
        print("  errors               - Show error statistics")
    else:
        print("  diag                 - (Diagnostics not available)")
    
    print("\n📊 SYSTEM COMMANDS:")
    print("  status               - Show system status")
    print("  help                 - Show this help")
    print("  cli                  - Switch to full CLI mode")
    print("  exit/quit            - Exit system")
    
    print("\n💡 EXAMPLES:")
    print("  Project-S> What is machine learning?")
    print("  Project-S> compare Explain quantum computing")
    print("  Project-S> tools file")
    print("  Project-S> dashboard start")
    print("  Project-S> workflow code-generator")
    print()

async def show_available_tools():
    """Show available tools with descriptions."""
    if not system_state.tools_loaded:
        print("❌ Tools not loaded. Tool registry unavailable.")
        return
    
    print("\n🔧 AVAILABLE TOOLS")
    print("=" * 50)
    
    try:
        tools = tool_registry.get_available_tools()
        categories = {}
        
        # Group tools by category
        for name, tool_class in tools.items():
            category = getattr(tool_class, 'category', 'General')
            if category not in categories:
                categories[category] = []
            categories[category].append((name, tool_class))
        
        # Display by category
        for category, tool_list in categories.items():
            print(f"\n📁 {category.upper()}:")
            for name, tool_class in tool_list:
                description = getattr(tool_class, 'description', 'No description')
                print(f"  • {name}: {description}")
        
        print(f"\n📊 Total: {len(tools)} tools available")
        print("💡 Use 'tool <name>' for detailed information")
        
    except Exception as e:
        print(f"❌ Error loading tools: {e}")

async def show_system_status():
    """Show comprehensive system status."""
    print("\n📊 SYSTEM STATUS")
    print("=" * 50)
    
    # Basic info
    uptime = datetime.now() - system_state.session_start
    print(f"⏱️  Uptime: {uptime}")
    print(f"🤖 AI Models: {len(multi_model_ai_client.list_available_models())} available")
    print(f"🔧 Tools: {len(system_state.available_tools)} loaded" if system_state.tools_loaded else "🔧 Tools: Not loaded")
    
    # Diagnostics status
    if system_state.diagnostics_enabled:
        print(f"🏥 Diagnostics: ENABLED")
        print(f"📊 Dashboard: {'RUNNING' if system_state.dashboard_running else 'STOPPED'}")
        
        try:
            current_metrics = diagnostics_manager.get_current_metrics()
            if current_metrics:
                print(f"🖥️  CPU: {current_metrics.cpu_percent:.1f}%")
                print(f"💾 Memory: {current_metrics.memory_used_mb:.1f}MB ({current_metrics.memory_percent:.1f}%)")
        except:
            pass
    else:
        print(f"🏥 Diagnostics: DISABLED")
    
    # Workflow capabilities
    print(f"⚡ Workflows: {'AVAILABLE' if INTELLIGENT_WORKFLOWS_AVAILABLE else 'LIMITED'}")
    
    print("\n💡 Use 'help' for available commands")

async def handle_dashboard_command(action: str = None):
    """Handle dashboard-related commands."""
    if not system_state.diagnostics_enabled:
        print("❌ Diagnostics not available. Dashboard cannot be started.")
        return
    
    try:
        if action == "start" or action is None:
            if not system_state.dashboard_running:
                print("🚀 Starting diagnostics dashboard...")
                await start_dashboard()
                system_state.dashboard_running = True
                print("✅ Dashboard started at http://localhost:7777")
                
                # Try to open in browser
                try:
                    webbrowser.open("http://localhost:7777")
                    print("🌐 Dashboard opened in browser")
                except:
                    print("💡 Open http://localhost:7777 in your browser")
            else:
                print("📊 Dashboard is already running at http://localhost:7777")
                
        elif action == "stop":
            if system_state.dashboard_running:
                print("🛑 Stopping diagnostics dashboard...")
                await stop_dashboard()
                system_state.dashboard_running = False
                print("✅ Dashboard stopped")
            else:
                print("📊 Dashboard is not running")
                
        elif action == "open":
            if system_state.dashboard_running:
                webbrowser.open("http://localhost:7777")
                print("🌐 Dashboard opened in browser")
            else:
                print("❌ Dashboard is not running. Use 'dashboard start' first.")
                
    except Exception as e:
        logger.error(f"Dashboard command error: {e}")
        print(f"❌ Dashboard error: {e}")

async def process_enhanced_command(user_input: str):
    """Process commands with Phase 2 enhancements."""
    command = user_input.strip().lower()
    parts = user_input.strip().split()
    
    # Help commands
    if command in ['help', '?']:
        display_comprehensive_help()
        return
    
    # System status
    elif command == 'status':
        await show_system_status()
        return
    
    # Tool commands
    elif command == 'tools':
        await show_available_tools()
        return
    
    elif parts[0].lower() == 'tools' and len(parts) > 1:
        category = parts[1]
        print(f"🔧 Tools in category '{category}' - Feature coming soon!")
        return
    
    # Dashboard commands
    elif command == 'dashboard':
        await handle_dashboard_command()
        return
    
    elif parts[0].lower() == 'dashboard' and len(parts) > 1:
        await handle_dashboard_command(parts[1])
        return
    
    # Diagnostics
    elif command == 'diag':
        if system_state.diagnostics_enabled:
            await show_system_status()
        else:
            print("❌ Diagnostics not available")
        return
    
    # Model commands
    elif command == 'models':
        await display_available_models()
        return
    
    elif command == 'demo':
        await run_demo_comparison()
        return
    
    # CLI switch
    elif command == 'cli':
        print("🔄 Switching to full CLI mode...")
        print("💡 Run: python cli_main.py")
        return
    
    # Comparison command
    elif parts[0].lower() == 'compare' and len(parts) > 1:
        query = ' '.join(parts[1:])
        print(f"🔄 Running multi-model comparison for: {query}")
        await run_comparison_for_query(query)
        return
    
    # Default: process as regular AI query
    else:
        await process_user_task(user_input)

async def run_comparison_for_query(query: str):
    """Run a focused comparison for a specific query."""
    session_id = await session_manager.create_session({
        "type": "comparison",
        "query": query,
        "created_at": datetime.now().isoformat()
    })
    
    print(f"🤖 Processing with multiple models: {query}")
    print("⏳ Please wait...")
    
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
            # Show first 300 characters for comparison
            print(content[:300] + ("..." if len(content) > 300 else ""))
        print("-" * 40)
    
    print(f"\n💾 Session saved: {session_id}")

async def display_available_models():
    """Display information about available AI models."""
    print("\nAvailable AI Models:")
    print("-" * 50)
    
    models = multi_model_ai_client.list_available_models()
    by_provider = {}
    
    # Group by provider
    for model in models:
        provider = model["provider"]
        if provider not in by_provider:
            by_provider[provider] = []
        by_provider[provider].append(model)
    
    # Print by provider
    for provider, provider_models in by_provider.items():
        print(f"\n{provider.upper()}:")
        for model in provider_models:
            print(f"  - {model['name']} ({model['model_id']})")
            print(f"    {model['description']}")
            print(f"    Strengths: {', '.join(model['strengths'])}")
    
    print("\n" + "-" * 50)

async def display_task_mappings():
    """Display task-to-model mappings from configuration."""
    print("\nTask Type to Model Mappings:")
    print("-" * 50)
    
    mappings = multi_model_ai_client.config.get("task_model_mapping", {})
    
    for task, models in mappings.items():
        print(f"{task}: {', '.join(models)}")
    
    print("\n" + "-" * 50)

async def run_demo_comparison():
    """Run a demonstration of multi-model comparison."""
    print("\nRunning Multi-Model Comparison Demo")
    print("-" * 50)
    
    # Create a test session
    session_id = await session_manager.create_session({
        "type": "demo",
        "created_at": datetime.now().isoformat()
    })
    
    # Set up a comparison between different models
    test_query = "Explain the concept of recursion in programming with an example."
    
    print(f"Query: {test_query}\n")
    print("Processing with multiple models...\n")
    
    # Run with multiple models
    result = await session_manager.process_with_multiple_models(
        session_id=session_id,
        query=test_query,
        models=["gpt-3.5-turbo", "claude-3-sonnet"]  # Use specific models for comparison
    )
    
    # Display results
    print("\nResults:")
    for model, response in result["responses"].items():
        if "error" in response:
            print(f"\n{model}: Error - {response.get('message', 'Unknown error')}")
        else:
            print(f"\n{model}:")
            print("-" * 40)
            print(response.get("content", "No content")[:500] + "...")
            print("-" * 40)
    
    print(f"\nSession ID: {session_id}")
    
    return session_id

async def run_multi_model_workflow(session_id: str = None):
    """Run a multi-model workflow demonstration."""
    print("\nRunning Multi-Model Workflow Demo")
    print("-" * 50)
    
    test_command = "Create a Python function that sorts a list of dictionaries by a specified key."
    
    print(f"Command: {test_command}\n")
    print("Processing with multi-model workflow...\n")
    
    # Initialize the LangGraph workflow
    workflow = AdvancedLangGraphWorkflow()
    
    # Process with the multi-model workflow
    result = await workflow.process_with_multi_model_graph_with_persistence(
        command=test_command,
        session_id=session_id
    )
    
    # Display results
    print("\nWorkflow Result:")
    print("-" * 50)
    print(result["result"])
    print("-" * 50)
    
    print("\nModels Used:")
    for phase, model in result["models_used"].items():
        print(f"- {phase}: {model}")
    
    print(f"\nSession ID: {result['session_id']}")
    
    return result["session_id"]

async def continue_session(session_id: str):
    """Continue an existing session with a new query."""
    print(f"\nContinuing Session: {session_id}")
    print("-" * 50)
    
    # First, show the conversation history
    history = await persistent_state_manager.get_conversation_history(session_id)
    
    print("Conversation history:")
    for msg in history:
        role = msg["role"]
        content = msg["content"]
        # Truncate long messages for display
        if len(content) > 100:
            content = content[:100] + "..."
        print(f"{role}: {content}")
    
    # New query for the session
    followup_query = "Can you modify the previous solution to handle cases where the key doesn't exist in some dictionaries?"
    
    print(f"\nNew query: {followup_query}")
    
    # Process in the same session
    result = await session_manager.process_in_session(
        session_id=session_id,
        query=followup_query,
        workflow_type="multi_model"
    )
    
    # Display result
    print("\nResult:")
    print("-" * 50)
    print(result["result"])
    print("-" * 50)

async def process_user_task(task: str):
    """Process a user task with the multi-model workflow and print the result."""
    try:
        # Create a new session for each task
        session_id = await session_manager.create_session({
            "type": "user",
            "created_at": datetime.now().isoformat()
        })
        workflow = AdvancedLangGraphWorkflow()
        print("\nMulti-model AI workflow indítása...")
        result = await workflow.process_with_multi_model_graph_with_persistence(
            command=task,
            session_id=session_id
        )
        print("\nEredmény:")
        print("=" * 50)
        print(result.get("result", result))
        print("=" * 50)
    except Exception as e:
        print(f"Hiba a feladat feldolgozása során: {e}")

async def interactive_main():
    print("=== Project-S Interaktív Mód (🔥 VALÓDI VÉGREHAJTÁS + INTELLIGENT WORKFLOWS) ===")
    print("Írj be egy utasítást (pl. 'Hozz létre test.txt fájlt') vagy 'exit' a kilépéshez.")
    print("🆕 ÚJ: Intelligent workflow támogatás (pl. 'Elemezd ezt a weboldalt: https://example.com')")
    print("🔥 JAVÍTOTT: Valódi fájlműveletek és shell parancsok!")
    print("📂 ÚJ: Intelligens mappaszervezés!")
    print("\nElérhető funkciók:")
    print("- Egyszerű fájlműveletek: 'hozz létre egy test.txt fájlt'")
    print("- Fájl olvasás: 'olvasd el a config.yaml fájlt'")
    print("- Könyvtár listázás: 'listázd ki a fájlokat'")
    print("- Shell parancsok: 'futtasd: dir'")
    print("- 📂 Mappaszervezés: 'rendszerezd a toti mappát'")
    print("- 🧪 Teszt fájlok: 'hozz létre minta fájlokat teszt_mappa mappában'")
    print("- Multi-modell AI válaszok: 'magyarázd el a rekurziót'")
    print("- Workflow lista: 'workflows' (elérhető intelligent workflow-k listája)")
    
    while True:
        user_input = input("\nProject-S> ").strip()
        if user_input.lower() in ("exit", "quit", "q"): 
            print("Kilépés...")
            break
        if user_input.lower() == "workflows":
            # Display available intelligent workflows
            try:
                from integrations.intelligent_workflow_integration import intelligent_workflow_orchestrator
                workflows_info = intelligent_workflow_orchestrator.list_available_workflows()
                print("\n🚀 ELÉRHETŐ INTELLIGENT WORKFLOWS:")
                print("=" * 50)
                for workflow in workflows_info["available_workflows"]:
                    print(f"\n📋 {workflow['name']}")
                    print(f"   Leírás: {workflow['description']}")
                    print("   Példa parancsok:")
                    for example in workflow.get('example_commands', [])[:2]:
                        print(f"   - {example}")
                print(f"\nÖsszesen: {workflows_info['total_workflows']} workflow elérhető")
                print("=" * 50)
            except Exception as e:
                print(f"❌ Hiba a workflow lista betöltésében: {e}")
            continue
        
        if not user_input:
            continue
        
        print("\n⏳ Végrehajtás folyamatban...")
        
        # 🔥 ENHANCED: Intelligens parancs felismerés confidence scoring-gal
        parsed_command = await intelligent_command_parser(user_input)
        
        # Display confidence information
        confidence = parsed_command.get("confidence", 0.0)
        confidence_level = parsed_command.get("confidence_level", "Unknown")
        
        print(f"🎯 Intent Analysis: {parsed_command['type']} ({confidence:.0%} confidence - {confidence_level})")
        
        # Handle confidence-based decisions
        if parsed_command.get("requires_confirmation", False):
            confirmation_msg = parsed_command.get("confirmation_message", "Execute this command?")
            user_confirm = input(f"\n❓ {confirmation_msg} (y/n): ").strip().lower()
            if user_confirm not in ['y', 'yes', 'igen', 'i']:
                print("⏸️ Command execution cancelled by user.")
                continue
        
        # Show alternatives if available
        if parsed_command.get("suggest_alternatives", False) and parsed_command.get("alternatives"):
            print(f"\n💡 Alternative interpretations found:")
            for i, alt in enumerate(parsed_command["alternatives"], 1):
                print(f"  {i}. {alt['intent_type']} - {alt['operation']} ({alt['confidence']:.0%})")
            
            choice = input("\nSelect option (1-{}) or press Enter to continue with primary interpretation: ".format(len(parsed_command["alternatives"])))
            if choice.isdigit() and 1 <= int(choice) <= len(parsed_command["alternatives"]):
                selected_alt = parsed_command["alternatives"][int(choice) - 1]
                print(f"🔄 Switching to alternative: {selected_alt['intent_type']} - {selected_alt['operation']}")
                # Update parsed_command with selected alternative
                parsed_command.update(selected_alt)
        
        # Show detailed analysis in debug mode
        if parsed_command.get("matched_patterns"):
            logger.debug(f"Matched patterns: {parsed_command['matched_patterns']}")
        if parsed_command.get("extraction_details"):
            logger.debug(f"Extraction details: {parsed_command['extraction_details']}")
        
        # Execute based on command type
        if parsed_command["type"] == "FILE_OPERATION":
            print(f"🔥 VALÓDI FÁJLMŰVELET VÉGREHAJTÁSA: {parsed_command['operation']}")
            result = await process_file_operation_directly(
                parsed_command["operation"],
                parsed_command.get("path"),
                parsed_command.get("content")
            )
            print("\n=== VALÓDI FÁJLMŰVELET EREDMÉNY ===")
            if result["status"] == "success":
                print(f"✅ {result['message']}")
                if "content" in result:
                    print(f"📄 Tartalom:\n{result['content'][:500]}...")
                if "files" in result:
                    print(f"📁 Fájlok ({result['count']} db):")
                    for file_info in result["files"][:10]:
                        file_type = "📁" if file_info["type"] == "directory" else "📄"
                        size_info = f" ({file_info['size']} byte)" if file_info.get('size') else ""
                        print(f"  {file_type} {file_info['name']}{size_info}")
                    if result['count'] > 10:
                        print(f"  ... és még {result['count'] - 10} elem")
            else:
                print(f"❌ {result['message']}")
            continue
        
        elif parsed_command["type"] == "DIRECTORY_ORGANIZATION":
            operation = parsed_command["operation"]
            path = parsed_command["path"]
            
            if operation == "organize":
                print(f"🔥 INTELLIGENS MAPPASZERVEZÉS: {path}")
                result = await organize_directory_intelligently(path)
                print("\n=== MAPPASZERVEZÉS EREDMÉNY ===")
                if result["status"] == "success":
                    print(f"✅ {result['message']}")
                    print(f"📁 Szervezett fájlok: {result['organized_files']} db")
                    print(f"📂 Létrehozott kategóriák: {result['categories_created']} db")
                    if result.get('categories'):
                        print(f"📋 Kategóriák: {', '.join(result['categories'])}")
                    if result.get('files_by_category'):
                        print("📊 Fájlok kategóriánként:")
                        for category, count in result['files_by_category'].items():
                            print(f"  📁 {category}: {count} fájl")
                else:
                    print(f"❌ {result['message']}")
            
            elif operation == "create_samples":
                print(f"🔥 MINTA FÁJLOK LÉTREHOZÁSA: {path}")
                result = await create_sample_files_in_directory(path)
                print("\n=== MINTA FÁJLOK EREDMÉNY ===")
                if result["status"] == "success":
                    print(f"✅ {result['message']}")
                    print(f"📄 Létrehozott fájlok: {result['count']} db")
                    print("📋 Fájlok:")
                    for filename in result['created_files']:
                        print(f"  📄 {filename}")
                else:
                    print(f"❌ {result['message']}")
            continue
            print(f"🔥 VALÓDI SHELL PARANCS VÉGREHAJTÁSA: {parsed_command['command']}")
            result = await execute_shell_command_directly(parsed_command["command"])
            print("\n=== SHELL PARANCS EREDMÉNY ===")
            if result["status"] == "success":
                print(f"✅ Parancs végrehajtva (return code: {result['returncode']})")
                if result["stdout"]:
                    print(f"📤 Kimenet:\n{result['stdout']}")
            else:
                print(f"❌ {result['message']}")
                if result.get("stderr"):
                    print(f"⚠️ Hiba: {result['stderr']}")
            continue
        
        # Ha nem fájlművelet vagy shell parancs, akkor AI feldolgozás
        result = await model_manager.execute_task_with_core_system(user_input)
        print("\n=== AI FELDOLGOZÁS EREDMÉNY ===")
        
        # Enhanced result display for intelligent workflows
        if result.get("command_type") == "INTELLIGENT_WORKFLOW":
            print("🎯 INTELLIGENT WORKFLOW EREDMÉNY:")
            workflow_result = result.get("execution_result", {})
            if workflow_result.get("success"):
                print(f"✅ Workflow típus: {workflow_result.get('workflow_type', 'unknown')}")
                print(f"📁 Generált fájlok: {len(workflow_result.get('output_paths', {}))}")
                
                # Display generated files
                output_paths = workflow_result.get('output_paths', {})
                if output_paths:
                    print("\n📁 Létrehozott fájlok:")
                    for name, path in output_paths.items():
                        print(f"  - {name}: {path}")
                
                # Display AI insights if available
                ai_insights = workflow_result.get('ai_insights')
                if ai_insights:
                    print(f"\n🤖 AI Betekintések:\n{ai_insights}")
            else:
                print(f"❌ Workflow hiba: {workflow_result.get('error', 'Unknown error')}")
        else:
            # Standard result display
            if isinstance(result, dict) and "execution_result" in result:
                exec_result = result["execution_result"]
                if isinstance(exec_result, dict) and "response" in exec_result:
                    response = exec_result["response"]
                    if len(response) > 1000:
                        print(f"🤖 AI Válasz (rövidített):\n{response[:1000]}...\n[Teljes válasz {len(response)} karakter]")
                    else:
                        print(f"🤖 AI Válasz:\n{response}")
                else:
                    print(result)
            else:
                print(result)

async def process_file_operation_directly(operation: str, path: str = None, content: str = None) -> dict:
    """Közvetlen fájlművelet végrehajtás - VALÓDI működés garantált."""
    try:
        import os
        from pathlib import Path
        
        if operation == "create":
            if not path:
                return {"status": "error", "message": "Path required for create operation"}
            
            file_path = Path(path)
            
            # Create directory if doesn't exist
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Write content to file
            write_content = content or f"# File created by Project-S Multi-Model System\n# Created at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(write_content)
            
            # Verify file was created
            if file_path.exists():
                return {
                    "status": "success",
                    "message": f"File created successfully: {file_path}",
                    "path": str(file_path),
                    "size": file_path.stat().st_size
                }
            else:
                return {"status": "error", "message": f"File creation failed: {file_path}"}
        
        elif operation == "read":
            if not path:
                return {"status": "error", "message": "Path required for read operation"}
            
            file_path = Path(path)
            if not file_path.exists():
                return {"status": "error", "message": f"File not found: {file_path}"}
            
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            return {
                "status": "success",
                "message": f"File read successfully: {file_path}",
                "path": str(file_path),
                "content": content,
                "size": len(content)
            }
        
        elif operation == "list":
            target_path = Path(path) if path else Path.cwd()
            if not target_path.exists():
                return {"status": "error", "message": f"Directory not found: {target_path}"}
            
            files = []
            for item in target_path.iterdir():
                files.append({
                    "name": item.name,
                    "type": "directory" if item.is_dir() else "file",
                    "size": item.stat().st_size if item.is_file() else None
                })
            
            return {
                "status": "success",
                "message": f"Directory listing for: {target_path}",
                "path": str(target_path),
                "files": files,
                "count": len(files)
            }
        
        else:
            return {"status": "error", "message": f"Unknown operation: {operation}"}
            
    except Exception as e:
        return {"status": "error", "message": f"File operation failed: {str(e)}"}

async def execute_shell_command_directly(command: str) -> dict:
    """Közvetlen shell parancs végrehajtás - VALÓDI működés garantált."""
    try:
        import subprocess
        import sys
        
        # Detect shell based on OS
        if sys.platform.startswith('win'):
            shell_cmd = ['powershell.exe', '-Command', command]
        else:
            shell_cmd = ['bash', '-c', command]
        
        # Execute command
        result = subprocess.run(
            shell_cmd,
            capture_output=True,
            text=True,
            timeout=30,
            encoding='utf-8'
        )
        
        return {
            "status": "success" if result.returncode == 0 else "error",
            "command": command,
            "returncode": result.returncode,
            "stdout": result.stdout.strip(),
            "stderr": result.stderr.strip(),
            "message": f"Command executed with return code: {result.returncode}"
        }
        
    except subprocess.TimeoutExpired:
        return {"status": "error", "message": "Command timed out after 30 seconds"}
    except Exception as e:
        return {"status": "error", "message": f"Shell command failed: {str(e)}"}

async def intelligent_command_parser(user_input: str) -> dict:
    """
    Enhanced intelligent command parser with confidence scoring.
    Integrates with the new Intelligence Engine for advanced NLU capabilities.    """
    # Import and use the new intelligence engine
    try:
        from core.intelligence_engine import intelligence_engine
        logger.info("🧠 Using enhanced intelligence engine for command analysis")
        
        # Use enhanced intelligence analysis
        intent_match = await intelligence_engine.analyze_intent_with_confidence(user_input)
        
        # Generate confidence report for debugging
        confidence_report = intelligence_engine.format_confidence_report(intent_match)
        logger.info(f"Intelligence Analysis:\n{confidence_report}")
        
        # Build enhanced result with confidence information
        result = {
            "type": intent_match.intent_type,
            "operation": intent_match.operation,
            "confidence": intent_match.confidence,
            "confidence_level": _get_confidence_level_name(intent_match.confidence),
            "matched_patterns": intent_match.matched_patterns,
            "extraction_details": intent_match.extraction_details
        }
        
        # Add parameters
        result.update(intent_match.parameters)
        
        # Add alternative interpretations if available
        if intent_match.alternative_interpretations:
            result["alternatives"] = intent_match.alternative_interpretations
        
        # Add confidence-based recommendations
        if intelligence_engine.should_request_confirmation(intent_match):
            result["requires_confirmation"] = True
            result["confirmation_message"] = f"Execute {intent_match.operation} with {intent_match.confidence:.0%} confidence?"
        
        if intelligence_engine.should_suggest_alternatives(intent_match):
            result["suggest_alternatives"] = True
        
        if intelligence_engine.should_fallback_to_ai(intent_match):
            result["fallback_to_ai"] = True
        
        logger.info(f"🎯 Intelligence Engine Analysis Complete - Confidence: {intent_match.confidence:.0%}")
        return result
        
    except ImportError as e:
        logger.warning(f"Intelligence Engine not available, using legacy parser: {e}")
        return await _legacy_intelligent_command_parser(user_input)
    except Exception as e:
        logger.error(f"Intelligence Engine failed, using legacy parser: {e}", exc_info=True)
        return await _legacy_intelligent_command_parser(user_input)

def _get_confidence_level_name(confidence: float) -> str:
    """Convert confidence score to human-readable level name."""
    if confidence >= 0.85:
        return "Very High"
    elif confidence >= 0.60:
        return "High"
    elif confidence >= 0.40:
        return "Medium"
    elif confidence >= 0.30:
        return "Low"
    else:
        return "Very Low"

async def _legacy_intelligent_command_parser(user_input: str) -> dict:
    """Legacy command parser implementation (original logic)."""
    user_input_lower = user_input.lower().strip()
    
    # Mappaszervezési felismerés
    if any(phrase in user_input_lower for phrase in ["rendszerezd", "szervezd", "organize", "rendezd", "kategorizáld"]):
        # Mappa név kinyerése
        words = user_input.split()
        target_folder = None
        
        for i, word in enumerate(words):
            if word.lower() in ["mappát", "folder", "mappa", "directory"] and i > 0:
                target_folder = words[i-1]
                break
            elif word.lower() in ["rendszerezd", "szervezd", "organize", "rendezd"] and i < len(words) - 1:
                next_word = words[i+1]
                if next_word.lower() not in ["a", "az", "the"]:
                    target_folder = next_word
                elif i < len(words) - 2:
                    target_folder = words[i+2]
                break
        
        if not target_folder:
            target_folder = "."  # Aktuális mappa
        
        return {
            "type": "DIRECTORY_ORGANIZATION",
            "operation": "organize",
            "path": target_folder,
            "confidence": 0.8,  # Add legacy confidence
            "confidence_level": "High"
        }
    
    # Minta fájlok létrehozása teszteléshez
    elif any(phrase in user_input_lower for phrase in ["hozz létre minta", "create sample", "teszt fájlok", "test files"]):
        words = user_input.split()
        target_folder = "test_files"
        
        for i, word in enumerate(words):
            if word.lower() in ["mappában", "in", "folder"] and i > 0:
                target_folder = words[i-1]
                break
        
        return {
            "type": "DIRECTORY_ORGANIZATION",
            "operation": "create_samples",
            "path": target_folder,
            "confidence": 0.8,
            "confidence_level": "High"
        }
    
    # Fájlművelet felismerés
    elif any(phrase in user_input_lower for phrase in ["hozz létre", "create file", "létrehozz", "készíts"]):
        # Fájlnév kinyerése
        words = user_input.split()
        filename = None
        for i, word in enumerate(words):
            if word.lower() in ["fájlt", "file"] and i > 0:
                # Az előző szó valószínűleg a fájlnév
                filename = words[i-1]
                break
            elif "." in word and len(word) > 3:  # Valószínűleg fájlnév
                filename = word
                break
        
        if not filename:
            filename = "project_s_test.txt"
        
        return {
            "type": "FILE_OPERATION",
            "operation": "create",
            "path": filename,
            "content": f"# Fájl létrehozva a Project-S Multi-Model rendszer által\n# Időpont: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n# Felhasználói parancs: {user_input}\n",
            "confidence": 0.8,
            "confidence_level": "High"
        }
    
    elif any(phrase in user_input_lower for phrase in ["olvasd", "read file", "mutasd", "tartalom"]):
        # Fájlnév kinyerése
        words = user_input.split()
        filename = None
        for word in words:
            if "." in word and len(word) > 3:
                filename = word
                break
        
        return {
            "type": "FILE_OPERATION",
            "operation": "read",
            "path": filename,
            "confidence": 0.8,
            "confidence_level": "High"
        }
    
    elif any(phrase in user_input_lower for phrase in ["listázd", "list", "ls", "dir", "mappát", "fájlok"]):
        return {
            "type": "FILE_OPERATION", 
            "operation": "list",
            "path": ".",
            "confidence": 0.8,
            "confidence_level": "High"
        }
    
    # Shell parancs felismerés
    elif any(phrase in user_input_lower for phrase in ["futtat", "execute", "run", "powershell", "cmd"]):
        # Parancs kinyerése
        if "powershell" in user_input_lower:
            command = user_input[user_input.lower().find("powershell") + 10:].strip()
        elif "cmd" in user_input_lower:
            command = user_input[user_input.lower().find("cmd") + 3:].strip()
        else:
            command = user_input
        
        return {
            "type": "SHELL_COMMAND",
            "command": command,
            "confidence": 0.8,
            "confidence_level": "High"
        }
    
    # Alapértelmezett: AI kérdés
    return {
        "type": "AI_QUERY",
        "query": user_input,
        "confidence": 0.2,
        "confidence_level": "Low"
    }

async def organize_directory_intelligently(target_path: str) -> dict:
    """Intelligens mappaszervezés - kategóriákba rendezi a fájlokat."""
    try:
        import os
        import shutil
        from pathlib import Path
        from collections import defaultdict
        
        target_directory = Path(target_path)
        
        if not target_directory.exists():
            return {"status": "error", "message": f"Mappa nem található: {target_directory}"}
        
        if not target_directory.is_dir():
            return {"status": "error", "message": f"Nem mappa: {target_directory}"}
        
        # Fájltípus kategóriák
        categories = {
            "Documents": [".txt", ".doc", ".docx", ".pdf", ".rtf", ".odt"],
            "Images": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".svg", ".ico"],
            "Videos": [".mp4", ".avi", ".mkv", ".mov", ".wmv", ".flv", ".webm"],
            "Audio": [".mp3", ".wav", ".flac", ".aac", ".ogg", ".wma"],
            "Archives": [".zip", ".rar", ".7z", ".tar", ".gz", ".bz2"],
            "Code": [".py", ".js", ".html", ".css", ".java", ".cpp", ".c", ".php"],
            "Data": [".json", ".xml", ".csv", ".xlsx", ".sql", ".db"],
            "Configs": [".ini", ".conf", ".cfg", ".yaml", ".yml", ".toml"]
        }
        
        # Fájlok kategorizálása
        files_to_organize = []
        categorized_files = defaultdict(list)
        
        for item in target_directory.iterdir():
            if item.is_file():
                file_extension = item.suffix.lower()
                categorized = False
                
                for category, extensions in categories.items():
                    if file_extension in extensions:
                        categorized_files[category].append(item)
                        categorized = True
                        break
                
                if not categorized:
                    categorized_files["Other"].append(item)
                
                files_to_organize.append(item)
        
        if not files_to_organize:
            return {
                "status": "success",
                "message": f"A mappa már üres vagy csak almappákat tartalmaz: {target_directory}",
                "organized_files": 0,
                "categories_created": 0
            }
        
        # Kategória mappák létrehozása és fájlok mozgatása
        organized_count = 0
        categories_created = []
        
        for category, files in categorized_files.items():
            if files:  # Csak akkor hozza létre a kategóriát, ha vannak fájlok
                category_path = target_directory / category
                category_path.mkdir(exist_ok=True)
                categories_created.append(category)
                
                for file_path in files:
                    try:
                        destination = category_path / file_path.name
                        # Ha már létezik ugyanolyan nevű fájl, számozás hozzáadása
                        counter = 1
                        original_destination = destination
                        while destination.exists():
                            stem = original_destination.stem
                            suffix = original_destination.suffix
                            destination = category_path / f"{stem}_{counter}{suffix}"
                            counter += 1
                        
                        shutil.move(str(file_path), str(destination))
                        organized_count += 1
                    except Exception as e:
                        # Ha nem sikerül mozgatni, folytatjuk a többivel
                        pass
        
        return {
            "status": "success",
            "message": f"Mappaszervezés befejezve: {target_directory}",
            "organized_files": organized_count,
            "categories_created": len(categories_created),
            "categories": categories_created,
            "files_by_category": {cat: len(files) for cat, files in categorized_files.items() if files}
        }
        
    except Exception as e:
        return {"status": "error", "message": f"Mappaszervezési hiba: {str(e)}"}

async def create_sample_files_in_directory(target_path: str) -> dict:
    """Minta fájlok létrehozása teszteléshez."""
    try:
        from pathlib import Path
        
        target_directory = Path(target_path)
        target_directory.mkdir(exist_ok=True)
        
        sample_files = [
            ("test_document.txt", "Ez egy teszt dokumentum."),
            ("image_sample.jpg", "JPEG header simulation"),
            ("data_file.json", '{"test": "data", "type": "sample"}'),
            ("script_file.py", "# Python script sample\nprint('Hello World')"),
            ("config_file.ini", "[Settings]\ntest=true"),
            ("readme.md", "# README\nThis is a sample markdown file."),
            ("archive_simulation.zip", "ZIP file content simulation"),
            ("random_file.unknown", "Unknown file type content")
        ]
        
        created_files = []
        for filename, content in sample_files:
            file_path = target_directory / filename
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            created_files.append(filename)
        
        return {
            "status": "success",
            "message": f"Minta fájlok létrehozva: {target_directory}",
            "created_files": created_files,
            "count": len(created_files)
        }
        
    except Exception as e:
        return {"status": "error", "message": f"Minta fájlok létrehozási hiba: {str(e)}"}

async def main():
    """Enhanced main function with Phase 2 integration."""
    # Initialize enhanced system
    await initialize_enhanced_system()
    
    # Display enhanced banner
    display_enhanced_banner()
    
    print("🔥 Enhanced Interactive Mode Started!")
    print("💡 Type 'help' for commands, 'exit' to quit")
    print("💡 New features: diagnostics, tools, dashboard, CLI integration")
    print()
    
    while True:
        try:
            user_input = input("Project-S> ").strip()
            
            if not user_input:
                continue
                
            if user_input.lower() in ("exit", "quit", "bye"):
                print("👋 Goodbye!")
                
                # Cleanup
                if system_state.dashboard_running:
                    print("🛑 Stopping dashboard...")
                    await handle_dashboard_command("stop")
                
                break
            
            # Process with enhanced command handling
            await process_enhanced_command(user_input)
            
        except KeyboardInterrupt:
            print("\n\n👋 Interrupted. Type 'exit' to quit gracefully.")
            continue
        except Exception as e:
            logger.error(f"Error in main loop: {e}")
            print(f"❌ Error: {e}")
            continue

async def interactive_main():
    """Legacy interactive main for backward compatibility."""
    print("\n⚠️  LEGACY MODE - Consider using enhanced 'main()' function")
    print("🔄 Switching to enhanced mode...")
    await main()

if __name__ == "__main__":
    try:
        asyncio.run(interactive_main())
    except KeyboardInterrupt:
        print("\nProcess interrupted by user.")
    except Exception as e:
        logger.critical(f"Unhandled exception: {e}", exc_info=True)
        print(f"\nCritical error: {e}")
        sys.exit(1)
