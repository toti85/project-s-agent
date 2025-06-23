"""
Hybrid AI-Powered Workflow System for Project-S
==============================================
Combines proven template workflows with multi-AI intelligence for ultimate automation capability.

Architecture:
1. Template Engine: Fast, reliable workflows for known patterns
2. Multi-AI Engine: Intelligent workflow generation for new scenarios  
3. Learning System: Convert successful AI workflows to templates
4. Hybrid Router: Intelligently chooses between template and AI approaches
"""

import asyncio
import logging
import json
import time
from typing import Dict, Any, List, Optional, Union, Tuple
from datetime import datetime
from pathlib import Path
import os
import hashlib

# Import proven foundation components
from tools.system_tools import SystemCommandTool, CommandValidator
from tools.file_tools import FileWriteTool, FileReadTool

# Simple FileManager wrapper for compatibility
class FileManager:
    """Simple wrapper around file tools for compatibility"""
    
    def __init__(self):
        self.write_tool = FileWriteTool()
        self.read_tool = FileReadTool()
    
    async def create_file(self, file_path: str, content: str) -> Dict[str, Any]:
        """Create a file with given content"""
        return await self.write_tool.execute(path=file_path, content=content)
from tools.tool_registry import tool_registry

logger = logging.getLogger(__name__)

class MultiAICoordinator:
    """
    Coordinates multiple AI models for intelligent workflow generation
    """
    
    def __init__(self):
        """Initialize the multi-AI coordination system"""
        self.available_models = {
            "gpt4_planner": {
                "role": "Strategic Planning",
                "specialization": "High-level workflow design and task decomposition",
                "model": "gpt-4",
                "priority": 1
            },
            "claude_executor": {
                "role": "Detailed Execution",
                "specialization": "Step-by-step implementation and error handling",
                "model": "claude-3-opus",
                "priority": 2
            },
            "qwen_coordinator": {
                "role": "Technical Coordination", 
                "specialization": "System integration and command optimization",
                "model": "qwen-max",
                "priority": 3
            }
        }
        
    async def generate_workflow_strategy(self, user_request: str) -> Dict[str, Any]:
        """
        Use GPT-4 for strategic workflow planning
        """
        try:
            strategy_prompt = f"""
            ROLE: Expert System Automation Strategist
            TASK: Analyze user request and create high-level workflow strategy
            
            USER REQUEST: "{user_request}"
            
            ANALYSIS FRAMEWORK:
            1. Intent Classification - What is the user trying to achieve?
            2. Task Decomposition - Break into logical steps
            3. Resource Requirements - What tools/systems needed?
            4. Risk Assessment - Potential issues or conflicts
            5. Success Criteria - How to measure completion
            
            OUTPUT FORMAT:
            {{
                "intent": "clear description of user goal",
                "complexity": "simple|moderate|complex",
                "task_type": "file_operation|system_management|development|analysis|other",
                "estimated_steps": "number",
                "required_tools": ["tool1", "tool2"],
                "potential_risks": ["risk1", "risk2"],
                "success_criteria": ["criteria1", "criteria2"],
                "workflow_outline": ["step1", "step2", "step3"]
            }}
            
            Respond ONLY with valid JSON.
            """
            
            # For now, simulate GPT-4 response with intelligent analysis
            # TODO: Replace with actual GPT-4 API call
            strategy = await self._simulate_gpt4_planning(user_request)
            
            logger.info(f"🧠 GPT-4 Strategy generated for: {user_request}")
            return strategy
            
        except Exception as e:
            logger.error(f"Strategy generation failed: {e}")
            return self._fallback_strategy(user_request)
    
    async def generate_detailed_steps(self, strategy: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Use Claude for detailed step generation
        """
        try:
            steps_prompt = f"""
            ROLE: Expert System Implementation Specialist
            TASK: Convert high-level strategy into detailed executable steps
            
            STRATEGY: {json.dumps(strategy, indent=2)}
            
            STEP GENERATION GUIDELINES:
            1. Each step must be atomic and executable
            2. Include specific commands where possible
            3. Add error handling and validation
            4. Consider platform differences (Windows/Linux)
            5. Include progress indicators
            
            OUTPUT FORMAT:
            [
                {{
                    "step_id": 1,
                    "action": "specific action to perform",  
                    "command": "exact command if applicable",
                    "tool": "tool_name_to_use",
                    "parameters": {{"param1": "value1"}},
                    "validation": "how to verify success",
                    "error_handling": "what to do if fails",
                    "estimated_time": "seconds"
                }}
            ]
            
            Respond ONLY with valid JSON array.
            """
            
            # For now, simulate Claude response with detailed step generation
            # TODO: Replace with actual Claude API call
            steps = await self._simulate_claude_execution(strategy)
            
            logger.info(f"🔧 Claude generated {len(steps)} detailed steps")
            return steps
            
        except Exception as e:
            logger.error(f"Step generation failed: {e}")
            return self._fallback_steps(strategy)
    
    async def optimize_workflow(self, workflow: Dict[str, Any]) -> Dict[str, Any]:
        """
        Use Qwen for technical optimization and system integration
        """
        try:
            optimization_prompt = f"""
            ROLE: System Integration and Optimization Expert
            TASK: Optimize workflow for current system and improve efficiency
            
            WORKFLOW: {json.dumps(workflow, indent=2)}
            SYSTEM: Windows
            
            OPTIMIZATION AREAS:
            1. Command translation (Linux → Windows)
            2. Performance optimization  
            3. Resource usage minimization
            4. Error prevention
            5. Parallel execution opportunities
            
            OUTPUT FORMAT:
            {{
                "optimized_steps": [...],
                "performance_improvements": ["improvement1", "improvement2"],
                "platform_adaptations": ["adaptation1", "adaptation2"],
                "parallel_groups": [[step1, step2], [step3, step4]],
                "estimated_total_time": "seconds"
            }}
            
            Respond ONLY with valid JSON.
            """
            
            # For now, simulate Qwen response with technical optimization
            # TODO: Replace with actual Qwen API call
            optimized = await self._simulate_qwen_optimization(workflow)
            
            logger.info(f"⚡ Qwen optimized workflow with {len(optimized.get('performance_improvements', []))} improvements")
            return optimized
            
        except Exception as e:
            logger.error(f"Workflow optimization failed: {e}")
            return {"optimized_steps": workflow.get("steps", []), "performance_improvements": []}
    
    # Simulation methods (to be replaced with actual AI calls)
    async def _simulate_gpt4_planning(self, request: str) -> Dict[str, Any]:
        """Simulate GPT-4 strategic planning"""
        await asyncio.sleep(0.1)  # Simulate API delay
        
        # Intelligent analysis based on request keywords
        request_lower = request.lower()
        
        if any(word in request_lower for word in ["file", "create", "write", "save", "document"]):
            return {
                "intent": "Create or manipulate files",
                "complexity": "simple",
                "task_type": "file_operation",
                "estimated_steps": 3,
                "required_tools": ["file_manager", "system_command"],
                "potential_risks": ["file_overwrite", "permission_denied"],
                "success_criteria": ["file_created", "content_verified"],
                "workflow_outline": ["analyze_request", "create_file", "verify_result"]
            }
        elif any(word in request_lower for word in ["system", "optimize", "clean", "performance"]):
            return {
                "intent": "Optimize system performance",
                "complexity": "moderate", 
                "task_type": "system_management",
                "estimated_steps": 5,
                "required_tools": ["system_command", "file_manager", "process_monitor"],
                "potential_risks": ["system_disruption", "data_loss"],
                "success_criteria": ["performance_improved", "cleanup_completed"],
                "workflow_outline": ["system_analysis", "cleanup_temp", "optimize_registry", "verify_improvements"]
            }
        else:
            return {
                "intent": "General task automation",
                "complexity": "moderate",                "task_type": "other",
                "estimated_steps": 4,
                "required_tools": ["system_command", "file_manager"],
                "potential_risks": ["unexpected_behavior"],
                "success_criteria": ["task_completed"],
                "workflow_outline": ["analyze_request", "plan_execution", "execute_steps", "verify_completion"]
            }

    async def _simulate_claude_execution(self, strategy: Dict[str, Any]) -> List[Dict[str, Any]]:
        """🔧 SURGICAL FIX: Generate REAL executable steps instead of simulation"""
        await asyncio.sleep(0.1)  # Simulate API delay
        
        task_type = strategy.get("task_type", "other")
        user_request = strategy.get("user_request", "")
        
        # 🚀 REAL COMMAND GENERATION based on user request analysis
        if "folder" in user_request or "directory" in user_request or "mkdir" in user_request:
            # Extract folder name from request
            folder_name = self._extract_folder_name(user_request)
            return [
                {
                    "step_id": 1,
                    "action": f"Create directory {folder_name}",
                    "command": f"mkdir {folder_name}",
                    "tool": "system_command",
                    "parameters": {"command": f"mkdir {folder_name}"},
                    "validation": "directory_exists",
                    "error_handling": "retry_with_force",
                    "estimated_time": "5"
                }
            ]
        
        elif "copy" in user_request or "cp" in user_request:
            # Extract source and destination from request
            source, dest = self._extract_copy_params(user_request)
            return [
                {
                    "step_id": 1,
                    "action": f"Copy {source} to {dest}",
                    "command": f"copy {source} {dest}",
                    "tool": "system_command", 
                    "parameters": {"command": f"copy {source} {dest}"},
                    "validation": "file_exists_in_destination",
                    "error_handling": "retry_with_force",
                    "estimated_time": "10"
                }
            ]
        
        elif "list" in user_request or "dir" in user_request or "ls" in user_request:
            return [
                {
                    "step_id": 1,
                    "action": "List directory contents",
                    "command": "dir",
                    "tool": "system_command",
                    "parameters": {"command": "dir"},
                    "validation": "output_received",
                    "error_handling": "try_alternative_command",
                    "estimated_time": "3"
                }
            ]
        
        elif task_type == "file_operation":
            return [
                {
                    "step_id": 1,
                    "action": "Parse user request for file details",
                    "command": None,
                    "tool": "request_parser",
                    "parameters": {"request": "user_input"},
                    "validation": "file_path_extracted",
                    "error_handling": "request_clarification",
                    "estimated_time": "1"
                },
                {
                    "step_id": 2,
                    "action": "Create file with specified content",
                    "command": "create_file",
                    "tool": "file_manager",
                    "parameters": {"path": "extracted_path", "content": "extracted_content"},
                    "validation": "file_exists",
                    "error_handling": "retry_with_backup_location",
                    "estimated_time": "2"
                },
                {
                    "step_id": 3,
                    "action": "Verify file creation and content", 
                    "command": "verify_file",
                    "tool": "file_manager",
                    "parameters": {"path": "created_file_path"},
                    "validation": "content_matches",
                    "error_handling": "report_verification_failure",
                    "estimated_time": "1"
                }
            ]
        
        else:
            # 🔧 GENERIC SYSTEM COMMAND GENERATION
            command = self._generate_system_command_from_request(user_request)
            return [
                {
                    "step_id": 1,
                    "action": f"Execute: {user_request}",
                    "command": command,
                    "tool": "system_command",
                    "parameters": {"command": command},                    "validation": "command_completed",
                    "error_handling": "log_error_and_continue",
                    "estimated_time": "10"
                }
            ]
    
    def _extract_folder_name(self, user_request: str) -> str:
        """🔧 Extract folder name from user request"""
        import re
        # Look for patterns like "create folder named X" or "mkdir X"
        patterns = [
            r"folder named (\w+)",
            r"directory named (\w+)", 
            r"mkdir (\w+)",
            r"create (\w+) folder",
            r"make directory (\w+)"
        ]
        
        for pattern in patterns:
            match = re.search(pattern, user_request, re.IGNORECASE)
            if match:
                return match.group(1)
        
        # Default fallback
        return "new_folder"
    
    def _extract_copy_params(self, user_request: str) -> tuple:
        """🔧 Extract source and destination from copy request"""
        import re
        # Look for patterns like "copy X to Y"
        copy_pattern = r"copy (\S+) to (\S+)"
        match = re.search(copy_pattern, user_request, re.IGNORECASE)
        
        if match:
            return match.group(1), match.group(2)
        
        # Default fallback
        return "source_file", "destination"
    
    def _generate_system_command_from_request(self, user_request: str) -> str:
        """Generate actual system command from natural language request, cross-platform."""
        import platform
        request_lower = user_request.lower()
        is_windows = platform.system().lower() == "windows"

        # Directory listing
        if any(cmd in request_lower for cmd in ["list", "show", "ls", "dir"]):
            return "dir" if is_windows else "ls"
        # Folder creation
        if any(cmd in request_lower for cmd in ["mkdir", "create folder", "create directory"]):
            folder = self._extract_folder_name(user_request)
            return f"mkdir {folder}"
        # File copy
        if any(cmd in request_lower for cmd in ["copy", "cp"]):
            src, dst = self._extract_copy_params(user_request)
            return f"copy {src} {dst}" if is_windows else f"cp {src} {dst}"
        # File move
        if any(cmd in request_lower for cmd in ["move", "mv"]):
            src, dst = self._extract_copy_params(user_request)
            return f"move {src} {dst}" if is_windows else f"mv {src} {dst}"
        # File delete
        if any(cmd in request_lower for cmd in ["delete", "remove", "rm"]):
            file = self._extract_folder_name(user_request)
            return f"del {file}" if is_windows else f"rm {file}"
        # Fallback
        return "auto_detect"

    async def _execute_ai_generic_step(self, step: Dict[str, Any]) -> Dict[str, Any]:
        """Execute REAL commands instead of simulation."""
        try:
            action = step.get("action", "unknown")
            command = step.get("command")
            tool = step.get("tool", "system_command")            # Real execution for system commands
            if tool == "system_command" and command:
                from tools.system_tools import CommandValidator
                import os
                translated_command = CommandValidator.translate_command(command)
                system_tool = SystemCommandTool()
                result = await system_tool.execute(
                    command=translated_command,
                    timeout=int(step.get("estimated_time", "30")),
                    workdir=os.getcwd()  # Use current directory instead of temp
                )
                return {
                    "success": result.get("success", False),
                    "action": action,
                    "command": translated_command,
                    "stdout": result.get("stdout", ""),
                    "stderr": result.get("stderr", ""),                    "exit_code": result.get("exit_code", -1),
                    "message": f"Command '{translated_command}' executed"
                }
            elif tool == "file_manager":
                return await self._execute_ai_file_operation(step)
            elif command == "auto_detect":
                # For auto_detect commands, try to determine the right action
                if "folder" in action or "directory" in action:
                    folder_name = self._extract_folder_name(action)
                    from tools.system_tools import CommandValidator
                    translated_command = CommandValidator.translate_command(f"mkdir {folder_name}")
                    system_tool = SystemCommandTool()
                    result = await system_tool.execute(translated_command, workdir=os.getcwd())
                    return {
                        "success": result.get("success", False),
                        "action": action,
                        "command": translated_command,
                        "message": f"Created directory: {folder_name}"
                    }
                else:
                    from tools.system_tools import CommandValidator
                    translated_command = CommandValidator.translate_command("dir")
                    system_tool = SystemCommandTool()
                    result = await system_tool.execute(translated_command, workdir=os.getcwd())
                    return {
                        "success": result.get("success", False),
                        "action": action,
                        "command": translated_command,                        "stdout": result.get("stdout", ""),
                        "message": "Listed directory contents"
                    }
            else:
                if command:
                    from tools.system_tools import CommandValidator
                    translated_command = CommandValidator.translate_command(command)
                    system_tool = SystemCommandTool()
                    result = await system_tool.execute(translated_command, workdir=os.getcwd())
                    return {
                        "success": result.get("success", False),
                        "action": action,
                        "command": translated_command,
                        "stdout": result.get("stdout", ""),
                        "stderr": result.get("stderr", ""),
                        "exit_code": result.get("exit_code", -1),
                        "message": f"Command '{translated_command}' executed"
                    }
                return {"success": False, "action": action, "error": "No command to execute"}
        except Exception as e:
            return {
                "success": False,
                "action": action,
                "error": str(e)
            }
    
    def _fallback_strategy(self, user_request: str) -> Dict[str, Any]:
        """Fallback strategy when GPT-4 planning fails"""
        return {
            "intent": "Emergency fallback processing",
            "complexity": "simple",
            "task_type": "other",
            "estimated_steps": 1,
            "required_tools": ["system_command"],
            "potential_risks": ["limited_analysis"],
            "success_criteria": ["basic_execution"],
            "workflow_outline": ["execute_basic_command"]
        }
    
    def _fallback_steps(self, strategy: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Fallback steps when Claude execution fails"""
        return [
            {
                "step_id": 1,
                "action": "Execute basic command",
                "command": "dir",
                "tool": "system_command",
                "parameters": {"command": "dir"},
                "validation": "output_received",
                "error_handling": "log_error",
                "estimated_time": "5"
            }
        ]
    
    async def _simulate_qwen_optimization(self, workflow: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate Qwen optimization"""
        await asyncio.sleep(0.1)  # Simulate API delay
        return {
            "optimized_steps": workflow.get("steps", []),
            "performance_improvements": ["cross_platform_commands", "error_handling"],
            "platform_adaptations": ["windows_cmd_translation"],
            "parallel_groups": [],
            "estimated_total_time": "30"
        }
    
    async def _execute_ai_file_operation(self, step: Dict[str, Any]) -> Dict[str, Any]:
        """Execute file operations"""
        try:
            action = step.get("action", "unknown")
            parameters = step.get("parameters", {})
            
            if "create_file" in step.get("command", ""):
                file_manager = FileManager()
                result = await file_manager.create_file(
                    parameters.get("path", "test_file.txt"),
                    parameters.get("content", "Test content")
                )
                return {
                    "success": result.get("success", False),
                    "action": action,
                    "message": f"File operation completed"
                }
            else:
                return {
                    "success": False,
                    "action": action,
                    "error": "Unsupported file operation"
                }
        except Exception as e:
            return {
                "success": False,
                "action": step.get("action", "unknown"),
                "error": str(e)
            }

    # ...existing code...
    
    def get_system_stats(self) -> Dict[str, Any]:
        """Get system performance statistics"""
        total = self.stats["total_executions"]
        if total == 0:
            return self.stats
        
        return {
            **self.stats,
            "template_percentage": (self.stats["template_executions"] / total) * 100,
            "ai_percentage": (self.stats["ai_executions"] / total) * 100,
            "learned_percentage": (self.stats["learned_executions"] / total) * 100,
            "efficiency_score": (self.stats["template_executions"] + self.stats["learned_executions"]) / total * 100
        }


# Global instance for easy access - COMMENTED OUT to avoid import errors
# hybrid_workflow_system = HybridWorkflowSystem()  # Will be created after class definition

async def process_hybrid_workflow(user_input: str, **kwargs) -> Dict[str, Any]:
    """
    Main entry point for hybrid workflow processing
    
    Args:
        user_input: The user's request
        **kwargs: Additional parameters
        
    Returns:
        Dict[str, Any]: Processing result
    """
    # Create instance dynamically to avoid import errors
    hybrid_system = HybridWorkflowSystem()
    return await hybrid_system.process_user_request(user_input, **kwargs)

class HybridWorkflowSystem:
    """
    Orchestrator for the Hybrid Workflow System. Wraps MultiAICoordinator and exposes the required interface.
    """
    def __init__(self):
        self.ai_coordinator = MultiAICoordinator()
        self.stats = {
            "total_executions": 0,
            "template_executions": 0,
            "ai_executions": 0,
            "learned_executions": 0
        }

    async def process_user_request(self, user_input: str, **kwargs) -> dict:
        start_time = time.time()
        self.stats["total_executions"] += 1
        # For this minimal version, always use AI path
        try:
            # Step 1: Generate high-level strategy
            strategy = await self.ai_coordinator.generate_workflow_strategy(user_input)
            strategy["user_request"] = user_input  # Pass user request for downstream extraction
            # Step 2: Generate detailed steps
            steps = await self.ai_coordinator.generate_detailed_steps(strategy)
            # Step 3: Optionally optimize (skipped for now)
            # Step 4: Execute steps
            results = []
            all_success = True
            for step in steps:
                result = await self.ai_coordinator._execute_ai_generic_step(step)
                results.append(result)
                if not result.get("success", False):
                    all_success = False
            self.stats["ai_executions"] += 1
            return {
                "success": all_success,
                "steps": results,
                "processing_strategy": "ai",
                "total_processing_time": time.time() - start_time
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "processing_strategy": "ai",
                "total_processing_time": time.time() - start_time
            }

    def get_system_stats(self):
        total = self.stats["total_executions"]
        if total == 0:
            return self.stats
        return {
            **self.stats,
            "template_percentage": (self.stats["template_executions"] / total) * 100,
            "ai_percentage": (self.stats["ai_executions"] / total) * 100,
            "learned_percentage": (self.stats["learned_executions"] / total) * 100,
            "efficiency_score": (self.stats["template_executions"] + self.stats["learned_executions"]) / total * 100
        }

if __name__ == "__main__":
    # Create global instance for testing
    hybrid_workflow_system = HybridWorkflowSystem()
    
    # Test the hybrid workflow system
    async def test_hybrid_system():
        print("🚀 Testing Hybrid AI-Powered Workflow System")
        print("=" * 60)
        
        test_requests = [
            "optimize my system",  # Should use template
            "create a file called test-report.txt",  # Should use template  
            "analyze the website https://example.com",  # Should use template
            "setup a React development environment with Docker and TypeScript",  # Should use AI
            "create a comprehensive security audit report for my Windows system"  # Should use AI
        ]
        
        for i, request in enumerate(test_requests, 1):
            print(f"\n🧪 Test {i}: {request}")
            print("-" * 40)
            
            try:
                result = await process_hybrid_workflow(request)
                
                strategy = result.get("processing_strategy", "unknown")
                success = result.get("success", False)
                time_taken = result.get("total_processing_time", 0)
                
                status = "✅ SUCCESS" if success else "❌ FAILED"
                print(f"{status} | Strategy: {strategy} | Time: {time_taken:.2f}s")
                
                if not success:
                    print(f"Error: {result.get('error', 'Unknown error')}")
                    
            except Exception as e:
                print(f"❌ EXCEPTION: {str(e)}")
        
        # Show system statistics
        print(f"\n📊 SYSTEM STATISTICS:")
        print("=" * 30)
        stats = hybrid_workflow_system.get_system_stats()
        for key, value in stats.items():
            if isinstance(value, float):
                print(f"{key}: {value:.2f}")
            else:
                print(f"{key}: {value}")
    
    # Run test
    asyncio.run(test_hybrid_system())
