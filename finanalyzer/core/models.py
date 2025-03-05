"""Data models for the Settle Up Analyzer."""
from dataclasses import dataclass
from pandas import DataFrame


@dataclass
class AnalyzerData:
    """Container for commonly used dataframes to avoid recomputation."""
    df: DataFrame
    df_expenses: DataFrame
    df_ingress: DataFrame
    df_summary: DataFrame
