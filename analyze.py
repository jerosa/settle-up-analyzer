import os

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from pandas import DataFrame

from config import logger, settings

sns.set_style("whitegrid")


def get_plot_filename(workdir: str, filename: str):
    return os.path.join(workdir, filename)


class Analyzer:
    def __init__(self) -> None:
        self.workdir = settings["workdir"]
        self.plotdir = os.path.join(self.workdir, "plots")

    def read_excel(self):
        excel_name = settings["expenses_excel_filename"]

        filepath = os.path.join(self.workdir, excel_name)
        logger.debug(f"Reading excel {filepath}")
        df: DataFrame = pd.read_excel(
            filepath,
            converters={"Date & time": pd.to_datetime},
            index_col="Date & time",
        )

        # df.loc[:, "YearMonth"] = df.index.to_period("M")
        df.loc[:, "Year"] = df.index.year
        df.loc[:, "Month"] = df.index.month

        return df

    def plot_total_month(self, df: DataFrame, year: int):
        logger.info("Starting total expenses by month")
        sns.barplot(
            x="Month",
            y="Amount",
            data=df,
            estimator=sum,
            ci=None,
        )
        plt.title(f"Monthly Expenses - {year}", fontsize=14)
        plt.savefig(get_plot_filename(self.plotdir, f"{year}_Monthly Expenses"))
        plt.close()

    def plot_by_category(self, df: DataFrame, year: int):
        logger.info(f"{year} - Starting plots by category")
        excluded_cols = settings["category_filters"]
        for idx, exc_col in enumerate(excluded_cols):
            cat_df = df.loc[~df["Category"].isin(exc_col)]
            g = sns.catplot(
                x="Month",
                y="Amount",
                col="Category",
                data=cat_df,
                kind="bar",
                col_wrap=4,
                estimator=sum,
                ci=None,
            )
            g.fig.subplots_adjust(top=0.92)
            g.fig.suptitle(f"Expenses by category - {year}", fontsize=20)
            plt.savefig(
                get_plot_filename(
                    self.plotdir, f"{year}_Expenses by Category and Month - {idx}"
                )
            )
            plt.close()

    def plot_monthly(self, df: DataFrame, year: int):
        logger.info(f"{year} - Starting monthly plots")

        year_dir = os.path.join(self.plotdir, str(year))
        os.makedirs(year_dir, exist_ok=True)
        for month in df["Month"].unique().tolist():
            logger.info(f"Processing month {month}")
            df_month = df.loc[df["Month"] == month]
            g = sns.catplot(
                data=df_month,
                x="Category",
                y="Amount",
                kind="bar",
                estimator=sum,
                ci=None,
                height=8,
                aspect=1,
            )
            g.fig.suptitle(f"Expenses {year}-{month}")
            g.ax.tick_params(axis="x", labelrotation=45)
            plt.savefig(get_plot_filename(year_dir, f"{year}_{month:02d}_Expenses"))
            plt.close()

            df_j = (
                df_month.groupby(["Category"])["Amount"]
                .sum()
                .round(2)
                .sort_values(ascending=False)
            )
            pie, _ = plt.subplots(figsize=[10, 6])
            labels = df_j.keys()
            _, l, p = plt.pie(
                x=df_j,
                autopct="%.1f%%",
                explode=[0.01] * len(labels),
                labels=labels,
                pctdistance=0.65,
            )
            [t.set_rotation(0) for t in p]
            [t.set_fontsize(12) for t in p]
            [t.set_fontsize(12) for t in l]
            plt.axis("equal")
            plt.title(f"Expenses by category {year}-{month}", fontsize=14)
            plt.legend(df_j)
            pie.savefig(
                get_plot_filename(year_dir, f"{year}_{month:02d}_Expenses_by_category")
            )
            plt.close()

    def start(self):
        logger.info("Starting analyser")
        df = self.read_excel()
        logger.info("Total expenses %s", df["Amount"].sum())
        for year in df.loc[:, "Year"].unique().tolist():
            logger.info(f"Analyzing {year}")
            year_df = df.loc[df["Year"] == year]
            self.plot_total_month(year_df, year)
            self.plot_by_category(year_df, year)
            self.plot_monthly(year_df, year)


if __name__ == "__main__":
    analyzer = Analyzer()
    analyzer.start()
