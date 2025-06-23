# Enhanced Cognitive Core with LangGraph Integration

This document describes the enhanced cognitive core component of Project-S that uses LangGraph for graph-based workflow processing.

## Overview

The enhanced cognitive core replaces the previous linear task processing model with a graph-based workflow system powered by LangGraph. This enables more sophisticated processing patterns, better error handling, and specialized AI models for different cognitive tasks.

## Key Features

### 1. Graph-based Workflow Architecture

The cognitive processing is now modeled as a directed graph with specialized nodes for:

- **Planning**: Breaking down complex tasks into executable steps
- **Execution**: Running individual task steps
- **Analysis**: Processing and extracting information from results
- **Reflection**: Suggesting next actions based on context
- **Memory Management**: Consolidating information into the agent's memory
- **Error Handling**: Gracefully managing failures

### 2. Multi-layered LLM Integration

The cognitive core can now use different specialized models for different types of cognitive tasks:

- **Planning models**: Optimized for breaking down complex tasks into steps
- **Reasoning models**: Specialized for analytical tasks and deep thinking
- **Coding models**: Focused on code generation, analysis, and understanding
- **Creative models**: Best for content generation and creative tasks
- **Fast models**: For quick responses and simple tasks

Configuration for these models is stored in `config/multi_model_config.json`.

### 3. Enhanced Memory System

The memory system has been improved to:

- Store conversation history with better structure
- Extract and retain entities from interactions
- Maintain workspace context across sessions
- Provide more relevant context for ongoing tasks

### 4. State Management

The core's state is now managed using Pydantic models to ensure type safety and make the code more robust:

- `CognitiveGraphState`: The overall state of the cognitive system
- `Memory`: Manages conversation history and extracted entities
- `Task`: Represents individual tasks and their progress

## Architecture

```
                    ┌───────────┐
                    │  Planner  │
                    └─────┬─────┘
                          │
                          ▼
                    ┌───────────┐
                    │ Executor  │
                    └─────┬─────┘
                          │
                          ▼
                    ┌───────────┐
                    │ Analyser  │
                    └─────┬─────┘
                          │
                          ▼
               ┌──────────────────────┐
               │   Memory Updater     │
               └──────────┬───────────┘
                          │
                          ▼
                    ┌───────────┐
                    │ Reflector │
                    └───────────┘
                          
    Error Handler ◄─── (connects to all nodes)
```

## Usage Example

```python
from core.cognitive_core import cognitive_core

async def main():
    # Define a complex task
    task = {
        "id": "analysis_task",
        "description": "Analyze the performance data and create a summary report",
        "type": "data_analysis"
    }
    
    # Process the task using the enhanced cognitive core
    result = await cognitive_core.process_task(task)
    
    # Check the results
    if result["status"] == "completed":
        print("Task completed successfully")
        print(f"Steps completed: {len(result.get('steps', []))}")
    else:
        print(f"Task failed: {result.get('error')}")
    
    # Get a suggestion for the next action
    next_action = await cognitive_core.suggest_next_action()
    if next_action:
        print(f"Suggested next action: {next_action['action']}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
```

## Integration with Project-S

The enhanced cognitive core integrates seamlessly with the existing Project-S architecture:

- It uses the same event bus system for inter-component communication
- It works with the existing command router for handling different command types
- It maintains backward compatibility with the AICommandHandler

## Configuration

### Multi-model Configuration

The multi-layered LLM integration can be configured through the `config/multi_model_config.json` file, which specifies which models to use for different cognitive tasks and their parameters.

Example configuration:

```json
{
    "models": {
        "planning": {
            "provider": "openrouter",
            "model_name": "anthropic/claude-3-haiku-20240307",
            "parameters": {
                "temperature": 0.2,
                "max_tokens": 2000
            }
        },
        "coding": {
            "provider": "openrouter",
            "model_name": "meta-llama/codellama-70b-instruct",
            "parameters": {
                "temperature": 0.1,
                "max_tokens": 4000
            }
        },
        "default": {
            "provider": "ollama",
            "model_name": "qwen:7b",
            "parameters": {
                "temperature": 0.3
            }
        }
    },
    "task_mappings": {
        "planning": "planning",
        "coding": "coding",
        "default": "default"
    }
}
```

## Error Handling

The enhanced cognitive core includes improved error handling through:

1. The dedicated error handler node in the graph
2. Better state tracking to identify which parts of a task have failed
3. Recovery mechanisms for non-critical errors
4. Detailed error reporting to aid in debugging

## Future Enhancements

Planned future enhancements include:

1. Direct integration with vector databases for improved memory
2. User feedback mechanisms to train the system over time
3. More specialized nodes for domain-specific tasks
4. Integration with external tools and APIs through a tool-use framework
