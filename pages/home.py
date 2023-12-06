import dash
import dash_bootstrap_components as dbc
import plotly.express as px
from dash import dcc, html

from analyze import Analyzer

dash.register_page(__name__, path="/")


analyzer = Analyzer()
analyzer.summary()

summary = analyzer.df_summary.reset_index().loc[
    :, ["Ingress", "Expenses", "Savings", "Year"]
]

fig_year = px.bar(
    summary, x="Year", y=summary.columns, barmode="group", title="Total summary by year"
)
fig_year.update_layout(yaxis_title="€")
fig_year.update_xaxes(dtick="M1", tickformat="%Y")

month_summary = analyzer.month_summary()

halflife = 2
fig_month = px.scatter(
    month_summary,
    trendline="ewm",
    trendline_options=dict(halflife=halflife),
    title=f"Monthly Exponentially-weighted moving average (halflife of {halflife} points)",
)
fig_month.update_layout(yaxis_title="€")

# fig_month.data = [t for t in fig_month.data if t.mode == "lines"]
# fig_month.update_traces(showlegend=True)  # trendlines have showlegend=False by default

layout = dbc.Container(
    [
        html.H1(children="Summary"),
        html.Hr(),
        dcc.Graph(figure=fig_year),
        dcc.Graph(figure=fig_month),
    ]
)
