import os

import dash
import pandas as pd
from dash import html, dash_table, dcc, callback, Input, Output, State
import dash_bootstrap_components as dbc

from datetime import datetime
import base64
import io

from config import logger, settings


dash.register_page(__name__)


def table_type(df_column):
    if isinstance(df_column.dtype, pd.DatetimeTZDtype):
        return ("datetime",)
    elif (
        isinstance(df_column.dtype, pd.StringDtype)
        or isinstance(df_column.dtype, pd.BooleanDtype)
        or isinstance(df_column.dtype, pd.CategoricalDtype)
        or isinstance(df_column.dtype, pd.PeriodDtype)
    ):
        return "text"
    elif (
        isinstance(df_column.dtype, pd.SparseDtype)
        or isinstance(df_column.dtype, pd.IntervalDtype)
        or isinstance(df_column.dtype, pd.Int8Dtype)
        or isinstance(df_column.dtype, pd.Int16Dtype)
        or isinstance(df_column.dtype, pd.Int32Dtype)
        or isinstance(df_column.dtype, pd.Int64Dtype)
    ):
        return "numeric"
    else:
        return "any"


layout = dbc.Container(
    children=[
        html.H1(children="Table"),
        html.Hr(),
        dbc.Container(
            [
                dcc.Upload(
                    dbc.Button("Upload File"),
                    id="upload-data",
                ),
                html.Div(
                    id="output-data-upload",
                ),
            ]
        ),
    ]
)


def get_datatable(df):
    datatable = dash_table.DataTable(
        columns=[{"name": i, "id": i, "type": table_type(df[i])} for i in df.columns],
        data=df.to_dict("records"),
        page_size=20,
        filter_action="native",
        style_data={
            "width": "150px",
            "minWidth": "150px",
            "maxWidth": "150px",
            "overflow": "hidden",
            "textOverflow": "ellipsis",
        },
    )

    return datatable


def parse_content(contents, filename, date):
    _, content_string = contents.split(",")

    decoded = base64.b64decode(content_string)

    logger.debug("Reading content")
    try:
        if "csv" in filename:
            df = pd.read_csv(io.StringIO(decoded.decode("utf-8")))
        elif "xls" in filename:
            df = pd.read_excel(io.BytesIO(decoded))
        else:
            raise TypeError("Invalid content type when loading table")
    except Exception as e:
        logger.error(e)
        return html.Div(["There was an error processing this file."])

    return html.Div(
        [
            html.H5(filename),
            html.H6(datetime.fromtimestamp(date)),
            get_datatable(df),
            html.Hr(),
        ]
    )


@callback(
    Output("output-data-upload", "children"),
    Input("upload-data", "contents"),
    State("upload-data", "filename"),
    State("upload-data", "last_modified"),
)
def update_output(content, name, date):
    if content is not None:
        children = [parse_content(content, name, date)]
        return children
    else:
        # Default
        excel_name = settings["expenses_excel_filename"]
        filepath = os.path.join(settings.workdir, excel_name)
        logger.debug(f"Reading excel {filepath}")
        df = pd.read_excel(filepath)
        return html.Div(
            [html.H5(f"Using default Expenses Sheet: {excel_name}"), get_datatable(df)],
        )
