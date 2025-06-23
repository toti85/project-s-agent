# Multi-Model AI Integration Guide

This document provides a comprehensive guide to the multi-model AI integration in Project-S, including persistent state management, model selection, and workflow capabilities.

## Architecture Overview

The multi-model AI integration consists of several key components:

1. **Multi-Model AI Client** (`multi_model_ai_client.py`)
   - Manages connections to different AI providers (OpenAI, Anthropic, Ollama, OpenRouter)
   - Provides a unified interface for generating responses
   - Handles API-specific requirements and error recovery

2. **Model Manager** (`model_manager.py`)
   - Selects appropriate models based on task type and context
   - Tracks model performance metrics
   - Provides high-level task execution methods

3. **Persistent State Manager** (`persistent_state_manager.py`)
   - Maintains conversation history across sessions
   - Saves and loads LangGraph workflow checkpoints
   - Preserves context across system restarts

4. **Advanced LangGraph Workflows** (`advanced_langgraph_workflow.py`)
   - Implements structured workflows for complex tasks
   - Supports multi-model execution for different workflow phases
   - Enables conditional routing based on task analysis

5. **Session Manager** (`session_manager.py`)
   - Provides high-level session management capabilities
   - Coordinates between state management and model execution
   - Handles session creation, tracking, and cleanup

## Persistent State Management

### Storage Structure

The persistent state manager uses the following directory structure:

```
memory/
  ├── state/
  │   ├── conversations/ - Conversation history by session
  │   ├── checkpoints/   - LangGraph workflow checkpoints
  │   ├── sessions/      - Session metadata and tracking
  │   │   └── archived/  - Ended/archived sessions 
  │   └── context/       - Persistent context data
  └── model_performance_cache.json - Model performance metrics
```

### Session Lifecycle

1. **Session Creation**: A unique session ID is generated and initial metadata is stored
2. **Conversation Storage**: User and assistant messages are saved with timestamps and metadata
3. **Workflow Checkpoints**: LangGraph states are saved to enable resuming complex workflows
4. **Session Continuation**: New queries can be processed with full context of previous interactions
5. **Session Archiving**: Completed sessions are moved to archive for reference

## Model Selection

The system selects models based on several factors:

1. **Task Type Detection**: Analyzes input text to determine the task category (coding, creative writing, etc.)
2. **Task-Model Mapping**: Uses configuration to map task types to appropriate models
3. **Performance History**: Considers past performance metrics for similar tasks
4. **Availability**: Checks if preferred models are available and falls back if needed
5. **Explicit Preference**: Honors user-specified model preferences when provided

## Multi-Model Workflows

The LangGraph integration enables sophisticated multi-model workflows:

### Basic Workflow
For simple tasks that can be handled by a single model in one pass.

### Multi-Step Workflow
For complex tasks requiring multiple stages of processing:
1. **Analysis**: Understand the request and break it down
2. **Execution**: Process each component of the task
3. **Integration**: Combine results into a coherent response

### Multi-Model Workflow
For tasks benefiting from different models at different stages:
1. **Planning**: Using a strong reasoning model (e.g., GPT-4)
2. **Execution**: Using a specialized model (e.g., Claude for code)
3. **Verification**: Using a critical analysis model to check results

## Configuration

### Model Configuration

Models are configured in `config/models_config.yaml`:

```yaml
# Example configuration for OpenAI models
openai:
  enabled: true
  models:
    gpt-4:
      name: "GPT-4"
      description: "Strong reasoning and planning model"
      context_length: 8192
      strengths: ["planning", "reasoning", "complex thinking"]
      cost_tier: "high"
      default_temperature: 0.7
```

### Task-Model Mappings

Task types are mapped to appropriate models:

```yaml
task_model_mapping:
  planning: ["gpt-4", "claude-3-opus"]
  coding: ["claude-3-opus", "claude-3-sonnet", "gpt-4"]
  documentation: ["gpt-4", "claude-3-sonnet"]
  data_analysis: ["claude-3-opus", "gpt-4"]
```

## API Guide

### Session Management

```python
# Create new session
session_id = await session_manager.create_session(metadata={"user": "user123"})

# Process in session
result = await session_manager.process_in_session(
    session_id=session_id,
    query="Write a Python function to calculate Fibonacci numbers",
    workflow_type="multi_model"
)

# Get conversation history
history = await persistent_state_manager.get_conversation_history(session_id)

# End session
await session_manager.end_session(session_id)
```

### Model Management

```python
# Execute with automatic model selection
result = await model_manager.execute_task_with_model(
    query="Explain quantum computing",
    task_type="explanation"
)

# Execute with specific model
result = await model_manager.execute_task_with_model(
    query="Write a regex to match email addresses",
    model="gpt-4",
    temperature=0.3
)

# Compare multiple models
results = await model_manager.run_task_with_multiple_models(
    query="Translate this paragraph to French",
    models=["gpt-3.5-turbo", "claude-3-sonnet"]
)
```

### Workflow Execution

```python
# LangGraph workflow with persistence
workflow = AdvancedLangGraphWorkflow()
result = await workflow.process_with_multi_model_graph_with_persistence(
    command="Create an algorithm to detect anomalies in time series data",
    session_id=session_id
)
```

## Best Practices

1. **Session Management**
   - Create sessions for related interactions
   - End sessions when conversations are complete
   - Use metadata to track session purpose and origin

2. **Model Selection**
   - Let the system select models automatically when possible
   - Specify models only when needed for specific capabilities
   - Consider cost implications of model choices

3. **Workflow Design**
   - Use basic workflow for simple queries
   - Use multi-step workflow for complex but single-model tasks
   - Use multi-model workflow when different phases benefit from different models

4. **Performance Optimization**
   - Monitor model metrics to identify optimal models for tasks
   - Use session contexts to avoid redundant information in queries
   - Consider checkpointing for long-running processes

## Metrics and Monitoring

The system collects the following metrics:

- Response time by model and task type
- Success rates for API calls
- Model usage frequency
- Session counts and durations
- Workflow completion rates

These metrics are available through the `get_model_performance_stats()` method in the model manager.

## Error Handling

The system implements several error recovery mechanisms:

- Connection retry with exponential backoff
- Automatic fallback to alternative models
- Session state preservation during errors
- Detailed error logging for diagnostics

## Future Enhancements

Planned enhancements for the multi-model system:

1. **Adaptive Learning**: Automatically adjust model preferences based on performance
2. **Parallel Processing**: Execute suitable parts of workflows in parallel
3. **Cost Optimization**: Intelligent selection based on cost-performance tradeoffs
4. **Enhanced Metrics**: More detailed performance analysis and visualization
5. **Custom Model Support**: Integration with custom-trained models
