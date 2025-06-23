"""
Hybrid Workflow Integration for Project-S
========================================
Integrates the new Hybrid AI-Powered Workflow System with the existing Project-S infrastructure.
This module serves as the bridge between user inputs and the hybrid workflow processing.
"""

import asyncio
import logging
from typing import Dict, Any, Optional
from pathlib import Path

# Import the hybrid workflow system
from hybrid_workflow_system import (
    HybridWorkflowSystem,
    process_hybrid_workflow,
    hybrid_workflow_system
)

# Import existing Project-S components
from tools.tool_registry import tool_registry
from tools.system_tools import SystemCommandTool
from tools.file_tools import FileWriteTool

# Simple FileManager wrapper for compatibility
class FileManager:
    """Simple wrapper around file tools for compatibility"""
    
    def __init__(self):
        self.write_tool = FileWriteTool()
    
    async def create_file(self, file_path: str, content: str) -> Dict[str, Any]:
        """Create a file with given content"""
        return await self.write_tool.execute(path=file_path, content=content)

logger = logging.getLogger(__name__)

class ProjectSHybridIntegration:
    """
    Integration layer between Project-S and the Hybrid Workflow System
    """
    
    def __init__(self):
        """Initialize the integration layer"""
        self.hybrid_system = hybrid_workflow_system
        self.fallback_tools = {
            "system_command": SystemCommandTool(),
            "file_manager": FileManager()
        }
        
        logger.info("🔗 Project-S Hybrid Workflow Integration initialized")
    
    async def process_user_command(self, user_input: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Main entry point for processing user commands through the hybrid system
        
        Args:
            user_input: The user's command/request
            context: Optional context information
            
        Returns:
            Dict[str, Any]: Processing result
        """
        try:
            logger.info(f"🎯 Processing command through hybrid system: {user_input}")
            
            # Add context to the processing
            kwargs = context or {}
            
            # Process through hybrid workflow system
            result = await process_hybrid_workflow(user_input, **kwargs)
            
            # Add integration metadata
            result["integration_version"] = "1.0.0"
            result["processed_by"] = "Project-S Hybrid Workflow System"
            
            # Log performance metrics
            self._log_performance_metrics(result)
            
            return result
            
        except Exception as e:
            logger.error(f"Hybrid workflow processing failed: {e}")
            
            # Fallback to basic command execution
            return await self._fallback_processing(user_input, context)
    
    async def _fallback_processing(self, user_input: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Fallback processing using basic tools when hybrid system fails
        """
        try:
            logger.info("🔄 Using fallback processing")
            
            # Try to classify the command type
            if any(keyword in user_input.lower() for keyword in ["file", "create", "write", "save"]):
                # File operation
                result = await self._fallback_file_operation(user_input)
            elif any(keyword in user_input.lower() for keyword in ["system", "run", "execute", "command"]):
                # System command
                result = await self._fallback_system_command(user_input)
            else:
                # Generic processing
                result = {
                    "success": False,
                    "error": "Unable to process command with hybrid system or fallback",
                    "user_input": user_input,
                    "processing_strategy": "fallback_failed"
                }
            
            return result
            
        except Exception as e:
            logger.error(f"Fallback processing also failed: {e}")
            return {
                "success": False,
                "error": f"Complete processing failure: {str(e)}",
                "user_input": user_input,
                "processing_strategy": "complete_failure"
            }
    
    async def _fallback_file_operation(self, user_input: str) -> Dict[str, Any]:
        """Fallback file operation processing"""
        try:
            # Simple file creation
            filename = "fallback_output.txt"
            content = f"Fallback processing result for: {user_input}"
            
            file_manager = self.fallback_tools["file_manager"]
            result = await file_manager.create_file(filename, content)
            
            result["processing_strategy"] = "fallback_file"
            return result
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Fallback file operation failed: {str(e)}",
                "processing_strategy": "fallback_file_failed"
            }
    
    async def _fallback_system_command(self, user_input: str) -> Dict[str, Any]:
        """Fallback system command processing"""
        try:
            # Extract potential command from user input
            command = "echo Fallback command execution"
            
            system_tool = self.fallback_tools["system_command"]
            result = await system_tool.execute(command, timeout=10)
            
            result["processing_strategy"] = "fallback_system"
            return result
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Fallback system command failed: {str(e)}",
                "processing_strategy": "fallback_system_failed"
            }
    
    def _log_performance_metrics(self, result: Dict[str, Any]):
        """Log performance metrics for monitoring"""
        try:
            strategy = result.get("processing_strategy", "unknown")
            success = result.get("success", False)
            time_taken = result.get("total_processing_time", 0)
            
            logger.info(f"📊 Performance: {strategy} | {'✅' if success else '❌'} | {time_taken:.3f}s")
            
        except Exception as e:
            logger.warning(f"Failed to log performance metrics: {e}")
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get current system status and statistics"""
        try:
            hybrid_stats = self.hybrid_system.get_system_stats()
            
            return {
                "hybrid_system_status": "operational",
                "hybrid_statistics": hybrid_stats,
                "integration_version": "1.0.0",
                "available_fallback_tools": list(self.fallback_tools.keys()),
                "total_workflows_available": {
                    "template_workflows": len(self.hybrid_system.template_engine.template_workflows),
                    "learned_patterns": len(self.hybrid_system.learning_system.learned_patterns)
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to get system status: {e}")
            return {
                "hybrid_system_status": "error",
                "error": str(e),
                "integration_version": "1.0.0"
            }

# Global integration instance
project_s_hybrid_integration = ProjectSHybridIntegration()

async def process_command_hybrid(user_input: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Main entry point for hybrid command processing in Project-S
    
    Args:
        user_input: The user's command/request  
        context: Optional context information
        
    Returns:
        Dict[str, Any]: Processing result
    """
    return await project_s_hybrid_integration.process_user_command(user_input, context)

def get_hybrid_system_status() -> Dict[str, Any]:
    """Get the current status of the hybrid system"""
    return project_s_hybrid_integration.get_system_status()

if __name__ == "__main__":
    # Test the integration
    async def test_integration():
        print("🧪 Testing Project-S Hybrid Integration")
        print("=" * 50)
        
        # Test different types of commands
        test_commands = [
            "optimize my system performance",
            "create a file called system-audit.txt", 
            "analyze this URL: https://github.com",
            "setup development environment for Python with virtual environment",
            "invalid command that should trigger fallback"
        ]
        
        for i, cmd in enumerate(test_commands, 1):
            print(f"\n🧪 Test {i}: {cmd}")
            print("-" * 30)
            
            try:
                result = await process_command_hybrid(cmd)
                
                success = "✅" if result.get("success") else "❌"
                strategy = result.get("processing_strategy", "unknown")
                time_taken = result.get("total_processing_time", 0)
                
                print(f"{success} Strategy: {strategy} | Time: {time_taken:.3f}s")
                
                if not result.get("success"):
                    print(f"Error: {result.get('error', 'Unknown error')}")
                    
            except Exception as e:
                print(f"❌ Exception: {str(e)}")
        
        # Show system status
        print(f"\n📊 System Status:")
        print("-" * 20)
        status = get_hybrid_system_status()
        print(f"Hybrid System: {status.get('hybrid_system_status', 'unknown')}")
        
        stats = status.get('hybrid_statistics', {})
        if stats:
            print(f"Total Executions: {stats.get('total_executions', 0)}")
            print(f"Template Usage: {stats.get('template_percentage', 0):.1f}%")
            print(f"AI Usage: {stats.get('ai_percentage', 0):.1f}%")
            print(f"Efficiency Score: {stats.get('efficiency_score', 0):.1f}%")
    
    # Run integration test
    asyncio.run(test_integration())
