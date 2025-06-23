#!/usr/bin/env python3
"""
Project-S CLI Entry Point
Exported CLI configuration for external use.
"""
import sys
from pathlib import Path

# Add the parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from cli_main import ProjectSCLI, main

if __name__ == "__main__":
    sys.exit(main())
