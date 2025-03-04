from dash import dcc


def generate_year_dropdown(years: list, selected_year):
    return dcc.Dropdown(
        id="year-filter",
        options=[{"label": year, "value": year} for year in years],
        placeholder="Select a Year",
        multi=False,
        clearable=False,
        value=selected_year,
        style={"width": "70px"},
        # className="xs-3",
    )
