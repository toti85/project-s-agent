"""
Universal Request Processing Chain
---------------------------------
Restored and enhanced universal request processing chain that was 95% functional.
Handles template vs AI decision balance and multi-step execution coordination.
"""

import asyncio
import logging
import json
import time
from datetime import datetime
from typing import Dict, List, Any, Optional, Union
from pathlib import Path, WindowsPath, PosixPath

from core.event_bus import event_bus
from core.error_handler import error_handler
from core.command_router import router
from utils.performance_monitor import monitor_performance

logger = logging.getLogger(__name__)

class SerializationHelper:
    """Helper for handling JSON serialization issues with Path objects"""
    
    @staticmethod
    def path_to_str(obj):
        """Convert Path objects to strings for JSON serialization"""
        if isinstance(obj, (Path, WindowsPath, PosixPath)):
            return str(obj)
        elif isinstance(obj, dict):
            return {k: SerializationHelper.path_to_str(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [SerializationHelper.path_to_str(item) for item in obj]
        return obj
    
    @staticmethod
    def safe_json_dumps(obj, **kwargs):
        """JSON dumps with Path object handling"""
        cleaned_obj = SerializationHelper.path_to_str(obj)
        return json.dumps(cleaned_obj, **kwargs)

class AsyncIOManager:
    """Manages AsyncIO event loops to prevent warnings and cleanup issues"""
    
    def __init__(self):
        self.active_tasks = set()
        self.cleanup_callbacks = []
    
    async def safe_execute(self, coro, timeout=60):
        """Safely execute coroutine with proper cleanup"""
        try:
            task = asyncio.create_task(coro)
            self.active_tasks.add(task)
            
            try:
                result = await asyncio.wait_for(task, timeout=timeout)
                return result
            except asyncio.TimeoutError:
                logger.warning(f"Operation timed out after {timeout} seconds")
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass
                return {"error": f"Operation timed out after {timeout} seconds"}
                
        finally:
            self.active_tasks.discard(task)
    
    async def cleanup(self):
        """Clean up remaining tasks"""
        if self.active_tasks:
            logger.info(f"Cleaning up {len(self.active_tasks)} remaining tasks")
            for task in self.active_tasks:
                if not task.done():
                    task.cancel()
            
            if self.active_tasks:
                await asyncio.gather(*self.active_tasks, return_exceptions=True)
            
            self.active_tasks.clear()
        
        # Run cleanup callbacks
        for callback in self.cleanup_callbacks:
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback()
                else:
                    callback()
            except Exception as e:
                logger.error(f"Error in cleanup callback: {e}")

class TemplateAIDecisionEngine:
    """Balances template-based responses with AI decision making"""
    
    def __init__(self):
        self.templates = {
            "file_operations": {
                "read": "Reading file content",
                "write": "Writing to file",
                "create": "Creating new file",
                "delete": "Deleting file"
            },
            "cmd_operations": {
                "dir": "Listing directory contents",
                "cd": "Changing directory",
                "mkdir": "Creating directory"
            }        }
        self.ai_required_patterns = [
            "analyze", "explain", "suggest", "recommend", 
            "what", "how", "why", "help me understand"
        ]
    
    def should_use_ai(self, request: Dict[str, Any]) -> bool:
        """Determine if AI processing is needed or template response suffices"""
        
        # Check for AI-required patterns - safely handle None values
        query = request.get("query") or ""
        command = request.get("command") or ""
        request_text = str(query).lower()
        request_text += " " + str(command).lower()
        
        if any(pattern in request_text for pattern in self.ai_required_patterns):
            return True
        
        # Check command type
        cmd_type = request.get("type", "").upper()
        
        # Simple operations can use templates
        if cmd_type in ["FILE", "CMD"]:
            action = request.get("action") or ""
            command = request.get("cmd") or ""
            action = str(action).lower()
            command = str(command).lower()
            
            # Standard file operations
            if action in ["read", "write", "create", "delete"]:
                return False
            
            # Standard cmd operations
            if any(simple_cmd in command for simple_cmd in ["dir", "cd", "mkdir", "echo"]):
                return False
          # Default to AI for complex operations
        return True
    
    def get_template_response(self, request: Dict[str, Any]) -> Optional[str]:
        """Get template response if available"""
        cmd_type = request.get("type", "").upper()
        
        if cmd_type == "FILE":
            action = request.get("action") or ""
            action = str(action).lower()
            if action in self.templates["file_operations"]:
                return self.templates["file_operations"][action]
        
        elif cmd_type == "CMD":
            command = request.get("cmd") or ""
            command = str(command).lower()
            for template_cmd, response in self.templates["cmd_operations"].items():
                if template_cmd in command:
                    return response
        
        return None

class UniversalRequestProcessor:
    """
    Restored universal request processing chain with enhanced capabilities
    """
    
    def __init__(self):
        self.serialization_helper = SerializationHelper()
        self.asyncio_manager = AsyncIOManager()
        self.decision_engine = TemplateAIDecisionEngine()
        
        # Performance tracking
        self.request_count = 0
        self.total_processing_time = 0
        self.success_count = 0
        
        logger.info("Universal Request Processor initialized")
    
    @monitor_performance
    async def process_request(self, request: Union[str, Dict[str, Any]], 
                            context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Process any type of request through the universal chain
        
        Args:
            request: The request to process (string or dict)
            context: Optional context information
            
        Returns:
            Dict containing the response
        """
        start_time = time.time()
        request_id = f"req_{int(time.time())}_{self.request_count}"
        self.request_count += 1
        
        try:
            logger.info(f"Processing request {request_id}")
            
            # Step 1: Normalize request format
            normalized_request = await self._normalize_request(request, context)
            
            # Step 2: Template vs AI decision
            use_ai = self.decision_engine.should_use_ai(normalized_request)
            logger.info(f"Request {request_id} - AI decision: {use_ai}")
            
            # Step 3: Get template response if available
            if not use_ai:
                template_response = self.decision_engine.get_template_response(normalized_request)
                if template_response:
                    logger.info(f"Using template response for {request_id}")
                    return {
                        "status": "success",
                        "response": template_response,
                        "source": "template",
                        "request_id": request_id,
                        "processing_time": time.time() - start_time
                    }
            
            # Step 4: Multi-step execution coordination
            result = await self._execute_multi_step(normalized_request, request_id)
            
            # Step 5: Post-process and serialize safely
            final_result = self._post_process_result(result, request_id, start_time)
            
            self.success_count += 1
            self.total_processing_time += time.time() - start_time
            
            return final_result
            
        except Exception as e:
            logger.error(f"Error processing request {request_id}: {e}")
            error_context = {
                "component": "universal_processor",
                "request_id": request_id,
                "operation": "process_request"
            }
            await error_handler.handle_error(e, error_context)
            
            return {
                "status": "error",
                "error": str(e),
                "request_id": request_id,
                "processing_time": time.time() - start_time
            }
    
    async def _normalize_request(self, request: Union[str, Dict[str, Any]], 
                               context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Normalize request to standard format"""
        
        if isinstance(request, str):
            # Try to parse as JSON first
            try:
                parsed = json.loads(request)
                if isinstance(parsed, dict):
                    return parsed
            except json.JSONDecodeError:
                pass
            
            # Treat as natural language query
            return {
                "type": "ASK",
                "query": request,
                "source": "natural_language"
            }
        
        elif isinstance(request, dict):
            # Ensure required fields
            if "type" not in request:
                # Try to infer type
                if "query" in request or "ask" in str(request).lower():
                    request["type"] = "ASK"
                elif "cmd" in request or "command" in request:
                    request["type"] = "CMD"
                elif "path" in request or "file" in str(request).lower():
                    request["type"] = "FILE"
                else:
                    request["type"] = "ASK"  # Default
            
            # Add context if provided
            if context:
                request["context"] = context
            
            return request
        
        else:
            # Fallback for other types
            return {
                "type": "ASK",
                "query": str(request),
                "source": "fallback"
            }
    
    async def _execute_multi_step(self, request: Dict[str, Any], request_id: str) -> Dict[str, Any]:
        """Execute request with multi-step coordination"""
        
        # Check if this is a complex multi-step request
        if self._is_multi_step_request(request):
            return await self._handle_multi_step_workflow(request, request_id)
        else:
            return await self._handle_single_step(request, request_id)
    
    def _is_multi_step_request(self, request: Dict[str, Any]) -> bool:
        """Determine if request requires multi-step processing"""
        
        # Check for workflow indicators
        request_text = str(request.get("query", "")).lower()
        request_text += " " + str(request.get("command", "")).lower()
        
        multi_step_indicators = [
            "create and", "read then", "analyze and", "organize files",
            "workflow", "steps", "process", "pipeline"
        ]
        
        return any(indicator in request_text for indicator in multi_step_indicators)
    
    async def _handle_multi_step_workflow(self, request: Dict[str, Any], request_id: str) -> Dict[str, Any]:
        """Handle complex multi-step workflows"""
        
        logger.info(f"Executing multi-step workflow for {request_id}")
        
        # Use existing workflow system through cognitive core
        try:
            from core.cognitive_core_langgraph import cognitive_core_langgraph
            
            # Convert request to task format
            task = {
                "id": request_id,
                "description": request.get("query", str(request)),
                "type": "general",
                "source_request": request
            }
            
            # Process through cognitive core
            result = await self.asyncio_manager.safe_execute(
                cognitive_core_langgraph.process_task(task),
                timeout=120  # 2 minutes for complex workflows
            )
            
            return {
                "status": "success",
                "result": result,
                "source": "multi_step_workflow",
                "request_id": request_id
            }
            
        except Exception as e:
            logger.error(f"Multi-step workflow failed for {request_id}: {e}")
            # Fallback to single-step processing
            return await self._handle_single_step(request, request_id)
    
    async def _handle_single_step(self, request: Dict[str, Any], request_id: str) -> Dict[str, Any]:
        """Handle single-step requests through command router"""
        
        logger.info(f"Executing single-step command for {request_id}")
        
        try:
            # Route through existing command router
            result = await self.asyncio_manager.safe_execute(
                router.route_command(request),
                timeout=60  # 1 minute for single commands
            )
            
            return {
                "status": "success",
                "result": result,
                "source": "single_step",
                "request_id": request_id
            }
            
        except Exception as e:
            logger.error(f"Single-step execution failed for {request_id}: {e}")
            return {
                "status": "error",
                "error": str(e),
                "request_id": request_id
            }
    
    def _post_process_result(self, result: Dict[str, Any], request_id: str, start_time: float) -> Dict[str, Any]:
        """Post-process result with safe serialization"""
        
        processing_time = time.time() - start_time
        
        # Clean up Path objects and ensure JSON serializable
        cleaned_result = self.serialization_helper.path_to_str(result)
          # Add metadata and extract response for compatibility
        final_result = {
            "request_id": request_id,
            "processing_time": processing_time,
            "timestamp": datetime.now().isoformat(),
            **cleaned_result
        }
        
        # Extract response content for compatibility with tests
        if "execution_result" in cleaned_result and "content" in cleaned_result["execution_result"]:
            final_result["response"] = cleaned_result["execution_result"]["content"]
        elif "result" in cleaned_result and isinstance(cleaned_result["result"], str):
            final_result["response"] = cleaned_result["result"]
        
        # Validate JSON serialization
        try:
            self.serialization_helper.safe_json_dumps(final_result)
        except Exception as e:
            logger.warning(f"Result not JSON serializable, converting: {e}")
            final_result = {
                "request_id": request_id,
                "processing_time": processing_time,
                "timestamp": datetime.now().isoformat(),
                "status": cleaned_result.get("status", "unknown"),
                "response": str(cleaned_result),
                "serialization_note": "Result converted to string due to serialization issues"
            }
        
        return final_result
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get performance statistics"""
        avg_time = self.total_processing_time / max(self.request_count, 1)
        success_rate = self.success_count / max(self.request_count, 1)
        
        return {
            "total_requests": self.request_count,
            "successful_requests": self.success_count,
            "success_rate": success_rate,
            "average_processing_time": avg_time,
            "total_processing_time": self.total_processing_time
        }
    
    async def shutdown(self):
        """Clean shutdown with proper cleanup"""
        logger.info("Shutting down Universal Request Processor")
        await self.asyncio_manager.cleanup()

# Create singleton instance
universal_processor = UniversalRequestProcessor()
