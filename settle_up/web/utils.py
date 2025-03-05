"""Shared web components and utilities."""
from typing import List

from dash import dcc, html


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
            html.Label("Select Year:", htmlFor="year-filter"),
            dcc.Dropdown(
                id="year-filter",
                options=[{"label": str(year), "value": year} for year in years],
                value=default_year,
                clearable=False,
                style={"width": "200px"},
            ),
        ],
        style={"margin": "10px 0"},
    )


# Common figure settings
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
