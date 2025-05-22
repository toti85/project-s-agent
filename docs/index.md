# Project-S Agent Documentation

## Welcome to Project-S

Project-S is a sophisticated, modular, event-driven AI agent system that combines the capabilities of multiple AI models with the structured workflow capabilities of LangGraph.

## Key Features

- **Event-Driven Architecture**: Loose coupling and flexible communication between components.
- **LangGraph Integration**: Structured workflows for complex AI processes.
- **Cognitive Core**: The "brain" of the system, maintaining context, planning tasks, and learning.
- **VS Code Integration**: Direct code generation and execution within VS Code.
- **DOM-Based Communication**: Processes commands originating from the browser.
- **Plugin System**: Easily extendable with new capabilities.
- **Comprehensive Diagnostics**: Advanced monitoring, debugging, and visualization.

## Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/project-s-agent.git
cd project-s-agent

# Install dependencies
pip install -r requirements.txt

# Install diagnostics dependencies
pip install -r requirements-diagnostics.txt
```

### Starting the System

```bash
# On Windows
start.bat

# On Linux/macOS
chmod +x start.sh
./start.sh
```

### Starting with Diagnostics Dashboard

```bash
# On Windows
start_diagnostics.bat

# On Linux/macOS
chmod +x start_diagnostics.sh
./start_diagnostics.sh
```

## Documentation Structure

- [Architecture](architecture.md): System architecture overview
- [Usage Guide](usage.md): How to use Project-S
- [Extension Guide](extension.md): Extending Project-S with plugins
- [Diagnostics System](diagnostics_system.md): Monitoring and debugging
- [LangGraph Integration](langgraph_integration.md): Working with LangGraph

## Diagnostics System

The Project-S Diagnostics System provides comprehensive monitoring, debugging, and visualization capabilities:

- Web-based dashboard at http://localhost:7777
- Command-line interface via `diagnostics_cli.py`
- Workflow visualization and state tracking
- Performance monitoring and alerting
- Detailed error tracking and context gathering

See the [Diagnostics System](diagnostics_system.md) documentation for details.

## Contributing

We welcome contributions! See our [Contributing Guide](contributing.md) for details on how to get involved.

## License

Project-S is licensed under the MIT License. See the [LICENSE](license.md) file for details.
