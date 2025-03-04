"""
Prediction page for analyzing the impact of income changes.

This module provides interactive visualizations to explore how changes in 'Nomina' income
would affect monthly and yearly savings. It includes:
1. A line plot showing monthly trends with target thresholds
2. A bar plot showing yearly summaries
"""

from datetime import datetime
from typing import Dict, Tuple, Optional

import dash
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
from dash import dcc, html, callback, Input, Output, State
import pandas as pd
import numpy as np

from analyze import Analyzer

dash.register_page(__name__)

# Initialize data
analyzer = Analyzer()
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

# Common figure settings for better performance
FIGURE_CONFIG = {
    "scrollZoom": False,
    "displayModeBar": False,
}

LAYOUT_TEMPLATE = {
    "margin": dict(l=50, r=30, t=50, b=30),  # Reduced top margin
    "paper_bgcolor": "rgba(0,0,0,0)",
    "plot_bgcolor": "rgba(0,0,0,0)",
    "hovermode": "closest",
    "font": dict(size=11),  # Slightly smaller font
    "title": dict(
        font=dict(size=14, color="#2c3e50"),  # Smaller title
        x=0.5,
        xanchor="center",
        y=0.95
    )
}

# Color scheme
COLORS = {
    "Ingress": "#2ecc71",
    "Savings": "#3498db",
    "Savings Predicted": "#e74c3c",
    "Target": "#f39c12",
    "Break Even": "#c0392b"
}

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
        height=600  # Fixed height for better layout
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
            yanchor="top",  # Changed from bottom to top
            y=-0.15,  # Move legend below the plot
            xanchor="center",  # Center the legend
            x=0.5,  # Center position
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
        height=500  # Fixed height for better layout
    )
    bar_fig.update_layout(
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="top",  # Changed from bottom to top
            y=-0.15,  # Move legend below the plot
            xanchor="center",  # Center the legend
            x=0.5,  # Center position
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

# Define the page layout
layout = dbc.Container(
    [
        html.H1(
            children="Income Prediction Analysis",
            className="text-center mb-3",  # Reduced margin
            style={"color": "#2c3e50", "fontSize": "24px"}  # Smaller heading
        ),
        html.Hr(className="my-2"),  # Reduced margin
        dbc.Row([
            dbc.Col([
                dbc.Card(
                    dbc.CardBody([
                        html.H4(
                            "Adjust Monthly 'Nomina' Income",
                            className="card-title text-center mb-2",  # Reduced margin
                            style={"fontSize": "18px"}  # Smaller heading
                        ),
                        html.P(
                            "Analysis based on the last 12 months of data",
                            className="text-muted text-center mb-2 small"  # Smaller text and margin
                        ),
                        dbc.InputGroup([
                            dbc.InputGroupText("€"),
                            dbc.Input(
                                id="input-number",
                                type="number",
                                min=0,
                                value=default_nomina,
                                step=100
                            ),
                        ], className="mb-2"),  # Reduced margin
                        html.Small(
                            f"Default value is the average Nomina from the last 12 months",
                            className="text-muted d-block text-center mb-2"  # Reduced margin
                        ),
                        html.Div(id="impact-summary", className="mt-3"),  # Reduced margin
                    ]),
                    className="mb-3 shadow-sm"  # Reduced margin
                ),
            ], md=6, className="mx-auto"),
        ]),
        dbc.Row([
            dbc.Col(
                dcc.Graph(
                    id="pred-line",
                    config=FIGURE_CONFIG,
                    className="shadow-sm"
                ),
                className="mb-3"  # Reduced margin
            ),
        ]),
        dbc.Row([
            dbc.Col(
                dcc.Graph(
                    id="pred-bar",
                    config=FIGURE_CONFIG,
                    className="shadow-sm"
                ),
                className="mb-3"  # Reduced margin
            ),
        ]),
    ],
    fluid=True,
    className="py-3"  # Reduced padding
)

@callback(
    [
        Output("pred-line", "figure"),
        Output("pred-bar", "figure"),
        Output("impact-summary", "children")
    ],
    Input("input-number", "value"),
)
def update_predictions(value: Optional[float]) -> Tuple[dict, dict, html.Div]:
    """Update prediction figures and impact summary based on new Nomina value."""
    summary = calculate_predictions(value)
    line_fig, bar_fig = create_prediction_figures(summary)
    
    # Calculate impact metrics
    impact = calculate_impact_summary(summary)
    
    # Create impact summary cards with consistent styling
    card_header_style = {
        "fontSize": "14px",
        "padding": "0.5rem 1rem",  # Reduced padding
    }
    
    card_body_style = {
        "padding": "0.75rem",  # Reduced padding
    }
    
    # Create impact summary cards
    impact_summary = dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader(
                    "Monthly Savings Impact (12-Month Average)", 
                    className="text-center",
                    style=card_header_style
                ),
                dbc.CardBody([
                    html.H5(
                        f"€{impact['difference_monthly']:,.2f}",
                        className="text-center mb-2",
                        style={"fontSize": "16px"}
                    ),
                    html.P([
                        "Current Monthly Savings: ",
                        html.Span(f"€{impact['current_monthly']:,.2f}", className="text-muted"),
                        html.Br(),
                        "Predicted Monthly Savings: ",
                        html.Span(f"€{impact['predicted_monthly']:,.2f}", className="text-muted")
                    ], className="card-text small mb-0")  # Remove bottom margin
                ], style=card_body_style)
            ], className="shadow-sm h-100")
        ], md=6, className="mb-0"),  # Remove bottom margin
        dbc.Col([
            dbc.Card([
                dbc.CardHeader(
                    "Yearly Savings Impact (Last 12 Months)", 
                    className="text-center",
                    style=card_header_style
                ),
                dbc.CardBody([
                    html.H5(
                        f"€{impact['difference_yearly']:,.2f}",
                        className="text-center mb-2",
                        style={"fontSize": "16px"}
                    ),
                    html.P([
                        "Current Annual Savings: ",
                        html.Span(f"€{impact['current_yearly']:,.2f}", className="text-muted"),
                        html.Br(),
                        "Predicted Annual Savings: ",
                        html.Span(f"€{impact['predicted_yearly']:,.2f}", className="text-muted")
                    ], className="card-text small mb-0")  # Remove bottom margin
                ], style=card_body_style)
            ], className="shadow-sm h-100")
        ], md=6, className="mb-0")  # Remove bottom margin
    ], className="g-2")  # Reduced gap between cards
    
    return line_fig, bar_fig, impact_summary
