"""
Project-S Enhanced Autonomous System Launcher
============================================
Launches the complete autonomous ecosystem with all proactive capabilities.
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

async def initialize_autonomous_ecosystem():
    """Initialize the complete autonomous ecosystem."""
    logger.info("🚀 Initializing Project-S Autonomous Ecosystem")
    
    try:
        # 1. Core System Components
        logger.info("📡 Initializing core event bus...")
        from core.event_bus import event_bus
        
        logger.info("🧠 Initializing cognitive core...")
        from core.cognitive_core_langgraph import cognitive_core_langgraph
        
        logger.info("⚡ Initializing central executor...")
        from core.central_executor import executor
        await executor.initialize()
        
        # 2. Diagnostics and Monitoring
        logger.info("📊 Initializing diagnostics manager...")
        from core.diagnostics import diagnostics_manager
        
        logger.info("🌐 Starting diagnostics dashboard...")
        from integrations.diagnostics_dashboard import dashboard
        # Start dashboard in background
        asyncio.create_task(dashboard.start())
        
        # 3. Enhanced Autonomous Manager
        logger.info("🤖 Initializing enhanced autonomous manager...")
        from core.autonomous_manager import autonomous_manager
        await autonomous_manager.start()
        
        # 4. System Health Monitoring
        logger.info("💓 Starting system health monitoring...")
        from check_system import SystemHealthCheck, cpu_usage_check, memory_usage_check, disk_space_check
        
        health_checker = SystemHealthCheck(check_interval=60)
        health_checker.register_check("CPU Usage", cpu_usage_check)
        health_checker.register_check("Memory Usage", memory_usage_check)
        health_checker.register_check("Disk Space", disk_space_check)
        
        # Start health monitoring in background
        asyncio.create_task(health_checker.start())
        
        # 5. Chrome Extension Integration
        logger.info("🌐 Initializing Chrome extension integration...")
        from interfaces.dom_listener import dom_listener
        # DOM listener starts automatically when configured
        
        # 6. AI Model Manager
        logger.info("🤖 Initializing AI model manager...")
        from integrations.simplified_model_manager import model_manager
        
        # 7. Tool Registry
        logger.info("🛠️ Loading tool registry...")
        from tools.tool_registry import tool_registry
        tool_count = await tool_registry.load_tools()
        logger.info(f"✅ Loaded {tool_count} tools")
        
        # 8. API Server (if available)
        try:
            logger.info("🚪 Starting API server...")
            from interfaces.api_server import app
            # API server would be started separately in production
            logger.info("✅ API server initialized")
        except Exception as e:
            logger.warning(f"⚠️ API server not started: {e}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to initialize autonomous ecosystem: {e}")
        return False

async def display_system_status():
    """Display comprehensive system status."""
    logger.info("📋 System Status Overview")
    print("\n" + "="*60)
    print("🤖 PROJECT-S AUTONOMOUS ECOSYSTEM STATUS")
    print("="*60)
    
    try:
        # Autonomous Manager Status
        from core.autonomous_manager import autonomous_manager
        auto_status = autonomous_manager.get_status()
        
        print(f"🔄 Autonomous Manager: {'✅ Running' if auto_status['is_running'] else '❌ Stopped'}")
        print(f"📊 Monitoring Interval: {auto_status['monitoring_interval']}s")
        print(f"⚡ Total Actions Executed: {auto_status['total_actions_executed']}")
        print(f"📈 Metrics History: {auto_status['metrics_history_size']} entries")
        print(f"🎯 Active Strategies: {len(auto_status['active_strategies'])}")
        
        # Recent autonomous actions
        if auto_status['recent_actions']:
            print("\n🕒 Recent Autonomous Actions:")
            for action in auto_status['recent_actions'][-5:]:
                status_icon = "✅" if action['success'] else "❌"
                print(f"  {status_icon} {action['action_type']} (triggered by: {action['triggered_by']})")
        
        # Diagnostics Status
        from core.diagnostics import diagnostics_manager
        if hasattr(diagnostics_manager, 'get_current_metrics'):
            metrics = diagnostics_manager.get_current_metrics()
            print(f"\n💻 System Metrics:")
            print(f"  CPU: {metrics.get('cpu_percent', 0):.1f}%")
            print(f"  Memory: {metrics.get('memory_percent', 0):.1f}%")
            print(f"  Threads: {metrics.get('threads_count', 0)}")
        
        # Tool Registry Status
        from tools.tool_registry import tool_registry
        tools = tool_registry.list_tools()
        print(f"\n🛠️ Tools Available: {len(tools)}")
        
        # Model Manager Status
        try:
            from integrations.simplified_model_manager import model_manager
            print(f"🧠 AI Models: Initialized")
        except:
            print(f"🧠 AI Models: Not available")
        
    except Exception as e:
        print(f"❌ Error getting system status: {e}")
    
    print("="*60)
    print("🌐 Dashboard: http://localhost:7777")
    print("📚 Commands: Type 'help', 'status', or natural language")
    print("="*60 + "\n")

async def run_interactive_mode():
    """Run the autonomous system in interactive mode."""
    print("\n🎯 PROJECT-S AUTONOMOUS MODE ACTIVE")
    print("The system is now running autonomously with enhanced capabilities.")
    print("You can still issue commands or just observe autonomous operations.\n")
    
    # Import the main AI handler for interactive commands
    from core.ai_command_handler import ai_handler
    from core.command_processor import CommandProcessor
    
    command_processor = CommandProcessor()
    
    while True:
        try:
            user_input = input("🤖 Project-S> ").strip()
            
            if not user_input:
                continue
            
            if user_input.lower() in ['exit', 'quit', 'bye']:
                print("👋 Shutting down autonomous system...")
                break
            
            if user_input.lower() == 'status':
                await display_system_status()
                continue
            
            if user_input.lower() == 'help':
                print("\n📖 Available Commands:")
                print("  status    - Show system status")
                print("  help      - Show this help")
                print("  exit/quit - Shutdown system")
                print("  Or type any natural language command\n")
                continue
            
            # Process the command through the AI system
            print(f"🔄 Processing: {user_input}")
            start_time = time.time()
            
            # Create command structure
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
            
        except KeyboardInterrupt:
            print("\n👋 Shutdown requested...")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
            logger.error(f"Interactive mode error: {e}")

async def monitor_autonomous_operations():
    """Monitor and display autonomous operations in real-time."""
    from core.autonomous_manager import autonomous_manager
    
    last_action_count = 0
    
    while True:
        try:
            await asyncio.sleep(30)  # Check every 30 seconds
            
            status = autonomous_manager.get_status()
            current_action_count = status['total_actions_executed']
            
            if current_action_count > last_action_count:
                print(f"\n🤖 Autonomous Activity Detected:")
                
                # Show new actions
                new_actions = status['recent_actions'][-(current_action_count - last_action_count):]
                for action in new_actions:
                    status_icon = "✅" if action['success'] else "❌"
                    timestamp = action['timestamp']
                    print(f"  {status_icon} {action['action_type']} at {timestamp}")
                
                last_action_count = current_action_count
                print()  # Add spacing
            
        except Exception as e:
            logger.error(f"Monitoring error: {e}")
            await asyncio.sleep(5)

async def main():
    """Main entry point for the autonomous system."""
    print("\n" + "🚀"*20)
    print("PROJECT-S AUTONOMOUS ECOSYSTEM")
    print("Advanced AI Agent with Proactive Capabilities")
    print("🚀"*20 + "\n")
    
    # Initialize the ecosystem
    success = await initialize_autonomous_ecosystem()
    
    if not success:
        print("❌ Failed to initialize autonomous ecosystem")
        return
    
    # Display initial status
    await display_system_status()
    
    # Start background monitoring
    monitor_task = asyncio.create_task(monitor_autonomous_operations())
    
    try:
        # Run interactive mode
        await run_interactive_mode()
    
    except KeyboardInterrupt:
        print("\n🛑 Interrupt received")
    
    finally:
        # Cleanup
        print("🧹 Cleaning up autonomous system...")
        
        try:
            from core.autonomous_manager import autonomous_manager
            await autonomous_manager.stop()
        except:
            pass
        
        # Cancel monitoring
        monitor_task.cancel()
        
        print("✅ Autonomous system shutdown complete")

if __name__ == "__main__":
    import json
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        logger.error(f"System error: {e}")
        print(f"💥 System error: {e}")
