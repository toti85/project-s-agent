#!/bin/bash
# Project-S Diagnostics Dashboard Startup Script for Linux/macOS

# Default port
DASHBOARD_PORT=7777

# Check for custom port
if [ $# -eq 1 ]; then
    DASHBOARD_PORT=$1
fi

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

echo "Starting Project-S Diagnostics Dashboard on port $DASHBOARD_PORT..."
echo
echo "Dashboard will be available at: http://localhost:$DASHBOARD_PORT"
echo "Press Ctrl+C to stop the dashboard"
echo

# Run the diagnostics dashboard
python -c "import asyncio; from integrations.diagnostics_dashboard import dashboard, start_dashboard; dashboard.port = $DASHBOARD_PORT; asyncio.run(start_dashboard())"

echo "Dashboard stopped"
