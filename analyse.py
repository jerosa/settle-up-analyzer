import os

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from pandas import DataFrame

from config import logger, settings

sns.set_style("whitegrid")


def get_plot_filename(workdir: str, filename: str):
    return os.path.join(workdir, filename)


class Analyser:
    def __init__(self) -> None:
        self.workdir = settings["workdir"]
        excel_name = settings["expenses_excel_filename"]

        filepath = os.path.join(self.workdir, excel_name)
        logger.info("Reading excel")
        self.df: DataFrame = pd.read_excel(filepath)

        logger.info("Total expenses %s", self.df["Amount"].sum())

    def plot_total_month(self):
        logger.info("Starting total expenses by month")
        sns.barplot(
            x="Month",
            y="Amount",
            data=self.df,
            estimator=sum,
            ci=None,
        )
        plt.title(f"Gastos por mes", fontsize=14)
        plt.savefig(get_plot_filename(self.workdir, "Montly Expenses"))
        plt.close()

    def plot_by_category(self):
        logger.info("Starting plots by category")
        excluded_cols = settings["category_filters"]
        for idx, exc_col in enumerate(excluded_cols):
            cat_df = self.df.loc[~self.df["Category"].isin(exc_col)]
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
            g.fig.suptitle(f"Gastos por categorias", fontsize=20)
            plt.savefig(
                get_plot_filename(self.workdir, f"Expenses by Category - {idx}")
            )
            plt.close()

    def plot_monthly(self):
        logger.info("Starting monthly plots")
        workdir = os.path.join(self.workdir, "plots")

        for month in self.df["Month"].unique().tolist():
            logger.info(f"Processing month {month}")
            df_month = self.df.loc[self.df["Month"] == month]
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
            g.fig.suptitle(f"Expenses 2021-{month}")
            g.ax.tick_params(axis="x", labelrotation=45)
            plt.savefig(get_plot_filename(workdir, f"{month:02d}_expense"))
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
            plt.title(f"Gastos por categorias - Mes {month}", fontsize=14)
            plt.legend(df_j)
            pie.savefig(get_plot_filename(workdir, f"{month:02d}_by_category"))
            plt.close()


if __name__ == "__main__":
    analyser = Analyser()
    analyser.plot_total_month()
    analyser.plot_by_category()
    analyser.plot_monthly()
