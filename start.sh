#!/bin/bash

# Process command line arguments
ENABLE_DASHBOARD=true
DASHBOARD_PORT=7777

# Check for command line arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --no-dashboard)
      ENABLE_DASHBOARD=false
      shift
      ;;
    --port)
      DASHBOARD_PORT="$2"
      shift 2
      ;;
    *)
      echo "Unknown option: $1"
      echo "Usage: start.sh [--no-dashboard] [--port PORT]"
      exit 1
      ;;
  esac
done

# Set environment variables for diagnostics configuration
export PROJECT_S_DIAGNOSTICS_DASHBOARD=$ENABLE_DASHBOARD
export PROJECT_S_DIAGNOSTICS_PORT=$DASHBOARD_PORT

# Aktiválja a virtuális környezetet, ha létezik
if [ -d "venv" ]; then
    source venv/bin/activate
fi

echo "Starting Project-S Agent..."
if [ "$ENABLE_DASHBOARD" = true ]; then
    echo "Diagnostics dashboard will be available at http://localhost:$DASHBOARD_PORT"
fi

# Elindítja a Project-S agentet
python main.py