"""
Home page showing summary statistics and visualizations.

This module provides an overview of expenses with three main visualizations:
1. Yearly summary showing ingress, expenses, and savings
2. Monthly summary for a selected year
3. Category breakdown for a selected year
"""

from datetime import datetime
from functools import lru_cache
from typing import Dict

import dash
import dash_bootstrap_components as dbc
import plotly.express as px
from dash import Input, Output, callback, dcc, html
import pandas as pd

from analyze import Analyzer
from pages.utils import generate_year_dropdown

dash.register_page(__name__, path="/")

# Initialize data
analyzer = Analyzer()
df_expenses = analyzer.data.df_expenses

# Pre-aggregate yearly summary data
df_yearly_summary = (
    analyzer.data.df_summary.reset_index()
    .loc[:, ["Ingress", "Expenses", "Savings", "Year"]]
)

# Pre-aggregate monthly data by year
df_monthly_summary = {
    year: analyzer.month_summary(year)
    for year in df_yearly_summary.Year.unique()
}

# Pre-aggregate category data by year
df_category_summary = {
    year: df_expenses[df_expenses.Year == year].groupby("Category")["Amount"].sum()
    for year in df_yearly_summary.Year.unique()
}

# Common figure settings for better performance
FIGURE_CONFIG = {
    "scrollZoom": False,
    "displayModeBar": False,
}

LAYOUT_TEMPLATE = {
    "margin": dict(l=50, r=30, t=50, b=30),
    "paper_bgcolor": "rgba(0,0,0,0)",
    "plot_bgcolor": "rgba(0,0,0,0)",
    "hovermode": "closest",
}

def create_yearly_summary_figure() -> dict:
    """Create figure showing yearly summary of finances.
    
    Returns:
        Plotly figure showing ingress, expenses and savings by year
    """
    fig = px.bar(
        df_yearly_summary,
        x="Year",
        y=["Ingress", "Expenses", "Savings"],
        barmode="group",
        title="Total summary by year"
    )
    fig.update_layout(
        yaxis_title="€",
        **LAYOUT_TEMPLATE
    )
    fig.update_xaxes(dtick="M1", tickformat="%Y")
    return fig

def create_monthly_summary_figure(year: int) -> dict:
    """Create figure showing monthly summary for a specific year.
    
    Args:
        year: The year to visualize
        
    Returns:
        Plotly figure showing monthly financial summary
    """
    fig = px.bar(
        df_monthly_summary[year],
        title=f"{year} Monthly summary",
    )
    fig.update_layout(
        yaxis_title="€",
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        **LAYOUT_TEMPLATE
    )
    return fig

def create_category_summary_figure(year: int) -> dict:
    """Create pie chart showing expense distribution by category.
    
    Args:
        year: The year to visualize
        
    Returns:
        Plotly figure showing category expense breakdown
    """
    df = df_category_summary[year].reset_index()
    fig = px.pie(
        df,
        title=f"{year} Categories expenses",
        values="Amount",
        names="Category",
        height=800,
    )
    fig.update_layout(
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5),
        **LAYOUT_TEMPLATE
    )
    return fig

# Initialize years and current year
years = sorted(df_yearly_summary.Year.unique().tolist())
current_year = datetime.now().year

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

# Define the page layout
layout = dbc.Container(
    [
        html.H1(children="Summary"),
        html.Hr(),
        dcc.Graph(
            figure=fig_yearly_summary,
            config=FIGURE_CONFIG
        ),
        html.H2(children="Monthly"),
        html.Hr(),
        generate_year_dropdown(years, current_year),
        dcc.Graph(
            id="fig_month_summary",
            config=FIGURE_CONFIG
        ),
        dcc.Graph(
            id="fig_cat_summary",
            config=FIGURE_CONFIG
        ),
    ]
)

@callback(
    Output("fig_month_summary", "figure"),
    Input("year-filter", "value"),
)
def update_monthly_summary(year: int) -> dict:
    """Update monthly summary figure based on selected year.
    
    Args:
        year: Selected year to display
        
    Returns:
        Updated monthly summary figure
    """
    return fig_monthly_summary[year]

@callback(
    Output("fig_cat_summary", "figure"),
    Input("year-filter", "value"),
)
def update_category_summary(year: int) -> dict:
    """Update category summary figure based on selected year.
    
    Args:
        year: Selected year to display
        
    Returns:
        Updated category summary figure
    """
    return fig_category_summary[year]
