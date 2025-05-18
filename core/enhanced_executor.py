import asyncio
import uuid
import time
from enum import Enum
from typing import Dict, Any, Optional, Callable, Awaitable

class CommandPriority(Enum):
    LOW = 0
    NORMAL = 1
    HIGH = 2
    CRITICAL = 3

class CommandStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class Command:
    def __init__(self, 
                 type: str, 
                 content: Dict[str, Any], 
                 priority: CommandPriority = CommandPriority.NORMAL,
                 timeout: Optional[float] = None):
        self.id = str(uuid.uuid4())
        self.type = type
        self.content = content
        self.priority = priority
        self.timeout = timeout
        self.status = CommandStatus.PENDING
        self.created_at = time.time()
        self.started_at = None
        self.completed_at = None
        self.result = None
        self.error = None
        
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "type": self.type,
            "content": self.content,
            "priority": self.priority.name,
            "status": self.status.name,
            "created_at": self.created_at,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
            "result": self.result,
            "error": self.error
        }
        
    def __repr__(self) -> str:
        return f"Command({self.id}, {self.type}, {self.status.name})"

class EnhancedCommandExecutor:
    def __init__(self, max_concurrent: int = 5):
        self.max_concurrent = max_concurrent
        self.handlers: Dict[str, Callable[[Command], Awaitable[Dict[str, Any]]]] = {}
        self.command_queue: asyncio.PriorityQueue = asyncio.PriorityQueue()
        self.active_commands: Dict[str, Command] = {}
        self.command_history: Dict[str, Command] = {}
        self.running = False
        self.semaphore = asyncio.Semaphore(max_concurrent)
        
    def register_handler(self, command_type: str, handler: Callable[[Command], Awaitable[Dict[str, Any]]]):
        self.handlers[command_type] = handler
        
    async def submit(self, command: Command) -> str:
        priority_value = 10 - command.priority.value  # Invert for priority queue
        await self.command_queue.put((priority_value, command))
        self.command_history[command.id] = command
        return command.id
        
    async def start(self):
        self.running = True
        workers = [asyncio.create_task(self._worker()) for _ in range(self.max_concurrent)]
        await asyncio.gather(*workers, return_exceptions=True)
        
    async def stop(self):
        self.running = False
        for command_id, command in self.active_commands.items():
            command.status = CommandStatus.CANCELLED
        while not self.command_queue.empty():
            try:
                await self.command_queue.get()
                self.command_queue.task_done()
            except:
                pass
                
    async def _worker(self):
        while self.running:
            try:
                _, command = await self.command_queue.get()
                if command.status == CommandStatus.CANCELLED:
                    self.command_queue.task_done()
                    continue
                await self._process_command(command)
                self.command_queue.task_done()
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"Error in command worker: {str(e)}")
                
    async def _process_command(self, command: Command):
        command.status = CommandStatus.RUNNING
        command.started_at = time.time()
        self.active_commands[command.id] = command
        try:
            handler = self.handlers.get(command.type)
            if not handler:
                raise ValueError(f"No handler registered for command type: {command.type}")
            if command.timeout:
                result = await asyncio.wait_for(handler(command), timeout=command.timeout)
            else:
                result = await handler(command)
            command.result = result
            command.status = CommandStatus.COMPLETED
        except asyncio.TimeoutError:
            command.error = "Command execution timed out"
            command.status = CommandStatus.FAILED
        except Exception as e:
            command.error = str(e)
            command.status = CommandStatus.FAILED
        finally:
            command.completed_at = time.time()
            if command.id in self.active_commands:
                del self.active_commands[command.id]
                
    async def get_command_status(self, command_id: str) -> Optional[Dict[str, Any]]:
        command = self.command_history.get(command_id)
        if not command:
            return None
        return command.to_dict()
