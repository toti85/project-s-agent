# Project-S Diagnostics System

This document provides comprehensive information about the diagnostics system implemented in Project-S.

## Overview

The diagnostics system of Project-S provides extensive monitoring, debugging, and visualization capabilities for the hybrid LangGraph + AI system. It is designed to provide deep insights into system operations, performance metrics, workflow execution, and error conditions.

## Key Components

### 1. Diagnostics Manager (`core/diagnostics.py`)

The central component that coordinates all diagnostics activities:

- Performance monitoring and metrics collection
- Error tracking and contextual information gathering
- Alerting system for critical conditions
- Logging configuration and management
- Report generation

### 2. LangGraph Diagnostics Bridge (`integrations/langgraph_diagnostics_bridge.py`)

Connects LangGraph events to the diagnostics system:

- Captures workflow starts, completions, and failures
- Monitors state transitions within workflows
- Tracks performance of individual workflow steps
- Provides context for workflow failures

### 3. Diagnostics Dashboard (`integrations/diagnostics_dashboard.py`)

Web-based monitoring interface:

- Real-time system metrics visualization
- Workflow statistics and performance graphs
- Error tracking and reporting
- Alerts display and management

### 4. Diagnostics CLI (`diagnostics_cli.py`)

Command-line interface for diagnostics operations:

- System status checking
- Performance reporting
- Workflow visualization and export
- Error analysis
- Log viewing and management

### 5. Diagnostics Initializer (`core/diagnostics_initializer.py`)

Sets up the diagnostics subsystem during application startup:

- Directory creation and management
- Component configuration and initialization
- Dashboard startup

## Usage

### Starting the Dashboard

```bash
# Windows
start_diagnostics.bat [port]

# Linux/macOS
python -c "import asyncio; from integrations.diagnostics_dashboard import dashboard, start_dashboard; asyncio.run(start_dashboard())"
```

### Using the CLI

```bash
# Check system status
python diagnostics_cli.py status

# Generate a performance report
python diagnostics_cli.py performance --report --output report.json

# Visualize a workflow
python diagnostics_cli.py workflow --id workflow_123 --visualize

# Monitor the system in real-time
python diagnostics_cli.py monitor --interval 2

# View the recent alerts
python diagnostics_cli.py alerts --count 10
```

### Programmatic Usage

```python
# Access the diagnostics manager in code
from core.diagnostics import diagnostics_manager

# Register an error
diagnostics_manager.register_error(
    error=exception,
    component="my_component",
    workflow_id="workflow_123"
)

# Send an alert
from core.diagnostics import AlertLevel
diagnostics_manager.send_alert(
    level=AlertLevel.WARNING,
    message="Resource limit approaching",
    source="resource_monitor"
)

# Update workflow metrics
diagnostics_manager.update_workflow_metrics(
    workflow_id="workflow_123",
    execution_time_ms=1500,
    status="completed"
)
```

## Configuration

The diagnostics system can be configured through the following environment variables:

- `PROJECT_S_LOG_LEVEL`: Sets the logging level (debug, info, warning, error, critical)
- `PROJECT_S_MONITORING_INTERVAL`: Sets the interval in seconds for performance measurement
- `PROJECT_S_DIAGNOSTICS_DASHBOARD`: Enables or disables the dashboard (true/false)
- `PROJECT_S_DIAGNOSTICS_PORT`: Sets the port for the diagnostics dashboard

## Extending the Diagnostics System

### Adding New Metrics

To add new metrics to the diagnostics system:

1. Extend the `PerformanceMetrics` class in `core/diagnostics.py`
2. Update the metrics collection in the `_performance_monitoring_loop` method
3. Add visualization for the new metrics in the dashboard if needed

### Creating New Visualizations

To add new visualizations:

1. Extend the `_generate_performance_graphs` method in the `DiagnosticsManager` class
2. Add new chart types to the dashboard's frontend
3. Create new API endpoints in `_setup_routes` if required

## Best Practices

- Use the decorator `@track_workflow_execution` to automatically track workflow execution metrics
- Use `log_execution_time` decorator for performance-critical functions
- Register errors with proper component and context information
- Use appropriate alert levels for different conditions
