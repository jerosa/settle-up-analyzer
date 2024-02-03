import os

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from pandas import DataFrame
from datetime import datetime
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

        df.loc[:, "Year"] = df.index.year
        df.loc[:, "Month"] = df.index.month

        return df

    def plot_total_expenses(self, df: DataFrame):
        logger.info("Starting total expenses")
        g = sns.catplot(
            x="Year",
            y="Amount",
            col="Category",
            data=df,
            estimator=sum,
            col_wrap=4,
            errorbar=None,
            kind="bar",
        )
        g.fig.subplots_adjust(top=0.92)
        g.fig.suptitle(f"Total Expenses by Category", fontsize=20)
        plt.savefig(get_plot_filename(self.plotdir, f"Total Expenses by Category"))
        plt.close()

    def plot_monthly_balance(self, df: DataFrame, year: int):
        logger.info("Starting total expenses/ingress by month")
        sns.barplot(
            x="Month",
            y="Amount",
            hue="Type",
            data=df,
            estimator=sum,
            errorbar=None,
        )
        plt.title(f"Monthly Balance - {year}", fontsize=14)
        plt.savefig(get_plot_filename(self.plotdir, f"{year}_Monthly Balance"))
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
                errorbar=None,
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
                errorbar=None,
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

    def summary(self):
        logger.debug("SUMMARY STARTING")
        df = self.read_excel()
        df_expenses = df.loc[df["Type"] == "Expense"]
        df_ingress = df.loc[df["Type"] == "Ingress"]

        expenses_year = df_expenses.groupby("Year")["Amount"].sum()
        ingress_year = df_ingress.groupby("Year")["Amount"].sum()
        summary = pd.concat(
            [expenses_year, ingress_year], axis=1, keys=["Expenses", "Ingress"]
        )
        summary.fillna(0, inplace=True)
        summary["Savings"] = summary["Ingress"] - summary["Expenses"]
        summary["Savings %"] = (
            (summary["Ingress"] - summary["Expenses"]) / summary["Ingress"] * 100
        )
        self.df_summary = summary.round(2)
        logger.debug("Total balance \n%s", summary)
        return df, df_expenses, df_ingress

    def month_summary(self):
        df = self.read_excel()
        df_ingress = df.loc[df["Type"] == "Ingress"]
        per = df_ingress.index.to_period("M")
        ingress_year_month = df_ingress.groupby(per)["Amount"].sum()

        df_expenses = df.loc[df["Type"] == "Expense"]
        per = df_expenses.index.to_period("M")
        expenses_year_month = df_expenses.groupby(per)["Amount"].sum()
        summary = pd.concat(
            [expenses_year_month, ingress_year_month],
            axis=1,
            keys=["Expenses", "Ingress"],
        )
        summary.fillna(0, inplace=True)
        summary["Savings"] = summary["Ingress"] - summary["Expenses"]
        summary.index = summary.index.to_timestamp()
        return summary

    def start(self):
        logger.info("Starting analyser")

        df, df_expenses, df_ingress = self.summary()

        self.plot_total_expenses(df_expenses)
        for year in df_expenses.loc[:, "Year"].unique().tolist():
            if year != datetime.now().year:
                continue
            logger.info(f"Analyzing {year}")
            year_expenses_df = df_expenses.loc[df_expenses["Year"] == year]
            year_df = df.loc[df["Year"] == year]
            self.plot_monthly_balance(year_df, year)
            self.plot_by_category(year_expenses_df, year)
            self.plot_monthly(year_expenses_df, year)


if __name__ == "__main__":
    analyzer = Analyzer()
    analyzer.start()
