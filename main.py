#!/usr/bin/env python3
"""
PROJECT-S: THE DEFINITIVE UNIFIED ENTRY POINT
============================================
One file. One command. All capabilities.

This is THE single entry point for Project-S that intelligently combines:
- Multi-model AI chat and comparison
- Professional CLI command interface  
- Real-time diagnostics and monitoring
- Complete tool ecosystem access
- Smart mode detection and seamless switching

Usage: python main.py

Features:
- Smart detection of user intent (chat vs commands vs diagnostics)
- Seamless mode switching in same session
- All 13+ tools accessible
- Real-time system monitoring
- Professional enterprise-grade experience
- Cross-capability navigation without interface switching

Author: Project-S Team
Version: 3.0 - The Unified Experience
Date: June 22, 2025
"""

import asyncio
import logging
import os
import sys
import time
import webbrowser
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional, List, Tuple

# Fix Unicode encoding issues FIRST
import fix_unicode_encoding

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('logs/project_s_main.log', mode='w', encoding='utf-8')
    ]
)

logger = logging.getLogger("ProjectS")

logger = logging.getLogger("ProjectS")
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

# AI and Workflow Systems
from integrations.session_manager import session_manager
from integrations.model_manager import model_manager
from integrations.multi_model_ai_client import multi_model_ai_client
from integrations.advanced_langgraph_workflow import AdvancedLangGraphWorkflow
from integrations.persistent_state_manager import persistent_state_manager

# Intelligent workflow integration
try:
    from integrations.intelligent_workflow_integration import intelligent_workflow_orchestrator
    INTELLIGENT_WORKFLOWS_AVAILABLE = True
    logger.info("✅ Intelligent workflow integration loaded")
except ImportError as e:
    INTELLIGENT_WORKFLOWS_AVAILABLE = False
    logger.warning(f"⚠️ Intelligent workflow integration not available: {e}")

# Initialize error handler
error_handler = ErrorHandler()

# --- System Status ---
def get_system_status(agent) -> Dict[str, Any]:
    return {
        "version": agent.version,
        "uptime": str(datetime.now() - agent.session_start),
        "models": agent.get_available_models() if hasattr(agent, 'get_available_models') else [],
        "tools": agent.available_tools if hasattr(agent, 'available_tools') else [],
        "memory_entries": len(agent.session_history),
        "mode": "unified",
        "startup_time": f"{time.time() - getattr(agent, 'start_time', time.time()):.2f}s"
    }

class ProjectSUnified:
    """
    THE definitive Project-S unified interface.
    Intelligently handles all user interactions with smart mode detection.
    """
    
    def __init__(self):
        self.version = "3.0"
        self.session_start = datetime.now()
        self.start_time = time.time()
        self.current_session_id: Optional[str] = None
        self.workflow: Optional[AdvancedLangGraphWorkflow] = None
        self.session_history: List[Dict[str, Any]] = []
        self.diagnostics_enabled = False
        self.dashboard_running = False
        self.tools_loaded = False
        self.available_tools = []
        self.mode_stack = ['unified']  # Track mode history for smart switching
        
        # Smart detection patterns
        self.command_patterns = {
            'help': r'^(help|\?|commands?)$',
            'status': r'^(status|info|system)$',
            'tools': r'^(tools?|list\s+tools?)(\s+\w+)?$',
            'models': r'^(models?|list\s+models?|ai\s+models?)$',
            'compare': r'^(compare|comparison)\s+(.+)$',
            'diag': r'^(diag|diagnostic|health)(\s+\w+)*$',
            'dashboard': r'^(dashboard|dash)(\s+\w+)?$',
            'file': r'^(file|read|write|create|list)\s+(.+)$',
            'workflow': r'^(workflow|run)\s+(.+)$',
            'shell': r'^(cmd|shell|run|execute)\s+(.+)$',
            'analyze': r'^(analyze|analyse|check)\s+(https?://\S+|\S+\.\w+)$',
        }
        
    async def initialize(self) -> bool:
        """Initialize the unified Project-S system."""
        try:
            logger.info("🚀 Initializing Project-S Unified System...")
            
            # Initialize diagnostics
            if DIAGNOSTICS_AVAILABLE:
                await initialize_diagnostics({
                    "enable_dashboard": True,
                    "dashboard_port": 7777,
                    "enable_performance_monitoring": True,
                    "monitoring_interval_seconds": 30
                })
                self.diagnostics_enabled = True
                logger.info("✅ Diagnostics system initialized")
            
            # Initialize tool registry
            if TOOL_REGISTRY_AVAILABLE:
                await tool_registry.load_tools()
                self.tools_loaded = True
                self.available_tools = list(tool_registry.get_available_tools().keys())
                logger.info(f"✅ Tools loaded: {len(self.available_tools)} available")
            
            # Initialize core systems
            event_bus.register_default_handlers()
            self.workflow = AdvancedLangGraphWorkflow()
            
            logger.info("🎉 Project-S Unified System initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize unified system: {e}")
            await error_handler.handle_error(e, {"component": "unified", "operation": "initialization"})
            return False
    
    def display_unified_banner(self):
        """Display the ultimate Project-S banner."""
        print("\n" + "🌟" * 40)
        print("🚀 PROJECT-S: THE DEFINITIVE AI PLATFORM")
        print("🌟" * 40)
        print(f"📱 One Interface | 🤖 Multi-AI | 🔧 {len(self.available_tools)}+ Tools | 🏥 Real-time Diagnostics")
        print(f"📅 Session: {self.session_start.strftime('%Y-%m-%d %H:%M:%S')} | v{self.version}")
        
        # System status line
        status_items = []
        if self.diagnostics_enabled:
            status_items.append("🏥 Diagnostics: ON")
        if self.dashboard_running:
            status_items.append("📊 Dashboard: LIVE")
        if self.tools_loaded:
            status_items.append(f"🔧 Tools: {len(self.available_tools)}")
        if INTELLIGENT_WORKFLOWS_AVAILABLE:
            status_items.append("⚡ Workflows: READY")
        
        if status_items:
            print("📊 " + " | ".join(status_items))
        
        print("-" * 80)
        print("💡 SMART MODE: I understand natural language, commands, and questions")
        print("💡 EXAMPLES: 'What is AI?' | 'tools file' | 'compare models' | 'diag'")
        print("💡 HELP: Type 'help' for commands or just ask me anything!")
        print("-" * 80)
    
    def detect_user_intent(self, user_input: str) -> Tuple[str, Dict[str, Any]]:
        """
        Smart detection of user intent and mode.
        Returns: (intent_type, extracted_data)
        """
        user_input = user_input.strip()
        
        # Check for exact command matches first
        for intent, pattern in self.command_patterns.items():
            match = re.match(pattern, user_input, re.IGNORECASE)
            if match:
                extracted_data = {
                    'raw': user_input,
                    'intent': intent,
                    'groups': match.groups() if match.groups() else []
                }
                return intent, extracted_data
        
        # Special case: exit commands
        if user_input.lower() in ['exit', 'quit', 'bye']:
            return 'exit', {'raw': user_input}
        
        # If it contains a question word or ends with ?, assume it's a chat
        if any(word in user_input.lower() for word in ['what', 'how', 'why', 'when', 'where', 'who']) or user_input.endswith('?'):
            return 'chat', {'raw': user_input, 'confidence': 'high'}
        
        # If it starts with an action verb, treat as task
        action_verbs = ['create', 'make', 'build', 'generate', 'write', 'code', 'develop', 'implement']
        if any(user_input.lower().startswith(verb) for verb in action_verbs):
            return 'task', {'raw': user_input, 'confidence': 'medium'}
        
        # Default to chat for conversational input
        return 'chat', {'raw': user_input, 'confidence': 'low'}
    
    def display_help(self):
        """Display comprehensive unified help."""
        print("\n🆘 PROJECT-S UNIFIED HELP SYSTEM")
        print("=" * 60)
        
        print("\n🤖 AI & CHAT:")
        print("  <question>           - Ask AI any question")
        print("  compare <question>   - Compare multiple AI models")
        print("  models               - Show available AI models")
        
        print("\n🔧 TOOLS & COMMANDS:")
        if self.tools_loaded:
            print("  tools                - Show all available tools")
            print("  tools <category>     - Show tools by category")
            print("  file <operation>     - File operations")
            print("  workflow <type>      - Run intelligent workflow")
        else:
            print("  tools                - (Tools not loaded)")
        
        print("\n🏥 DIAGNOSTICS:")
        if self.diagnostics_enabled:
            print("  diag                 - Show system diagnostics")
            print("  dashboard            - Open diagnostics dashboard")
            print("  status               - Show system status")
        else:
            print("  diag                 - (Diagnostics not available)")
        
        print("\n📊 SYSTEM:")
        print("  help                 - Show this help")
        print("  exit/quit            - Exit system")
        
        print("\n💡 EXAMPLES:")
        print("  Project-S> What is machine learning?")
        print("  Project-S> compare Explain quantum computing")
        print("  Project-S> tools file")
        print("  Project-S> create a Python script")
        print("  Project-S> diag")
    
    def display_models(self):
        """Display available AI models."""
        print("\n🤖 AVAILABLE AI MODELS\n" + "=" * 50)
        try:
            models = model_manager.get_available_models()
            for model in models:
                print(f"  • {model.get('name', 'Unknown')} ({model.get('provider', 'Unknown')})")
                if model.get('description'):
                    print(f"    {model['description']}")
        except Exception as e:
            print(f"❌ Error loading models: {e}")
        print(f"\nTotal: {len(models) if 'models' in locals() else 0} models")

    def display_tools(self):
        """Display available tools."""
        print("\n🛠️  AVAILABLE TOOLS\n" + "=" * 50)
        if self.tools_loaded:
            tools = tool_registry.list_tools()
            for t in tools:
                print(f"  • {t['name']} ({t['category']}) - {t.get('description', '')}")
            print(f"\nTotal: {len(tools)} tools")
        else:
            print("Tools not loaded. Please restart with tool registry enabled.")

    def display_status(self):
        """Display system status."""
        print("\n📊 SYSTEM STATUS\n" + "=" * 50)
        status = get_system_status(self)
        for key, value in status.items():
            print(f"  {key}: {value}")
        
        print(f"\n📊 Dashboard: {'RUNNING at http://localhost:7777' if self.dashboard_running else 'Available - use dashboard to start'}")

    async def handle_chat_intent(self, data: Dict[str, Any]):
        """Handle conversational AI requests."""
        query = data['raw']
        
        try:
            print(f"🤖 Processing: {query}")
            start_time = datetime.now()
            
            # Use the working AI system from main_multi_model.py
            result = await model_manager.execute_task_with_core_system(query)
            
            duration = (datetime.now() - start_time).total_seconds()
            
            # Display result
            print("─" * 60)
            if result:
                if isinstance(result, dict):
                    if "content" in result:
                        print(result["content"])
                    elif "response" in result:
                        print(result["response"])
                    else:
                        print(str(result))
                else:
                    print(str(result))
                
                print("─" * 60)
            
            print(f"⏱️ Response time: {duration:.2f}s")
            
            # Update diagnostics if available
            if self.diagnostics_enabled:
                diagnostics_manager.update_response_time("ai_chat", duration * 1000)
            
        except Exception as e:
            logger.error(f"Chat processing error: {e}")
            print(f"❌ AI processing failed: {e}")
    
    async def handle_task_intent(self, data: Dict[str, Any]):
        """Handle task/instruction requests."""
        task = data['raw']
        
        try:
            print(f"🔧 Executing task: {task}")
            start_time = datetime.now()
            
            # Use intelligent workflow orchestrator if available
            if INTELLIGENT_WORKFLOWS_AVAILABLE:
                result = await intelligent_workflow_orchestrator.execute_task(task)
            else:
                # Fallback to basic model execution
                result = await model_manager.execute_task_with_core_system(task)
            
            duration = (datetime.now() - start_time).total_seconds()
              # Display result
            print("─" * 60)
            if result:
                if isinstance(result, dict):
                    print(str(result))
                else:
                    print(str(result))
                
                print("─" * 60)
            
            print(f"⏱️ Execution time: {duration:.2f}s")
            
        except Exception as e:
            logger.error(f"Task execution error: {e}")
            print(f"❌ Task execution failed: {e}")
    
    async def process_user_input(self, user_input: str):
        """Process any user input with ENHANCED intelligence from main_multi_model.py."""
        
        try:
            # First try basic command detection for system commands
            intent_type, data = self.detect_user_intent(user_input)
            
            # Handle system commands first
            if intent_type == 'exit':
                return False
            elif intent_type == 'help':
                self.display_help()
                return True
            elif intent_type == 'status':
                self.display_status()
                return True
            elif intent_type == 'models':
                self.display_models()
                return True
            elif intent_type == 'tools':
                self.display_tools()
                return True
            elif intent_type == 'diag':
                await self.handle_diagnostics()
                return True
            elif intent_type == 'dashboard':
                await self.handle_dashboard()
                return True
            elif intent_type == 'compare':
                await self.handle_compare_intent(data)
                return True
            
            # For everything else, use the INTELLIGENT COMMAND PARSER
            print("\n⏳ Processing with enhanced intelligence...")
            
            # 🔥 ENHANCED: Intelligent command recognition with confidence scoring
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
                    return True
            
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
            
            # Execute based on command type
            if parsed_command["type"] == "FILE_OPERATION":
                print(f"🔥 REAL FILE OPERATION EXECUTION: {parsed_command['operation']}")
                result = await process_file_operation_directly(
                    parsed_command["operation"],
                    parsed_command.get("path"),
                    parsed_command.get("content")
                )
                print("\n=== REAL FILE OPERATION RESULT ===")
                if result["status"] == "success":
                    print(f"✅ {result['message']}")
                    if "content" in result:
                        print(f"📄 Content:\n{result['content'][:500]}...")
                    if "files" in result:
                        print(f"📁 Files ({result['count']} count):")
                        for file_info in result["files"][:10]:
                            file_type = "📁" if file_info["type"] == "directory" else "📄"
                            size_info = f" ({file_info['size']} byte)" if file_info.get('size') else ""
                            print(f"  {file_type} {file_info['name']}{size_info}")
                        if result['count'] > 10:
                            print(f"  ... and {result['count'] - 10} more items")
                else:
                    print(f"❌ {result['message']}")
                return True
            
            elif parsed_command["type"] == "DIRECTORY_ORGANIZATION":
                operation = parsed_command["operation"]
                path = parsed_command["path"]
                
                if operation == "organize":
                    print(f"🔥 INTELLIGENT DIRECTORY ORGANIZATION: {path}")
                    result = await organize_directory_intelligently(path)
                    print("\n=== DIRECTORY ORGANIZATION RESULT ===")
                    if result["status"] == "success":
                        print(f"✅ {result['message']}")
                        print(f"📁 Organized files: {result['organized_files']} count")
                        print(f"📂 Created categories: {result['categories_created']} count")
                        if result.get('categories'):
                            print(f"📋 Categories: {', '.join(result['categories'])}")
                        if result.get('files_by_category'):
                            print("📊 Files by category:")
                            for category, count in result['files_by_category'].items():
                                print(f"  📁 {category}: {count} files")
                    else:
                        print(f"❌ {result['message']}")
                return True
            
            elif parsed_command["type"] == "SHELL_COMMAND":
                print(f"🔥 REAL SHELL COMMAND EXECUTION: {parsed_command['command']}")
                result = await execute_shell_command_directly(parsed_command["command"])
                print("\n=== SHELL COMMAND RESULT ===")
                if result["status"] == "success":
                    print(f"✅ Command executed (return code: {result['returncode']})")
                    if result["stdout"]:
                        print(f"📤 Output:\n{result['stdout']}")
                else:
                    print(f"❌ {result['message']}")
                    if result.get("stderr"):
                        print(f"⚠️ Error: {result['stderr']}")
                return True
            
            elif parsed_command["type"] == "SYSTEM_ANALYSIS":
                print(f"🔥 SYSTEM PERFORMANCE ANALYSIS AND REPORTING")
                result = await generate_system_analysis_report(parsed_command.get("report_file", "system_analysis_report.txt"))
                print("\n=== SYSTEM ANALYSIS RESULT ===")
                if result["status"] == "success":
                    print(f"✅ {result['message']}")
                    print(f"📄 Report saved to: {result['report_path']}")
                    print(f"📊 Report size: {result['size']} bytes")
                    if result.get("summary"):
                        print(f"📋 Summary: {result['summary']}")
                else:
                    print(f"❌ {result['message']}")
                return True
            
            # If not a special command, use AI processing
            elif parsed_command["type"] == "AI_PROCESSING":
                await self.handle_chat_intent({"raw": parsed_command["query"]})
                return True
            
            # Fallback to chat for unrecognized types
            else:
                await self.handle_chat_intent({"raw": user_input})
                return True
                
        except Exception as e:
            logger.error(f"Error processing input: {e}")
            print(f"❌ Error: {e}")
            print("💡 Try again or type 'help' for assistance")
            return True
    
    async def handle_diagnostics(self):
        """Handle diagnostics display."""
        if not self.diagnostics_enabled:
            print("❌ Diagnostics not available")
            return
        
        try:
            print("\n🏥 SYSTEM DIAGNOSTICS\n" + "=" * 50)
            
            # Current metrics
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
            
            # Performance metrics
            print(f"\n⚡ Performance:")
            recent_history = diagnostics_manager.performance_history[-10:]
            if recent_history:
                avg_cpu = sum(m.cpu_percent for m in recent_history) / len(recent_history)
                avg_memory = sum(m.memory_percent for m in recent_history) / len(recent_history)
                print(f"   Average CPU (10 samples): {avg_cpu:.1f}%")
                print(f"   Average Memory (10 samples): {avg_memory:.1f}%")
            
            print(f"\n📊 Dashboard: {'RUNNING at http://localhost:7777' if self.dashboard_running else 'Available - use dashboard to start'}")
            
        except Exception as e:
            print(f"❌ Error retrieving diagnostics: {e}")
    
    async def handle_dashboard(self):
        """Handle dashboard operations."""
        if not self.diagnostics_enabled:
            print("❌ Dashboard not available (diagnostics disabled)")
            return
        
        try:
            if not self.dashboard_running:
                print("🚀 Starting diagnostics dashboard...")
                await start_dashboard()
                self.dashboard_running = True
                print("✅ Dashboard started at http://localhost:7777")
                webbrowser.open("http://localhost:7777")
            else:
                print("📊 Dashboard already running at http://localhost:7777")
                webbrowser.open("http://localhost:7777")
        except Exception as e:
            print(f"❌ Error starting dashboard: {e}")
    
    async def handle_compare_intent(self, data: Dict[str, Any]):
        """Handle model comparison requests."""
        query = data['groups'][0] if data.get('groups') else data['raw']
        
        try:
            print(f"🔬 Comparing models for: {query}")
            # Implement model comparison logic here
            result = await model_manager.compare_models(query)
            print("─" * 60)
            print(result)
            print("─" * 60)
        except Exception as e:
            print(f"❌ Model comparison failed: {e}")
    
    async def run_unified_interface(self):
        """Run the main unified interface loop."""
        self.display_unified_banner()
        
        while True:
            try:
                # Get user input
                user_input = input("\nProject-S> ").strip()
                
                if not user_input:
                    continue
                
                # Record in session history
                self.session_history.append({
                    "timestamp": datetime.now().isoformat(),
                    "input": user_input,
                    "type": "user"
                })
                
                # Process input
                should_continue = await self.process_user_input(user_input)
                if not should_continue:
                    break
                
            except KeyboardInterrupt:
                print("\n\n👋 Interrupted. Type 'exit' to quit gracefully.")
                continue
            except Exception as e:
                logger.error(f"Error in unified interface: {e}")
                print(f"\n❌ Error: {e}")
                print("💡 Try again or type 'help' for assistance")
                continue
    
    async def cleanup(self):
        """Cleanup resources before exit."""
        try:
            if self.dashboard_running:
                logger.info("Stopping diagnostics dashboard...")
                await stop_dashboard()
            
            logger.info("Project-S unified cleanup completed")
            
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")

# === MISSING CORE FUNCTIONALITY FROM main_multi_model.py ===

async def intelligent_command_parser(user_input: str) -> dict:
    """
    Enhanced intelligent command parser with confidence scoring.
    This is the CORE intelligence engine missing from main.py.
    """
    try:
        # Try to use the advanced intelligence engine
        from core.intelligence_engine import intelligence_engine
        
        logger.info(f"🧠 Intelligence Engine analyzing: {user_input}")
        intent_match = await intelligence_engine.analyze_intent_with_confidence(user_input)
        
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
        
        # 🔥 ENHANCED: If confidence is too low, fallback to legacy parser
        if intent_match.confidence < 0.5:
            logger.info(f"⚠️ Low confidence ({intent_match.confidence:.0%}), falling back to legacy parser")
            return await _legacy_intelligent_command_parser(user_input)
        
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
    
    # File operation detection
    if any(phrase in user_input_lower for phrase in ["create file", "write file", "make file", "új fájl", "létrehozás"]):
        # Extract file path
        words = user_input.split()
        file_path = None
        for i, word in enumerate(words):
            if word.lower() in ["file", "fájl"] and i < len(words) - 1:
                file_path = words[i + 1]
                break
        
        return {
            "type": "FILE_OPERATION",
            "operation": "create",
            "path": file_path or "new_file.txt",
            "confidence": 0.8,
            "confidence_level": "High"
        }
    
    elif any(phrase in user_input_lower for phrase in ["read file", "show file", "open file", "olvasás"]):
        words = user_input.split()
        file_path = None
        for i, word in enumerate(words):
            if word.lower() in ["file", "fájl"] and i < len(words) - 1:
                file_path = words[i + 1]
                break
        
        return {
            "type": "FILE_OPERATION",
            "operation": "read",
            "path": file_path,
            "confidence": 0.8,
            "confidence_level": "High"
        }
    
    elif any(phrase in user_input_lower for phrase in ["list files", "show files", "ls", "dir", "fájlok"]):
        return {
            "type": "FILE_OPERATION",
            "operation": "list",
            "path": ".",
            "confidence": 0.9,
            "confidence_level": "Very High"
        }
    
    # Directory organization detection
    elif any(phrase in user_input_lower for phrase in ["rendszerezd", "szervezd", "organize", "rendezd", "kategorizáld"]):
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
            target_folder = ".",
        
        return {
            "type": "DIRECTORY_ORGANIZATION",
            "operation": "organize",
            "path": target_folder,
            "confidence": 0.8,
            "confidence_level": "High"        }
    
    # Shell command detection
    elif any(phrase in user_input_lower for phrase in ["run command", "execute", "shell", "cmd", "parancs"]):
        # Extract command
        command = user_input
        if "run command" in user_input_lower:
            command = user_input.split("run command", 1)[1].strip()
        elif "execute" in user_input_lower:
            command = user_input.split("execute", 1)[1].strip()
        
        return {
            "type": "SHELL_COMMAND",
            "command": command,
            "confidence": 0.7,
            "confidence_level": "High"
        }
      # System analysis and reporting detection (enhanced patterns)
    elif any(phrase in user_input_lower for phrase in [
        "analyze system", "system analysis", "performance analysis", "generate report", "create report",
        "system performance", "performance report", "analyze performance", "system report",
        "output paste to report", "paste to report", "output to report"
    ]):
        # Extract report file name if specified
        report_file = "system_performance_report.txt"
        
        # Enhanced file name extraction logic
        words = user_input.split()
        for i, word in enumerate(words):
            # Look for "report file", "to report", "paste to", "output to" patterns
            if word.lower() in ["report", "paste", "output"] and i < len(words) - 1:
                next_word = words[i + 1].lower()
                if next_word == "file":
                    report_file = "system_performance_report.txt"
                elif next_word == "to" and i < len(words) - 2:
                    potential_file = words[i + 2]
                    if potential_file.lower() == "file":
                        report_file = "system_performance_report.txt"
                    else:
                        report_file = potential_file if "." in potential_file else f"{potential_file}.txt"
                elif next_word not in ["to", "file", "into"]:
                    report_file = next_word if "." in next_word else f"{next_word}.txt"
                break
        
        return {
            "type": "SYSTEM_ANALYSIS",
            "operation": "analyze_and_report",
            "report_file": report_file,
            "confidence": 0.95,
            "confidence_level": "Very High"
        }
    
    # Default to AI processing
    return {
        "type": "AI_PROCESSING",
        "query": user_input,
        "confidence": 0.5,
        "confidence_level": "Medium"
    }

async def process_file_operation_directly(operation: str, path: str = None, content: str = None) -> dict:
    """Direct file operation execution - GUARANTEED real functionality."""
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
            write_content = content or f"# File created by Project-S Unified System\n# Created at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            
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
            
            if file_path.is_file():
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                return {
                    "status": "success",
                    "message": f"File read successfully: {file_path}",
                    "content": content,
                    "size": file_path.stat().st_size
                }
            else:
                return {"status": "error", "message": f"Path is not a file: {file_path}"}
        
        elif operation == "list":
            list_path = Path(path) if path else Path(".")
            
            if not list_path.exists():
                return {"status": "error", "message": f"Directory not found: {list_path}"}
            
            if not list_path.is_dir():
                return {"status": "error", "message": f"Path is not a directory: {list_path}"}
            
            files = []
            for item in list_path.iterdir():
                files.append({
                    "name": item.name,
                    "type": "directory" if item.is_dir() else "file",
                    "size": item.stat().st_size if item.is_file() else None
                })
            
            return {
                "status": "success",
                "message": f"Directory listed: {list_path}",
                "files": files,
                "count": len(files)
            }
        
        else:
            return {"status": "error", "message": f"Unknown operation: {operation}"}
            
    except Exception as e:
        return {"status": "error", "message": f"File operation failed: {str(e)}"}

async def execute_shell_command_directly(command: str) -> dict:
    """Direct shell command execution - GUARANTEED real functionality."""
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

async def organize_directory_intelligently(target_path: str) -> dict:
    """Intelligent directory organization functionality."""
    try:
        import shutil
        from pathlib import Path
        
        target_directory = Path(target_path)
        
        if not target_directory.exists():
            return {"status": "error", "message": f"Directory not found: {target_directory}"}
        
        if not target_directory.is_dir():
            return {"status": "error", "message": f"Path is not a directory: {target_directory}"}
        
        # File categorization logic
        categories = {
            "documents": [".txt", ".doc", ".docx", ".pdf", ".rtf", ".md"],
            "images": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".svg", ".ico"],
            "videos": [".mp4", ".avi", ".mkv", ".mov", ".wmv", ".flv"],
            "audio": [".mp3", ".wav", ".flac", ".aac", ".ogg"],
            "archives": [".zip", ".rar", ".7z", ".tar", ".gz"],
            "code": [".py", ".js", ".html", ".css", ".java", ".cpp", ".c"],
            "data": [".json", ".xml", ".csv", ".sql", ".db"]
        }
        
        categorized_files = {cat: [] for cat in categories}
        categorized_files["other"] = []
        
        # Categorize files
        for file_path in target_directory.iterdir():
            if file_path.is_file():
                extension = file_path.suffix.lower()
                categorized = False
                
                for category, extensions in categories.items():
                    if extension in extensions:
                        categorized_files[category].append(file_path)
                        categorized = True
                        break
                
                if not categorized:
                    categorized_files["other"].append(file_path)
        
        # Create category directories and move files
        organized_count = 0
        categories_created = []
        
        for category, files in categorized_files.items():
            if files:
                category_path = target_directory / category
                category_path.mkdir(exist_ok=True)
                categories_created.append(category)
                
                for file_path in files:
                    try:
                        destination = category_path / file_path.name
                        
                        # Handle duplicate names
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
                        # If can't move, continue with others
                        pass
        
        return {
            "status": "success",
            "message": f"Directory organization completed: {target_directory}",
            "organized_files": organized_count,
            "categories_created": len(categories_created),
            "categories": categories_created,
            "files_by_category": {cat: len(files) for cat, files in categorized_files.items() if files}
        }
        
    except Exception as e:
        return {"status": "error", "message": f"Directory organization error: {str(e)}"}

async def generate_system_analysis_report(report_file: str = "system_analysis_report.txt") -> dict:
    """Generate comprehensive system analysis and performance report."""
    try:
        import psutil
        import platform
        import os
        import json
        from datetime import datetime
        from pathlib import Path
        
        # Collect system information
        report_data = {
            "timestamp": datetime.now().isoformat(),
            "system_info": {
                "platform": platform.platform(),
                "processor": platform.processor(),
                "architecture": platform.architecture()[0],
                "python_version": platform.python_version(),
                "machine": platform.machine(),
                "node": platform.node()
            },
            "performance_metrics": {
                "cpu_percent": psutil.cpu_percent(interval=1),
                "cpu_count_logical": psutil.cpu_count(logical=True),
                "cpu_count_physical": psutil.cpu_count(logical=False),
                "memory": {
                    "total": psutil.virtual_memory().total,
                    "available": psutil.virtual_memory().available,
                    "percent": psutil.virtual_memory().percent,
                    "used": psutil.virtual_memory().used,
                    "free": psutil.virtual_memory().free
                },
                "disk": {
                    "total": psutil.disk_usage('/').total if os.name != 'nt' else psutil.disk_usage('C:').total,
                    "used": psutil.disk_usage('/').used if os.name != 'nt' else psutil.disk_usage('C:').used,
                    "free": psutil.disk_usage('/').free if os.name != 'nt' else psutil.disk_usage('C:').free,
                    "percent": psutil.disk_usage('/').percent if os.name != 'nt' else psutil.disk_usage('C:').percent
                }
            },
            "network": {
                "io_counters": psutil.net_io_counters()._asdict(),
                "connections": len(psutil.net_connections())
            },
            "processes": {
                "count": len(psutil.pids()),
                "top_cpu": []
            }
        }
        
        # Get top CPU consuming processes
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
            try:
                processes.append(proc.info)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        
        # Sort by CPU usage and get top 5
        processes.sort(key=lambda x: x['cpu_percent'] or 0, reverse=True)
        report_data["processes"]["top_cpu"] = processes[:5]
        
        # Project-S specific diagnostics
        project_s_status = {
            "modules_loaded": [],
            "diagnostic_available": False,
            "dashboard_status": "Not Running",
            "ai_models_status": "Unknown"
        }
        
        # Check if Project-S components are available
        try:
            import diagnostics_manager
            project_s_status["diagnostic_available"] = True
            project_s_status["modules_loaded"].append("diagnostics_manager")
        except ImportError:
            pass
        
        try:
            import model_manager
            project_s_status["modules_loaded"].append("model_manager")
            project_s_status["ai_models_status"] = "Available"
        except ImportError:
            pass
        
        try:
            import intelligent_workflow_orchestrator
            project_s_status["modules_loaded"].append("intelligent_workflow_orchestrator")
        except ImportError:
            pass
        
        report_data["project_s"] = project_s_status
        
        # Generate human-readable report
        report_content = f"""
PROJECT-S SYSTEM ANALYSIS REPORT
Generated: {report_data['timestamp']}
{'=' * 50}

SYSTEM INFORMATION:
- Platform: {report_data['system_info']['platform']}
- Processor: {report_data['system_info']['processor']}
- Architecture: {report_data['system_info']['architecture']}
- Python Version: {report_data['system_info']['python_version']}
- Machine: {report_data['system_info']['machine']}
- Node: {report_data['system_info']['node']}

PERFORMANCE METRICS:
- CPU Usage: {report_data['performance_metrics']['cpu_percent']:.1f}%
- CPU Cores (Logical): {report_data['performance_metrics']['cpu_count_logical']}
- CPU Cores (Physical): {report_data['performance_metrics']['cpu_count_physical']}

MEMORY:
- Total: {report_data['performance_metrics']['memory']['total'] / (1024**3):.2f} GB
- Used: {report_data['performance_metrics']['memory']['used'] / (1024**3):.2f} GB
- Available: {report_data['performance_metrics']['memory']['available'] / (1024**3):.2f} GB
- Usage: {report_data['performance_metrics']['memory']['percent']:.1f}%

DISK USAGE:
- Total: {report_data['performance_metrics']['disk']['total'] / (1024**3):.2f} GB
- Used: {report_data['performance_metrics']['disk']['used'] / (1024**3):.2f} GB
- Free: {report_data['performance_metrics']['disk']['free'] / (1024**3):.2f} GB
- Usage: {report_data['performance_metrics']['disk']['percent']:.1f}%

NETWORK:
- Bytes Sent: {report_data['network']['io_counters']['bytes_sent'] / (1024**2):.2f} MB
- Bytes Received: {report_data['network']['io_counters']['bytes_recv'] / (1024**2):.2f} MB
- Active Connections: {report_data['network']['connections']}

PROCESSES:
- Total Running: {report_data['processes']['count']}

TOP CPU CONSUMING PROCESSES:
"""
        
        for i, proc in enumerate(report_data['processes']['top_cpu'], 1):
            report_content += f"{i}. {proc['name']} (PID: {proc['pid']}) - CPU: {proc['cpu_percent'] or 0:.1f}% Memory: {proc['memory_percent'] or 0:.1f}%\n"
        
        report_content += f"""
PROJECT-S STATUS:
- Loaded Modules: {', '.join(report_data['project_s']['modules_loaded']) if report_data['project_s']['modules_loaded'] else 'None'}
- Diagnostics: {'Available' if report_data['project_s']['diagnostic_available'] else 'Not Available'}
- AI Models: {report_data['project_s']['ai_models_status']}

ANALYSIS SUMMARY:
"""
        
        # Generate analysis summary
        memory_status = "Good" if report_data['performance_metrics']['memory']['percent'] < 80 else "High"
        cpu_status = "Good" if report_data['performance_metrics']['cpu_percent'] < 70 else "High"
        disk_status = "Good" if report_data['performance_metrics']['disk']['percent'] < 85 else "High"
        
        report_content += f"""- Memory Usage: {memory_status} ({report_data['performance_metrics']['memory']['percent']:.1f}%)
- CPU Usage: {cpu_status} ({report_data['performance_metrics']['cpu_percent']:.1f}%)
- Disk Usage: {disk_status} ({report_data['performance_metrics']['disk']['percent']:.1f}%)
- Overall System Health: {'Good' if all(status == 'Good' for status in [memory_status, cpu_status, disk_status]) else 'Needs Attention'}

Raw data (JSON format):
{json.dumps(report_data, indent=2)}
"""
        
        # Write report to file
        report_path = Path(report_file)
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        return {
            "status": "success",
            "message": f"System analysis report generated successfully",
            "report_path": str(report_path.absolute()),
            "size": report_path.stat().st_size,
            "summary": f"System Health: {'Good' if all(status == 'Good' for status in [memory_status, cpu_status, disk_status]) else 'Needs Attention'} | CPU: {report_data['performance_metrics']['cpu_percent']:.1f}% | Memory: {report_data['performance_metrics']['memory']['percent']:.1f}% | Disk: {report_data['performance_metrics']['disk']['percent']:.1f}%"
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to generate system analysis report: {str(e)}"
        }

# === END OF MISSING CORE FUNCTIONALITY ===

# === MAIN ENTRY POINT ===
async def main():
    """Main entry point for Project-S Unified System."""
    try:
        print("🚀 PROJECT-S UNIFIED SYSTEM STARTING...")
        
        # Create and initialize the unified agent
        agent = ProjectSUnified()
        
        # Initialize the system
        logger.info("🚀 Initializing Project-S Unified System...")
        initialized = await agent.initialize()
        
        if not initialized:
            print("❌ Failed to initialize Project-S system")
            return False
        
        logger.info("🎉 Project-S Unified System initialized successfully")
        
        # Run the unified interface
        await agent.run_unified_interface()
        
        # Cleanup on exit
        await agent.cleanup()
        print("\n👋 Project-S session ended. Goodbye!")
        return True
        
    except KeyboardInterrupt:
        print("\n\n⏸️ System interrupted by user")
        if 'agent' in locals():
            await agent.cleanup()
        print("👋 Project-S session ended. Goodbye!")
        return True
    except Exception as e:
        logger.error(f"❌ Fatal error in main: {e}")
        print(f"💥 Fatal error: {e}")
        if 'agent' in locals():
            await agent.cleanup()
        return False

if __name__ == "__main__":
    # Run the unified Project-S system
    asyncio.run(main())