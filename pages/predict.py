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


layout = dbc.Container(
    [
        html.H1(children="Predict"),
        html.Hr(),
        html.P(f"Change 'Nomina' Ingress to a fixed value:"),
        dbc.Input(id="input-number", type="number", min=0, value=2400, step=100),
        dcc.Graph(id="pred-line"),
        dcc.Graph(id="pred-bar"),
    ]
)


def calc_preds(df, value):
    df_ingress = df.loc[df["Type"] == "Ingress"]
    ingress_per = df_ingress.index.to_period("M")
    ingress_year_month = df_ingress.groupby(ingress_per)["Amount"].sum()

    df_expenses = df.loc[df["Type"] == "Expense"]
    expenses_per = df_expenses.index.to_period("M")
    expenses_year_month = df_expenses.groupby(expenses_per)["Amount"].sum()

    # Change ingress to a fixed value
    df_ingress_predict = df_ingress
    df_ingress_predict.loc[df_ingress_predict.Category == "Nomina"] = value
    ingress_predict_year_month = df_ingress_predict.groupby(ingress_per)["Amount"].sum()

    summary = pd.concat(
        [expenses_year_month, ingress_predict_year_month, ingress_year_month],
        axis=1,
        keys=["Expenses", "Ingress P", "Ingress"],
    )
    summary.fillna(0, inplace=True)
    summary["Savings"] = summary["Ingress"] - summary["Expenses"]
    summary["Savings Predict"] = summary["Ingress P"] - summary["Expenses"]
    return summary


@callback(
    [Output("pred-line", "figure"), Output("pred-bar", "figure")],
    [
        Input("input-number", "value"),
    ],
)
def generate_pred(value):
    summary = calc_preds(df, value)
    summary = summary.loc[:, ["Ingress", "Savings", "Savings Predict"]]
    summary_year = summary.groupby(summary.index.year).sum()

    summary.index = summary.index.astype(str) # to plot it

    fig = px.line(
        summary,
        labels={"value": "€"},
        markers=True
    )
    saving_limit = np.full(len(summary.index), 500, dtype=int)
    fig.add_trace(go.Scatter(x=summary.index, y=saving_limit, name="500", line={"dash": "dash", "color": "orange"}))
    saving_limit = np.full(len(summary.index), 0, dtype=int)
    fig.add_trace(go.Scatter(x=summary.index, y=saving_limit, name="0", line={"dash": "dash", "color": "red"}))

    fig_bar = px.bar(
        summary_year,
        barmode="group",
        labels={"value": "€"}
    )
    return fig, fig_bar
