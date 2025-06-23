"""
Enhanced LangGraph Workflow with Tool Execution
-----------------------------------------------
This is an enhanced version of the Project-S workflow that includes actual tool execution,
not just AI text generation.
"""

import asyncio
import logging
import re
from typing import Dict, Any, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

try:
    from langgraph.graph import StateGraph, END
    LANGGRAPH_AVAILABLE = True
except ImportError:
    logger.warning("LangGraph not available")
    LANGGRAPH_AVAILABLE = False

# State type
State = Dict[str, Any]

class EnhancedWorkflowExecutor:
    """
    Enhanced workflow executor that combines AI reasoning with actual tool execution.
    """
    
    def __init__(self):
        """Initialize the enhanced workflow executor."""
        self.tool_registry = None
        self.model_manager = None
        
        # Import dependencies
        try:
            from tools.tool_registry import tool_registry
            from integrations.model_manager import model_manager
            self.tool_registry = tool_registry
            self.model_manager = model_manager
            logger.info("Enhanced workflow executor initialized with tools and AI")
        except ImportError as e:
            logger.error(f"Failed to import dependencies: {e}")
    
    async def analyze_task_and_plan_tools(self, command: str) -> Dict[str, Any]:
        """
        Use AI to analyze the task and plan which tools to use.
        
        Args:
            command: User command to analyze
            
        Returns:
            Dict containing the analysis and tool plan
        """
        if not self.model_manager:
            return {"error": "Model manager not available"}
        
        # Get AI to analyze the task and suggest tools
        analysis_prompt = f"""
        Analyze this user request and determine what tools need to be executed:
        
        USER REQUEST: {command}
        
        Available tools: {list(self.tool_registry.tools.keys()) if self.tool_registry else []}
        
        Please respond in this exact format:
        TASK_TYPE: [planning/execution/analysis/file_operation/system_command]
        TOOLS_NEEDED: [list of tool names that should be executed]
        EXECUTION_PLAN: [step by step plan]
        REQUIRES_FILES: [true/false - does this need file system access]
        REQUIRES_SYSTEM: [true/false - does this need system commands]
        
        Be specific about which tools to use and in what order.
        """
        
        try:
            analysis_result = await self.model_manager.execute_task_with_model(
                query=analysis_prompt,
                system_message="You are a task analysis expert. Analyze tasks and recommend specific tools for execution.",
                task_type="planning"
            )
            
            return {
                "success": True,
                "analysis": analysis_result.get("content", ""),
                "original_command": command
            }
            
        except Exception as e:
            logger.error(f"Error in task analysis: {e}")
            return {"error": str(e)}
    
    def parse_ai_analysis(self, analysis_text: str) -> Dict[str, Any]:
        """
        Parse the AI analysis response to extract structured information.
        
        Args:
            analysis_text: The AI response text to parse
            
        Returns:
            Dict containing parsed analysis
        """
        parsed = {
            "task_type": "execution",
            "tools_needed": [],
            "execution_plan": "",
            "requires_files": False,
            "requires_system": False
        }
        
        try:
            # Extract task type
            task_type_match = re.search(r'TASK_TYPE:\s*\[?([^\]]+)\]?', analysis_text, re.IGNORECASE)
            if task_type_match:
                parsed["task_type"] = task_type_match.group(1).strip()
            
            # Extract tools needed
            tools_match = re.search(r'TOOLS_NEEDED:\s*\[([^\]]+)\]', analysis_text, re.IGNORECASE)
            if tools_match:
                tools_text = tools_match.group(1)
                # Split by comma and clean up
                tools = [tool.strip().strip("'\"") for tool in tools_text.split(',')]
                parsed["tools_needed"] = [tool for tool in tools if tool]
            
            # Extract execution plan
            plan_match = re.search(r'EXECUTION_PLAN:\s*\[([^\]]+)\]', analysis_text, re.IGNORECASE)
            if plan_match:
                parsed["execution_plan"] = plan_match.group(1).strip()
            
            # Extract file requirements
            files_match = re.search(r'REQUIRES_FILES:\s*\[?([^\]]+)\]?', analysis_text, re.IGNORECASE)
            if files_match:
                parsed["requires_files"] = files_match.group(1).strip().lower() == "true"
            
            # Extract system requirements
            system_match = re.search(r'REQUIRES_SYSTEM:\s*\[?([^\]]+)\]?', analysis_text, re.IGNORECASE)
            if system_match:
                parsed["requires_system"] = system_match.group(1).strip().lower() == "true"
                
        except Exception as e:
            logger.error(f"Error parsing AI analysis: {e}")
        
        return parsed
    
    async def execute_tools_based_on_analysis(self, command: str, parsed_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the actual tools based on the AI analysis.
        
        Args:
            command: Original user command
            parsed_analysis: Parsed analysis from AI
            
        Returns:
            Dict containing execution results
        """
        if not self.tool_registry:
            return {"error": "Tool registry not available"}
        
        execution_results = []
        
        # Get tools to execute
        tools_needed = parsed_analysis.get("tools_needed", [])
        
        if not tools_needed:
            # If AI didn't specify tools, try to infer from command
            tools_needed = self.infer_tools_from_command(command)
        
        logger.info(f"Executing tools: {tools_needed}")
        
        # Execute each tool
        for tool_name in tools_needed:
            try:
                # Clean up tool name
                clean_tool_name = tool_name.lower().strip()
                
                # Map common tool names to actual tool registry names
                tool_mapping = {
                    "file_write": "file_write",
                    "file_read": "file_read", 
                    "file_search": "file_search",
                    "system_command": "system_command",
                    "system_info": "system_info",
                    "web_fetch": "web_page_fetch",
                    "web_search": "web_search"
                }
                
                actual_tool_name = tool_mapping.get(clean_tool_name, clean_tool_name)
                
                if actual_tool_name in self.tool_registry.tools:
                    # Determine parameters based on command and tool
                    params = self.generate_tool_parameters(command, actual_tool_name, parsed_analysis)
                    
                    logger.info(f"Executing {actual_tool_name} with params: {params}")
                    
                    # Execute the tool
                    result = await self.tool_registry.execute_tool(actual_tool_name, **params)
                    
                    execution_results.append({
                        "tool": actual_tool_name,
                        "params": params,
                        "result": result,
                        "success": result.get("success", False)
                    })
                    
                    logger.info(f"Tool {actual_tool_name} executed: {result.get('success', False)}")
                    
                else:
                    execution_results.append({
                        "tool": actual_tool_name,
                        "error": f"Tool {actual_tool_name} not found in registry",
                        "success": False
                    })
                    
            except Exception as e:
                logger.error(f"Error executing tool {tool_name}: {e}")
                execution_results.append({
                    "tool": tool_name,
                    "error": str(e),
                    "success": False
                })
        
        return {
            "execution_results": execution_results,
            "tools_executed": len(execution_results),
            "successful_tools": len([r for r in execution_results if r.get("success", False)])
        }
    
    def infer_tools_from_command(self, command: str) -> List[str]:
        """
        Infer which tools to use based on command keywords.
        
        Args:
            command: User command
            
        Returns:
            List of tool names to execute
        """
        command_lower = command.lower()
        tools_to_use = []
        
        # File operations
        if any(word in command_lower for word in ["create", "write", "save", "file"]):
            tools_to_use.append("file_write")
        
        if any(word in command_lower for word in ["read", "open", "show", "display"]):
            tools_to_use.append("file_read")
        
        if any(word in command_lower for word in ["search", "find", "look for"]):
            tools_to_use.append("file_search")
        
        # System operations
        if any(word in command_lower for word in ["run", "execute", "command", "cmd"]):
            tools_to_use.append("system_command")
        
        if any(word in command_lower for word in ["system", "info", "status"]):
            tools_to_use.append("system_info")
        
        # Web operations
        if any(word in command_lower for word in ["download", "fetch", "web", "url", "http"]):
            tools_to_use.append("web_page_fetch")
        
        return tools_to_use
    
    def generate_tool_parameters(self, command: str, tool_name: str, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate parameters for tool execution based on command and analysis.
        
        Args:
            command: Original user command
            tool_name: Name of tool to execute
            analysis: Parsed AI analysis
            
        Returns:
            Dict of parameters for the tool
        """
        params = {}
        
        if tool_name == "file_write":
            # Extract file path and content from command
            if "create" in command.lower() and "file" in command.lower():
                # Try to extract filename
                import re
                file_match = re.search(r'file\s+(?:called\s+|named\s+)?([^\s]+)', command, re.IGNORECASE)
                if file_match:
                    params["path"] = file_match.group(1)
                else:
                    params["path"] = "output.txt"
                
                # Extract content
                content_match = re.search(r'(?:with\s+)?content\s+[\'"]?([^\'"]+)[\'"]?', command, re.IGNORECASE)
                if content_match:
                    params["content"] = content_match.group(1)
                else:
                    params["content"] = f"Generated by Project-S: {command}"
        
        elif tool_name == "file_read":
            # Extract file path
            import re
            file_match = re.search(r'(?:read|open|show)\s+(?:file\s+)?([^\s]+)', command, re.IGNORECASE)
            if file_match:
                params["path"] = file_match.group(1)
            else:
                params["path"] = "README.md"  # Default file
        
        elif tool_name == "file_search":
            # Extract search pattern
            import re
            search_match = re.search(r'(?:search|find)\s+(?:for\s+)?[\'"]?([^\'"]+)[\'"]?', command, re.IGNORECASE)
            if search_match:
                params["pattern"] = search_match.group(1)
            else:
                params["pattern"] = "*.txt"  # Default pattern
        
        elif tool_name == "system_command":
            # Extract command to run
            import re
            cmd_match = re.search(r'(?:run|execute)\s+[\'"]?([^\'"]+)[\'"]?', command, re.IGNORECASE)
            if cmd_match:
                params["command"] = cmd_match.group(1)
            else:
                params["command"] = "echo Hello from Project-S"
        
        elif tool_name == "system_info":
            params["info_type"] = "all"
        
        elif tool_name == "web_page_fetch":
            # Extract URL
            import re
            url_match = re.search(r'https?://[^\s]+', command)
            if url_match:
                params["url"] = url_match.group(0)
            else:
                params["url"] = "https://httpbin.org/json"  # Default test URL
        
        return params
    
    async def process_command_with_tools(self, command: str) -> Dict[str, Any]:
        """
        Process a command by combining AI analysis with actual tool execution.
        
        Args:
            command: User command to process
            
        Returns:
            Dict containing the complete results
        """
        logger.info(f"Processing command with tools: {command}")
        
        try:
            # Step 1: AI Analysis
            analysis_result = await self.analyze_task_and_plan_tools(command)
            if "error" in analysis_result:
                return analysis_result
            
            # Step 2: Parse AI Analysis
            parsed_analysis = self.parse_ai_analysis(analysis_result["analysis"])
            
            # Step 3: Execute Tools
            execution_result = await self.execute_tools_based_on_analysis(command, parsed_analysis)
            
            # Step 4: Generate Final Response with AI
            final_response = await self.generate_final_response(command, analysis_result, execution_result)
            
            # Combine all results
            return {
                "success": True,
                "command": command,
                "ai_analysis": analysis_result,
                "parsed_analysis": parsed_analysis,
                "tool_execution": execution_result,
                "final_response": final_response,
                "execution_summary": {
                    "tools_planned": len(parsed_analysis.get("tools_needed", [])),
                    "tools_executed": execution_result.get("tools_executed", 0),
                    "successful_executions": execution_result.get("successful_tools", 0)
                }
            }
            
        except Exception as e:
            logger.error(f"Error in enhanced workflow: {e}")
            return {"error": str(e)}
    
    async def generate_final_response(self, command: str, analysis: Dict[str, Any], execution: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a final response by having AI interpret the tool execution results.
        
        Args:
            command: Original command
            analysis: AI analysis results
            execution: Tool execution results
            
        Returns:
            Dict containing final response
        """
        if not self.model_manager:
            return {"content": "Task completed with tool execution results."}
        
        # Prepare summary for AI
        execution_summary = []
        for result in execution.get("execution_results", []):
            tool_name = result.get("tool", "unknown")
            success = result.get("success", False)
            if success:
                execution_summary.append(f"✅ {tool_name}: Success")
            else:
                error = result.get("error", "Unknown error")
                execution_summary.append(f"❌ {tool_name}: {error}")
        
        response_prompt = f"""
        I have completed executing tools for this user request:
        
        ORIGINAL REQUEST: {command}
        
        TOOL EXECUTION RESULTS:
        {chr(10).join(execution_summary)}
        
        EXECUTION DETAILS:
        - Tools planned: {execution.get('tools_executed', 0)}
        - Successful executions: {execution.get('successful_tools', 0)}
        
        Please provide a natural language summary of what was accomplished and any results.
        Be specific about what files were created, commands run, or information gathered.
        """
        
        try:
            response = await self.model_manager.execute_task_with_model(
                query=response_prompt,
                system_message="You are summarizing the results of tool executions. Be clear and helpful.",
                task_type="summary"
            )
            
            return response
            
        except Exception as e:
            logger.error(f"Error generating final response: {e}")
            return {"content": f"Tools executed but error generating summary: {e}"}

# Create global instance
enhanced_workflow_executor = EnhancedWorkflowExecutor()
