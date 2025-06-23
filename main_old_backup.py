import asyncio
import logging
import os
from core.command_router import router  # already initialized singleton
from core.central_executor import executor
from interfaces.dom_listener import dom_listener
from integrations.vscode_cline_controller import VSCodeClineController
from integrations.vscode_cline_router import register_vscode_cline_handlers
from core.diagnostics_initializer import initialize_diagnostics  # Added for diagnostics integration

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(levelname)s] %(name)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('logs/system.log')
    ]
)

logger = logging.getLogger(__name__)

async def main():
    """Main entry point for the Project-S agent."""
    print("\n" + "="*50)
    print("Project-S Agent")
    print("="*50 + "\n")
    
    try:
        # Initialize diagnostic components
        diagnostics_config = {
            "log_level": os.environ.get("PROJECT_S_LOG_LEVEL", "info"),
            "monitoring_interval": int(os.environ.get("PROJECT_S_MONITORING_INTERVAL", "60")),
            "enable_dashboard": os.environ.get("PROJECT_S_DIAGNOSTICS_DASHBOARD", "true").lower() == "true",
            "dashboard_port": int(os.environ.get("PROJECT_S_DIAGNOSTICS_PORT", "7777"))
        }
        
        await initialize_diagnostics(diagnostics_config)
        logger.info("Diagnostics system initialized")
        
        if diagnostics_config["enable_dashboard"]:
            print(f"Diagnostics dashboard available at http://127.0.0.1:{diagnostics_config['dashboard_port']}")
        
        # Start the DOM listener
        await dom_listener.start()
        logger.info("DOM listener started")
        print("DOM listener is now active")
        
        # Initialize VSCode Cline controller if enabled
        vscode_cline_config = {
            "enabled": True,
            "openrouter": {
                "enabled": True,
                "model": "qwen/qwen-72b",
                "api_key": "${OPENROUTER_API_KEY}"
            },
            "commands": {
                "timeout": 60,
                "auto_format": True,
                "auto_save": True
            },
            "workflows": {
                "enable_advanced": True,
                "context_window_size": 12000
            }
        }
        
        # Only initialize VSCode Cline if API key is available
        if os.environ.get("OPENROUTER_API_KEY"):
            try:
                vscode_cline_controller = VSCodeClineController(vscode_cline_config)
                register_vscode_cline_handlers(router, vscode_cline_controller)
                logger.info("VSCode Cline controller initialized and handlers registered")
                print("VSCode Cline integration is active")
            except Exception as e:
                logger.error(f"Failed to initialize VSCode Cline controller: {e}")
                print(f"VSCode Cline integration failed: {e}")
        else:
            logger.warning("OPENROUTER_API_KEY not found, VSCode Cline integration disabled")
            print("VSCode Cline integration disabled (OPENROUTER_API_KEY not set)")
        
        # Start the command executor
        executor_task = asyncio.create_task(executor.run())
        logger.info("Command executor started")
        print("Command executor is now running")
        
        # Test commands
        await run_test_commands()
        
        # Keep the application running
        print("\nProject-S Agent is running. Press Ctrl+C to exit.")
        while True:
            await asyncio.sleep(1)
            
    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt, shutting down...")
        print("\nShutting down Project-S Agent...")
        dom_listener.stop()
        executor_task.cancel()
        
        # Shutdown diagnostics dashboard if running
        try:
            from integrations.diagnostics_dashboard import dashboard, stop_dashboard
            await stop_dashboard()
            logger.info("Diagnostics dashboard stopped")
        except (ImportError, Exception) as e:
            logger.warning(f"Failed to stop diagnostics dashboard: {e}")
        
    except Exception as e:
        logger.error(f"Error in main function: {str(e)}")
        print(f"An error occurred: {str(e)}")
    
    print("\n" + "="*50)
    print("Project-S Agent - Shutdown Complete")
    print("="*50 + "\n")

async def run_test_commands():
    """Run test commands to verify the system is working."""
    # Test commands removed for production/DOM-only mode
    pass

if __name__ == "__main__":
    asyncio.run(main())