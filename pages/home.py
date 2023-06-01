import dash
import dash_bootstrap_components as dbc
import plotly.express as px
from dash import dcc, html

from analyze import Analyzer

dash.register_page(__name__, path="/")


analyzer = Analyzer()
analyzer.summary()

df_test = analyzer.df_summary.reset_index().loc[
    :, ["Ingress", "Expenses", "Savings", "Year"]
]

fig = px.bar(df_test, x="Year", y=df_test.columns, barmode="group")
fig.update_layout(yaxis_title="€")
fig.update_xaxes(dtick="M1", tickformat="%Y")


layout = dbc.Container(
    [
        html.H1(children="Summary"),
        html.Hr(),
        dcc.Graph(figure=fig),
    ]
)
