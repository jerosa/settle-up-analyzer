import os

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

from config import settings

headers = [
    "Who paid",
    "Amount",
    "Currency",
    "For whom",
    "Split amounts",
    "Purpose",
    "Category",
    "Date & time",
    "Exchange rate",
    "Converted amount",
    "Type",
    "Receipt",
]
dtypes = {
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
    "Receipt": "str",
}
DATE_COL = "Date & time"
FOR_WHOM_COL = "For whom"
SPLIT_COL = "Split amounts"


USER = settings["user_to_analyse"]
WANTED_COLUMNS = ["Purpose", "Category", "Month", USER]


class SettleUpProcessor:
    def __init__(self):
        self.workdir = settings["workdir"]
        self.users = np.empty(0, dtype=object)

    def read_raw_csv(self):
        filepath = os.path.join(self.workdir, settings["filename_to_process"])

        self.df = pd.read_csv(
            filepath,
            header=0,
            encoding="utf8",
            sep=",",
            usecols=headers,
            names=headers,
            dtype=dtypes,
            index_col=DATE_COL,
            parse_dates=[DATE_COL],
        )
        # Remove transfers
        self.df = self.df.loc[self.df["Type"] == "expense"]
        self.df.loc[:, "Month"] = self.df.index.month

    def set_users(self, who_df):
        """Get unique users in the expenses"""
        for col in who_df.columns:
            self.users = np.append(self.users, who_df[col].unique())
        self.users = set(self.users)
        if None in self.users:
            self.users.remove(None)
        self.users = list(self.users)

    def calc_user_expenses(self):
        who_df = self.df[FOR_WHOM_COL].str.split(";", expand=True)
        who_df.columns = ["for_" + str(i) for i in range(0, len(who_df.columns))]

        ammount_df = self.df[SPLIT_COL].str.split(";", expand=True)
        ammount_df.columns = [
            "amount_" + str(i) for i in range(0, len(ammount_df.columns))
        ]

        assert len(who_df.columns) == len(ammount_df.columns)
        self.set_users(who_df)

        self.df = self.df.join(who_df).join(ammount_df)

        # calculate expenses by user (order)
        for user in self.users:
            for i in range(0, len(self.users)):
                self.df.loc[self.df[f"for_{i}"] == user, user] = self.df.loc[
                    self.df[f"for_{i}"] == user, f"amount_{i}"
                ]
            self.df = self.df.astype({user: float})

    def export_processed_csv(self):
        wanted_filename = (
            settings["filename_to_process"].split(".", maxsplit=1)[0]
            + "_processed.xlsx"
        )

        self.df = self.df.dropna(subset=[USER])
        self.df = self.df.loc[:, WANTED_COLUMNS]
        self.df = self.df.rename({USER: "Amount"}, axis=1)

        filepath = os.path.join(self.workdir, wanted_filename)
        self.df.to_excel(filepath)

    def total_expenses(self):
        print(self.df.loc[:, self.users].sum().head(20))
        df_sum = self.df.groupby([pd.Grouper(freq="M")])[self.users].sum()
        print(df_sum.head(100))

        _, ax = plt.subplots(figsize=(10, 10))
        ax = sns.scatterplot(data=df_sum)
        ax.set_xlabel("Month")
        ax.set_ylabel("€")
        ax.set_title("Monthly total expenses")
        ax.tick_params(axis="x", labelrotation=45)
        plt.savefig(f"{self.workdir}/total_expenses")
        plt.close()

    def generate_users_plots(self):
        self.total_expenses()


if __name__ == "__main__":
    processor = SettleUpProcessor()
    processor.read_raw_csv()
    processor.calc_user_expenses()
    processor.generate_users_plots()
    processor.export_processed_csv()
