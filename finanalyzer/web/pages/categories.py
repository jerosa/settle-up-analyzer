"""
Categories page for expense analysis by category.

This module provides visualization and analysis of expenses grouped by categories.
It supports two main views:
1. Total view: Shows expenses by category across all years
2. Year view: Shows monthly expenses by category for a specific year
"""

from datetime import datetime
from functools import lru_cache
from typing import Dict, List, Tuple

import dash
import dash_bootstrap_components as dbc
import plotly.express as px
from dash import Input, Output, callback, dcc, html
import pandas as pd

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
    path="/categories",
    name="Categories",
    title="FinAnalyzer - Categories",
    description="Analyze expenses by category across years and months.",
)

# Initialize analyzer
analyzer = Analyzer(config["workdir"], config["excel_filename"])

try:
    # Pre-aggregate data for better performance
    df_by_category_year = analyzer.data.df.pivot_table(
        index="Category",
        columns="Year",
        values="Amount",
        aggfunc="sum",
        fill_value=0
    ).round(2)

    # Pre-aggregate monthly data by year
    df_by_category_month = {
        year: analyzer.data.df[analyzer.data.df.Year == year].pivot_table(
            index="Category",
            columns="Month",
            values="Amount",
            aggfunc="sum",
            fill_value=0
        ).round(2)
        for year in analyzer.data.df.Year.unique()
    }

    def get_categories(df: pd.DataFrame) -> List[str]:
        """Get sorted list of categories by total amount.
        
        Args:
            df: DataFrame with categories as index and amounts in columns
            
        Returns:
            List of categories sorted by total amount
        """
        return (
            df.sum(axis=1)
            .sort_values(ascending=False)
            .index.tolist()
        )

    def create_base_figure(data: pd.DataFrame, **plot_kwargs) -> dict:
        """Create a standardized bar plot with consistent styling.
        
        Args:
            data: DataFrame to plot
            **plot_kwargs: Additional arguments for px.bar
            
        Returns:
            Styled Plotly figure object
        """
        fig = px.bar(data, height=800, template="plotly_white", **plot_kwargs)
        
        # Apply consistent styling
        fig.for_each_yaxis(lambda y: y.update(title=""))
        fig.add_annotation(
            x=-0.05,
            y=0.5,
            text="€",
            showarrow=False,
            textangle=-90,
            xref="paper",
            yref="paper",
        )
        fig.update_layout(**LAYOUT_TEMPLATE)
        return fig

    @lru_cache(maxsize=32)
    def create_total_figure(categories_tuple: Tuple[str, ...]) -> dict:
        """Create figure showing expenses by category across years.
        
        Args:
            categories_tuple: Tuple of category names to include in visualization
            
        Returns:
            Plotly figure object showing the expenses breakdown
        """
        categories = list(categories_tuple)
        df_selected = df_by_category_year.loc[categories]
        
        df_plot = df_selected.reset_index().melt(
            id_vars=["Category"],
            var_name="Year",
            value_name="Amount"
        )
        
        return create_base_figure(
            df_plot,
            x="Year",
            y="Amount",
            color="Year",
            facet_col="Category",
            facet_col_wrap=4,
            category_orders={"Category": categories}
        )

    @lru_cache(maxsize=32)
    def create_year_figure(year: int) -> dict:
        """Create figure showing monthly expenses by category for a specific year.
        
        Args:
            year: The year to visualize
            
        Returns:
            Plotly figure object showing the monthly breakdown
        """
        df_selected = df_by_category_month[year]
        
        df_plot = df_selected.reset_index().melt(
            id_vars=["Category"],
            var_name="Month",
            value_name="Amount"
        )
        
        return create_base_figure(
            df_plot,
            x="Category",
            y="Amount",
            facet_col="Month",
            facet_col_wrap=3,
            color="Category",
            category_orders={"Category": get_categories(df_by_category_year)}
        )

    # Initialize categories and years
    categories = get_categories(df_by_category_year)
    years = sorted(analyzer.data.df.Year.unique().tolist())
    current_year = datetime.now().year
    if current_year not in years:
        current_year = max(years)

    # Define the page layout
    layout = html.Div([
        dbc.Row([
            dbc.Col([
                html.H1("Categories Analysis", className="section-title mb-0"),
            ], className="content-section py-3"),
        ], className="mb-3"),
        
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        dbc.Tabs(
                            [
                                dbc.Tab(
                                    label="Total",
                                    tab_id="total",
                                    children=[
                                        html.Div([
                                            html.Label(
                                                "Select Categories to Display:",
                                                htmlFor="cat-filter",
                                                className="form-label"
                                            ),
                                            dcc.Dropdown(
                                                id="cat-filter",
                                                options=[
                                                    {"label": cat, "value": cat} 
                                                    for cat in categories
                                                ],
                                                placeholder="Select Categories",
                                                multi=True,
                                                value=categories[:12],  # Default to top 12
                                                className="mb-3",
                                            ),
                                        ], className="year-dropdown-container"),
                                    ],
                                ),
                                dbc.Tab(
                                    label="By Year",
                                    tab_id="year",
                                    children=generate_year_dropdown(years, current_year),
                                ),
                            ],
                            id="categories-tabs",
                            active_tab="year",
                            persistence=True,
                            className="nav-tabs-custom",
                        ),
                        html.Div([
                            dcc.Graph(
                                id="fig-container",
                                config=FIGURE_CONFIG,
                                className="mt-3",
                            ),
                        ], className="graph-content"),
                    ]),
                ], className="content-section"),
            ]),
        ]),
    ])

    @callback(
        Output("fig-container", "figure"),
        [
            Input("categories-tabs", "active_tab"),
            Input("cat-filter", "value"),
            Input("year-filter", "value"),
        ],
    )
    def update_figure(active_tab: str, categories: List[str], year: int) -> dict:
        """Update the figure based on user selections.
        
        Args:
            active_tab: Currently active tab ('total' or 'year')
            categories: List of selected categories
            year: Selected year for year view
            
        Returns:
            Updated Plotly figure
        """
        if active_tab == "total":
            return create_total_figure(tuple(sorted(categories)))
        return create_year_figure(year)

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
