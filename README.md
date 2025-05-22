# Project-S Agent: LangGraph + AI Hybrid System

## Overview

Project-S is a sophisticated, modular, event-driven AI agent system capable of processing and executing various types of commands. The system creates an intelligent, autonomous internet-interacting agent that combines the capabilities of multiple AI models with the structured workflow capabilities of LangGraph.

## Key Features

- **Event-Driven Architecture**: Loose coupling and flexible communication between components.
- **LangGraph Integration**: Structured workflows for complex AI processes.
- **Cognitive Core**: The "brain" of the system, maintaining context, planning tasks, and learning.
- **VS Code Integration**: Direct code generation and execution within VS Code.
- **DOM-Based Communication**: Processes commands originating from the browser.
- **Plugin System**: Easily extendable with new capabilities.
- **Comprehensive Diagnostics**: Advanced monitoring, debugging, and visualization.

## Components

- **CentralExecutor**: The central component responsible for executing commands.
- **CognitiveCore**: Maintains context and plans tasks.
- **LangGraph Workflows**: Structured processing pipelines for complex tasks.
- **EventBus**: Enables event-driven communication between components.
- **DOMListener**: Handles commands originating from the browser.
- **VSCodeInterface**: Manages integration with Visual Studio Code.
- **Diagnostics System**: Comprehensive monitoring and debugging tools.

## Getting Started

### Installation

# Clone the repository
git clone https://github.com/yourusername/project-s-agent.git
cd project-s-agent

# Install dependencies
pip install -r requirements.txt

# Install testing dependencies (optional)
pip install -r requirements-test.txt

### Running the System

#### Regular Startup

```bash
# On Windows
start.bat

# On Linux/macOS
./start.sh
```

#### Startup with Diagnostics Dashboard

```bash
# On Windows
start_diagnostics.bat [port]

# On Linux/macOS
python -c "import asyncio; from integrations.diagnostics_dashboard import dashboard, start_dashboard; dashboard.port = 7777; asyncio.run(start_dashboard())"
```

### Diagnostics CLI

Project-S includes a comprehensive diagnostics CLI for monitoring and debugging:

```bash
# Display system status
python diagnostics_cli.py status

# Show performance metrics
python diagnostics_cli.py performance --report

# Start the diagnostic dashboard
python diagnostics_cli.py dashboard --start

# Monitor the system in real-time
python diagnostics_cli.py monitor

# Check recent alerts
python diagnostics_cli.py alerts

# View system logs
python diagnostics_cli.py logs --follow
```

## Diagnostics and Monitoring

Project-S provides comprehensive diagnostics and monitoring capabilities:

### Diagnostics Dashboard

A web-based dashboard for real-time monitoring of system metrics, errors, and workflow statistics. Access at http://localhost:7777 when enabled.

Features:
- Real-time resource utilization monitoring (CPU, memory)
- Workflow execution visualization and statistics
- Error tracking and alerting
- Performance metrics and graphs

### LangGraph Diagnostics

Advanced monitoring and visualization for LangGraph workflows:
- Workflow state visualization
- Execution path tracking
- Performance bottleneck identification
- Error context collection

### CLI Interface

A comprehensive command-line interface for diagnostics:
```bash
python diagnostics_cli.py [command] [options]
```

Available commands:
- `status`: Display system status
- `performance`: Show performance metrics
- `errors`: Display error information
- `workflow`: Visualize and export workflow data
- `dashboard`: Control the diagnostics dashboard
- `logs`: View and follow system logs
- `monitor`: Real-time system monitoring
- `alerts`: View system alerts

## Documentation

For more details, refer to the following documents:

- [Architecture](docs/architecture.md): Detailed description of the system architecture.
- [Usage](docs/usage.md): Instructions on how to use the system.
- [Extension](docs/extension.md): Guide on extending the system.
- [LangGraph Integration](docs/langgraph_integration.md): Guide on LangGraph workflow integration.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please see the [CONTRIBUTING.md](CONTRIBUTING.md) file for guidelines.

## Testing

Project-S includes a comprehensive testing system that covers all aspects of the system:

### Quick Verification

To quickly verify if the system is working correctly:

```bash
python quick_verification.py
```

### Running Full Tests

To run the complete test suite:

```bash
python run_integrated_tests.py
```

For specific test types:

```bash
python run_integrated_tests.py --test-type unit
python run_integrated_tests.py --test-type integration
python run_integrated_tests.py --test-type e2e
```

### Test Documentation

For detailed information about the testing system:

- [Complete Testing Guide](complete_testing_guide.md): Detailed guide for using the testing system
- [Comprehensive Verification Plan](comprehensive_verification_plan.md): Overall testing strategy
- [Testing Strategy Summary](testing_strategy_summary.md): High-level overview of the testing approach

### Test Reports

Generate HTML test reports:

```bash
python run_integrated_tests.py --report --report-dir test_reports
```