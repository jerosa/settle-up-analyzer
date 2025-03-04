from datetime import datetime

import dash
import dash_bootstrap_components as dbc
import plotly.express as px
from dash import Input, Output, callback, dcc, html

from analyze import Analyzer
from pages.utils import generate_year_dropdown

dash.register_page(__name__, path="/")


analyzer = Analyzer()
_, df_expenses, _ = analyzer.summary()


summary = analyzer.df_summary.reset_index().loc[
    :, ["Ingress", "Expenses", "Savings", "Year"]
]

years = summary.Year.unique().tolist()
year = datetime.now().year

fig_year = px.bar(
    summary, x="Year", y=summary.columns, barmode="group", title="Total summary by year"
)
fig_year.update_layout(yaxis_title="€")
fig_year.update_xaxes(dtick="M1", tickformat="%Y")


layout = dbc.Container(
    [
        html.H1(children="Summary"),
        html.Hr(),
        dcc.Graph(figure=fig_year),
        html.H2(children="Monthly"),
        html.Hr(),
        generate_year_dropdown(years, year),
        dcc.Graph(id="fig_month_summary"),
        dcc.Graph(id="fig_cat_summary"),
    ]
)


@callback(
    Output("fig_month_summary", "figure"),
    Input("year-filter", "value"),
)
def month_summary_filtered(year):
    month_summary = analyzer.month_summary(year)

    fig_month = px.bar(
        month_summary,
        title=f"{year} Monthly summary",
    )
    fig_month.update_layout(yaxis_title="€")
    return fig_month


@callback(
    Output("fig_cat_summary", "figure"),
    Input("year-filter", "value"),
)
def month_category_summary(year):
    df_filtered = df_expenses.loc[df_expenses.Year == year]

    fig_month = px.pie(
        df_filtered,
        title=f"{year} Categories expenses",
        values="Amount",
        names="Category",
        height=800,
    )
    return fig_month
