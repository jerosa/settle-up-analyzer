import dash
import dash_bootstrap_components as dbc
import plotly.express as px
from dash import dcc, html, callback, dcc, Input, Output
import pandas as pd

import numpy as np

import plotly.graph_objects as go

from analyze import Analyzer

dash.register_page(__name__)

analyzer = Analyzer()
df = analyzer.read_excel()

alquiler = df.loc[df.Category == "Alquiler"]["Amount"].mean().round(2)

layout = dbc.Container(
    [
        html.H1(children="Predict"),
        html.Hr(),
        html.P(f"Current avg alquiler {alquiler}"),
        dbc.Input(id="test", type="number", min=0, value=1000, step=100),
        dcc.Graph(id="pred-line"),
        dcc.Graph(id="pred-bar"),
    ]
)


def calc_preds(df, value):
    df_ingress = df.loc[df["Type"] == "Ingress"]
    per = df_ingress.index.to_period("M").astype(str)
    ingress_year_month = df_ingress.groupby(per)["Amount"].sum()

    df_expenses = df.loc[df["Type"] == "Expense"]
    per = df_expenses.index.to_period("M").astype(str)
    expenses_year_month = df_expenses.groupby(per)["Amount"].sum()
    # print(value)
    # predict
    df_expenses_predict = df_expenses
    # print(df_expenses_predict)
    df_expenses_predict.loc[df_expenses_predict.Category == "Alquiler"] = value
    # print(df_expenses_predict)
    # print(df_expenses_predict.loc[df_expenses_predict.Category == "Alquiler"])
    expenses_predict_year_month = df_expenses_predict.groupby(per)["Amount"].sum()

    summary = pd.concat(
        [expenses_year_month, expenses_predict_year_month, ingress_year_month],
        axis=1,
        keys=["Expenses", "Expenses P", "Ingress"],
    )
    # print("AAAAAA")
    summary.fillna(0, inplace=True)
    summary["Savings"] = summary["Ingress"] - summary["Expenses"]
    summary["Savings Predict"] = summary["Ingress"] - summary["Expenses P"]
    return summary


@callback(
    [Output("pred-line", "figure"), Output("pred-bar", "figure")],
    [
        Input("test", "value"),
    ],
)
def generate_pred(value):
    summary = calc_preds(df, value)

    fig = px.scatter(
        summary,
    )
    saving_limit = np.full(len(summary.index), 500, dtype=int)
    fig.add_trace(go.Scatter(x=summary.index, y=saving_limit, name="500"))
    saving_limit = np.full(len(summary.index), 0, dtype=int)
    fig.add_trace(go.Scatter(x=summary.index, y=saving_limit, name="0"))
    fig_bar = px.bar(
        summary,
        # x=summary["Date & time"],
        # y=summary["Amount"],
        # color=summary.Type,
        barmode="group",
    )
    return fig, fig_bar
