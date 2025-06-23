import sys
from pathlib import Path
import os

print("Script location:", __file__)
print("Current dir before:", os.getcwd())

# apps/cli/main.py -> project root
project_root = Path(__file__).parent.parent.parent
print("Project root calculated:", project_root)
print("Project root absolute:", project_root.absolute())

os.chdir(project_root)
print("Current dir after chdir:", os.getcwd())

# Add src to path
src_path = project_root / "src" 
print("Src path:", src_path)
print("Src path exists:", src_path.exists())

sys.path.insert(0, str(src_path))
sys.path.insert(0, str(project_root))

print("Python path first few entries:", sys.path[:3])

# Check if cli module exists
cli_path = src_path / "cli"
print("CLI path:", cli_path)
print("CLI path exists:", cli_path.exists())
print("CLI contents:", list(cli_path.iterdir()) if cli_path.exists() else "N/A")

# Try import
try:
    from cli.main import ProjectSCLI
    print("✅ Import successful")
except ImportError as e:
    print(f"❌ Import failed: {e}")
