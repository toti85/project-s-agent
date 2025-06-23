# LangGraph Examples for Project-S

This directory contains example code demonstrating how to use LangGraph with Project-S. LangGraph is a framework for building stateful, multi-actor applications with LLMs.

## Overview

The examples in this directory show different ways to use LangGraph with Project-S:

1. **Basic Example** (`langgraph_example.py`): A simple sequential workflow using LangGraph
2. **Advanced Example** (`advanced_langgraph_example.py`): A more complex workflow with conditional execution
3. **Branching Example** (`branching_langgraph_example.py`): A workflow that demonstrates dynamic branching based on intermediate results
4. **State Message Handling Example** (`state_message_handling_example.py`): An example showing advanced state and message handling techniques

## Getting Started

### Prerequisites

Make sure you have installed LangGraph:

```bash
pip install langgraph -U
```

### Running the Examples

To run any example, use Python to execute the script:

```bash
python examples/langgraph_example.py
```

## Example Descriptions

### Basic Example

This example demonstrates the simplest form of LangGraph integration with Project-S. It creates a workflow that:

1. Executes a shell command to list files
2. Creates a Python script to analyze those files
3. Runs the script
4. Summarizes the results

### Advanced Example

The advanced example shows how to create workflows with conditional paths. It:

1. Analyzes a codebase
2. Makes decisions about next steps based on the analysis
3. Executes different commands based on those decisions

### Branching Example

The branching example demonstrates a dynamic workflow that changes execution path based on intermediate results:

1. Performs an initial analysis
2. Dynamically selects one of three possible branches:
   - Standard processing
   - API integration
   - Error recovery
3. Executes branch-specific steps

## Key Concepts

### Workflow Creation

```python
workflow_command = {
    "type": "WORKFLOW",
    "operation": "create",
    "name": "my_workflow",
    "steps": [
        {"type": "CMD", "cmd": "echo Hello"},
        {"type": "ASK", "query": "What happened?"}
    ],
    "context": {
        "purpose": "Demonstration"
    }
}
result = await router.route_command(workflow_command)
graph_id = result["graph_id"]
```

### Workflow Execution

```python
await router.route_command({
    "type": "WORKFLOW",
    "operation": "start",
    "graph_id": graph_id
})
```

### Branching Workflows

```python
# Define main steps
steps = [initial_step]

# Define branches
branches = {
    "branch_1": [step1, step2, step3],
    "branch_2": [stepA, stepB]
}

# Create context with decision function
context = {
    "decision_function": "my_decision_function"
}

# Create workflow
result = await router.route_command({
    "type": "WORKFLOW",
    "operation": "create",
    "steps": steps,
    "branches": branches,
    "context": context
})
```

## Workflow Events

The LangGraph integration publishes the following events you can subscribe to:

- `workflow.started`: When a workflow begins execution
- `workflow.completed`: When a workflow completes all steps
- `workflow.error`: When a workflow encounters an error
- `workflow.decision`: When a workflow makes a branching decision
- `workflow.step.retrying`: When a workflow step is being retried after failure

## Further Reading

For more detailed information, check:

- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [Project-S Integration Documentation](../docs/langgraph_integration.md)
