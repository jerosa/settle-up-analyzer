"""Expenses table page with data upload functionality."""
import base64
import io
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple, Union

import dash
import dash_bootstrap_components as dbc
import pandas as pd
from dash import Input, Output, State, callback, dcc, dash_table, html
from pandas import DataFrame

from finanalyzer.core.analyzer import Analyzer
from finanalyzer.core.config import config
from finanalyzer.core.utils import safe_read_excel

# Register the page
dash.register_page(
    __name__,
    path="/table",
    name="Table",
    title="FinAnalyzer - Expenses Table",
    description="View and analyze your FinAnalyzer expenses in a table format.",
)


def determine_column_type(column: pd.Series) -> str:
    """Determine the appropriate column type for the DataTable.
    
    Args:
        column: DataFrame column to analyze
        
    Returns:
        Column type string for Dash DataTable
    """
    if isinstance(column.dtype, pd.DatetimeTZDtype):
        return "datetime"
    elif (
        isinstance(column.dtype, (pd.StringDtype, pd.BooleanDtype, pd.CategoricalDtype, pd.PeriodDtype))
    ):
        return "text"
    elif (
        isinstance(column.dtype, (pd.SparseDtype, pd.IntervalDtype)) or
        any(isinstance(column.dtype, t) for t in (pd.Int8Dtype, pd.Int16Dtype, pd.Int32Dtype, pd.Int64Dtype))
    ):
        return "numeric"
    else:
        return "any"


def create_data_table(df: DataFrame) -> dash_table.DataTable:
    """Create a Dash DataTable from a DataFrame.
    
    Args:
        df: DataFrame to display
        
    Returns:
        Configured DataTable component
    """
    return dash_table.DataTable(
        columns=[
            {
                "name": col,
                "id": col,
                "type": determine_column_type(df[col])
            }
            for col in df.columns
        ],
        data=df.to_dict("records"),
        page_size=20,
        filter_action="native",
        sort_action="native",
        style_table={
            "overflowX": "auto",
            "backgroundColor": "white",
        },
        style_data={
            "width": "150px",
            "minWidth": "150px",
            "maxWidth": "150px",
            "overflow": "hidden",
            "textOverflow": "ellipsis",
        },
        style_header={
            "backgroundColor": "rgb(230, 230, 230)",
            "fontWeight": "bold",
            "textAlign": "center",
        },
        style_cell={
            "fontFamily": "-apple-system,BlinkMacSystemFont,Segoe UI,Roboto,Helvetica Neue,Arial,sans-serif",
            "fontSize": "14px",
            "padding": "10px",
        },
        tooltip_data=[
            {
                column: {"value": str(value), "type": "markdown"}
                for column, value in row.items()
            }
            for row in df.to_dict("records")
        ],
        tooltip_duration=None,
    )


def parse_uploaded_file(
    contents: str,
    filename: str,
    date: float
) -> Tuple[Optional[DataFrame], Optional[str]]:
    """Parse uploaded file contents into a DataFrame.
    
    Args:
        contents: Base64 encoded file contents
        filename: Name of the uploaded file
        date: Upload timestamp
        
    Returns:
        Tuple of (DataFrame or None, error message or None)
    """
    try:
        # Parse content
        content_type, content_string = contents.split(",")
        decoded = base64.b64decode(content_string)
        
        # Read file based on type
        if filename.endswith(".csv"):
            df = pd.read_csv(io.StringIO(decoded.decode("utf-8")))
        elif filename.endswith((".xls", ".xlsx")):
            df = pd.read_excel(io.BytesIO(decoded))
        else:
            return None, f"Unsupported file type: {filename}"
            
        return df, None
        
    except Exception as e:
        return None, f"Error processing file: {str(e)}"


def create_upload_result(
    df: Optional[DataFrame] = None,
    filename: Optional[str] = None,
    date: Optional[float] = None,
    error: Optional[str] = None
) -> html.Div:
    """Create the upload result component.
    
    Args:
        df: DataFrame to display
        filename: Name of the uploaded file
        date: Upload timestamp
        error: Error message if any
        
    Returns:
        Div containing the result or error message
    """
    if error:
        return html.Div([
            dbc.Alert(
                [
                    html.H4("Upload Error", className="alert-heading"),
                    html.P(error),
                ],
                color="danger",
            )
        ])
        
    children = []
    
    if filename and date:
        children.extend([
            html.H5(filename, className="text-muted"),
            html.H6(
                datetime.fromtimestamp(date).strftime("%Y-%m-%d %H:%M:%S"),
                className="text-muted mb-4",
            ),
        ])
        
    if df is not None:
        children.append(
            dbc.Card(
                dbc.CardBody(create_data_table(df)),
                className="shadow-sm",
            )
        )
        
    return html.Div(children)


# Define the page layout
layout = html.Div([
    dbc.Row([
        dbc.Col([
            html.H1("Expenses Table"),
            html.Hr(),
        ]),
    ]),
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    dbc.Row([
                        dbc.Col([
                            dcc.Upload(
                                id="upload-data",
                                children=dbc.Button(
                                    [
                                        html.I(className="fas fa-upload me-2"),
                                        "Upload File",
                                    ],
                                    color="primary",
                                ),
                                multiple=False,
                            ),
                        ], width="auto"),
                        dbc.Col([
                            html.P(
                                "Upload a CSV or Excel file to view and analyze expenses data.",
                                className="text-muted mb-0",
                                style={"marginTop": "8px"},
                            ),
                        ]),
                    ]),
                ]),
            ], className="shadow-sm mb-4"),
        ]),
    ]),
    dbc.Row([
        dbc.Col([
            html.Div(id="output-data-upload"),
        ]),
    ]),
])


@callback(
    Output("output-data-upload", "children"),
    Input("upload-data", "contents"),
    State("upload-data", "filename"),
    State("upload-data", "last_modified"),
)
def update_output(
    content: Optional[str],
    name: Optional[str],
    date: Optional[float]
) -> html.Div:
    """Update the table based on file upload or show default data.
    
    Args:
        content: Base64 encoded file contents
        name: Name of the uploaded file
        date: Upload timestamp
        
    Returns:
        Div containing the table or error message
    """
    if content:
        # Handle uploaded file
        df, error = parse_uploaded_file(content, name, date)
        return create_upload_result(df, name, date, error)
    
    try:
        # Show default data
        analyzer = Analyzer(config["workdir"], config["excel_filename"])
        df = analyzer.data.df
        return create_upload_result(
            df,
            filename=config["excel_filename"],
            error=None
        )
    except Exception as e:
        return create_upload_result(error=f"Error loading default data: {str(e)}") 
