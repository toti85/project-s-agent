#!/usr/bin/env python3
"""
Project-S CLI Entry Point
=========================
Clean entry point for the Project-S command-line interface.
All complex logic has been moved to dedicated modules.

Author: Project-S Team
Version: 2.0 - Modular CLI
"""

import sys
import asyncio
from pathlib import Path
import os

# Calculate project root correctly (apps/cli/main.py -> project root is 2 levels up)
project_root = Path(__file__).parent.parent
os.chdir(project_root)

# Add src to path for imports
src_path = project_root / "src" 
sys.path.insert(0, str(src_path))

from cli.main import ProjectSCLI


async def main():
    """Main entry point for Project-S CLI."""
    cli = ProjectSCLI()
    return await cli.run()


if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n👋 CLI session interrupted.")
        sys.exit(0)
    except Exception as e:
        print(f"Fatal error: {e}")
        sys.exit(1)
