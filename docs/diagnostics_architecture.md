# Diagnostics System Technical Architecture

This document provides a technical overview of the diagnostics system architecture in the Project-S + LangGraph hybrid system.

## System Architecture

The diagnostics system is designed with a modular, event-driven architecture that integrates with the core Project-S components while maintaining separation of concerns.

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  LangGraph      │     │  Project-S      │     │  VS Code        │
│  Workflows      │     │  Core           │     │  Extension      │
└────────┬────────┘     └────────┬────────┘     └────────┬────────┘
         │                       │                       │
         └───────────┬───────────┴───────────┬───────────┘
                     │                       │
             ┌───────┴───────┐       ┌───────┴───────┐
             │   Event Bus   │◄─────►│  Error Handler│
             └───────┬───────┘       └───────┬───────┘
                     │                       │
┌────────────────────┼───────────────────────┼────────────────────┐
│                    │                       │                    │
│      ┌─────────────▼─────────────┐         │                    │
│      │                           │         │                    │
│      │   Diagnostics Manager     │◄────────┘                    │
│      │                           │                              │
│      └─────────┬─────────────────┘                              │
│                │                                                │
│                ▼                                                │
│      ┌─────────────────────┐     ┌─────────────────────┐        │
│      │                     │     │                     │        │
│      │  LangGraph          │     │  Diagnostics        │        │
│      │  Diagnostics Bridge │     │  Dashboard          │        │
│      │                     │     │                     │        │
│      └─────────┬───────────┘     └─────────┬───────────┘        │
│                │                           │                    │
│                │                           │                    │
│      ┌─────────▼───────────┐   ┌───────────▼─────────┐          │
│      │                     │   │                     │          │
│      │  Workflow           │   │  Diagnostics CLI    │          │
│      │  Visualizer         │   │                     │          │
│      │                     │   │                     │          │
│      └─────────────────────┘   └─────────────────────┘          │
│                                                                 │
│                          Diagnostics Subsystem                  │
└─────────────────────────────────────────────────────────────────┘
```

## Key Components & Interactions

### 1. Diagnostics Manager (`DiagnosticsManager` class)

**Role**: Central coordinator for all diagnostics activities.

**Responsibilities**:
- Collecting and storing performance metrics
- Tracking errors and their context
- Managing alerts and notifications
- Generating performance reports and visualizations
- Configuring and managing logging

**Key Methods**:
- `register_error()`: Logs and tracks error information
- `send_alert()`: Issues system alerts
- `update_workflow_metrics()`: Updates metrics for workflows
- `generate_performance_report()`: Creates diagnostic reports
- `visualize_workflow()`: Generates workflow visualizations

### 2. LangGraph Diagnostics Bridge

**Role**: Connects LangGraph events to the diagnostics system.

**Responsibilities**:
- Subscribing to LangGraph workflow events
- Translating events into diagnostic metrics
- Capturing workflow states for visualization
- Providing error context for workflow failures

**Event Handlers**:
- `_on_workflow_error()`: Captures workflow failures
- `_on_workflow_start()`: Records workflow initiation
- `_on_workflow_complete()`: Records successful completion
- `_on_state_transition()`: Tracks state changes

### 3. Diagnostics Dashboard

**Role**: Provides web-based visualization and monitoring.

**Responsibilities**:
- Presenting real-time system metrics
- Visualizing workflows and their states
- Displaying error trends and statistics
- Showing alerts and notifications

**Key Components**:
- Web server (aiohttp-based)
- Data cache for metrics
- API endpoints for metrics retrieval
- Front-end UI with charts and visualizations

### 4. Diagnostics CLI

**Role**: Command-line interface for diagnostic operations.

**Responsibilities**:
- Providing status information
- Generating performance reports
- Visualizing and exporting workflows
- Displaying logs and error information

**Commands**:
- `status`: Shows system status
- `performance`: Displays performance metrics
- `errors`: Shows error statistics
- `workflow`: Visualizes workflows
- `dashboard`: Controls the web dashboard
- `logs`: Views system logs
- `monitor`: Real-time monitoring
- `alerts`: Shows system alerts

### 5. Diagnostics Initializer

**Role**: Sets up and configures the diagnostics subsystem.

**Responsibilities**:
- Creating necessary directories
- Initializing the diagnostics manager
- Setting up the LangGraph bridge
- Starting the diagnostics dashboard

## Data Flow

1. **Error Tracking Flow**:
   - Exception occurs in the system
   - Error handler captures exception
   - Diagnostics manager records error context
   - Dashboard updates with new error information
   - Alerts are generated if needed

2. **Performance Monitoring Flow**:
   - Background thread collects metrics at regular intervals
   - Metrics are stored in the diagnostics manager
   - Dashboard retrieves and displays metrics
   - Reports and visualizations are generated on demand

3. **Workflow Monitoring Flow**:
   - LangGraph emits workflow events
   - Diagnostics bridge captures events
   - State transitions and performance are recorded
   - Workflow visualizer generates state graphs

## Storage & Persistence

- **In-memory storage**: For real-time metrics and recent errors
- **File-based storage**: For logs, reports, and visualizations
- **Directory structure**:
  - `logs/`: System and error logs
  - `diagnostics/errors/`: Detailed error reports
  - `diagnostics/reports/`: Performance reports
  - `diagnostics/graphs/`: Visualization images
  - `diagnostics/workflows/`: Workflow state data

## Technologies Used

- **Python**: Core implementation language
- **aiohttp**: Web server for the dashboard
- **matplotlib**: For generating visualizations
- **networkx**: For workflow graph visualization
- **rich**: Enhanced console output

## Integration Points

- **Event Bus**: Main integration point for system events
- **Error Handler**: Integration for error capturing
- **LangGraph**: Integration via event subscriptions
- **Main Application**: Integration via initialization in startup sequence

## Extension Points

The diagnostics system can be extended in these areas:

1. **New Metrics**: Add new metrics to the `PerformanceMetrics` class
2. **Additional Visualizations**: Extend the visualization capabilities
3. **External Integrations**: Add connectors to external monitoring systems
4. **Custom Alerts**: Implement new alert types and notification channels

## Security Considerations

- Dashboard access is limited to localhost by default
- No sensitive data is exposed through the diagnostics interfaces
- Performance impact is managed through configurable sampling rates
