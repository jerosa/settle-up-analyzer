"""Shared web components and utilities."""
from typing import List

from dash import dcc, html
import dash_bootstrap_components as dbc


def generate_year_dropdown(years: List[int], default_year: int) -> html.Div:
    """Generate a year filter dropdown component.
    
    Args:
        years: List of available years
        default_year: Default year to select
        
    Returns:
        Dash component containing the year dropdown
    """
    return html.Div(
        [
            html.Label("Select Year:", htmlFor="year-filter", className="form-label"),
            dcc.Dropdown(
                id="year-filter",
                options=[{"label": str(year), "value": year} for year in years],
                value=default_year,
                clearable=False,
                style={"width": "200px"},
            ),
        ],
        className="year-dropdown-container",
    )

def generate_alert_layout(e: Exception):
    return dbc.Alert(
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


# Common figure settings
FIGURE_CONFIG = {
    "scrollZoom": False,
    "displayModeBar": False,
}

LAYOUT_TEMPLATE = {
    "margin": dict(l=60, r=40, t=60, b=50),
    "paper_bgcolor": "rgba(0,0,0,0)",
    "plot_bgcolor": "rgba(0,0,0,0)",
    "hovermode": "closest",
    "font": dict(family="Arial, sans-serif", size=12),
    "title_font": dict(family="Arial, sans-serif", size=16, color="#495057"),
    "legend_title_font": dict(family="Arial, sans-serif", size=12),
    "xaxis": dict(
        gridcolor="rgba(0,0,0,0.05)",
        zerolinecolor="rgba(0,0,0,0.1)",
    ),
    "yaxis": dict(
        gridcolor="rgba(0,0,0,0.05)",
        zerolinecolor="rgba(0,0,0,0.1)",
    ),
} 
