"""Utility functions for the FinAnalyzer."""
import os

import pandas as pd
from pandas import DataFrame


def safe_read_excel(filepath: str, **kwargs) -> DataFrame:
    """Safely read an Excel file with error handling.
    
    Args:
        filepath: Path to the Excel file
        **kwargs: Additional arguments for pd.read_excel
        
    Returns:
        DataFrame containing the Excel data
        
    Raises:
        FileNotFoundError: If the file doesn't exist
        ValueError: If the file is empty or invalid
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Excel file not found: {filepath}")
        
    df = pd.read_excel(filepath, **kwargs)
    
    if df.empty:
        raise ValueError(f"Excel file is empty: {filepath}")
        
    return df
