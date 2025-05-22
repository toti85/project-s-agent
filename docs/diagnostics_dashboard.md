# Diagnostics Dashboard

The Project-S Diagnostics Dashboard provides a web-based interface for monitoring the system's performance, tracking errors, visualizing workflows, and receiving alerts.

## Overview

The dashboard offers real-time insights into the Project-S + LangGraph hybrid system's operations, helping developers and operators identify issues, optimize performance, and understand system behavior.

![Dashboard Screenshot](../assets/dashboard_screenshot.png)

## Features

### System Metrics

- **CPU Usage**: Real-time CPU utilization by the Project-S agent
- **Memory Usage**: Memory consumption with historical trends
- **Thread Count**: Number of active threads
- **Uptime**: System runtime statistics

### Workflow Monitoring

- **Active Workflows**: Currently running workflow count
- **Completed Workflows**: Successfully completed workflow count
- **Failed Workflows**: Count of workflows that terminated with errors
- **Success Rate**: Percentage of successfully completed workflows
- **Performance**: Average execution time by workflow type

### Error Tracking

- **Error Count**: Total number of errors
- **Error Rate**: Errors per hour/minute
- **Error Types**: Distribution of error types
- **Component Analysis**: Which components generate the most errors
- **Error Timeline**: When errors occur over time

### Alerts

- **Recent Alerts**: List of recent system alerts
- **Alert Levels**: Color-coded by severity (info, warning, critical)
- **Alert Sources**: Components that generated the alerts
- **Alert Details**: Additional context for each alert

## Usage

### Accessing the Dashboard

The dashboard is available at http://localhost:7777 by default when the diagnostics system is enabled.

To explicitly start the dashboard:

```bash
# Windows
start_diagnostics.bat [port]

# Linux/macOS
./start_diagnostics.sh [port]
```

Or from the CLI:

```bash
python diagnostics_cli.py dashboard --start --port 7777
```

### Dashboard Sections

#### 1. System Overview

The top section provides a snapshot of system health, including CPU, memory usage, and uptime.

#### 2. Workflow Statistics

This section shows workflow execution statistics, including counts and success rates.

#### 3. Error Insights

This section provides error counts, rates, and distribution by type and component.

#### 4. Recent Alerts

This section displays recent alerts sorted by timestamp, with the most recent alerts at the top.

## Configuration

The dashboard's behavior can be configured through:

### Environment Variables

- `PROJECT_S_DIAGNOSTICS_PORT`: Port number (default: 7777)
- `PROJECT_S_DIAGNOSTICS_REFRESH`: Refresh interval in seconds (default: 10)

### Command Line Options

When starting with start_diagnostics.bat/sh:

```bash
# Set custom port
start_diagnostics.bat 8080

# Or on Linux/macOS
./start_diagnostics.sh 8080
```

## Technical Details

The dashboard is built using:

- **Backend**: Python with aiohttp web server
- **Frontend**: HTML, CSS, JavaScript with Chart.js for visualizations
- **Data Source**: Direct access to the DiagnosticsManager instance

## Extending the Dashboard

To add new metrics or visualizations:

1. Add new metric collection in `DiagnosticsManager` in core/diagnostics.py
2. Add the metric to the appropriate API endpoint in diagnostics_dashboard.py
3. Update the frontend JavaScript to display the new metric

Example:

```python
# In diagnostics_dashboard.py
async def _handle_custom_metrics(self, request):
    """Handle request for custom metrics"""
    custom_data = {
        "my_metric": self._cache.get("my_custom_metric", 0)
    }
    return web.json_response(custom_data)
```

## Troubleshooting

### Dashboard Not Starting

- Verify the port is not in use by another application
- Check if aiohttp is installed (`pip install aiohttp`)
- Examine logs for detailed error information

### Metrics Not Updating

- Ensure the monitoring thread is running
- Check if the refresh interval is set too high
- Verify the diagnostic manager is collecting the expected metrics

### Visualization Issues

- Verify JavaScript console for errors
- Ensure Chart.js is loading correctly
- Check if the API endpoint is returning the expected data format
