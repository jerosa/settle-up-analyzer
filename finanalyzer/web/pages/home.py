"""Home page showing summary statistics and visualizations."""
from datetime import datetime
from typing import Dict

import dash
import dash_bootstrap_components as dbc
import plotly.express as px
from dash import Input, Output, callback, dcc, html

from finanalyzer.core.analyzer import Analyzer
from finanalyzer.core.config import config
from finanalyzer.web.utils import (
    generate_year_dropdown,
    FIGURE_CONFIG,
    LAYOUT_TEMPLATE,
)

# Register the page
dash.register_page(
    __name__,
    path="/",
    name="Home",
    title="FinAnalyzer - Home",
    description="Summary statistics and visualizations for your FinAnalyzer expenses.",
)

# Initialize analyzer
analyzer = Analyzer(config["workdir"], config["excel_filename"])

try:
    # Pre-aggregate yearly summary data
    df_yearly_summary = (
        analyzer.data.df_summary.reset_index()
        .loc[:, ["Ingress", "Expenses", "Savings", "Year"]]
    )

    # Get available years and current year
    years = sorted(df_yearly_summary.Year.unique().tolist())
    current_year = datetime.now().year
    if current_year not in years:
        current_year = max(years)

    # Pre-aggregate monthly and category data by year
    df_monthly_summary = {
        year: analyzer.month_summary(year)
        for year in years
    }
    df_category_summary = {
        year: analyzer.get_category_summary(year)
        for year in years
    }

    def create_yearly_summary_figure() -> dict:
        """Create figure showing yearly summary of finances."""
        fig = px.bar(
            df_yearly_summary,
            x="Year",
            y=["Ingress", "Expenses", "Savings"],
            barmode="group",
            title="Total summary by year",
            template="plotly_white",
        )
        fig.update_layout(
            yaxis_title="€",
            **LAYOUT_TEMPLATE
        )
        fig.update_xaxes(dtick="M1", tickformat="%Y")
        return fig

    def create_monthly_summary_figure(year: int) -> dict:
        """Create figure showing monthly summary for a specific year."""
        fig = px.bar(
            df_monthly_summary[year],
            title=f"{year} Monthly summary",
            template="plotly_white",
        )
        fig.update_layout(
            yaxis_title="€",
            showlegend=True,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            **LAYOUT_TEMPLATE
        )
        return fig

    def create_category_summary_figure(year: int) -> dict:
        """Create pie chart showing expense distribution by category."""
        df = df_category_summary[year].reset_index()
        fig = px.pie(
            df,
            title=f"{year} Categories expenses",
            values="sum",
            names="Category",
            height=800,
            template="plotly_white",
        )
        fig.update_layout(
            showlegend=True,
            legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5),
            **LAYOUT_TEMPLATE
        )
        return fig

    # Pre-compute all figures
    fig_yearly_summary = create_yearly_summary_figure()
    fig_monthly_summary = {
        year: create_monthly_summary_figure(year)
        for year in years
    }
    fig_category_summary = {
        year: create_category_summary_figure(year)
        for year in years
    }

    # Define the page layout with data
    layout = html.Div([
        dbc.Row([
            dbc.Col([
                html.H1("Summary", className="section-title"),
                dcc.Graph(
                    figure=fig_yearly_summary,
                    config=FIGURE_CONFIG,
                    className="graph-container",
                ),
            ], className="content-section"),
        ], className="mb-4"),
        
        dbc.Row([
            dbc.Col([
                html.H2("Monthly Analysis", className="section-title"),
                html.Div([
                    html.Label("Select Year:", htmlFor="year-filter", className="form-label"),
                    dcc.Dropdown(
                        id="year-filter",
                        options=[{"label": str(year), "value": year} for year in years],
                        value=current_year,
                        clearable=False,
                        style={"width": "200px"},
                    ),
                ], className="year-dropdown-container"),
                dcc.Graph(
                    id="fig_month_summary",
                    config=FIGURE_CONFIG,
                    className="graph-container",
                ),
            ], className="content-section"),
        ], className="mb-4"),
        
        dbc.Row([
            dbc.Col([
                html.H2("Category Breakdown", className="section-title"),
                dcc.Graph(
                    id="fig_cat_summary",
                    config=FIGURE_CONFIG,
                    className="graph-container",
                ),
            ], className="content-section"),
        ]),
    ])

    @callback(
        Output("fig_month_summary", "figure"),
        Input("year-filter", "value"),
    )
    def update_monthly_summary(year: int) -> dict:
        """Update monthly summary figure based on selected year."""
        return fig_monthly_summary[year]

    @callback(
        Output("fig_cat_summary", "figure"),
        Input("year-filter", "value"),
    )
    def update_category_summary(year: int) -> dict:
        """Update category summary figure based on selected year."""
        return fig_category_summary[year]

except Exception as e:
    # Fallback layout if data loading fails
    layout = dbc.Alert(
        [
            html.H4("Data Loading Error", className="alert-heading"),
            html.P(f"Failed to load data: {str(e)}"),
            html.Hr(),
            html.P(
                "Please check your configuration and ensure the data files exist.",
                className="mb-0"
            ),
        ],
        color="danger",
        className="m-3",
    ) 
