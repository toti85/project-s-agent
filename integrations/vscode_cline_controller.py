"""
VSCode Cline Controller for Project-S
------------------------------------
This module integrates VSCode Cline with Project-S, enabling the use of 
OpenRouter's Qwen3 model for code generation and other development tasks.
"""

import os
import json
import logging
import subprocess
import asyncio
from typing import Dict, Any, List, Optional, Union

logger = logging.getLogger("VSCode_Cline_Controller")

class VSCodeClineController:
    """VSCode Cline interface control from the Project-S system"""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize the VSCode Cline controller"""
        self.config = config or {}
        self.openrouter_api_key = self._get_api_key()
        self.model = self.config.get("openrouter", {}).get("model", "qwen/qwen-72b")
        self.timeout = self.config.get("commands", {}).get("timeout", 60)
        self.auto_format = self.config.get("commands", {}).get("auto_format", True)
        self.auto_save = self.config.get("commands", {}).get("auto_save", True)
        self.setup_cline_environment()
        logger.info(f"VSCode Cline controller initialized with model: {self.model}")
    
    def _get_api_key(self) -> str:
        """Get OpenRouter API key from environment, config, or docs/openrouter_api_key.py"""
        env_key = os.environ.get("OPENROUTER_API_KEY", "")
        config_key = self.config.get("openrouter", {}).get("api_key", "")
        
        # If config key contains ${ENV_VAR}, replace with environment variable
        if config_key and "${" in config_key:
            env_var = config_key.strip("${}")
            env_var = env_var.strip("}")
            return os.environ.get(env_var, "")
        
        if env_key or config_key:
            return env_key or config_key
        
        # Try to load from docs/openrouter_api_key.py
        try:
            import importlib.util
            import sys
            key_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "docs", "openrouter_api_key.py"))
            spec = importlib.util.spec_from_file_location("openrouter_api_key", key_path)
            module = importlib.util.module_from_spec(spec)
            sys.modules["openrouter_api_key"] = module
            spec.loader.exec_module(module)
            return getattr(module, "OPENROUTER_API_KEY", "")
        except Exception as e:
            logger.warning(f"Could not load OpenRouter API key from docs/openrouter_api_key.py: {e}")
            return ""
    
    def setup_cline_environment(self):
        """Set up Cline environment and OpenRouter integration"""
        try:
            # Create or update Cline config directory
            cline_config_dir = os.path.expanduser("~/.config/vscode-cline")
            os.makedirs(cline_config_dir, exist_ok=True)
            
            # Create/update config.json file
            config_path = os.path.join(cline_config_dir, "config.json")
            
            # Read existing config if it exists
            cline_config = {}
            if os.path.exists(config_path):
                try:
                    with open(config_path, 'r') as f:
                        cline_config = json.load(f)
                except json.JSONDecodeError:
                    logger.warning("Could not parse existing Cline config, creating new one")
            
            # Update config with OpenRouter settings
            cline_config.update({
                "openrouter": {
                    "enabled": True,
                    "api_key": self.openrouter_api_key,
                    "model": self.model,
                    "context_window_size": self.config.get("workflows", {}).get("context_window_size", 12000)
                },
                "auto_format": self.auto_format,
                "auto_save": self.auto_save
            })
            
            # Write updated config
            with open(config_path, 'w') as f:
                json.dump(cline_config, f, indent=2)
                
            logger.info("VSCode Cline environment configured successfully")
            
            # Test if Cline extension is installed
            self._check_cline_installation()
            
        except Exception as e:
            logger.error(f"Error setting up Cline environment: {e}")
            raise
    
    def _check_cline_installation(self):
        """Check if VSCode Cline extension is installed"""
        try:
            # Use PowerShell to check if Cline extension is installed
            cmd = 'powershell -Command "& {code --list-extensions | Select-String -Pattern \'cline\' -Quiet}"'
            result = subprocess.run(cmd, capture_output=True, text=True, shell=True)
            
            if "True" not in result.stdout:
                logger.warning("VSCode Cline extension not detected. Installing...")
                self._install_cline_extension()
            else:
                logger.info("VSCode Cline extension is installed")
        except Exception as e:
            logger.error(f"Error checking Cline installation: {e}")
    
    def _install_cline_extension(self):
        """Install VSCode Cline extension"""
        try:
            logger.info("Installing VSCode Cline extension...")
            cmd = 'powershell -Command "& {code --install-extension cline-ai.cline}"'
            result = subprocess.run(cmd, capture_output=True, text=True, shell=True)
            
            if result.returncode == 0:
                logger.info("VSCode Cline extension installed successfully")
            else:
                logger.error(f"Failed to install Cline extension: {result.stderr}")
        except Exception as e:
            logger.error(f"Error installing Cline extension: {e}")
    
    async def generate_code(self, prompt: str, language: str, 
                           filename: Optional[str] = None, 
                           context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Generate code with Qwen3 model using Cline"""
        try:
            logger.info(f"Generating {language} code with prompt: {prompt[:50]}...")
            
            # Format the command for Cline
            command_args = [
                "code", "--cli", "cline",
                "--generate", 
                "--language", language,
                "--model", self.model
            ]
            
            # Add filename if provided
            if filename:
                command_args.extend(["--filename", filename])
            
            # Create temporary file with prompt
            import tempfile
            with tempfile.NamedTemporaryFile(mode='w+', delete=False, suffix='.txt') as temp:
                temp.write(prompt)
                temp_path = temp.name
            
            command_args.extend(["--prompt-file", temp_path])
            
            # Execute command
            process = await asyncio.create_subprocess_exec(
                *command_args,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            # Clean up temporary file
            try:
                os.unlink(temp_path)
            except:
                pass
                
            if process.returncode != 0:
                error_msg = stderr.decode() if stderr else "Unknown error"
                logger.error(f"Code generation failed: {error_msg}")
                return {
                    "status": "error",
                    "message": f"Code generation failed: {error_msg}"
                }
            
            output = stdout.decode()
            
            # Parse the output to extract the generated code
            code = self._extract_code_from_output(output)
            
            return {
                "status": "success",
                "language": language,
                "code": code,
                "filename": filename
            }
            
        except Exception as e:
            logger.error(f"Error in code generation: {e}")
            return {
                "status": "error",
                "message": f"Code generation error: {str(e)}"
            }
    
    async def refactor_code(self, code: str, instructions: str, 
                           context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Refactor existing code with instructions"""
        try:
            logger.info(f"Refactoring code with instructions: {instructions[:50]}...")
            
            # Create temporary file with code to refactor
            import tempfile
            with tempfile.NamedTemporaryFile(mode='w+', delete=False, suffix='.txt') as temp_code:
                temp_code.write(code)
                code_path = temp_code.name
                
            with tempfile.NamedTemporaryFile(mode='w+', delete=False, suffix='.txt') as temp_instr:
                temp_instr.write(instructions)
                instr_path = temp_instr.name
            
            # Format the command for Cline
            command_args = [
                "code", "--cli", "cline",
                "--refactor", 
                "--file", code_path,
                "--model", self.model,
                "--prompt-file", instr_path
            ]
            
            # Execute command
            process = await asyncio.create_subprocess_exec(
                *command_args,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            # Clean up temporary files
            try:
                os.unlink(code_path)
                os.unlink(instr_path)
            except:
                pass
                
            if process.returncode != 0:
                error_msg = stderr.decode() if stderr else "Unknown error"
                logger.error(f"Code refactoring failed: {error_msg}")
                return {
                    "status": "error",
                    "message": f"Code refactoring failed: {error_msg}"
                }
            
            output = stdout.decode()
            
            # Parse the output to extract the refactored code
            refactored_code = self._extract_code_from_output(output)
            
            return {
                "status": "success",
                "original_code": code,
                "refactored_code": refactored_code
            }
            
        except Exception as e:
            logger.error(f"Error in code refactoring: {e}")
            return {
                "status": "error",
                "message": f"Code refactoring error: {str(e)}"
            }
    
    async def execute_workflow(self, workflow_name: str, 
                              parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute predefined development workflow"""
        try:
            logger.info(f"Executing workflow '{workflow_name}' with parameters: {parameters}")
            
            # Define workflow handlers
            workflows = {
                "create_rest_api": self._workflow_create_rest_api,
                "add_feature": self._workflow_add_feature,
                "test_and_debug": self._workflow_test_and_debug,
                "refactor_module": self._workflow_refactor_module,
                "document_code": self._workflow_document_code
            }
            
            # Check if workflow exists
            if workflow_name not in workflows:
                return {
                    "status": "error",
                    "message": f"Unknown workflow: {workflow_name}"
                }
            
            # Execute the workflow
            return await workflows[workflow_name](parameters)
            
        except Exception as e:
            logger.error(f"Error executing workflow '{workflow_name}': {e}")
            return {
                "status": "error",
                "message": f"Workflow execution error: {str(e)}"
            }
    
    def _extract_code_from_output(self, output: str) -> str:
        """Extract code from Cline output"""
        # Cline typically returns code between ```language and ``` markers
        import re
        pattern = r"```(?:\w+)?\s*([\s\S]*?)```"
        matches = re.findall(pattern, output)
        
        if matches:
            return matches[0].strip()
        
        # If no code blocks found, return the raw output
        return output.strip()
    
    async def _workflow_create_rest_api(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Create a REST API project workflow"""
        try:
            endpoints = parameters.get("endpoints", ["users"])
            database = parameters.get("database", "sqlite")
            auth = parameters.get("auth", False)
            
            # Step 1: Create project structure
            prompt = f"""
            Create a complete REST API project with the following specifications:
            
            - Database: {database}
            - Endpoints: {', '.join(endpoints)}
            - Authentication: {"Yes" if auth else "No"}
            
            Please include:
            1. Project structure with proper separation of concerns
            2. Database models for each endpoint
            3. API routes and handlers
            4. {"Authentication middleware and logic" if auth else ""}
            5. Basic error handling and validation
            6. Requirements file and setup instructions
            """
            
            # Generate main app file
            main_result = await self.generate_code(
                prompt=prompt,
                language="python",
                filename="app.py"
            )
            
            results = [main_result]
            
            # Step 2: Create models for each endpoint
            for endpoint in endpoints:
                model_prompt = f"""
                Create a complete model file for the '{endpoint}' resource in our REST API.
                Use {database} as the database. Include all necessary fields, relationships,
                and utility methods. The model should work with the main app.py file.
                """
                
                model_result = await self.generate_code(
                    prompt=model_prompt,
                    language="python",
                    filename=f"models/{endpoint}.py"
                )
                results.append(model_result)
            
            # Step 3: Create tests
            test_prompt = """
            Create test cases for our REST API endpoints. Include tests for:
            1. Endpoint validation
            2. CRUD operations
            3. Error handling
            """
            
            test_result = await self.generate_code(
                prompt=test_prompt,
                language="python",
                filename="tests/test_api.py"
            )
            results.append(test_result)
            
            return {
                "status": "success",
                "workflow": "create_rest_api",
                "results": results
            }
            
        except Exception as e:
            logger.error(f"Error in create_rest_api workflow: {e}")
            return {
                "status": "error",
                "message": f"Workflow error: {str(e)}"
            }
    
    async def _workflow_add_feature(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Add a new feature to existing code workflow"""
        # Implementation for add_feature workflow
        feature_name = parameters.get("feature", "")
        file_path = parameters.get("file_path", "")
        
        prompt = f"""
        Add the following feature to the existing code: {feature_name}
        Make sure the implementation is consistent with the existing codebase,
        follows the same patterns and coding style, and includes proper error handling.
        """
        
        # TODO: Implement workflow
        return {"status": "not_implemented", "workflow": "add_feature"}
    
    async def _workflow_test_and_debug(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Test and debug workflow"""
        # Implementation for test_and_debug workflow
        # TODO: Implement workflow
        return {"status": "not_implemented", "workflow": "test_and_debug"}
    
    async def _workflow_refactor_module(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Refactor and optimize code module workflow"""
        # Implementation for refactor_module workflow
        # TODO: Implement workflow
        return {"status": "not_implemented", "workflow": "refactor_module"}
    
    async def _workflow_document_code(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Generate code documentation workflow"""
        # Implementation for document_code workflow
        # TODO: Implement workflow
        return {"status": "not_implemented", "workflow": "document_code"}
