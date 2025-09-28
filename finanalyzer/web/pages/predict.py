"""
Predict: Analyze impact of payroll income changes.

Simplified rewrite for clear impact analysis: period selector (Monthly/Annual),
target amount input and monthly trend/annual comparison visualizations.
"""

from typing import Dict, Tuple, Optional, List

import dash
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
from dash import dcc, html, callback, Input, Output
import pandas as pd
import numpy as np

from finanalyzer.core.analyzer import Analyzer
from finanalyzer.core.config import config
from finanalyzer.web.utils import (
    FIGURE_CONFIG,
    LAYOUT_TEMPLATE,
    generate_alert_layout,
)

# Page registration
dash.register_page(
    __name__,
    path="/predict",
    name="Predict",
    title="FinAnalyzer - Income Impact",
    description="Analyze the impact of changing your payroll income on savings.",
)

COLORS = {
    "Income": "#2ecc71",
    "Expenses": "#e67e22",
    "Savings": "#3498db",
    "Savings (simulated)": "#e74c3c",
    "Target": "#f39c12",
    "Break-even": "#7f8c8d",
}

HOUSING_CATEGORY = config["housing_category"]
PAYROLL_CATEGORY = config["payroll_category"]
EXTRA_CATEGORY = config["extra_category"]
BONUS_CATEGORY = config["bonus_category"]

try:
    analyzer = Analyzer(config["workdir"], config["excel_filename"])
    df_income = analyzer.data.df_ingress
    df_expenses = analyzer.data.df_expenses

    # Monthly series
    expenses_monthly = df_expenses.groupby(df_expenses.index.to_period("M"))["Amount"].sum()
    income_monthly = df_income.groupby(df_income.index.to_period("M"))["Amount"].sum()

    # Get current housing expenses
    housing_expenses = df_expenses[df_expenses.Category == HOUSING_CATEGORY]
    housing_monthly = housing_expenses.groupby(housing_expenses.index.to_period("M"))["Amount"].sum()

    # Create annual data structure
    def create_annual_summary() -> pd.DataFrame:
        """Create annual summary DataFrame with calendar years."""
        # Get all years from the data
        all_years = sorted(set(df_income.index.year) | set(df_expenses.index.year))
        
        annual_data = []
        current_year = pd.Timestamp.now().year
        
        for year in all_years:
            # Income by category for this year
            year_income = df_income[df_income.index.year == year]
            year_expenses = df_expenses[df_expenses.index.year == year]
            
            regular = year_income[year_income.Category == PAYROLL_CATEGORY]["Amount"].sum()
            extra = year_income[year_income.Category == EXTRA_CATEGORY]["Amount"].sum()
            bonus = year_income[year_income.Category == BONUS_CATEGORY]["Amount"].sum()
            total_income = regular + extra + bonus
            
            housing = year_expenses[year_expenses.Category == HOUSING_CATEGORY]["Amount"].sum()
            
            total_expenses = year_expenses["Amount"].sum()
            savings = total_income - total_expenses
            
            # Determine if year is complete
            is_complete = year < current_year
            status = "Complete" if is_complete else "Incomplete"
            
            annual_data.append({
                "Year": year,
                "Regular": regular,
                "Extra": extra,
                "Bonus": bonus,
                "Total_Income": total_income,
                "Housing": housing,
                "Expenses": total_expenses,
                "Savings": savings,
                "Status": status,
                "Is_Complete": is_complete
            })
        
        return pd.DataFrame(annual_data).set_index("Year")
    
    # Create annual summary
    annual_summary = create_annual_summary()
    
    # Get most recent complete year as default
    complete_years = annual_summary[annual_summary["Is_Complete"]]
    default_year = complete_years.index.max() if len(complete_years) > 0 else annual_summary.index.max()

    # TODO: predict incomplete year using total income / 12

    def build_annual_analysis(selected_year: int, annual_income_target: float, housing_amount: Optional[float] = None) -> Tuple[pd.DataFrame, Dict]:
        """Build annual analysis based on selected year and target income."""
        # Calculate baseline housing for the selected year
        year_housing = housing_monthly[housing_monthly.index.year == selected_year]
        baseline_housing = int(round(year_housing.mean())) if len(year_housing) > 0 else 0
        
        if housing_amount is None or np.isnan(housing_amount):
            housing_amount = baseline_housing

        # Get baseline year data
        baseline_data = annual_summary.loc[selected_year]
        baseline_income = baseline_data["Total_Income"]
        baseline_expenses = baseline_data["Expenses"]
        baseline_savings = baseline_data["Savings"]
        
        # Calculate income change
        income_change = annual_income_target - baseline_income
        
        # Get months for the selected year
        year_months = pd.period_range(start=f"{selected_year}-01", end=f"{selected_year}-12", freq="M")
        
        # Create monthly DataFrame for the year
        df = pd.DataFrame(index=year_months)
        
        # Get actual monthly data for the year
        year_income = income_monthly[income_monthly.index.year == selected_year]
        year_expenses = expenses_monthly[expenses_monthly.index.year == selected_year]
        
        # Fill with actual data, 0 for missing months
        df["Income"] = year_income.reindex(year_months, fill_value=0.0)
        df["Expenses"] = year_expenses.reindex(year_months, fill_value=0.0)
        df["Savings"] = df["Income"] - df["Expenses"]
        
        # Simulated income: distribute income change evenly across months
        monthly_change = income_change / 12.0
        df["Income (sim)"] = df["Income"] + monthly_change
        
        # Simulated expenses (adjust housing if specified)
        df["Expenses (sim)"] = df["Expenses"].copy()
        if housing_amount != baseline_housing:
            housing_adjustment = housing_amount - baseline_housing
            df["Expenses (sim)"] = df["Expenses (sim)"] + housing_adjustment
        
        df["Savings (sim)"] = df["Income (sim)"] - df["Expenses (sim)"]
        
        # Calculate annual KPIs
        annual_kpis = {
            "baseline_income": baseline_income,
            "baseline_expenses": baseline_expenses,
            "baseline_savings": baseline_savings,
            "target_income": annual_income_target,
            "income_change": income_change,
            "target_savings": df["Savings (sim)"].sum(),
            "savings_change": df["Savings (sim)"].sum() - baseline_savings,
            "monthly_avg_current": df["Savings"].mean(),
            "monthly_avg_simulated": df["Savings (sim)"].mean(),
            "monthly_change": df["Savings (sim)"].mean() - df["Savings"].mean(),
            "year_status": baseline_data["Status"],
        }
        
        return df, annual_kpis


    def create_value_card(title: str, value: float, delta: Optional[float] = None) -> dbc.Card:
        """Create a Bootstrap card showing a value with optional delta."""
        def format_amount(x: float, show_sign: bool = False) -> str:
            s = f"€{x:,.0f}"
            if show_sign and x > 0:
                return "+" + s
            return s

        color = "success" if (delta is not None and delta > 0) else ("danger" if (delta is not None and delta < 0) else "secondary")
        body: List = [html.H5(title, className="card-title mb-1"), html.H3(format_amount(value), className="mb-2")]
        if delta is not None:
            body.append(html.Div([html.Span("Δ "), html.Strong(format_amount(delta, True), className=f"text-{color}")]))
        return dbc.Card([dbc.CardBody(body)], className="info-card")

    # Layout
    layout = html.Div([
        dbc.Row([
            dbc.Col([html.H1("Annual Income & Housing Impact Analysis", className="section-title mb-0")], className="content-section py-3"),
        ], className="mb-3"),
        
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.Div([
                            html.H4("Configure Annual Scenario", className="mb-3"),
                            dbc.Row([
                                dbc.Col([
                                    dbc.Label("Baseline Year", className="form-label"),
                                    dcc.Dropdown(
                                        id="year-selector",
                                        options=[
                                            {"label": f"{year} ({annual_summary.loc[year, 'Status']})", "value": year}
                                            for year in annual_summary.index
                                        ],
                                        value=default_year,
                                        clearable=False,
                                    ),
                                    html.Small(
                                        f"Default: Most recent complete year",
                                        className="text-muted",
                                    ),
                                ], md=3),
                                dbc.Col([
                                    dbc.Label("Annual Income Target", className="form-label"),
                                    dbc.Input(
                                        id="annual-income",
                                        type="number",
                                        value=int(round(annual_summary.loc[default_year, "Total_Income"])),
                                        step=1000,
                                        min=0,
                                    ),
                                    html.Small(
                                        id="annual-income-help",
                                        className="text-muted",
                                    ),
                                ], md=3),
                                dbc.Col([
                                    dbc.Label("Monthly Housing", className="form-label"),
                                    dbc.Input(
                                        id="housing-amount",
                                        type="number",
                                        value=int(round(annual_summary.loc[default_year, "Housing"] / 12)),
                                        step=50,
                                        min=0,
                                    ),
                                    html.Small(
                                        id="housing-help",
                                        className="text-muted",
                                    ),
                                ], md=4),
                            ])
                        ], className="controls-section"),

                        dbc.Row([
                            dbc.Col(html.Div(id="annual-kpis"), md=12)
                        ], className="mb-3"),

                        dbc.Row([
                            dbc.Col(dcc.Graph(id="annual-chart", config=FIGURE_CONFIG), md=7),
                            dbc.Col(dcc.Graph(id="monthly-chart", config=FIGURE_CONFIG), md=5),
                        ]),
                    ])
                ], className="content-section"),
            ])
        ]),
    ])

    def create_annual_chart(annual_summary: pd.DataFrame, selected_year: int, annual_kpis: Dict) -> dict:
        """Create annual comparison chart."""
        fig = go.Figure()
        
        # Add actual savings bars
        fig.add_trace(go.Bar(
            x=annual_summary.index,
            y=annual_summary["Savings"],
            name="Actual Savings",
            marker_color=COLORS["Savings"],
            opacity=0.8
        ))
        
        # Add simulated savings for selected year
        fig.add_trace(go.Bar(
            x=[selected_year],
            y=[annual_kpis["target_savings"]],
            name="Simulated Savings",
            marker_color=COLORS["Savings (simulated)"],
            opacity=0.8
        ))
        
        # Add break-even line
        fig.add_hline(y=0, line_dash="dash", line_color=COLORS["Break-even"], 
                     annotation_text="Break-even", annotation_position="bottom right")
        
        fig.update_layout(
            title="Annual Savings Comparison",
            xaxis_title="Year",
            yaxis_title="€",
            barmode="group",
            template="plotly_white",
            height=400,
            **LAYOUT_TEMPLATE
        )
        
        return fig

    def create_monthly_chart(monthly_df: pd.DataFrame) -> dict:
        """Create monthly distribution chart."""
        df_plot = monthly_df[["Savings", "Savings (sim)"]].copy()
        df_plot.index = df_plot.index.astype(str)
        
        fig = px.line(
            df_plot,
            labels={"value": "€", "index": "Month"},
            markers=True,
            title="Monthly Savings Distribution",
            color_discrete_map={"Savings": COLORS["Savings"], "Savings (sim)": COLORS["Savings (simulated)"]},
            template="plotly_white",
            height=400,
        )
        
        # Add break-even line
        months = list(df_plot.index)
        fig.add_trace(
            go.Scatter(
                x=months,
                y=[0] * len(months),
                name="Break-even",
                line={"dash": "dash", "color": COLORS["Break-even"]},
                hovertemplate="€0",
            )
        )
        
        fig.update_layout(
            legend=dict(orientation="h", yanchor="top", y=-0.2, xanchor="center", x=0.5),
            **LAYOUT_TEMPLATE
        )
        
        return fig

    @callback(
        [Output("annual-income", "value"), Output("annual-income-help", "children"), Output("housing-help", "children")],
        Input("year-selector", "value"),
    )
    def update_inputs_when_year_changes(selected_year: int) -> Tuple[int, str, str]:
        """Update annual income input and help texts when year selector changes."""
        current_income = int(round(annual_summary.loc[selected_year, "Total_Income"]))
        income_help_text = f"Current {selected_year}: €{current_income:,}"
        
        # Calculate average housing for the selected year
        year_housing = housing_monthly[housing_monthly.index.year == selected_year]
        if len(year_housing) > 0:
            avg_housing = int(round(year_housing.mean()))
        else:
            avg_housing = 0
        housing_help_text = f"Current monthly: €{avg_housing:,}"
        
        return current_income, income_help_text, housing_help_text

    @callback(
        [Output("annual-chart", "figure"), Output("monthly-chart", "figure"), Output("annual-kpis", "children")],
        [Input("year-selector", "value"), Input("annual-income", "value"), Input("housing-amount", "value")],
    )
    def update_annual_analysis(selected_year: int, annual_income: Optional[float], housing_value: Optional[float]) -> Tuple[dict, dict, List[dbc.Card]]:
        """Update annual analysis based on all input parameters."""
        # Handle inputs
        if annual_income is None or (isinstance(annual_income, float) and np.isnan(annual_income)):
            annual_income = int(round(annual_summary.loc[selected_year, "Total_Income"]))
        
        if housing_value is None or (isinstance(housing_value, float) and np.isnan(housing_value)):
            # Calculate baseline housing for the selected year
            year_housing = housing_monthly[housing_monthly.index.year == selected_year]
            housing_value = int(round(year_housing.mean())) if len(year_housing) > 0 else 0

        # Build analysis
        monthly_df, annual_kpis = build_annual_analysis(selected_year, annual_income, housing_value)
        
        # Calculate baseline housing for KPI display
        year_housing = housing_monthly[housing_monthly.index.year == selected_year]
        baseline_housing = int(round(year_housing.mean())) if len(year_housing) > 0 else 0
        
        # Create charts
        annual_fig = create_annual_chart(annual_summary, selected_year, annual_kpis)
        monthly_fig = create_monthly_chart(monthly_df)
        
        # Create KPI cards
        cards = [
            dbc.Row([
                dbc.Col(create_value_card("Annual Savings (Baseline)", annual_kpis["baseline_savings"]), md=3),
                dbc.Col(create_value_card("Annual Savings (Simulated)", annual_kpis["target_savings"], annual_kpis["savings_change"]), md=3),
                dbc.Col(create_value_card("Annual Δ", annual_kpis["savings_change"]), md=3),
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H5("Year Status", className="card-title mb-1"),
                            html.H3([
                                html.Span("●", className=f"text-{'success' if annual_kpis['year_status'] == 'Complete' else 'warning'} me-2"),
                                annual_kpis['year_status']
                            ], className="mb-0"),
                        ])
                    ], className="info-card")
                ], md=3),
            ], className="mb-2"),
            dbc.Row([
                dbc.Col(create_value_card("Monthly Avg (Current)", annual_kpis["monthly_avg_current"]), md=3),
                dbc.Col(create_value_card("Monthly Avg (Simulated)", annual_kpis["monthly_avg_simulated"], annual_kpis["monthly_change"]), md=3),
                dbc.Col(create_value_card("Monthly Δ", annual_kpis["monthly_change"]), md=3),
                dbc.Col(create_value_card("Housing Δ", housing_value - baseline_housing), md=3),
            ]),
        ]
        
        return annual_fig, monthly_fig, cards

except Exception as e:
    layout = generate_alert_layout(e)