import asyncio
import logging
import subprocess
import os
import json
from llm_clients.qwen_client import QwenClient
from utils.performance_monitor import monitor_performance
from core.error_handler import error_handler
from integrations.vscode_interface import VSCodeInterface

logger = logging.getLogger(__name__)

class AICommandHandler:
    def __init__(self):
        self.supported_commands = ["analyze", "generate", "summarize", "ask", "cmd", "code", "file"]
        self.qwen = QwenClient()
        self.vscode = VSCodeInterface()  # Initialize VSCodeInterface
        logger.info("AI Command Handler initialized with Qwen client and VSCode interface")
    
    @monitor_performance
    async def process_json_command(self, json_input):
        """
        Process a command from JSON input and route to the appropriate handler
        
        Args:
            json_input (str or dict): JSON string or already parsed dict with command data
        
        Returns:
            dict: The result of the operation
        """
        try:
            # Parse JSON if it's a string
            if isinstance(json_input, str):
                try:
                    command_data = json.loads(json_input)
                    logger.info(f"Parsed JSON command: {command_data}")
                except json.JSONDecodeError as e:
                    logger.error(f"Invalid JSON input: {str(e)}")
                    return {"error": f"Invalid JSON input: {str(e)}"}
            else:
                command_data = json_input
            
            # Extract command type
            cmd_type = command_data.get("type", "").upper()
            if not cmd_type:
                logger.error("Missing 'type' field in command")
                return {"error": "Missing 'type' field in command"}
            
            logger.info(f"Processing {cmd_type} command")
            
            # Route to appropriate handler based on type
            if cmd_type == "ASK":
                # For ASK commands, the "command" field contains the query
                query = command_data.get("command", "")
                if not query:
                    return {"error": "Missing 'command' field with query text"}
                
                # Create a properly formatted command for the handler
                ask_command = {
                    "query": query
                }
                return await self.handle_ask_command(ask_command)
                
            elif cmd_type == "CMD":
                # For CMD commands, the "command" field contains the shell command
                shell_cmd = command_data.get("command", "")
                if not shell_cmd:
                    return {"error": "Missing 'command' field with shell command"}
                
                # Create a properly formatted command for the handler
                cmd_command = {
                    "cmd": shell_cmd
                }
                return await self.handle_cmd_command(cmd_command)
                
            elif cmd_type == "CODE":
                # For CODE commands, the "command" field contains action and other parameters
                code_params = command_data.get("command", {})
                if isinstance(code_params, str):
                    # Try to parse as JSON if it's a string
                    try:
                        code_params = json.loads(code_params)
                    except json.JSONDecodeError:
                        # If it's not valid JSON, treat it as a description for code generation
                        code_params = {
                            "action": "generate",
                            "description": code_params
                        }
                
                return await self.handle_code_command(code_params)
                
            elif cmd_type == "FILE":
                # For FILE commands, the "command" field contains action and other parameters
                file_params = command_data.get("command", {})
                if isinstance(file_params, str):
                    # Try to parse as JSON if it's a string
                    try:
                        file_params = json.loads(file_params)
                    except json.JSONDecodeError:
                        # If it's not valid JSON, treat it as a path for file read
                        file_params = {
                            "action": "read",
                            "path": file_params
                        }
                
                return await self.handle_file_command(file_params)
                
            else:
                logger.warning(f"Unsupported command type: {cmd_type}")
                return {"error": f"Unsupported command type: {cmd_type}"}
                
        except Exception as e:
            logger.error(f"Error processing command: {str(e)}")
            error_context = {"component": "ai_handler", "operation": "process_json_command"}
            await error_handler.handle_error(e, error_context)
            return {"error": f"Command processing failed: {str(e)}"}
    
    @monitor_performance
    async def handle_ask_command(self, command: dict):
        """
        Process an ASK command to handle queries
        
        Args:
            command (dict): The command containing a 'query' field with the query text
            
        Returns:
            dict: Response with the query results
        """
        query = command.get("query")
        if not query:
            logger.error("Missing query field in command")
            return {"error": "Missing query field in command"}

        try:
            logger.info(f"Handling ASK command with query: {query}")
            # Use Qwen to process the query
            response = await self.qwen.ask(query)
            return {
                "status": "success",
                "response": response
            }
        except Exception as e:
            logger.error(f"Error handling ASK command: {str(e)}")
            error_context = {"component": "ai_handler", "operation": "ask"}
            await error_handler.handle_error(e, error_context)
            return {"error": str(e)}
    
    @monitor_performance
    async def handle_cmd_command(self, command: dict):
        """
        Process a CMD command to execute shell commands
        
        Args:
            command (dict): The command containing a 'cmd' field with the shell command to execute
            
        Returns:
            dict: Response with the command execution results
        """
        cmd = command.get("cmd")
        if not cmd:
            logger.error("Missing cmd field in command")
            return {"error": "Missing cmd field in command"}

        try:
            logger.info(f"Executing shell command: {cmd}")
            # Execute the command and capture output
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            
            # Return response with stdout, stderr and return code
            return {
                "status": "success",
                "stdout": result.stdout,
                "stderr": result.stderr,
                "return_code": result.returncode
            }
        except Exception as e:
            logger.error(f"Error executing command: {str(e)}")
            error_context = {"component": "ai_handler", "operation": "cmd"}
            await error_handler.handle_error(e, error_context)
            return {"error": str(e)}
    
    @monitor_performance
    async def handle_code_command(self, command: dict):
        """
        Process code generation or execution requests
        
        Args:
            command (dict): The command containing code-related fields
            
        Returns:
            dict: Response with code generation or execution results
        """
        action = command.get("action")
        if not action:
            logger.error("Missing action field in code command")
            return {"error": "Missing action field in code command"}

        try:
            logger.info(f"Processing code {action} request")

            if action == "generate":
                # Generate code using VSCodeInterface
                description = command.get("description")
                if not description:
                    return {"error": "Missing description for code generation"}

                response = await self.vscode.generate_code(description)
                return response

            elif action == "execute":
                # Execute code using VSCodeInterface
                code = command.get("code")
                if not code:
                    return {"error": "Missing code for execution"}

                response = await self.vscode.execute_code(code)
                return response

            else:
                return {"error": f"Unsupported code action: {action}"}

        except Exception as e:
            logger.error(f"Error processing code command: {str(e)}")
            error_context = {"component": "ai_handler", "operation": "code"}
            await error_handler.handle_error(e, error_context)
            return {"error": str(e)}

    @monitor_performance
    async def handle_file_command(self, command: dict):
        """
        Handle file operations like read, write, update, delete
        
        Args:
            command (dict): The command containing file operation details
            
        Returns:
            dict: Response with file operation results
        """
        action = command.get("action")
        if not action:
            logger.error("Missing action field in file command")
            return {"error": "Missing action field in file command"}

        try:
            logger.info(f"Processing file {action} operation")

            if action == "read":
                path = command.get("path")
                if not path:
                    return {"error": "Missing path for file read operation"}

                response = await self.vscode.read_file(path)
                return response

            elif action == "write":
                path = command.get("path")
                content = command.get("content")

                if not path:
                    return {"error": "Missing path for file write operation"}
                if content is None:
                    return {"error": "Missing content for file write operation"}

                response = await self.vscode.create_file(path, content)
                return response

            elif action == "update":
                path = command.get("path")
                content = command.get("content")

                if not path:
                    return {"error": "Missing path for file update operation"}
                if content is None:
                    return {"error": "Missing content for file update operation"}

                response = await self.vscode.update_file(path, content)
                return response

            elif action == "delete":
                path = command.get("path")
                if not path:
                    return {"error": "Missing path for file delete operation"}

                response = await self.vscode.delete_file(path)
                return response

            else:
                return {"error": f"Unsupported file action: {action}"}

        except Exception as e:
            logger.error(f"Error processing file command: {str(e)}")
            error_context = {"component": "ai_handler", "operation": "file"}
            await error_handler.handle_error(e, error_context)
            return {"error": str(e)}
    
    async def _analyze_content(self, content):
        """Analyze the provided content using appropriate AI models"""
        # Placeholder for actual implementation
        await asyncio.sleep(1)  # Simulate processing time
        return {
            "status": "success",
            "result": {
                "analysis": "Content analysis result would go here",
                "sentiment": "neutral",
                "key_points": ["Point 1", "Point 2"]
            }
        }
    
    async def _generate_content(self, prompt):
        """Generate content based on the provided prompt"""
        # Placeholder for actual implementation
        await asyncio.sleep(1)  # Simulate processing time
        return {
            "status": "success",
            "result": {
                "generated_text": f"Generated content based on: {prompt}"
            }
        }
    
    async def _summarize_content(self, content):
        """Summarize the provided content"""
        # Placeholder for actual implementation
        await asyncio.sleep(1)  # Simulate processing time
        return {
            "status": "success",
            "result": {
                "summary": "This is a placeholder summary of the provided content."
            }
        }

# Create a singleton instance
ai_handler = AICommandHandler()