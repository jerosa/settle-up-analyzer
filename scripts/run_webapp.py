#!/usr/bin/env python3
"""Script to run the web application."""
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

def setup_environment():
    """Setup the environment for running the web app."""
    # Add the project root to Python path
    project_root = Path(__file__).parent.parent.absolute()
    sys.path.insert(0, str(project_root))
    
    # Load environment variables from .env file if it exists
    env_file = project_root / ".env"
    load_dotenv(env_file)
    
    # Set default environment variables if not set
    os.environ.setdefault("FLASK_DEBUG", "1")
    os.environ.setdefault("FLASK_APP", "finanalyzer.web.app")
    os.environ.setdefault("FLASK_RUN_HOST", "0.0.0.0")
    os.environ.setdefault("FLASK_RUN_PORT", "5000")

def main():
    """Main entry point for running the web application."""
    setup_environment()
    
    try:
        from finanalyzer.web.app import app
        host = os.getenv("FLASK_RUN_HOST", "0.0.0.0")
        port = int(os.getenv("FLASK_RUN_PORT", "5000"))
        debug = os.getenv("FLASK_DEBUG", "1").lower() in ("1", "true", "yes")
        
        # Use Dash's run_server method instead of Flask's run method
        app.run(
            debug=debug,
            host=host,
            port=port,
            dev_tools_hot_reload=True,  # Enable hot reloading
            dev_tools_ui=True,  # Enable dev tools UI
        )
    except ImportError as e:
        print("Error: Failed to import web application components.")
        print("Make sure you have installed the required dependencies:")
        print("pip install -r requirements.txt")
        print(f"\nDetailed error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error starting web application: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 
