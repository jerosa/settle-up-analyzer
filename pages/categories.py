from datetime import datetime

import dash
import dash_bootstrap_components as dbc
import plotly.express as px
from dash import Input, Output, callback, dcc

from analyze import Analyzer

dash.register_page(__name__)


print("CATEGORIES")
_, df_expenses, _ = Analyzer().summary()


def get_categories(df):
    categories = df.loc[:, ["Category", "Amount"]].groupby("Category").sum()
    return (
        categories.sort_values(["Amount"], ascending=False)
        .reset_index()["Category"]
        .tolist()
    )


_categories = get_categories(df_expenses)
_years = df_expenses.Year.unique().tolist()
_current_year = datetime.now().year


layout = dbc.Container(
    children=[
        dbc.Tabs(
            [
                dbc.Tab(
                    label="Total",
                    tab_id="total",
                    children=[
                        dcc.Dropdown(
                            id="cat-filter",
                            options=[
                                {"label": cat, "value": cat} for cat in _categories
                            ],
                            placeholder="Select a Category",
                            multi=True,
                            value=_categories,
                        ),
                    ],
                ),
                dbc.Tab(
                    label="By year",
                    tab_id="year",
                    children=[
                        dcc.Dropdown(
                            id="year-filter",
                            options=[{"label": year, "value": year} for year in _years],
                            placeholder="Select a Year",
                            multi=False,
                            clearable=False,
                            value=_current_year,
                            style={"width": "70px"},
                            # className="xs-3",
                        ),
                    ],
                ),
            ],
            id="categories-tabs",
            active_tab="year",
            persistence=True,
        ),
        dcc.Graph(id="fig-container"),
    ]
)


@callback(
    Output("fig-container", "figure"),
    [
        Input("categories-tabs", "active_tab"),
        Input("cat-filter", "value"),
        Input("year-filter", "value"),
    ],
)
def filter_category(active_tab, categories, year):
    if active_tab == "total":
        df_filtered = df_expenses[df_expenses["Category"].isin(categories)]
        fig = px.histogram(
            df_filtered,
            x="Year",
            y="Amount",
            color="Year",
            facet_col="Category",
            facet_col_wrap=4,
            height=800,
            category_orders={"Category": (categories)},
        )
        return fig
    else:
        df_filtered = df_expenses.loc[df_expenses.Year == year]
        fig = px.histogram(
            df_filtered,
            x="Category",
            y="Amount",
            facet_col="Month",
            facet_col_wrap=3,
            height=800,
            color="Category",
            category_orders={"Category": _categories},
        )
        return fig
