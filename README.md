# Project-S Agent

## Overview

Project-S is a modular, event-driven AI agent system capable of processing and executing various types of commands. The system aims to create an intelligent, autonomous internet-interacting agent that combines the capabilities of multiple AI models (e.g., Qwen3, Claude, ChatGPT).

## Key Features

- **Event-Driven Architecture**: Loose coupling and flexible communication between components.
- **Cognitive Core**: The "brain" of the system, maintaining context, planning tasks, and learning.
- **VS Code Integration**: Direct code generation and execution within VS Code.
- **DOM-Based Communication**: Processes commands originating from the browser.
- **Plugin System**: Easily extendable with new capabilities.

## Components

- **CentralExecutor**: The central component responsible for executing commands.
- **CognitiveCore**: Maintains context and plans tasks.
- **EventBus**: Enables event-driven communication between components.
- **DOMListener**: Handles commands originating from the browser.
- **VSCodeInterface**: Manages integration with Visual Studio Code.

## Getting Started

### Installation

# Clone the repository
git clone https://github.com/your-username/project-s-agent.git
cd project-s-agent

# Install dependencies
pip install -r requirements.txt
```

### Running the System

```bash
python main.py
```

## Documentation

For more details, refer to the following documents:

- [Architecture](docs/architecture.md): Detailed description of the system architecture.
- [Usage](docs/usage.md): Instructions on how to use the system.
- [Extension](docs/extension.md): Guide on extending the system.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please see the [CONTRIBUTING.md](CONTRIBUTING.md) file for guidelines.