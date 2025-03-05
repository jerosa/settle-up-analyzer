"""Core functionality for processing Settle Up CSV exports."""
from dataclasses import dataclass
from pathlib import Path
from typing import List, Set, Optional

import pandas as pd

@dataclass
class ProcessorConfig:
    """Configuration for the SettleUpProcessor."""
    workdir: Path
    filename_to_process: str
    user_to_analyse: str
    wanted_columns: List[str] = None

    def __post_init__(self):
        if self.wanted_columns is None:
            self.wanted_columns = ["Purpose", "Category", "Month", self.user_to_analyse]

class SettleUpProcessor:
    """Processes Settle Up CSV exports to analyze expenses."""
    
    HEADERS = [
        "Who paid", "Amount", "Currency", "For whom", "Split amounts",
        "Purpose", "Category", "Date & time", "Exchange rate",
        "Converted amount", "Type", "Receipt"
    ]
    
    DTYPES = {
        "Who paid": "str",
        "Amount": "float",
        "Currency": "str",
        "For whom": "str",
        "Split amounts": "str",
        "Purpose": "str",
        "Category": "str",
        "Date & time": "str",
        "Exchange rate": "str",
        "Converted amount": "float",
        "Type": "str",
        "Receipt": "str"
    }

    def __init__(self, config: ProcessorConfig):
        """Initialize the processor with configuration."""
        self.config = config
        self.df: Optional[pd.DataFrame] = None
        self.users: Set[str] = set()

    def _get_latest_filename(self) -> str:
        """Get the most recent transactions CSV file from the workdir."""
        files = list(self.config.workdir.glob("*transactions.csv"))
        if not files:
            raise FileNotFoundError("No transaction CSV files found in workdir")
        # Return just the filename rather than full path since workdir is added later
        return files[0].name

    def read_raw_csv(self) -> None:
        """Read and preprocess the CSV file."""
        filename = (self._get_latest_filename() if self.config.filename_to_process == "auto"
                   else self.config.filename_to_process)
        filepath = self.config.workdir / filename

        self.df = pd.read_csv(
            filepath,
            header=0,
            encoding="utf8",
            sep=",",
            usecols=self.HEADERS,
            names=self.HEADERS,
            dtype=self.DTYPES,
            index_col="Date & time",
            parse_dates=["Date & time"],
        )
        # Remove transfers, keep only expenses
        self.df = self.df.loc[self.df["Type"] == "expense"]
        self.df.loc[:, "Month"] = self.df.index.month

    def set_users(self, who_df: pd.DataFrame) -> None:
        """Extract unique users from the expenses data."""
        users = set()
        for col in who_df.columns:
            users.update(who_df[col].dropna().unique())
        self.users = users

    def calc_user_expenses(self) -> None:
        """Calculate expenses per user."""
        who_df = self.df["For whom"].str.split(";", expand=True)
        who_df.columns = [f"for_{i}" for i in range(len(who_df.columns))]

        amount_df = self.df["Split amounts"].str.split(";", expand=True)
        amount_df.columns = [f"amount_{i}" for i in range(len(amount_df.columns))]

        if len(who_df.columns) != len(amount_df.columns):
            raise ValueError("Mismatch between users and amounts columns")

        self.df = self.df.join(who_df).join(amount_df)
        self.set_users(who_df)

        # Calculate expenses by user
        for user in self.users:
            user_expenses = pd.Series(0.0, index=self.df.index)
            for i in range(len(who_df.columns)):
                mask = self.df[f"for_{i}"] == user
                user_expenses[mask] = self.df.loc[mask, f"amount_{i}"].astype(float)
            self.df[user] = user_expenses

    def export_processed_data(self, output_format: str = "excel") -> Path:
        """Export processed data to the specified format."""
        if self.df is None:
            raise ValueError("No data to export. Run process_data first.")

        self.df = self.df.dropna(subset=[self.config.user_to_analyse])
        result_df = self.df.loc[:, self.config.wanted_columns].copy()
        result_df = result_df.rename({self.config.user_to_analyse: "Amount"}, axis=1)

        base_name = Path(self.config.filename_to_process).stem
        if output_format == "excel":
            output_path = self.config.workdir / f"{base_name}_processed.xlsx"
            result_df.to_excel(output_path)
        elif output_format == "csv":
            output_path = self.config.workdir / f"{base_name}_processed.csv"
            result_df.to_csv(output_path)
        else:
            raise ValueError(f"Unsupported output format: {output_format}")
        
        return output_path

    def process_data(self) -> None:
        """Process the data end-to-end."""
        self.read_raw_csv()
        self.calc_user_expenses() 
