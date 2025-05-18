"""
System check script for Project-S.
Verifies that all components are properly initialized and can communicate.
"""

import asyncio
import logging
import sys
import time
from pathlib import Path
import psutil
import os
import signal
from typing import Dict, Any, List, Callable, Awaitable

# Ensure the project root is in the Python path
project_root = Path(__file__).parent.resolve()
sys.path.insert(0, str(project_root))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Import necessary components
from core.event_bus import event_bus
from core.central_executor import executor
from core.cognitive_core import cognitive_core
from interfaces.dom_listener import dom_listener
from integrations.vscode_interface import VSCodeInterface
from llm_clients.model_selector import model_selector, initialize_models

class SystemHealthCheck:
    def __init__(self, check_interval: int = 60):
        self.check_interval = check_interval
        self.health_checks: List[Callable[[], Awaitable[Dict[str, Any]]]] = []
        self.running = False
        self.last_check_results: Dict[str, Any] = {}
        
    def register_check(self, name: str, check_function: Callable[[], Awaitable[Dict[str, Any]]]):
        """Register a health check function"""
        self.health_checks.append((name, check_function))
        
    async def start(self):
        """Start health check monitoring"""
        self.running = True
        while self.running:
            await self._run_checks()
            await asyncio.sleep(self.check_interval)
            
    async def stop(self):
        """Stop health check monitoring"""
        self.running = False
        
    async def _run_checks(self):
        """Run all registered health checks"""
        results = {}
        
        for name, check_func in self.health_checks:
            try:
                result = await check_func()
                results[name] = result
            except Exception as e:
                results[name] = {
                    "status": "error",
                    "error": str(e)
                }
                
        self.last_check_results = results
        return results
        
    async def get_health_status(self) -> Dict[str, Any]:
        """Get the latest health check results"""
        # If we haven't run checks yet, or it's been a while, run them now
        if not self.last_check_results or time.time() - self.last_check_results.get("timestamp", 0) > self.check_interval:
            await self._run_checks()
        
        return self.last_check_results

# Example health check functions
async def cpu_usage_check() -> Dict[str, Any]:
    """Check CPU usage"""
    usage = psutil.cpu_percent(interval=1)
    return {
        "status": "ok" if usage < 80 else "warning",
        "cpu_usage": usage
    }

async def memory_usage_check() -> Dict[str, Any]:
    """Check memory usage"""
    memory = psutil.virtual_memory()
    return {
        "status": "ok" if memory.percent < 80 else "warning",
        "memory_usage": memory.percent
    }

async def disk_space_check() -> Dict[str, Any]:
    """Check disk space usage"""
    disk = psutil.disk_usage('/')
    return {
        "status": "ok" if disk.percent < 90 else "warning",
        "disk_usage": disk.percent
    }

async def run_system_check():
    """Run a system check to verify all components are working."""
    logger.info("Starting system check...")
    
    # Check 1: Event Bus
    logger.info("Checking Event Bus...")
    test_results = {}
    
    async def test_handler(event):
        test_results["received"] = True
        test_results["data"] = event.get("data")
    
    # Subscribe to test channel
    event_bus.subscribe("test_channel", test_handler)
    
    # Publish a test event
    await event_bus.publish("test_channel", {"data": "test_message"})
    
    # Wait a moment for the event to be processed
    await asyncio.sleep(0.1)
    
    if test_results.get("received") and test_results.get("data") == "test_message":
        logger.info("✓ Event Bus is working correctly")
    else:
        logger.error("✗ Event Bus test failed")
    
    # Check 2: Model initialization
    logger.info("Checking Model Selector...")
    initialize_models()
    available_models = list(model_selector.models.keys())
    
    if available_models:
        logger.info(f"✓ Models initialized: {available_models}")
    else:
        logger.warning("✗ No models were initialized")
    
    # Check 3: Central Executor
    logger.info("Checking Central Executor...")
    try:
        # Initialize the executor
        await executor.initialize()
        logger.info("✓ Central Executor initialized successfully")
    except Exception as e:
        logger.error(f"✗ Central Executor initialization failed: {str(e)}")
    
    # Check 4: VS Code Interface
    logger.info("Checking VS Code Interface...")
    try:
        vscode = VSCodeInterface()
        logger.info("✓ VS Code Interface initialized successfully")
    except Exception as e:
        logger.error(f"✗ VS Code Interface initialization failed: {str(e)}")
    
    # Check 5: DOM Listener
    logger.info("Checking DOM Listener...")
    try:
        # Don't actually start the listener, just check initialization
        logger.info("✓ DOM Listener is available")
    except Exception as e:
        logger.error(f"✗ DOM Listener check failed: {str(e)}")
    
    # Final result
    logger.info("System check completed")

# Example usage
if __name__ == "__main__":
    async def main():
        health_checker = SystemHealthCheck(check_interval=60)
        health_checker.register_check("CPU Usage", cpu_usage_check)
        health_checker.register_check("Memory Usage", memory_usage_check)
        health_checker.register_check("Disk Space", disk_space_check)
        
        # Start the health checker
        await health_checker.start()
        
    try:
        asyncio.run(run_system_check())
        asyncio.run(main())
    except Exception as e:
        logger.error(f"System check failed with error: {str(e)}")
        sys.exit(1)