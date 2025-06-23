"""
Initialization module for LangGraph integration components.
This ensures all LangGraph components are properly registered on system startup.
"""
import asyncio
import logging
import os
from core.command_router import router
from integrations.langgraph_router import register_langgraph_handlers
from integrations.langgraph_error_monitor import register_error_monitoring_handlers
from integrations.langgraph_state_manager import state_manager
import integrations.langgraph_state_enhanced

logger = logging.getLogger(__name__)

async def initialize_langgraph():
    """Initialize all LangGraph integration components"""
    # Register command handlers
    register_langgraph_handlers(router)
    
    # Register error monitoring
    await register_error_monitoring_handlers()
    
    # Ensure data directories exist for state persistence
    os.makedirs("data/graph_states/active", exist_ok=True)
    os.makedirs("data/graph_states/checkpoints", exist_ok=True)
    
    # Initialize state manager and enhanced state features
    # Note: langgraph_state_enhanced automatically initializes when imported
    
    logger.info("LangGraph integration components initialized")

def setup_langgraph():
    """Setup function called during system initialization"""
    # Run the initialization in an async task
    loop = asyncio.get_event_loop()
    loop.create_task(initialize_langgraph())
    logger.info("LangGraph setup complete, initialization scheduled")
