"""
Initializes and sets up diagnostic components for Project-S + LangGraph hybrid system
"""

import os
import asyncio
import logging
from typing import Dict, Any, Optional

# Configure directories
DEFAULT_LOG_DIR = "logs"
DEFAULT_DIAGNOSTICS_DIR = "diagnostics"

def setup_directories():
    """Set up required directories for diagnostics"""
    # Ensure log directory exists
    os.makedirs(DEFAULT_LOG_DIR, exist_ok=True)
    
    # Ensure diagnostics directories exist
    os.makedirs(DEFAULT_DIAGNOSTICS_DIR, exist_ok=True)
    os.makedirs(os.path.join(DEFAULT_DIAGNOSTICS_DIR, "graphs"), exist_ok=True)
    os.makedirs(os.path.join(DEFAULT_DIAGNOSTICS_DIR, "reports"), exist_ok=True)
    os.makedirs(os.path.join(DEFAULT_DIAGNOSTICS_DIR, "errors"), exist_ok=True)
    os.makedirs(os.path.join(DEFAULT_DIAGNOSTICS_DIR, "workflows"), exist_ok=True)

async def initialize_diagnostics(config: Optional[Dict[str, Any]] = None):
    """Initialize the diagnostics subsystem"""
    logger = logging.getLogger(__name__)
    logger.info("Initializing diagnostic components...")
    
    # Setup directories
    setup_directories()
    
    # Initialize diagnostics manager
    from core.diagnostics import diagnostics_manager
    
    # Apply configuration if provided
    if config:
        # Apply log level if specified
        if "log_level" in config:
            from core.diagnostics import LogLevel
            level_map = {
                "debug": LogLevel.DEBUG,
                "info": LogLevel.INFO,
                "warning": LogLevel.WARNING,
                "error": LogLevel.ERROR,
                "critical": LogLevel.CRITICAL
            }
            level = level_map.get(config["log_level"].lower(), LogLevel.INFO)
            diagnostics_manager.default_log_level = level
        
        # Apply monitoring interval if specified
        if "monitoring_interval" in config:
            diagnostics_manager.monitoring_interval_seconds = config["monitoring_interval"]
    
    # Initialize the LangGraph diagnostics bridge
    try:
        from integrations.langgraph_diagnostics_bridge import langgraph_diagnostics_bridge
        from integrations.langgraph_diagnostics_bridge import register_diagnostic_commands
        
        # Register diagnostic commands
        await register_diagnostic_commands()
        
        logger.info("LangGraph diagnostics bridge initialized")
    except ImportError as e:
        logger.warning(f"Failed to initialize LangGraph diagnostics bridge: {e}")
    
    # Initialize the diagnostic dashboard if enabled in config
    if config and config.get("enable_dashboard", False):
        try:
            from integrations.diagnostics_dashboard import dashboard, start_dashboard
            
            # Set dashboard port if specified
            if "dashboard_port" in config:
                dashboard.port = config["dashboard_port"]
            
            # Start the dashboard
            dashboard_started = await start_dashboard()
            if dashboard_started:
                logger.info(f"Diagnostic dashboard started at http://127.0.0.1:{dashboard.port}")
            else:
                logger.warning("Failed to start diagnostic dashboard")
        except ImportError as e:
            logger.warning(f"Failed to initialize diagnostic dashboard: {e}")
    
    logger.info("Diagnostics subsystem initialized")
    return True
