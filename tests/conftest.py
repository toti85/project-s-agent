import sys
import os
from pathlib import Path

# Add the parent directory to sys.path so tests can import project modules
parent_dir = Path(__file__).parent.parent.absolute()
sys.path.insert(0, str(parent_dir))

# Setup any test fixtures or configuration here