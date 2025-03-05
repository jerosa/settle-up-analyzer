"""Data analysis functionality for expenses."""
import os
from typing import Optional
from functools import lru_cache

import pandas as pd
from pandas import DataFrame

from .models import AnalyzerData


class Analyzer:
    """Analyzes processed expense data."""

    def __init__(self, workdir: str, excel_filename: str) -> None:
        """Initialize the analyzer.
        
        Args:
            workdir: Directory containing the Excel file
            excel_filename: Name of the Excel file to analyze
        """
        self.workdir = workdir
        self.excel_filename = excel_filename
        self._data: Optional[AnalyzerData] = None

    @property
    def data(self) -> AnalyzerData:
        """Cached access to commonly used dataframes."""
        if self._data is None:
            df = self._read_excel()
            df_expenses = df.loc[df["Type"] == "Expense"]
            df_ingress = df.loc[df["Type"] == "Ingress"]
            df_summary = self._calculate_summary(df_expenses, df_ingress)
            self._data = AnalyzerData(df, df_expenses, df_ingress, df_summary)
        return self._data

    def _read_excel(self) -> DataFrame:
        """Read and preprocess the Excel file."""
        filepath = os.path.join(self.workdir, self.excel_filename)
        
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
        """Calculate yearly summary statistics.
        
        Args:
            df_expenses: DataFrame containing expense records
            df_ingress: DataFrame containing ingress records
            
        Returns:
            DataFrame with yearly summary statistics
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
        """Calculate monthly summary for a specific year or all years.
        
        Args:
            year: Optional year to filter the data. If None, returns summary for all years.
            
        Returns:
            DataFrame with monthly summary statistics
        """
        df_ingress = self.data.df_ingress
        df_expenses = self.data.df_expenses

        if year:
            df_ingress = df_ingress.loc[df_ingress.Year == year]
            df_expenses = df_expenses.loc[df_expenses.Year == year]

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

    def get_category_summary(self, year: Optional[int] = None) -> DataFrame:
        """Get expense summary by category.
        
        Args:
            year: Optional year to filter the data
            
        Returns:
            DataFrame with category summary
        """
        df = self.data.df_expenses
        if year:
            df = df.loc[df.Year == year]
            
        return df.groupby("Category")["Amount"].agg(["sum", "count", "mean"]).round(2) 
