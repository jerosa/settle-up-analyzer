"""Configuration management for financial analysis."""
import os
from pathlib import Path
from typing import Dict, Any

from dotenv import load_dotenv


def load_config() -> Dict[str, Any]:
    """Load configuration from environment variables.
    
    Returns:
        Dictionary containing configuration values
    """
    # Load .env file if it exists
    load_dotenv()
    
    # Get configuration from environment variables
    config = {
        "workdir": os.getenv("FINANALYZER_WORKDIR", str(Path.home() / "data")),
        "user_to_analyze": os.getenv("FINANALYZER_USER", ""),
        "excel_filename": os.getenv("FINANALYZER_EXCEL", "expenses.xlsx"),
    }
    
    # Create workdir if it doesn't exist
    os.makedirs(config["workdir"], exist_ok=True)
    
    return config


# Global configuration
config = load_config() 
