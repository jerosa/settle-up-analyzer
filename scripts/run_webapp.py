#!/usr/bin/env python3
"""Script to run the web application."""
import os
from pathlib import Path

from dotenv import load_dotenv
from finanalyzer.web.app import app

def main():
    """Run the web application."""
    # Get the project root directory (where .env should be)
    project_root = Path(__file__).parent.parent
    
    # Load .env file from project root
    env_path = project_root / '.env'
    load_dotenv(env_path)
    
    # Run the app
    app.run_server(debug=True)

if __name__ == "__main__":
    main() 
