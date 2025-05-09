import asyncio
import logging
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('logs/system.log')
    ]
)
logger = logging.getLogger(__name__)

# Import the main system components
from core.central_executor import executor
from core.cognitive_core import cognitive_core
from core.event_bus import event_bus
from interfaces.dom_listener import dom_listener
from integrations.vscode_interface import VSCodeInterface

async def startup():
    """Initialize and start the Project-S agent system."""
    try:
        logger.info("Project-S agent starting up...")
        
        # Initialize the vscode interface
        vscode = VSCodeInterface()
        
        # Initialize the cognitive core
        # (No explicit initialization needed as the subscription happens in the constructor)
        
        # Initialize the central executor
        await executor.initialize()
        
        # Start the central executor
        await executor.submit({"type": "system", "command": "init"})
        
        # Publish a startup event
        await event_bus.publish("system_channel", {
            "type": "startup",
            "status": "success"
        })
        
        logger.info("Project-S agent successfully started")
        
        # Start the main execution loop
        await executor.run()
    except Exception as e:
        logger.error(f"Error during startup: {str(e)}")
        # Try to publish an error event
        try:
            await event_bus.publish("system_channel", {
                "type": "error",
                "error": f"Startup failed: {str(e)}"
            })
        except:
            pass
        raise

if __name__ == "__main__":
    try:
        asyncio.run(startup())
    except KeyboardInterrupt:
        logger.info("Project-S agent shutting down (user interrupted)")
    except Exception as e:
        logger.error(f"Fatal error: {str(e)}")
        sys.exit(1)