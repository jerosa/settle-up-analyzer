#!/usr/bin/env python3
"""Script to run the Settle Up CLI."""
import sys
from pathlib import Path

def setup_environment():
    """Setup the environment for running the CLI."""
    # Add the project root to Python path
    project_root = Path(__file__).parent.parent.absolute()
    sys.path.insert(0, str(project_root))

def main():
    """Main entry point for running the CLI."""
    setup_environment()
    
    try:
        from settle_up.cli.main import cli
        cli()
    except ImportError as e:
        print("Error: Failed to import CLI components.")
        print("Make sure you have installed the required dependencies:")
        print("pip install -r requirements.txt")
        print(f"\nDetailed error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error running CLI: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 
