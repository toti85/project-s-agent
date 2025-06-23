import logging
import json
import os
from typing import Dict, Any, Optional, List, Union
from integrations.vscode_cline_controller import VSCodeClineController

logger = logging.getLogger(__name__)

class VSCodeInterface:
    """
    Interface for communicating with the Qwen3 integration in VS Code (Cline).
    Provides methods for code generation, code execution, and file operations.
    """
    
    def __init__(self):
        """Initialize the VS Code interface."""
        logger.info("VSCode interface initialized")
        self.message_id = 0
        # Initialize the VSCode Cline Controller with default config
        self.cline_controller = VSCodeClineController({})

    async def send_request(self, action: str, content: str, options: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Send a request to the VS Code Qwen3 integration.
        
        Args:
            action: The action to perform ('generate_code', 'execute_code', or 'file_operation')
            content: The content of the request (code specification or code to execute)
            options: Additional options for the request
            
        Returns:
            Dict[str, Any]: The response from the VS Code Qwen3 integration
        """
        if options is None:
            options = {}
            
        self.message_id += 1
        
        logger.info(f"Sending request to VS Code: {json.dumps({'action': action, 'content': content, 'options': options})}")
        # Route to real implementation
        if action == "generate_code":
            language = options.get("language", "python")
            filename = options.get("filename")
            context = options.get("context")
            result = await self.cline_controller.generate_code(content, language=language, filename=filename, context=context)
            return {"status": "success", "id": self.message_id, "result": result}
        elif action == "execute_code":
            # Optionally implement code execution via Cline if needed
            return {"status": "error", "id": self.message_id, "result": "Code execution not implemented in VSCodeInterface."}
        else:
            return {"status": "error", "id": self.message_id, "result": f"Unknown action: {action}"}
    
    async def generate_code(self, specification: str, options: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Generate code using the Qwen3 integration in VS Code.
        
        Args:
            specification: The specification for the code to generate
            options: Additional options for code generation
            
        Returns:
            Dict[str, Any]: The generated code and metadata
        """
        logger.info(f"Generating code with specification: {specification}")
        return await self.send_request("generate_code", specification, options)
    
    async def execute_code(self, code: str, options: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Execute code using the Qwen3 integration in VS Code.
        
        Args:
            code: The code to execute
            options: Additional options for code execution
            
        Returns:
            Dict[str, Any]: The execution results
        """
        logger.info(f"Executing code: {code[:100]}...")
        return await self.send_request("execute_code", code, options)
    
    async def file_operation(self, operation: str, path: str, content: Optional[str] = None, options: Optional[Dict] = None) -> Dict:
        """
        Perform a file operation (create, read, update, delete) on the real filesystem.
        
        Args:
            operation: The operation to perform ('create', 'read', 'update', 'delete')
            path: The file path
            content: The file content (for create/update operations)
            options: Additional options
        
        Returns:
            Dict containing the operation result
        """
        if options is None:
            options = {}
        try:
            if operation == "create":
                dir_name = os.path.dirname(path)
                if dir_name:
                    os.makedirs(dir_name, exist_ok=True)
                with open(path, "w", encoding="utf-8") as f:
                    f.write(content or "")
                logger.info(f"File created: {path}")
                return {"status": "success", "result": f"File created: {path}"}
            elif operation == "read":
                with open(path, "r", encoding="utf-8") as f:
                    file_content = f.read()
                logger.info(f"File read: {path}")
                return {"status": "success", "result": file_content}
            elif operation == "update":
                with open(path, "w", encoding="utf-8") as f:
                    f.write(content or "")
                logger.info(f"File updated: {path}")
                return {"status": "success", "result": f"File updated: {path}"}
            elif operation == "delete":
                os.remove(path)
                logger.info(f"File deleted: {path}")
                return {"status": "success", "result": f"File deleted: {path}"}
            else:
                logger.error(f"Unknown file operation: {operation}")
                return {"status": "error", "error": f"Unknown file operation: {operation}"}
        except Exception as e:
            logger.error(f"File operation failed: {operation} {path} - {e}")
            return {"status": "error", "error": str(e)}
        
    async def create_file(self, path: str, content: str, options: Optional[Dict] = None) -> Dict:
        """
        Create a new file with the given content.
        
        Args:
            path: The file path to create
            content: The content to write to the file
            options: Additional options for the file operation
            
        Returns:
            Dict containing the operation result
        """
        return await self.file_operation("create", path, content, options)

    async def read_file(self, path: str, options: Optional[Dict] = None) -> Dict:
        """
        Read the content of a file.
        
        Args:
            path: The file path to read
            options: Additional options for the file operation
            
        Returns:
            Dict containing the file content and operation result
        """
        return await self.file_operation("read", path, None, options)

    async def update_file(self, path: str, content: str, options: Optional[Dict] = None) -> Dict:
        """
        Update an existing file with new content.
        
        Args:
            path: The file path to update
            content: The new content for the file
            options: Additional options for the file operation
            
        Returns:
            Dict containing the operation result
        """
        return await self.file_operation("update", path, content, options)

    async def delete_file(self, path: str, options: Optional[Dict] = None) -> Dict:
        """
        Delete a file.
        
        Args:
            path: The file path to delete
            options: Additional options for the file operation
            
        Returns:
            Dict containing the operation result
        """
        return await self.file_operation("delete", path, None, options)
        
    def _handle_response(self, response: Dict) -> Dict:
        """Handle the response from VS Code and format it appropriately."""
        if "error" in response:
            logger.error(f"VS Code operation failed: {response['error']}")
            return {"status": "error", "message": response["error"]}
        
        return {"status": "success", "result": response.get("result", {})}

# Create singleton instance for easy import
vscode_interface = VSCodeInterface()