# Diagnostics CLI

The Project-S Diagnostics CLI provides a command-line interface for accessing diagnostic features, monitoring system performance, and managing diagnostic tools.

## Overview

The CLI gives you direct access to diagnostic capabilities from the terminal, allowing you to check system status, analyze performance, visualize workflows, and manage the diagnostics dashboard without a web browser.

## Installation

The CLI is included with the main Project-S installation. No additional setup is required.

## Commands

### Status

Display current system status:

```bash
python diagnostics_cli.py status
```

With detailed information:

```bash
python diagnostics_cli.py status --verbose
```

### Performance

Show performance metrics:

```bash
python diagnostics_cli.py performance
```

Generate a full performance report:

```bash
python diagnostics_cli.py performance --report --output performance_report.json
```

### Errors

Show error information:

```bash
# Show recent errors
python diagnostics_cli.py errors --list

# Show error statistics
python diagnostics_cli.py errors --stats

# Control how many errors to display
python diagnostics_cli.py errors --list --count 20

# Export error data
python diagnostics_cli.py errors --list --output errors.json
```

### Workflow

Display and manage workflow information:

```bash
# Visualize a workflow
python diagnostics_cli.py workflow --id workflow_123 --visualize

# Export workflow data
python diagnostics_cli.py workflow --id workflow_123 --export json --output workflow_data.json
```

### Dashboard

Control the diagnostics dashboard:

```bash
# Start the dashboard
python diagnostics_cli.py dashboard --start

# Start on a specific port
python diagnostics_cli.py dashboard --start --port 8080

# Stop the dashboard
python diagnostics_cli.py dashboard --stop
```

### Logs

View and manage logs:

```bash
# Show recent logs
python diagnostics_cli.py logs

# Show last 50 log entries
python diagnostics_cli.py logs --tail 50

# Show only error logs
python diagnostics_cli.py logs --errors-only

# Follow logs in real-time
python diagnostics_cli.py logs --follow
```

### Monitor

Real-time monitoring of system metrics:

```bash
# Monitor with default settings
python diagnostics_cli.py monitor

# Set update interval
python diagnostics_cli.py monitor --interval 5

# Monitor specific metrics
python diagnostics_cli.py monitor --metrics cpu
```

### Alerts

View system alerts:

```bash
# Show recent alerts
python diagnostics_cli.py alerts

# Show specific number of alerts
python diagnostics_cli.py alerts --count 20

# Filter by alert level
python diagnostics_cli.py alerts --level critical
```

## Examples

### Basic Health Check

```bash
python diagnostics_cli.py status
```

Sample output:
```
Project-S System Status
======================
Status: Running
Uptime: 3h 45m
CPU Usage: 23.4%
Memory Usage: 512.3MB (15.7%)
Active Workflows: 3
Recent Errors: 2
```

### Real-time Monitoring

```bash
python diagnostics_cli.py monitor --interval 2
```

This will display a continuously updating view of system metrics.

### Error Investigation

```bash
# First check error statistics
python diagnostics_cli.py errors --stats

# Then examine specific errors
python diagnostics_cli.py errors --list

# Export errors for further analysis
python diagnostics_cli.py errors --list --output error_report.json
```

### Workflow Visualization

```bash
python diagnostics_cli.py workflow --id workflow_123 --visualize
```

This will generate a visualization of the workflow structure and state.

## Advanced Usage

### Combining Commands with Shell Tools

You can pipe CLI output to other tools:

```bash
# Filter errors by component
python diagnostics_cli.py errors --list --count 50 | grep "langgraph"

# Send performance report by email
python diagnostics_cli.py performance --report --output report.json && mail -a report.json -s "Performance Report" admin@example.com
```

### Scheduled Diagnostics

You can use cron jobs or task scheduler to run diagnostics periodically:

```bash
# Add to crontab on Linux
# Generate performance report every hour
0 * * * * cd /path/to/project-s && python diagnostics_cli.py performance --report --output /var/log/project-s/perf_$(date +\%Y\%m\%d\%H).json

# Alert on high error rates
*/15 * * * * cd /path/to/project-s && python diagnostics_cli.py errors --stats | grep -q "Error rate: [5-9][0-9]" && python notify.py "High error rate detected"
```

## Return Codes

The CLI returns standard exit codes:

- `0`: Success
- `1`: Generic error
- `2`: Command not found
- `3`: Invalid arguments
- `4`: System error

## Custom Configuration

You can create a `.diagnostics_cli_config.json` file in the project root to customize default behavior:

```json
{
  "default_output_dir": "diagnostic_reports",
  "default_log_level": "info",
  "default_count": 15,
  "default_interval": 3
}
```

## Implementation Details

The CLI is implemented in `diagnostics_cli.py` using Python's argparse module. It interfaces with the `DiagnosticsManager` class to retrieve and manage diagnostic information.
