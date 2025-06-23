#!/bin/bash
echo "Starting Project-S Multi-Model System..."
echo

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Python 3 is not installed. Please install Python 3.8 or later."
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Virtual environment not found, creating one..."
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo "Failed to create virtual environment."
        exit 1
    fi
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies if needed
pip install -r requirements-multi-model.txt

# Create necessary directories
mkdir -p logs
mkdir -p memory/state

# Run the multi-model system
python3 main_multi_model.py

# Deactivate virtual environment
deactivate
