"""
Project-S Agent system startup script.
Initializes all components in proper order.
"""

import asyncio
import logging
import sys
from pathlib import Path

# Configure logging
event_log = Path("logs")
event_log.mkdir(exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(event_log / 'system.log')
    ]
)
logger = logging.getLogger("system")

async def initialize_system():
    logger.info("Project-S system initialization starting...")
    # 1. Config Manager
    logger.info("Loading configuration...")
    from core.config_manager import ConfigManager
    config_manager = ConfigManager()

    # 2. Event Bus
    logger.info("Initializing event bus...")
    from core.event_bus import event_bus

    # 3. Memory System
    logger.info("Initializing memory system...")
    from core.memory_system import MemorySystem
    memory_system = MemorySystem()

    # 4. LLM Models
    logger.info("Initializing LLM models...")
    from llm_clients.model_selector import initialize_models
    # initialize_models is synchronous, so call without await
    initialize_models()

    # 5. VSCode Interface
    logger.info("Initializing VSCode interface...")
    from integrations.vscode_interface import vscode_interface

    # 6. API Server
    logger.info("Starting API server...")
    from interfaces.api_server import api_server
    await api_server.start()

    # 7. DOM Listener
    logger.info("Initializing DOM listener...")
    from interfaces.dom_listener import dom_listener

    # 8. Cognitive Core
    logger.info("Initializing cognitive core...")
    from core.cognitive_core import cognitive_core

    # 9. Central Executor
    logger.info("Initializing central executor...")
    from core.central_executor import executor
    await executor.initialize()

    logger.info("System initialization completed successfully.")
    return True

async def run_system():
    init_ok = await initialize_system()
    if not init_ok:
        logger.error("System initialization failed.")
        sys.exit(1)

    logger.info("Starting central executor main loop...")
    from core.central_executor import executor
    await executor.run()

if __name__ == '__main__':
    try:
        asyncio.run(run_system())
    except KeyboardInterrupt:
        logger.info("Shutdown requested by user.")
    except Exception as e:
        # Log full traceback for startup errors
        logger.error(f"Fatal error during startup: {e}", exc_info=True)
        sys.exit(1)