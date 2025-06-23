# Project-S Multi-Model AI System

This component of Project-S implements a sophisticated multi-model AI system with persistent state management capabilities. It allows the system to dynamically select and switch between different AI models based on task requirements, maintain conversation history, and preserve context across system restarts.

## Features

### Multi-Model Integration
- Supports multiple AI providers: OpenAI, Anthropic, Ollama (local models), and OpenRouter
- Intelligent model selection based on task type and requirements
- Fallback mechanisms for handling API errors
- Performance tracking and metrics collection for model evaluation

### Persistent State Management
- Session-based conversation history
- LangGraph workflow checkpointing
- Context preservation across system restarts
- Efficient storage and retrieval of AI interactions

### Advanced Workflows
- Multi-phase workflows using different models for different tasks
- Planning → Execution → Verification workflow pattern
- Task-specific model selection based on strengths
- Conditional routing based on task complexity

## Getting Started

### Prerequisites
- Python 3.8 or later
- API keys for OpenAI, Anthropic, and/or OpenRouter (optional for Ollama local models)

### Installation

1. Clone the repository
```bash
git clone https://github.com/your-repo/project-s.git
cd project-s
```

2. Install dependencies
```bash
pip install -r requirements-multi-model.txt
```

3. Set up environment variables for API keys
```bash
# For Windows
set OPENAI_API_KEY=your_openai_api_key
set ANTHROPIC_API_KEY=your_anthropic_api_key
set OPENROUTER_API_KEY=your_openrouter_api_key

# For Linux/Mac
export OPENAI_API_KEY=your_openai_api_key
export ANTHROPIC_API_KEY=your_anthropic_api_key
export OPENROUTER_API_KEY=your_openrouter_api_key
```

4. Run the startup script
```bash
# Windows
start_multi_model.bat

# Linux/Mac
./start_multi_model.sh
```

## Usage Examples

### Basic Model Selection

The system automatically selects the appropriate model based on the task:

```python
from integrations.model_manager import model_manager

# Let the system select the best model for the task
result = await model_manager.execute_task_with_model(
    query="Write a Python function to sort a dictionary by values",
    task_type="coding"
)

# Use a specific model
result = await model_manager.execute_task_with_model(
    query="Explain quantum computing in simple terms",
    model="claude-3-opus"
)
```

### Persistent Sessions

Maintain conversation context across multiple interactions:

```python
from integrations.session_manager import session_manager

# Create a new session
session_id = await session_manager.create_session()

# Process queries in the session
result1 = await session_manager.process_in_session(
    session_id=session_id,
    query="What is machine learning?"
)

# Follow-up query using the same context
result2 = await session_manager.process_in_session(
    session_id=session_id,
    query="Give me a simple example of it"
)
```

### Multi-Model Workflows

Use different models for different phases of a complex task:

```python
from integrations.advanced_langgraph_workflow import AdvancedLangGraphWorkflow

workflow = AdvancedLangGraphWorkflow()

# Uses GPT-4 for planning, Claude for execution, and GPT-3.5 for verification
result = await workflow.process_with_multi_model_graph_with_persistence(
    command="Design and implement a RESTful API for a blog system",
    session_id="optional-session-id"  # Creates new session if not provided
)
```

## Configuration

Model configurations are stored in `config/models_config.yaml`. You can customize:

- Which models are enabled
- Task-to-model mappings
- Model parameters (temperature, etc.)
- Provider-specific settings

## Contributing

Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code of conduct and the process for submitting pull requests.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
