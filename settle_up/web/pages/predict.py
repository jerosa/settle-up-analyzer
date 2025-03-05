"""
Prediction page for analyzing the impact of income changes.

This module provides interactive visualizations to explore how changes in 'Nomina' income
would affect monthly and yearly savings. It includes:
1. A line plot showing monthly trends with target thresholds
2. A bar plot showing yearly summaries
"""

from datetime import datetime
from typing import Dict, Tuple, Optional, List

import dash
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
from dash import dcc, html, callback, Input, Output, State
import pandas as pd
import numpy as np

from settle_up.core.analyzer import Analyzer
from settle_up.core.config import config
from settle_up.web.utils import (
    generate_year_dropdown,
    FIGURE_CONFIG,
    LAYOUT_TEMPLATE,
)

# Register the page
dash.register_page(
    __name__,
    path="/predict",
    name="Predict",
    title="Settle Up - Income Prediction",
    description="Analyze how changes in income would affect your savings.",
)

# Color scheme
COLORS = {
    "Ingress": "#2ecc71",
    "Savings": "#3498db",
    "Savings Predicted": "#e74c3c",
    "Target": "#f39c12",
    "Break Even": "#c0392b"
}

try:
    # Initialize analyzer
    analyzer = Analyzer(config["workdir"], config["excel_filename"])
    df_ingress = analyzer.data.df_ingress
    df_expenses = analyzer.data.df_expenses

    # Pre-aggregate monthly data
    expenses_per = df_expenses.index.to_period("M")
    expenses_monthly = df_expenses.groupby(expenses_per)["Amount"].sum()

    ingress_per = df_ingress.index.to_period("M")
    ingress_monthly = df_ingress.groupby(ingress_per)["Amount"].sum()

    # Pre-calculate base monthly Nomina amount
    nomina_data = df_ingress[df_ingress.Category == "Nomina"]
    nomina_monthly = nomina_data.groupby(nomina_data.index.to_period("M"))["Amount"].sum()
    # Use last 12 months for default Nomina calculation
    default_nomina = int(round(nomina_monthly.iloc[-12:].mean(), -2))  # Rounds to nearest 100

    def calculate_predictions(new_nomina_value: Optional[float]) -> pd.DataFrame:
        """Calculate predicted savings with new Nomina value.
        
        Args:
            new_nomina_value: New monthly Nomina amount
            
        Returns:
            DataFrame with original and predicted monthly savings
        """
        if not new_nomina_value:
            new_nomina_value = default_nomina
            
        # Calculate predicted ingress by adjusting Nomina
        adjustment = new_nomina_value - nomina_monthly.mean()
        ingress_predicted = ingress_monthly.copy()
        
        # Adjust each month's ingress by the difference in Nomina
        for month in nomina_monthly.index:
            if month in ingress_predicted.index:
                ingress_predicted[month] += adjustment
        
        # Combine all series into a DataFrame with consistent index
        all_months = sorted(set(expenses_monthly.index) | set(ingress_monthly.index))
        summary = pd.DataFrame(index=all_months)
        
        summary["Expenses"] = expenses_monthly
        summary["Ingress"] = ingress_monthly
        summary["Ingress Predicted"] = ingress_predicted
        
        # Fill any missing values with 0
        summary.fillna(0, inplace=True)
        
        summary["Savings"] = summary["Ingress"] - summary["Expenses"]
        summary["Savings Predicted"] = summary["Ingress Predicted"] - summary["Expenses"]
        
        return summary

    def create_prediction_figures(summary: pd.DataFrame) -> Tuple[dict, dict]:
        """Create line and bar figures for predictions.
        
        Args:
            summary: DataFrame with original and predicted values
            
        Returns:
            Tuple of (line_figure, bar_figure) showing predictions
        """
        # Prepare data for plotting
        plot_data = summary[["Ingress", "Savings", "Savings Predicted"]]
        yearly_summary = plot_data.groupby(plot_data.index.year).sum()
        
        # Convert Period index to string for plotting
        plot_data.index = plot_data.index.astype(str)
        
        # Create line plot
        line_fig = px.line(
            plot_data,
            labels={"value": "€", "index": "Month"},
            markers=True,
            title="Monthly Savings Trends",
            color_discrete_map=COLORS,
            template="plotly_white",
            height=400  # Reduced height for better grouping
        )
        
        # Add threshold lines
        months = plot_data.index
        line_fig.add_trace(
            go.Scatter(
                x=months,
                y=np.full(len(months), 500),
                name="Target Savings",
                line={"dash": "dash", "color": COLORS["Target"]},
                hovertemplate="Target: €500"
            )
        )
        line_fig.add_trace(
            go.Scatter(
                x=months,
                y=np.zeros(len(months)),
                name="Break Even",
                line={"dash": "dash", "color": COLORS["Break Even"]},
                hovertemplate="Break Even: €0"
            )
        )
        
        # Apply styling
        line_fig.update_layout(
            legend=dict(
                orientation="h",
                yanchor="top",
                y=-0.15,
                xanchor="center",
                x=0.5,
                bgcolor="rgba(255, 255, 255, 0.8)",
                bordercolor="rgba(0, 0, 0, 0.2)",
                borderwidth=1
            ),
            **LAYOUT_TEMPLATE
        )
        
        # Create bar plot
        bar_fig = px.bar(
            yearly_summary,
            barmode="group",
            labels={"value": "€", "index": "Year"},
            title="Yearly Summary Comparison",
            color_discrete_map=COLORS,
            template="plotly_white",
            height=300  # Reduced height for better grouping
        )
        bar_fig.update_layout(
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="top",
                y=-0.15,
                xanchor="center",
                x=0.5,
                bgcolor="rgba(255, 255, 255, 0.8)",
                bordercolor="rgba(0, 0, 0, 0.2)",
                borderwidth=1
            ),
            **LAYOUT_TEMPLATE
        )
        
        return line_fig, bar_fig

    def calculate_impact_summary(summary: pd.DataFrame) -> Dict[str, float]:
        """Calculate summary statistics of the prediction impact based on last year's data.
        
        This function analyzes only the most recent 12 months of data to provide
        more relevant predictions based on current spending patterns.
        
        Args:
            summary: DataFrame with prediction data
            
        Returns:
            Dictionary with impact metrics based on recent data
        """
        # Get the last 12 months of data
        last_12_months = summary.iloc[-12:]
        
        # Calculate current metrics
        current_savings = last_12_months["Savings"].sum()
        current_monthly_avg = last_12_months["Savings"].mean()
        
        # Calculate predicted metrics
        predicted_savings = last_12_months["Savings Predicted"].sum()
        predicted_monthly_avg = last_12_months["Savings Predicted"].mean()
        
        # Calculate differences
        monthly_difference = predicted_monthly_avg - current_monthly_avg
        yearly_difference = predicted_savings - current_savings
        
        return {
            # Monthly metrics (based on actual monthly average)
            "current_monthly": current_monthly_avg,
            "predicted_monthly": predicted_monthly_avg,
            "difference_monthly": monthly_difference,
            
            # Yearly metrics (based on last 12 months)
            "current_yearly": current_savings,
            "predicted_yearly": predicted_savings,
            "difference_yearly": yearly_difference
        }

    def create_impact_summary_cards(impact: Dict[str, float]) -> List[dbc.Card]:
        """Create Bootstrap cards showing impact summary statistics."""
        def format_amount(amount: float, include_sign: bool = False) -> str:
            """Format amount with euro symbol and optional sign."""
            if include_sign and amount > 0:
                return f"+€{amount:,.2f}"
            return f"€{amount:,.2f}"

        def get_color(amount: float) -> str:
            """Get Bootstrap color class based on amount."""
            if amount > 0:
                return "success"
            elif amount < 0:
                return "danger"
            return "warning"

        return [
            dbc.Card([
                dbc.CardBody([
                    html.H5("Monthly Impact", className="card-title"),
                    html.P([
                        "Current: ", format_amount(impact["current_monthly"]),
                        html.Br(),
                        "Predicted: ", format_amount(impact["predicted_monthly"]),
                        html.Br(),
                        html.Strong(
                            ["Change: ", format_amount(impact["difference_monthly"], True)],
                            className=f"text-{get_color(impact['difference_monthly'])}"
                        ),
                    ]),
                ]),
            ], className="shadow-sm mb-3"),
            dbc.Card([
                dbc.CardBody([
                    html.H5("Yearly Impact", className="card-title"),
                    html.P([
                        "Current: ", format_amount(impact["current_yearly"]),
                        html.Br(),
                        "Predicted: ", format_amount(impact["predicted_yearly"]),
                        html.Br(),
                        html.Strong(
                            ["Change: ", format_amount(impact["difference_yearly"], True)],
                            className=f"text-{get_color(impact['difference_yearly'])}"
                        ),
                    ]),
                ]),
            ], className="shadow-sm mb-3"),
        ]

    # Define the page layout
    layout = html.Div([
        dbc.Row([
            dbc.Col([
                html.H1("Income Prediction Analysis"),
                html.Hr(),
            ]),
        ]),
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H4("Adjust Monthly 'Nomina' Income"),
                        html.P(
                            "Analyze how changes in your monthly salary would affect your savings.",
                            className="text-muted",
                        ),
                        dbc.Input(
                            id="input-number",
                            type="number",
                            placeholder=f"Current average: €{default_nomina:,.2f}",
                            value=default_nomina,
                            step=100,
                            className="mb-3",
                        ),
                    ]),
                ], className="shadow-sm mb-4"),
            ]),
        ]),
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H4("Impact Analysis", className="mb-4"),
                        dbc.Row([
                            dbc.Col([
                                html.Div(id="impact-summary"),
                            ], md=4),
                            dbc.Col([
                                dcc.Graph(
                                    id="pred-bar",
                                    config=FIGURE_CONFIG,
                                ),
                            ], md=8),
                        ]),
                    ]),
                ], className="shadow-sm mb-4"),
            ]),
        ]),
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H4("Trends Analysis", className="mb-4"),
                        dcc.Graph(
                            id="pred-line",
                            config=FIGURE_CONFIG,
                        ),
                    ]),
                ], className="shadow-sm"),
            ]),
        ]),
    ])

    @callback(
        [
            Output("pred-line", "figure"),
            Output("pred-bar", "figure"),
            Output("impact-summary", "children")
        ],
        Input("input-number", "value"),
    )
    def update_predictions(value: Optional[float]) -> Tuple[dict, dict, List[dbc.Card]]:
        """Update all predictions based on new Nomina value.
        
        Args:
            value: New monthly Nomina amount
            
        Returns:
            Tuple of (line_figure, bar_figure, impact_summary_cards)
        """
        # Calculate predictions
        summary = calculate_predictions(value)
        
        # Create figures
        line_fig, bar_fig = create_prediction_figures(summary)
        
        # Calculate and format impact summary
        impact = calculate_impact_summary(summary)
        impact_cards = create_impact_summary_cards(impact)
        
        return line_fig, bar_fig, impact_cards

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
