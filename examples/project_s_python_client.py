"""
Project-S Python Client
----------------------
Example Python client for interacting with the Project-S API

This client demonstrates:
1. REST API usage (using requests library)
2. Authentication with JWT tokens
3. WebSocket communication (using websockets)
4. Workflow management
5. Decision routing integration
"""

import json
import uuid
import asyncio
import threading
import time
from typing import Dict, Any, List, Optional, Union, Callable, Set
import logging
import requests
import websockets
from urllib.parse import urljoin

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WebSocketClient:
    """Manages WebSocket connections for the Project-S client"""
    
    def __init__(self, url: str, token: str, connection_id: str = None):
        self.url = url
        self.token = token
        self.connection_id = connection_id or str(uuid.uuid4())
        self.websocket = None
        self.callbacks = {
            'message': [],
            'error': [],
            'workflow_update': [],
            'status_change': []
        }
        self.running = False
        self.thread = None
        self.ping_interval = 30  # seconds
    
    def register_callback(self, event_type: str, callback: Callable):
        """Register a callback for specific event types"""
        if event_type in self.callbacks:
            self.callbacks[event_type].append(callback)
            return True
        return False
    
    def remove_callback(self, event_type: str, callback: Callable):
        """Remove a callback for a specific event type"""
        if event_type in self.callbacks and callback in self.callbacks[event_type]:
            self.callbacks[event_type].remove(callback)
            return True
        return False
    
    def _notify_callbacks(self, event_type: str, data: Any):
        """Notify all callbacks for a specific event type"""
        if event_type in self.callbacks:
            for callback in self.callbacks[event_type]:
                try:
                    callback(data)
                except Exception as e:
                    logger.error(f"Error in {event_type} callback: {e}")
    
    async def _connect(self):
        """Connect to the WebSocket server"""
        headers = {"Authorization": f"Bearer {self.token}"}
        ws_url = f"{self.url}/ws/{self.connection_id}"
        
        try:
            self.websocket = await websockets.connect(ws_url, extra_headers=headers)
            logger.info(f"WebSocket connected: {self.connection_id}")
            return True
        except Exception as e:
            logger.error(f"WebSocket connection error: {e}")
            self._notify_callbacks('error', {'error': str(e)})
            return False
    
    async def _listen(self):
        """Listen for messages on the WebSocket"""
        if not self.websocket:
            return
        
        try:
            while self.running:
                try:
                    message = await self.websocket.recv()
                    data = json.loads(message)
                    
                    # Handle specific message types
                    if data.get('type') == 'workflow_update':
                        self._notify_callbacks('workflow_update', data)
                    elif data.get('type') == 'system_event':
                        self._notify_callbacks('status_change', data)
                    
                    # Notify general message callbacks
                    self._notify_callbacks('message', data)
                except websockets.exceptions.ConnectionClosed:
                    logger.warning("WebSocket connection closed")
                    break
                except json.JSONDecodeError:
                    logger.error(f"Invalid JSON received: {message}")
                except Exception as e:
                    logger.error(f"Error processing WebSocket message: {e}")
                    self._notify_callbacks('error', {'error': str(e)})
        finally:
            if self.websocket and not self.websocket.closed:
                await self.websocket.close()
                self.websocket = None
    
    async def _ping_periodically(self):
        """Send periodic pings to keep the connection alive"""
        if not self.websocket:
            return
        
        try:
            while self.running:
                try:
                    if self.websocket and not self.websocket.closed:
                        await self.websocket.send(json.dumps({"type": "ping"}))
                except Exception as e:
                    logger.error(f"Error sending ping: {e}")
                    break
                
                await asyncio.sleep(self.ping_interval)
        except Exception as e:
            logger.error(f"Error in ping loop: {e}")
    
    async def _run_async(self):
        """Run the WebSocket client in the foreground"""
        self.running = True
        connected = await self._connect()
        
        if connected:
            ping_task = asyncio.create_task(self._ping_periodically())
            await self._listen()
            
            if not ping_task.done():
                ping_task.cancel()
                try:
                    await ping_task
                except asyncio.CancelledError:
                    pass
        
        self.running = False
    
    def start(self):
        """Start the WebSocket client in a background thread"""
        if self.thread and self.thread.is_alive():
            logger.warning("WebSocket client is already running")
            return False
        
        def run_in_thread():
            asyncio.run(self._run_async())
        
        self.thread = threading.Thread(target=run_in_thread)
        self.thread.daemon = True
        self.thread.start()
        return True
    
    def stop(self):
        """Stop the WebSocket client"""
        self.running = False
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=2)
        return not (self.thread and self.thread.is_alive())
    
    async def send_message(self, message: Dict[str, Any]):
        """Send a message to the WebSocket server"""
        if not self.websocket or self.websocket.closed:
            connected = await self._connect()
            if not connected:
                return False
        
        try:
            await self.websocket.send(json.dumps(message))
            return True
        except Exception as e:
            logger.error(f"Error sending WebSocket message: {e}")
            self._notify_callbacks('error', {'error': str(e)})
            return False


class ProjectSClient:
    """Project-S API Client"""
    
    def __init__(self, base_url: str = 'http://localhost:8000'):
        """
        Initialize the Project-S client
        
        Args:
            base_url: The base URL of the Project-S API server
        """
        self.base_url = base_url
        self.api_url = f"{base_url}/api/v1"
        self.token = None
        self.websocket_client = None
    
    def _generate_id(self) -> str:
        """Generate a unique ID for requests"""
        return str(uuid.uuid4())
    
    def authenticate(self, username: str, password: str) -> bool:
        """
        Authenticate with the API server
        
        Args:
            username: The username for authentication
            password: The password for authentication
            
        Returns:
            bool: True if authentication succeeded
        """
        try:
            # Prepare form data for token request
            data = {'username': username, 'password': password}
            response = requests.post(f"{self.base_url}/token", data=data)
            
            # Check if authentication was successful
            if response.status_code != 200:
                logger.error(f"Authentication failed: {response.status_code} {response.reason}")
                return False
            
            # Store the token
            token_data = response.json()
            self.token = token_data.get('access_token')
            return bool(self.token)
        
        except Exception as e:
            logger.error(f"Authentication error: {e}")
            return False
    
    def _get_headers(self) -> Dict[str, str]:
        """
        Get the authorization headers for API requests
        
        Returns:
            Dict containing Authorization headers
        """
        if not self.token:
            raise ValueError("Not authenticated. Call authenticate() first")
        
        return {
            'Authorization': f"Bearer {self.token}",
            'Content-Type': 'application/json'
        }
    
    def get_system_status(self) -> Dict[str, Any]:
        """
        Get the current system status
        
        Returns:
            Dict containing system status information
        """
        try:
            response = requests.get(f"{self.api_url}/system/status", headers=self._get_headers())
            
            if response.status_code != 200:
                raise Exception(f"Failed to get system status: {response.status_code} {response.reason}")
            
            return response.json()
        
        except Exception as e:
            logger.error(f"Error getting system status: {e}")
            raise
    
    def ask(self, query: str) -> Dict[str, Any]:
        """
        Ask a question to the AI
        
        Args:
            query: The question to ask
            
        Returns:
            Dict containing AI response
        """
        try:
            command_id = self._generate_id()
            command = {
                'type': 'ASK',
                'id': command_id,
                'query': query
            }
            
            response = requests.post(
                f"{self.api_url}/command/sync",
                headers=self._get_headers(),
                json=command
            )
            
            if response.status_code != 200:
                raise Exception(f"Failed to ask question: {response.status_code} {response.reason}")
            
            return response.json()
        
        except Exception as e:
            logger.error(f"Error asking question: {e}")
            raise
    
    def execute_command(self, command: str) -> Dict[str, Any]:
        """
        Execute a shell command
        
        Args:
            command: The shell command to execute
            
        Returns:
            Dict containing command execution result
        """
        try:
            command_id = self._generate_id()
            command_obj = {
                'type': 'CMD',
                'id': command_id,
                'cmd': command
            }
            
            response = requests.post(
                f"{self.api_url}/command/sync",
                headers=self._get_headers(),
                json=command_obj
            )
            
            if response.status_code != 200:
                raise Exception(f"Failed to execute command: {response.status_code} {response.reason}")
            
            return response.json()
        
        except Exception as e:
            logger.error(f"Error executing command: {e}")
            raise
    
    def create_workflow(self, name: str, workflow_type: str, 
                        config: Dict[str, Any] = None, 
                        initial_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Create a new workflow
        
        Args:
            name: The name of the workflow
            workflow_type: The type of workflow
            config: Configuration options for the workflow
            initial_context: Initial context data for the workflow
            
        Returns:
            Dict containing workflow creation result
        """
        try:
            workflow_config = {
                'name': name,
                'type': workflow_type,
                'config': config or {},
                'initial_context': initial_context or {}
            }
            
            response = requests.post(
                f"{self.api_url}/workflow",
                headers=self._get_headers(),
                json=workflow_config
            )
            
            if response.status_code != 200:
                raise Exception(f"Failed to create workflow: {response.status_code} {response.reason}")
            
            return response.json()
        
        except Exception as e:
            logger.error(f"Error creating workflow: {e}")
            raise
    
    def get_workflow_status(self, workflow_id: str) -> Dict[str, Any]:
        """
        Get status of a workflow
        
        Args:
            workflow_id: The ID of the workflow
            
        Returns:
            Dict containing workflow status
        """
        try:
            response = requests.get(
                f"{self.api_url}/workflow/{workflow_id}",
                headers=self._get_headers()
            )
            
            if response.status_code != 200:
                raise Exception(f"Failed to get workflow status: {response.status_code} {response.reason}")
            
            return response.json()
        
        except Exception as e:
            logger.error(f"Error getting workflow status: {e}")
            raise
    
    def list_workflows(self, status: str = None) -> List[Dict[str, Any]]:
        """
        List all workflows
        
        Args:
            status: Filter workflows by status
            
        Returns:
            List of workflow information dictionaries
        """
        try:
            url = f"{self.api_url}/workflow"
            if status:
                url += f"?status={status}"
                
            response = requests.get(url, headers=self._get_headers())
            
            if response.status_code != 200:
                raise Exception(f"Failed to list workflows: {response.status_code} {response.reason}")
            
            return response.json()
        
        except Exception as e:
            logger.error(f"Error listing workflows: {e}")
            raise
    
    def delete_workflow(self, workflow_id: str) -> Dict[str, Any]:
        """
        Delete a workflow
        
        Args:
            workflow_id: The ID of the workflow
            
        Returns:
            Dict containing deletion result
        """
        try:
            response = requests.delete(
                f"{self.api_url}/workflow/{workflow_id}",
                headers=self._get_headers()
            )
            
            if response.status_code != 200:
                raise Exception(f"Failed to delete workflow: {response.status_code} {response.reason}")
            
            return response.json()
        
        except Exception as e:
            logger.error(f"Error deleting workflow: {e}")
            raise
    
    def execute_workflow_step(self, workflow_id: str, node_name: str, 
                             data: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Execute a step in a workflow
        
        Args:
            workflow_id: The ID of the workflow
            node_name: The name of the node to execute
            data: Additional data for the step
            
        Returns:
            Dict containing step execution result
        """
        try:
            step = {
                'node_name': node_name,
                'data': data or {}
            }
            
            response = requests.post(
                f"{self.api_url}/workflow/{workflow_id}/step",
                headers=self._get_headers(),
                json=step
            )
            
            if response.status_code != 200:
                raise Exception(f"Failed to execute workflow step: {response.status_code} {response.reason}")
            
            return response.json()
        
        except Exception as e:
            logger.error(f"Error executing workflow step: {e}")
            raise
    
    def make_workflow_decision(self, workflow_id: str, decision_point: str, 
                              selected_option: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Make a decision in a workflow
        
        Args:
            workflow_id: The ID of the workflow
            decision_point: The decision point
            selected_option: The selected option
            context: Additional context for the decision
            
        Returns:
            Dict containing decision result
        """
        try:
            decision = {
                'decision_point': decision_point,
                'selected_option': selected_option,
                'context': context or {}
            }
            
            response = requests.post(
                f"{self.api_url}/workflow/{workflow_id}/decision",
                headers=self._get_headers(),
                json=decision
            )
            
            if response.status_code != 200:
                raise Exception(f"Failed to make workflow decision: {response.status_code} {response.reason}")
            
            return response.json()
        
        except Exception as e:
            logger.error(f"Error making workflow decision: {e}")
            raise
    
    def get_decision_history(self, workflow_id: str) -> Dict[str, Any]:
        """
        Get decision history for a workflow
        
        Args:
            workflow_id: The ID of the workflow
            
        Returns:
            Dict containing decision history
        """
        try:
            response = requests.get(
                f"{self.api_url}/decision/history/{workflow_id}",
                headers=self._get_headers()
            )
            
            if response.status_code != 200:
                raise Exception(f"Failed to get decision history: {response.status_code} {response.reason}")
            
            return response.json()
        
        except Exception as e:
            logger.error(f"Error getting decision history: {e}")
            raise
    
    def get_pending_decisions(self, workflow_id: str = None) -> List[Dict[str, Any]]:
        """
        Get pending decisions for a workflow or all workflows
        
        Args:
            workflow_id: The ID of the workflow (optional)
            
        Returns:
            List of pending decisions
        """
        try:
            url = f"{self.api_url}/decision/pending"
            if workflow_id:
                url += f"/{workflow_id}"
                
            response = requests.get(url, headers=self._get_headers())
            
            if response.status_code != 200:
                raise Exception(f"Failed to get pending decisions: {response.status_code} {response.reason}")
            
            return response.json()
        
        except Exception as e:
            logger.error(f"Error getting pending decisions: {e}")
            raise
    
    def connect_websocket(self, message_callback: Callable = None, 
                          error_callback: Callable = None) -> bool:
        """
        Connect to the WebSocket server for real-time updates
        
        Args:
            message_callback: Callback for handling messages
            error_callback: Callback for handling errors
            
        Returns:
            bool: True if connection was successful
        """
        if not self.token:
            raise ValueError("Not authenticated. Call authenticate() first")
        
        # Create WebSocket client if it doesn't exist
        connection_id = self._generate_id()
        ws_url = f"{self.base_url}"
        
        try:
            self.websocket_client = WebSocketClient(ws_url, self.token, connection_id)
            
            # Register callbacks
            if message_callback:
                self.websocket_client.register_callback('message', message_callback)
            
            if error_callback:
                self.websocket_client.register_callback('error', error_callback)
            
            # Start WebSocket client
            return self.websocket_client.start()
        
        except Exception as e:
            logger.error(f"Error connecting to WebSocket: {e}")
            if error_callback:
                error_callback({"error": str(e)})
            return False
    
    def disconnect_websocket(self) -> bool:
        """
        Disconnect from the WebSocket server
        
        Returns:
            bool: True if disconnection was successful
        """
        if self.websocket_client:
            return self.websocket_client.stop()
        return True
    
    def register_callback(self, event_type: str, callback: Callable) -> bool:
        """
        Register a callback for specific WebSocket event types
        
        Args:
            event_type: Type of event ('message', 'error', 'workflow_update', 'status_change')
            callback: Callback function
            
        Returns:
            bool: True if callback was registered successfully
        """
        if not self.websocket_client:
            logger.warning("WebSocket not connected. Call connect_websocket() first")
            return False
        
        return self.websocket_client.register_callback(event_type, callback)
    
    def remove_callback(self, event_type: str, callback: Callable) -> bool:
        """
        Remove a callback for a specific WebSocket event type
        
        Args:
            event_type: Type of event ('message', 'error', 'workflow_update', 'status_change')
            callback: Callback function to remove
            
        Returns:
            bool: True if callback was removed successfully
        """
        if not self.websocket_client:
            logger.warning("WebSocket not connected. Call connect_websocket() first")
            return False
        
        return self.websocket_client.remove_callback(event_type, callback)


# Example usage
if __name__ == "__main__":
    # Create client instance
    client = ProjectSClient("http://localhost:8000")
    
    # Authenticate
    if not client.authenticate("admin", "password123"):
        print("Authentication failed")
        exit(1)
    
    print("Authentication successful")
    
    # Get system status
    try:
        status = client.get_system_status()
        print(f"System status: {status}")
    except Exception as e:
        print(f"Error getting system status: {e}")
    
    # Ask a question
    try:
        response = client.ask("What is Project-S?")
        print(f"AI response: {response}")
    except Exception as e:
        print(f"Error asking question: {e}")
    
    # Execute a shell command
    try:
        result = client.execute_command("echo 'Hello, Project-S!'")
        print(f"Command result: {result}")
    except Exception as e:
        print(f"Error executing command: {e}")
    
    # Create a workflow
    try:
        workflow = client.create_workflow(
            name="Test Workflow",
            workflow_type="decision_tree",
            config={"max_depth": 3},
            initial_context={"user_query": "How can I analyze this data?"}
        )
        workflow_id = workflow.get("id")
        print(f"Created workflow: {workflow}")
        
        # Get workflow status
        status = client.get_workflow_status(workflow_id)
        print(f"Workflow status: {status}")
        
        # Make a decision in the workflow
        decision_result = client.make_workflow_decision(
            workflow_id=workflow_id,
            decision_point="data_source_selection",
            selected_option="csv_file",
            context={"file_path": "/data/example.csv"}
        )
        print(f"Decision result: {decision_result}")
        
        # Get decision history
        history = client.get_decision_history(workflow_id)
        print(f"Decision history: {history}")
        
    except Exception as e:
        print(f"Error in workflow operations: {e}")
    
    # Connect to WebSocket for real-time updates
    def handle_message(message):
        print(f"Received message: {message}")
    
    def handle_error(error):
        print(f"WebSocket error: {error}")
    
    try:
        client.connect_websocket(handle_message, handle_error)
        print("WebSocket connected")
        
        # Sleep to allow for some WebSocket messages
        time.sleep(10)
        
    except Exception as e:
        print(f"Error with WebSocket: {e}")
    finally:
        # Disconnect WebSocket
        client.disconnect_websocket()
        print("WebSocket disconnected")
