import os
from typing import Optional
from functools import lru_cache
from dataclasses import dataclass

import pandas as pd
from pandas import DataFrame
from datetime import datetime
from config import logger, settings


def get_plot_filename(workdir: str, filename: str) -> str:
    return os.path.join(workdir, filename)


@dataclass
class AnalyzerData:
    """Container for commonly used dataframes to avoid recomputation"""
    df: DataFrame
    df_expenses: DataFrame
    df_ingress: DataFrame
    df_summary: DataFrame


class Analyzer:
    def __init__(self) -> None:
        self.workdir: str = settings["workdir"]
        self.plotdir: str = os.path.join(self.workdir, "plots")
        self._data: Optional[AnalyzerData] = None

    @property
    def data(self) -> AnalyzerData:
        """Cached access to commonly used dataframes"""
        if self._data is None:
            df = self._read_excel()
            df_expenses = df.loc[df["Type"] == "Expense"]
            df_ingress = df.loc[df["Type"] == "Ingress"]
            df_summary = self._calculate_summary(df_expenses, df_ingress)
            self._data = AnalyzerData(df, df_expenses, df_ingress, df_summary)
        return self._data

    def _read_excel(self) -> DataFrame:
        """Read and preprocess the Excel file"""
        excel_name = settings["expenses_excel_filename"]
        filepath = os.path.join(self.workdir, excel_name)
        logger.debug(f"Reading excel {filepath}")
        
        df: DataFrame = pd.read_excel(
            filepath,
            converters={"Date & time": pd.to_datetime},
            index_col="Date & time",
        )
        df.sort_index(ascending=True, inplace=True)

        df.loc[:, "Year"] = df.index.year
        df.loc[:, "Month"] = df.index.month

        return df

    def _calculate_summary(self, df_expenses: DataFrame, df_ingress: DataFrame) -> DataFrame:
        """Calculate yearly summary statistics
        
        Args:
            df_expenses: DataFrame containing expense records
            df_ingress: DataFrame containing ingress records
            
        Returns:
            DataFrame with yearly summary statistics including expenses, ingress, and savings
        """
        expenses_year = df_expenses.groupby("Year")["Amount"].sum()
        ingress_year = df_ingress.groupby("Year")["Amount"].sum()
        
        summary = pd.concat(
            [expenses_year, ingress_year], axis=1, keys=["Expenses", "Ingress"]
        )
        summary["Savings"] = summary["Ingress"] - summary["Expenses"]
        summary["Savings %"] = (
            (summary["Ingress"] - summary["Expenses"]) / summary["Ingress"] * 100
        )
        return summary.round(2)

    @lru_cache(maxsize=32)
    def month_summary(self, year: Optional[int] = None) -> DataFrame:
        """Calculate monthly summary for a specific year or all years
        
        Args:
            year: Optional year to filter the data. If None, returns summary for all years.
            
        Returns:
            DataFrame with monthly summary statistics including expenses, ingress, and savings
        """
        # Get cached dataframes
        df_ingress = self.data.df_ingress
        df_expenses = self.data.df_expenses

        # Filter by year if specified
        if year:
            df_ingress = df_ingress.loc[df_ingress.Year == year]
            df_expenses = df_expenses.loc[df_expenses.Year == year]

        # Calculate monthly summaries
        per_ingress = df_ingress.index.to_period("M")
        per_expenses = df_expenses.index.to_period("M")
        
        ingress_year_month = df_ingress.groupby(per_ingress)["Amount"].sum()
        expenses_year_month = df_expenses.groupby(per_expenses)["Amount"].sum()

        summary = pd.concat(
            [expenses_year_month, ingress_year_month],
            axis=1,
            keys=["Expenses", "Ingress"],
        )
        summary.fillna(0, inplace=True)
        summary["Savings"] = summary["Ingress"] - summary["Expenses"]
        summary.index = summary.index.to_timestamp()
        
        return summary
