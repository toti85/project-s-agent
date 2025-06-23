"""
API Server for Project-S
------------------------
This module implements a REST API and WebSocket server for Project-S,
providing external interfaces to interact with the system.

Key features:
1. REST API endpoints for system interaction
2. WebSocket support for real-time communication
3. Integration with LangGraph state machine
4. Authentication and authorization mechanisms
5. API versioning and documentation
"""
import asyncio
import logging
import json
import time
import uuid
import jwt
import os
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Union, Set

import uvicorn
from fastapi import FastAPI, HTTPException, Depends, WebSocket, WebSocketDisconnect, status, Request, BackgroundTasks
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.openapi.utils import get_openapi
from pydantic import BaseModel, Field
from pathlib import Path

from core.command_router import router
from core.central_executor import executor
from core.event_bus import event_bus
from core.error_handler import error_handler
from core.memory_system import MemorySystem

# Create memory system instance
memory_system = MemorySystem()
from integrations.decision_router import decision_router
from integrations.advanced_decision_router import advanced_decision_router
from integrations.cognitive_decision_integration import cognitive_decision_integration
# from integrations.langgraph_integration import langgraph_integrator  # TODO: Fix circular import
from integrations.langgraph_state_manager import state_manager

# Configure logging
logger = logging.getLogger(__name__)

# Define Pydantic models for request/response validation
class Command(BaseModel):
    """Base command model for API requests"""
    type: str
    id: Optional[str] = None


class AskCommand(Command):
    """Command for asking questions"""
    type: str = "ASK"
    query: str


class ExecuteCommand(Command):
    """Command for executing shell commands"""
    type: str = "CMD"
    cmd: str


class WorkflowConfig(BaseModel):
    """Configuration for workflow creation"""
    name: str
    type: str
    config: Dict[str, Any] = Field(default_factory=dict)
    initial_context: Dict[str, Any] = Field(default_factory=dict)


class WorkflowStep(BaseModel):
    """Step in a workflow"""
    node_name: str
    data: Dict[str, Any] = Field(default_factory=dict)


class WorkflowDecision(BaseModel):
    """Decision input for workflow"""
    decision_point: str
    selected_option: str
    context: Optional[Dict[str, Any]] = None


class User(BaseModel):
    """User model"""
    username: str
    email: Optional[str] = None
    full_name: Optional[str] = None
    disabled: Optional[bool] = None


class UserInDB(User):
    """User model with hashed password"""
    hashed_password: str


class Token(BaseModel):
    """Token response model"""
    access_token: str
    token_type: str


class TokenData(BaseModel):
    """Token data model"""
    username: Optional[str] = None


# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}
        self.user_connections: Dict[str, Set[str]] = {}  # username -> set of connection_ids
        
    async def connect(self, websocket: WebSocket, connection_id: str, user_id: Optional[str] = None):
        await websocket.accept()
        if connection_id not in self.active_connections:
            self.active_connections[connection_id] = []
        self.active_connections[connection_id].append(websocket)
        
        # Track user connections if authenticated
        if user_id:
            if user_id not in self.user_connections:
                self.user_connections[user_id] = set()
            self.user_connections[user_id].add(connection_id)
            
        logger.info(f"WebSocket connected: {connection_id}, user: {user_id}")
        
    def disconnect(self, websocket: WebSocket, connection_id: str, user_id: Optional[str] = None):
        if connection_id in self.active_connections:
            if websocket in self.active_connections[connection_id]:
                self.active_connections[connection_id].remove(websocket)
            
            # Clean up empty connection lists
            if not self.active_connections[connection_id]:
                del self.active_connections[connection_id]
                
        # Clean up user connections if authenticated
        if user_id and user_id in self.user_connections:
            if connection_id in self.user_connections[user_id]:
                self.user_connections[user_id].remove(connection_id)
            
            # Clean up empty user connections
            if not self.user_connections[user_id]:
                del self.user_connections[user_id]
                
        logger.info(f"WebSocket disconnected: {connection_id}, user: {user_id}")
        
    async def send_message(self, connection_id: str, message: Dict[str, Any]):
        if connection_id in self.active_connections:
            for connection in self.active_connections[connection_id]:
                try:
                    await connection.send_json(message)
                except Exception as e:
                    logger.error(f"Error sending message to {connection_id}: {e}")
                    
    async def broadcast(self, message: Dict[str, Any]):
        """Broadcast message to all connections"""
        for connection_id in self.active_connections:
            await self.send_message(connection_id, message)
            
    async def broadcast_to_user(self, user_id: str, message: Dict[str, Any]):
        """Broadcast message to all connections for a specific user"""
        if user_id in self.user_connections:
            for connection_id in self.user_connections[user_id]:
                await self.send_message(connection_id, message)


# Initialize FastAPI app
app = FastAPI(
    title="Project-S API",
    description="API for Project-S hybrid system",
    version="1.0.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize WebSocket connection manager
connection_manager = ConnectionManager()

# Setup OAuth2 with Password flow for authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Secret key for JWT token generation
# In production, load this from environment or secure configuration
SECRET_KEY = os.environ.get("PROJECT_S_JWT_SECRET", "temporarily_insecure_secret_key_change_in_production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Mock user database - in production, use a real database
fake_users_db = {
    "admin": {
        "username": "admin",
        "full_name": "Admin User",
        "email": "admin@example.com",
        "hashed_password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",  # "secret"
        "disabled": False,
    }
}


def get_user(db, username: str):
    """Get user from database"""
    if username in db:
        user_dict = db[username]
        return UserInDB(**user_dict)
    return None


async def get_current_user(token: str = Depends(oauth2_scheme)):
    """Get current user from JWT token"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except jwt.PyJWTError:
        raise credentials_exception
        
    user = get_user(fake_users_db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(current_user: User = Depends(get_current_user)):
    """Get current active user"""
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create JWT access token"""
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


# Event handlers for WebSocket broadcasts
async def on_command_completed(event_data: Dict[str, Any]):
    """Handle command.completed events"""
    command = event_data.get("command", {})
    result = event_data.get("result", {})
    
    # If the command has a connection_id, send response to that connection
    connection_id = command.get("connection_id")
    if connection_id:
        await connection_manager.send_message(connection_id, {
            "type": "command_completed",
            "command": command,
            "result": result,
            "timestamp": time.time()
        })


async def on_event_for_broadcast(event_data: Dict[str, Any]):
    """Handle events that should be broadcast via WebSocket"""
    # Get graph_id from event data to associate with the right workflow
    graph_id = None
    if isinstance(event_data, dict):
        graph_id = event_data.get("graph_id")
    
    if graph_id:
        # Send workflow updates to the specific workflow's connection
        await connection_manager.send_message(graph_id, {
            "type": "workflow_update",
            "data": event_data,
            "timestamp": time.time()
        })


async def on_system_event(event_data: Dict[str, Any]):
    """Handle system-wide events"""
    # Broadcast to all users (could be filtered by permissions)
    await connection_manager.broadcast({
        "type": "system_event",
        "data": event_data,
        "timestamp": time.time()
    })


@app.on_event("startup")
async def startup_event():
    """Initialize API server at startup"""
    # Register event handlers
    event_bus.subscribe("command.completed", on_command_completed)
    event_bus.subscribe("workflow.node.entered", on_event_for_broadcast)
    event_bus.subscribe("workflow.decision.made", on_event_for_broadcast)
    event_bus.subscribe("system.status_change", on_system_event)
    
    logger.info("API server started and event handlers registered")


@app.on_event("shutdown")
async def shutdown_event():
    """Clean up resources at shutdown"""
    # Unregister event handlers
    event_bus.unsubscribe("command.completed", on_command_completed)
    event_bus.unsubscribe("workflow.node.entered", on_event_for_broadcast)
    event_bus.unsubscribe("workflow.decision.made", on_event_for_broadcast)
    event_bus.unsubscribe("system.status_change", on_system_event)
    
    logger.info("API server shutting down, event handlers unregistered")


# Authentication endpoints
@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    """Authenticate user and provide JWT token"""
    user = get_user(fake_users_db, form_data.username)
    
    # In production, use proper password verification:
    # from passlib.context import CryptContext
    # pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    # if not pwd_context.verify(form_data.password, user.hashed_password):
    #     raise invalid_credentials
    
    # For demo, simply check if user exists and password is "secret"
    if not user or form_data.password != "secret":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username},
        expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


# REST API endpoints
@app.get("/api/v1/system/status")
async def get_system_status(current_user: User = Depends(get_current_active_user)):
    """Get the current system status"""    # Get integrator dynamically to avoid circular import
    try:
        from integrations.langgraph_integration import langgraph_integrator
        active_workflows = len(langgraph_integrator.active_graphs)
    except ImportError:
        active_workflows = 0
    
    return {
        "status": "online",
        "version": "1.0.0",
        "timestamp": time.time(),
        "active_workflows": active_workflows,
        "active_connections": len(connection_manager.active_connections)
    }


@app.post("/api/v1/command")
async def execute_command(
    command: Union[AskCommand, ExecuteCommand],
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_active_user)
):
    """Execute a command in the system"""
    # Generate ID if none provided
    if not command.id:
        command.id = str(uuid.uuid4())
    
    # Convert to dict for router
    command_dict = command.dict()
    
    # Add metadata
    command_dict["timestamp"] = time.time()
    command_dict["user"] = current_user.username
    command_dict["connection_id"] = command.id  # Use command ID as connection ID for response routing
    
    # Execute command in background to not block response
    background_tasks.add_task(executor.execute, command_dict)
    
    return {"status": "accepted", "command_id": command.id}


@app.post("/api/v1/command/sync")
async def execute_command_sync(
    command: Union[AskCommand, ExecuteCommand],
    current_user: User = Depends(get_current_active_user)
):
    """Execute a command synchronously and wait for result"""
    # Generate ID if none provided
    if not command.id:
        command.id = str(uuid.uuid4())
    
    # Convert to dict for router
    command_dict = command.dict()
    
    # Add metadata
    command_dict["timestamp"] = time.time()
    command_dict["user"] = current_user.username
    
    # Execute command synchronously
    result = await executor.execute(command_dict)
    
    return result


@app.post("/api/v1/workflow")
async def create_workflow(
    config: WorkflowConfig,
    current_user: User = Depends(get_current_active_user)
):
    """Create a new workflow"""
    # Generate a unique ID for the workflow
    workflow_id = f"workflow_{uuid.uuid4().hex[:8]}"
    
    # Add user info to context
    initial_context = config.initial_context or {}
    initial_context["created_by"] = current_user.username
    initial_context["created_at"] = time.time()
    
    try:
        # Import integrator dynamically to avoid circular import
        from integrations.langgraph_integration import langgraph_integrator
        
        # Create a workflow using LangGraph integrator
        graph = await langgraph_integrator.create_workflow(
            workflow_type=config.type,
            workflow_name=config.name,
            config=config.config,
            initial_context=initial_context,
            graph_id=workflow_id
        )
        
        return {
            "status": "created",
            "workflow_id": workflow_id,
            "name": config.name,
            "type": config.type
        }
    except Exception as e:
        logger.error(f"Error creating workflow: {e}")
        raise HTTPException(status_code=400, detail=f"Error creating workflow: {str(e)}")


@app.get("/api/v1/workflow/{workflow_id}")
async def get_workflow_status(
    workflow_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """Get the status of a workflow"""
    # Import integrator dynamically to avoid circular import
    from integrations.langgraph_integration import langgraph_integrator
    
    # Check if workflow exists
    if workflow_id not in langgraph_integrator.active_graphs:
        raise HTTPException(status_code=404, detail="Workflow not found")
    
    # Get workflow state
    state = state_manager.active_states.get(workflow_id)
    if not state:
        raise HTTPException(status_code=404, detail="Workflow state not found")
    
    # Check ownership/permissions
    if state["context"].get("created_by") != current_user.username:
        # In a real system, check for admin roles or shared permissions
        if current_user.username != "admin":
            raise HTTPException(status_code=403, detail="Not authorized to access this workflow")
    
    return {
        "workflow_id": workflow_id,
        "status": state.get("status", "unknown"),
        "current_node": state.get("current_node"),
        "error_info": state.get("error_info"),
        "context": {
            k: v for k, v in state.get("context", {}).items()
            if k not in ["full_history", "messages"] and not isinstance(v, (dict, list)) or k == "last_result"
        }
    }


@app.post("/api/v1/workflow/{workflow_id}/step")
async def execute_workflow_step(
    workflow_id: str,
    step: WorkflowStep,
    current_user: User = Depends(get_current_active_user)
):
    """Execute a step in a workflow"""
    # Import integrator dynamically to avoid circular import
    from integrations.langgraph_integration import langgraph_integrator
    
    # Check if workflow exists
    if workflow_id not in langgraph_integrator.active_graphs:
        raise HTTPException(status_code=404, detail="Workflow not found")
    
    try:
        # Execute the step
        result = await langgraph_integrator.execute_node(
            graph_id=workflow_id,
            node_name=step.node_name,
            data=step.data
        )
        
        return {
            "status": "executed",
            "workflow_id": workflow_id,
            "node": step.node_name,
            "result": result
        }
    except Exception as e:
        logger.error(f"Error executing workflow step: {e}")
        raise HTTPException(status_code=400, detail=f"Error executing workflow step: {str(e)}")


@app.post("/api/v1/workflow/{workflow_id}/decision")
async def make_workflow_decision(
    workflow_id: str,
    decision: WorkflowDecision,
    current_user: User = Depends(get_current_active_user)
):
    """Make a decision in a workflow"""
    # Import integrator dynamically to avoid circular import
    from integrations.langgraph_integration import langgraph_integrator
    
    # Check if workflow exists
    if workflow_id not in langgraph_integrator.active_graphs:
        raise HTTPException(status_code=404, detail="Workflow not found")
    
    try:
        # Make the decision
        # In a real implementation, this would call a specific method in the integrator
        await event_bus.publish("workflow.decision.provided", {
            "graph_id": workflow_id,
            "decision_point": decision.decision_point,
            "selected_option": decision.selected_option,
            "context": decision.context,
            "user": current_user.username
        })
        
        return {
            "status": "decision_made",
            "workflow_id": workflow_id,
            "decision_point": decision.decision_point,
            "selected_option": decision.selected_option
        }
    except Exception as e:
        logger.error(f"Error making workflow decision: {e}")
        raise HTTPException(status_code=400, detail=f"Error making workflow decision: {str(e)}")


@app.get("/api/v1/decision/history/{workflow_id}")
async def get_decision_history(
    workflow_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """Get the decision history for a workflow"""
    try:
        # Get decision history from the router
        history = decision_router.get_decision_history(workflow_id)
        
        return {
            "workflow_id": workflow_id,
            "decisions": history
        }
    except Exception as e:
        logger.error(f"Error getting decision history: {e}")
        raise HTTPException(status_code=400, detail=f"Error getting decision history: {str(e)}")


@app.get("/api/v1/decision/analyze/{workflow_id}")
async def analyze_decision_patterns(
    workflow_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """Analyze decision patterns for a workflow"""
    try:
        # Basic analysis
        basic_analysis = decision_router.analyze_decision_patterns(workflow_id)
        
        # Advanced analysis if available
        advanced_analysis = {}
        try:
            advanced_analysis = advanced_decision_router.detect_decision_patterns(workflow_id)
        except:
            pass
        
        return {
            "workflow_id": workflow_id,
            "basic_analysis": basic_analysis,
            "advanced_analysis": advanced_analysis
        }
    except Exception as e:
        logger.error(f"Error analyzing decision patterns: {e}")
        raise HTTPException(status_code=400, detail=f"Error analyzing decision patterns: {str(e)}")


# WebSocket endpoints
@app.websocket("/ws/{connection_id}")
async def websocket_endpoint(websocket: WebSocket, connection_id: str):
    """WebSocket endpoint for real-time communication"""
    await connection_manager.connect(websocket, connection_id)
    
    try:
        while True:
            # Receive and process messages
            data = await websocket.receive_text()
            
            try:
                # Parse JSON message
                message = json.loads(data)
                
                # Process message
                if message.get("type") == "command":
                    # Handle command message
                    command = message.get("command", {})
                    command["connection_id"] = connection_id
                    
                    # Execute command
                    result = await executor.execute(command)
                    
                    # Send result back to client
                    await connection_manager.send_message(connection_id, {
                        "type": "command_result",
                        "command_id": command.get("id"),
                        "result": result,
                        "timestamp": time.time()
                    })
                elif message.get("type") == "ping":
                    # Respond to ping
                    await connection_manager.send_message(connection_id, {
                        "type": "pong",
                        "timestamp": time.time()
                    })
                else:
                    # Unknown message type
                    await connection_manager.send_message(connection_id, {
                        "type": "error",
                        "error": "Unknown message type",
                        "timestamp": time.time()
                    })
            except json.JSONDecodeError:
                # Handle invalid JSON
                await connection_manager.send_message(connection_id, {
                    "type": "error",
                    "error": "Invalid JSON",
                    "timestamp": time.time()
                })
            except Exception as e:
                # Handle other errors
                logger.error(f"Error processing WebSocket message: {e}")
                await connection_manager.send_message(connection_id, {
                    "type": "error",
                    "error": str(e),
                    "timestamp": time.time()
                })
    except WebSocketDisconnect:
        connection_manager.disconnect(websocket, connection_id)


@app.websocket("/ws/auth/{connection_id}")
async def authenticated_websocket_endpoint(
    websocket: WebSocket,
    connection_id: str,
    token: str = None
):
    """Authenticated WebSocket endpoint for real-time communication"""
    # Get the token from the query parameters
    if not token:
        token = websocket.query_params.get("token")
    
    # Validate token
    try:
        if not token:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return
            
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        
        if not username:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return
            
        user = get_user(fake_users_db, username=username)
        if not user or user.disabled:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return
            
        # Connect with user context
        await connection_manager.connect(websocket, connection_id, user_id=username)
        
        try:
            while True:
                # Process messages similar to unauthenticated endpoint but with user context
                data = await websocket.receive_text()
                
                try:
                    message = json.loads(data)
                    
                    # Add user info to the message
                    if isinstance(message, dict):
                        message["user"] = username
                    
                    # Process authenticated message
                    if message.get("type") == "command":
                        command = message.get("command", {})
                        command["connection_id"] = connection_id
                        command["user"] = username
                        
                        # Execute command
                        result = await executor.execute(command)
                        
                        # Send result back
                        await connection_manager.send_message(connection_id, {
                            "type": "command_result",
                            "command_id": command.get("id"),
                            "result": result,
                            "timestamp": time.time()
                        })
                    elif message.get("type") == "subscribe_workflow":
                        # Subscribe to workflow updates
                        workflow_id = message.get("workflow_id")
                        if workflow_id:
                            # In a real implementation, check if user has access to this workflow
                            # For demo, just log the subscription
                            logger.info(f"User {username} subscribed to workflow {workflow_id}")
                    elif message.get("type") == "ping":
                        await connection_manager.send_message(connection_id, {
                            "type": "pong",
                            "timestamp": time.time(),
                            "user": username
                        })
                    else:
                        await connection_manager.send_message(connection_id, {
                            "type": "error",
                            "error": "Unknown message type",
                            "timestamp": time.time()
                        })
                except json.JSONDecodeError:
                    await connection_manager.send_message(connection_id, {
                        "type": "error",
                        "error": "Invalid JSON",
                        "timestamp": time.time()
                    })
                except Exception as e:
                    logger.error(f"Error processing authenticated WebSocket message: {e}")
                    await connection_manager.send_message(connection_id, {
                        "type": "error",
                        "error": str(e),
                        "timestamp": time.time()
                    })
        except WebSocketDisconnect:
            connection_manager.disconnect(websocket, connection_id, user_id=username)
            
    except jwt.PyJWTError:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        logger.warning(f"Invalid token for WebSocket connection: {connection_id}")


# Create singleton instance
api_server = APIServer = type('APIServer', (), {
    'app': app,
    'connection_manager': connection_manager,
    'start': lambda host="127.0.0.1", port=8000: uvicorn.run(app, host=host, port=port),
    'start_async': lambda host="127.0.0.1", port=8000: asyncio.create_task(
        uvicorn.run(app, host=host, port=port)
    )
})()