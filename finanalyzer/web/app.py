"""Main web application module."""
import dash
import dash_bootstrap_components as dbc
from dash import Input, Output, State, html, dcc

# Initialize the Dash app with Bootstrap and Font Awesome
app = dash.Dash(
    __name__,
    use_pages=True,
    external_stylesheets=[
        dbc.themes.BOOTSTRAP,
        dbc.icons.FONT_AWESOME,
        "/assets/responsive-sidebar.css",
        "/assets/custom-styles.css",
    ],
    meta_tags=[
        {"name": "viewport", "content": "width=device-width, initial-scale=1"}
    ],
)

# Sidebar header with navigation
sidebar_header = dbc.Row(
    [
        dbc.Col(html.H2("FinAnalyzer", className="display-5")),
        dbc.Col(
            [
                html.Button(
                    html.Span(className="navbar-toggler-icon"),
                    className="navbar-toggler",
                    id="navbar-toggle",
                ),
                html.Button(
                    html.Span(className="navbar-toggler-icon"),
                    className="navbar-toggler",
                    id="sidebar-toggle",
                ),
            ],
            width="auto",
            align="center",
        ),
    ]
)

# Sidebar with navigation links
sidebar = html.Div(
    [
        sidebar_header,
        html.Div(
            [
                html.Hr(),
                html.P(
                    "Analyze your expenses",
                    className="lead",
                ),
            ],
            id="blurb",
        ),
        dbc.Collapse(
            dbc.Nav(
                [
                    dbc.NavLink(
                        [
                            html.I(className={
                                "/": "fas fa-home me-2",
                                "/categories": "fas fa-chart-pie me-2",
                                "/predict": "fas fa-chart-line me-2",
                                "/table": "fas fa-table me-2",
                            }.get(page["path"], "fas fa-home me-2")),
                            page["name"],
                        ],
                        href=page["path"],
                        active="exact",
                    )
                    for page in dash.page_registry.values()
                ],
                vertical=True,
                pills=True,
            ),
            id="collapse",
        ),
    ],
    id="sidebar",
)

# Main layout
app.layout = html.Div(
    [
        dcc.Location(id="url"),
        sidebar,
        html.Div(
            dash.page_container,
            id="page-content",
        ),
    ],
    className="app-container",
)

# Sidebar toggle callbacks
@app.callback(
    Output("sidebar", "className"),
    Input("sidebar-toggle", "n_clicks"),
    State("sidebar", "className"),
)
def toggle_classname(n, classname):
    """Toggle sidebar collapse state."""
    if n and classname:
        return ""
    return "collapsed" if n else ""

@app.callback(
    Output("collapse", "is_open"),
    Input("navbar-toggle", "n_clicks"),
    State("collapse", "is_open"),
)
def toggle_collapse(n, is_open):
    """Toggle navigation menu collapse state."""
    return not is_open if n else is_open

if __name__ == "__main__":
    app.run_server(debug=True) 
