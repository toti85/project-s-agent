# Project-S CLI Export

This directory contains the exported CLI configuration for Project-S.

## Files:
- `cli_entry.py` - Main CLI entry point
- `config.ini` - Configuration file
- `README.md` - This file

## Usage:
1. Copy this directory to your target system
2. Ensure Project-S dependencies are installed
3. Run: `python cli_entry.py --help`

## Interactive Mode:
```bash
python cli_entry.py --interactive
```

## Direct Commands:
```bash
python cli_entry.py ask "What is Python?"
python cli_entry.py workflow code-generator "Create a FastAPI server"
```
