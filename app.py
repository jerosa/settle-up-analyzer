import dash
import dash_bootstrap_components as dbc
from dash import Input, Output, State, dcc, html

app = dash.Dash(
    __name__,
    use_pages=True,
    external_stylesheets=[dbc.themes.BOOTSTRAP, dbc.icons.FONT_AWESOME],
    meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}],
)


sidebar_header = dbc.Row(
    [
        dbc.Col(html.H2("Expenses Analyzer", className="display-5")),
        dbc.Col(
            [
                html.Button(
                    html.Span(className="navbar-toggler-icon"),
                    className="navbar-toggler",
                    style={
                        "color": "rgba(0,0,0,.5)",
                        "border-color": "rgba(0,0,0,.1)",
                    },
                    id="navbar-toggle",
                ),
                html.Button(
                    html.Span(className="navbar-toggler-icon"),
                    className="navbar-toggler",
                    style={
                        "color": "rgba(0,0,0,.5)",
                        "border-color": "rgba(0,0,0,.1)",
                    },
                    id="sidebar-toggle",
                ),
            ],
            width="auto",
            align="center",
        ),
    ]
)


sidebar = html.Div(
    [
        sidebar_header,
        html.Div(
            [
                html.Hr(),
                html.P(
                    "Expenses analyzer via interactive plots",
                    className="lead",
                ),
            ],
            id="blurb",
        ),
        dbc.Collapse(
            dbc.Nav(
                [
                    dbc.NavLink(
                        page["name"],
                        href=page["path"],
                        active="exact",
                    )
                    for page in dash.page_registry.values()
                    if page["module"] != "pages.not_found_404"
                ],
                vertical=True,
                pills=True,
            ),
            id="collapse",
        ),
    ],
    id="sidebar",
)

content = html.Div(dbc.Col([dash.page_container]), id="page-content")


layout = dbc.Container(
    [
        # TODO: Remove if not wanted
        # dbc.Row(
        #     [
        #         dbc.Col(
        #             html.Div(
        #                 "Expenses Analyzer",
        #                 style={"fontSize": 50, "textAlign": "center"},
        #             )
        #         )
        #     ]
        # ),
        # html.Hr(),
        html.Div([dcc.Location(id="url"), sidebar, content]),
    ],
    fluid=True,
)
app.layout = layout


@app.callback(
    Output("sidebar", "className"),
    [Input("sidebar-toggle", "n_clicks")],
    [State("sidebar", "className")],
)
def toggle_classname(n, classname):
    return "collapsed" if n and classname == "" else ""


@app.callback(
    Output("collapse", "is_open"),
    [Input("navbar-toggle", "n_clicks")],
    [State("collapse", "is_open")],
)
def toggle_collapse(n, is_open):
    return not is_open if n else is_open


####################################################


####################################################

if __name__ == "__main__":
    app.run_server(debug=True)
