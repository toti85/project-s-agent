# LangGraph Integration for Project-S

This document provides comprehensive guidance on using LangGraph with Project-S to create sophisticated multi-step workflows with state management.

## Table of Contents

1. [Introduction](#introduction)
2. [Installation](#installation)
3. [Core Concepts](#core-concepts)
4. [Basic Usage](#basic-usage)
5. [Advanced Features](#advanced-features)
6. [Examples](#examples)
7. [API Reference](#api-reference)

## Introduction

LangGraph is a library for building stateful, multi-actor applications with LLMs, based on a graph structure. Project-S integrates LangGraph to enable complex workflows with state persistence, branching execution paths, and event-driven architecture.

The integration provides:
- StateGraph management for complex workflows
- Event-driven workflow execution
- Command-based interface for creating and controlling workflows
- Error handling and recovery mechanisms

## Installation

To use LangGraph with Project-S, install the required package:

```bash
pip install langgraph -U
```

Or update your requirements.txt:

```
langgraph>=0.4.5
```

## Core Concepts

### StateGraph

LangGraph's `StateGraph` provides a way to manage state transitions in a workflow. In Project-S integration, each workflow is represented by a StateGraph instance.

### Events

Project-S uses an event bus system. The LangGraph integration publishes and subscribes to the following events:

- `workflow.started` - Triggered when a workflow begins execution
- `workflow.completed` - Triggered when a workflow completes all steps
- `workflow.error` - Triggered when a workflow encounters an error
- `workflow.cancelled` - Triggered when a workflow is cancelled

### Commands

The integration adds a new command type `WORKFLOW` to Project-S's command router with operations:

- `create` - Create a new workflow with steps
- `start` - Start workflow execution
- `cancel` - Cancel a running workflow
- `status` - Get the current status of a workflow

## Basic Usage

### Creating a Simple Workflow

```python
import asyncio
from core.command_router import router

async def run_workflow():
    # Define steps for the workflow
    steps = [
        {
            "type": "CMD",
            "cmd": "echo Hello, Project-S with LangGraph!"
        },
        {
            "type": "ASK",
            "query": "Explain what just happened in the workflow"
        }
    ]
    
    # Create and start the workflow
    result = await router.route_command({
        "type": "WORKFLOW",
        "operation": "create",
        "name": "simple_demo",
        "steps": steps,
        "start": True
    })
    
    return result["graph_id"]

# Execute the function
graph_id = asyncio.run(run_workflow())
print(f"Workflow started with ID: {graph_id}")
```

### Monitoring Workflow Status

```python
async def check_status(graph_id):
    status = await router.route_command({
        "type": "WORKFLOW",
        "operation": "status",
        "graph_id": graph_id
    })
    return status

# Get current status
workflow_status = asyncio.run(check_status(graph_id))
print(f"Current status: {workflow_status}")
```

## Advanced Features

### Conditional Workflows

You can create workflows with conditional branching by defining decision points in your workflow:

```python
# Define context with conditional logic
workflow_context = {
    "conditional_steps": {
        "success_path": [{"type": "CMD", "cmd": "echo Success path!"}],
        "error_path": [{"type": "CMD", "cmd": "echo Error path!"}]
    },
    "decision_function": "my_custom_decision_function"
}

# Your custom decision function
async def my_custom_decision_function(state):
    # Logic to determine which path to take
    if state["context"]["last_result"]["status"] == "success":
        state["context"]["workflow_steps"] = state["context"]["conditional_steps"]["success_path"]
    else:
        state["context"]["workflow_steps"] = state["context"]["conditional_steps"]["error_path"]
    return state
```

### Error Handling

Define error handlers in your workflow context:

```python
workflow_context = {
    "error_handler": {
        "type": "ASK",
        "query": "An error occurred in the workflow. Please analyze the error and suggest a solution."
    }
}
```

## Error Monitoring and Recovery

LangGraph integration with Project-S includes a comprehensive error monitoring and recovery system. This helps track, analyze, and recover from errors in your workflows.

### Error Monitor

The `LangGraphErrorMonitor` provides:

- Error tracking and classification
- Retry mechanisms with configurable limits
- Recovery recommendations based on error types
- Detailed error reports and analytics
- Error trend analysis

### Using Error Monitoring

```python
from integrations.langgraph_error_monitor import error_monitor

# Get an error report for a workflow
report = error_monitor.get_error_report(graph_id)

# Get recovery recommendations
recommendation = error_monitor.get_recovery_recommendation(error_type)

# Export error data
error_monitor.export_error_data("error_report.json")

# Command-based access
result = await router.route_command({
    "type": "ERROR_REPORT",
    "operation": "summary",
    "graph_id": "graph_1234"
})
```

### Error Recovery Patterns

Use these patterns in your workflows to handle errors gracefully:

1. **Retry Pattern**:
   ```python
   # Automatically retried up to max_retries times
   integrator.max_retries = 3  # Configure retry limit
   ```

2. **Fallback Pattern**:
   ```python
   # Define an error handler in your workflow
   workflow_context = {
       "error_handler": {
           "type": "ASK",
           "query": "There was an error in the workflow. How should we proceed?"
       }
   }
   ```

3. **Circuit Breaker Pattern**:
   ```python
   # Monitor error rates and stop if too high
   await error_monitor.monitor_workflow_execution(graph_id)
   ```

## State Management

The LangGraph integration includes robust state management capabilities that allow workflows to maintain state across sessions, synchronize with Project-S components, and persist to disk.

### State Model Integration

The integration harmonizes LangGraph's state model with Project-S's conversation and memory systems:

```python
class GraphState(TypedDict):
    # Core LangGraph fields
    messages: List[Dict[str, Any]]
    context: Dict[str, Any]] 
    command_history: List[Dict[str, Any]]
    status: str
    
    # Project-S integration fields
    conversation_id: Optional[str]
    session_data: Optional[Dict[str, Any]]
    memory_references: Optional[List[str]]
    system_state: Optional[Dict[str, Any]]
    persistence_metadata: Optional[Dict[str, Any]]
```
