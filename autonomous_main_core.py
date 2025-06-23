#!/usr/bin/env python3
"""
Project-S Autonomous System Launcher (No LangGraph)
===================================================
Launches the autonomous ecosystem without LangGraph components for testing.
"""

import asyncio
import logging
import time
from datetime import datetime
from pathlib import Path
import sys
import os

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('logs/autonomous_system.log', mode='w', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)

# Ensure logs directory exists
os.makedirs('logs', exist_ok=True)

# Add project root to path
project_root = Path(__file__).parent.absolute()
sys.path.insert(0, str(project_root))

async def initialize_core_autonomous_system():
    """Initialize core autonomous components without LangGraph."""
    logger.info("🚀 Initializing Project-S Core Autonomous System (No LangGraph)")
    
    try:
        # 1. Core System Components (No LangGraph)
        logger.info("📡 Initializing core event bus...")
        from core.event_bus import event_bus
        
        logger.info("💾 Initializing conversation manager...")
        from core.conversation_manager import conversation_manager
        
        logger.info("🧠 Initializing memory system...")
        from core.memory_system import MemorySystem
        memory_system = MemorySystem()
        
        # 2. Diagnostics and Monitoring (if available)
        try:
            logger.info("📊 Initializing diagnostics manager...")
            from core.diagnostics import diagnostics_manager
        except ImportError:
            logger.warning("⚠️ Diagnostics manager not available")
        
        # 3. Tool Registry
        logger.info("🛠️ Loading tool registry...")
        from tools.tool_registry import tool_registry
        tool_count = await tool_registry.load_tools()
        logger.info(f"✅ Loaded {tool_count} tools")
        
        # 4. Model Manager (simplified version)
        try:
            logger.info("🤖 Initializing simplified model manager...")
            from integrations.simplified_model_manager import model_manager
            logger.info("✅ Model manager initialized")
        except Exception as e:
            logger.warning(f"⚠️ Model manager not available: {e}")
        
        # 5. Command Processing System
        logger.info("⚙️ Initializing command processor...")
        from core.command_processor import CommandProcessor
        command_processor = CommandProcessor()
        
        # 6. AI Command Handler (basic version)
        try:
            logger.info("🎯 Initializing AI command handler...")
            from core.ai_command_handler import ai_handler
            logger.info("✅ AI command handler initialized")
        except Exception as e:
            logger.warning(f"⚠️ AI command handler not fully available: {e}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to initialize core autonomous system: {e}")
        import traceback
        traceback.print_exc()
        return False

async def display_core_system_status():
    """Display core system status."""
    logger.info("📋 Core System Status Overview")
    print("\n" + "="*60)
    print("🤖 PROJECT-S CORE AUTONOMOUS SYSTEM STATUS")
    print("="*60)
    
    try:
        # Event Bus Status
        from core.event_bus import event_bus
        print(f"📡 Event Bus: ✅ Active")
        
        # Conversation Manager Status
        from core.conversation_manager import conversation_manager
        print(f"💾 Conversation Manager: ✅ Active")
        
        # Memory System Status
        from core.memory_system import MemorySystem
        print(f"🧠 Memory System: ✅ Available")
        
        # Tool Registry Status
        from tools.tool_registry import tool_registry
        tools = tool_registry.list_tools()
        print(f"🛠️ Tools Available: {len(tools)}")
        if tools:
            print("   Available tools:")
            for tool_name in sorted(tools.keys())[:5]:  # Show first 5
                print(f"     - {tool_name}")
            if len(tools) > 5:
                print(f"     ... and {len(tools) - 5} more")
        
        # Model Manager Status
        try:
            from integrations.simplified_model_manager import model_manager
            print(f"🧠 AI Models: ✅ Available")
        except:
            print(f"🧠 AI Models: ⚠️ Limited availability")
        
    except Exception as e:
        print(f"❌ Error getting system status: {e}")
    
    print("="*60)
    print("📚 Commands: Type 'help', 'status', or natural language")
    print("📝 Note: Running in core mode (LangGraph features disabled)")
    print("="*60 + "\n")

async def run_core_interactive_mode():
    """Run the core system in interactive mode."""
    print("\n🎯 PROJECT-S CORE MODE ACTIVE")
    print("Core autonomous system running (enhanced features will be enabled when LangGraph is available).")
    print("You can issue commands and test the core functionality.\n")
    
    # Import command processing
    from core.command_processor import CommandProcessor
    command_processor = CommandProcessor()
    
    while True:
        try:
            user_input = input("🤖 Project-S-Core> ").strip()
            
            if not user_input:
                continue
            
            if user_input.lower() in ['exit', 'quit', 'bye']:
                print("👋 Shutting down core system...")
                break
            
            if user_input.lower() == 'status':
                await display_core_system_status()
                continue
            
            if user_input.lower() == 'help':
                print("\n📖 Available Commands:")
                print("  status    - Show system status")
                print("  help      - Show this help") 
                print("  tools     - List available tools")
                print("  test      - Run basic functionality test")
                print("  exit/quit - Shutdown system")
                print("  Or type any natural language command\n")
                continue
            
            if user_input.lower() == 'tools':
                from tools.tool_registry import tool_registry
                tools = tool_registry.list_tools()
                print(f"\n🛠️ Available Tools ({len(tools)}):")
                for tool_name, tool_info in sorted(tools.items()):
                    print(f"  • {tool_name}: {tool_info.get('description', 'No description')}")
                print()
                continue
            
            if user_input.lower() == 'test':
                print("🧪 Running core functionality test...")
                try:
                    # Test event bus
                    from core.event_bus import event_bus
                    event_bus.emit("test_event", {"message": "Core system test"})
                    print("  ✅ Event bus working")
                    
                    # Test conversation manager
                    from core.conversation_manager import conversation_manager
                    conversation_manager.add_message("system", "Test message")
                    print("  ✅ Conversation manager working")
                    
                    # Test tool registry
                    from tools.tool_registry import tool_registry
                    tools = tool_registry.list_tools()
                    print(f"  ✅ Tool registry working ({len(tools)} tools)")
                    
                    print("🎉 Core functionality test passed!\n")
                except Exception as e:
                    print(f"  ❌ Test failed: {e}\n")
                continue
            
            # Process basic commands
            print(f"🔄 Processing: {user_input}")
            start_time = time.time()
            
            # Try to use AI handler if available
            try:
                from core.ai_command_handler import ai_handler
                
                command_data = {
                    "type": "ASK",
                    "command": user_input
                }
                
                result = await ai_handler.process_json_command(json.dumps(command_data))
                
                end_time = time.time()
                
                print(f"\n📋 Result ({end_time - start_time:.2f}s):")
                print("-" * 40)
                
                if isinstance(result, dict):
                    if "error" in result:
                        print(f"❌ Error: {result['error']}")
                    else:
                        print(f"✅ {result}")
                else:
                    print(result)
                
                print("-" * 40 + "\n")
                
            except Exception as e:
                # Fallback to basic command processing
                print(f"⚠️ AI handler not available, using basic processing")
                print(f"📝 You said: {user_input}")
                print(f"🤖 Core system received your command. Enhanced processing will be available when LangGraph is installed.\n")
            
        except KeyboardInterrupt:
            print("\n👋 Shutdown requested...")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
            logger.error(f"Interactive mode error: {e}")

async def main():
    """Main entry point for the core autonomous system."""
    print("\n" + "🚀"*20)
    print("PROJECT-S CORE AUTONOMOUS SYSTEM")
    print("Core AI Agent Components (LangGraph features will be enabled when available)")
    print("🚀"*20 + "\n")
    
    # Initialize the core system
    success = await initialize_core_autonomous_system()
    
    if not success:
        print("❌ Failed to initialize core autonomous system")
        return
    
    # Display initial status
    await display_core_system_status()
    
    try:
        # Run interactive mode
        await run_core_interactive_mode()
    
    except KeyboardInterrupt:
        print("\n🛑 Interrupt received")
    
    finally:
        # Cleanup
        print("🧹 Cleaning up core system...")
        print("✅ Core system shutdown complete")

if __name__ == "__main__":
    import json
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        logger.error(f"System error: {e}")
        print(f"💥 System error: {e}")
