"""Dash HTML-ish layout."""

import logging
from typing import Dict, Iterator, List, Optional, Tuple, Union

import dash_bootstrap_components as dbc  # type: ignore[import]
import dash_daq as daq  # type: ignore[import]
import plotly.graph_objects as go  # type: ignore[import]
from dash import dcc  # type: ignore
from dash import html
from dash.dependencies import Input, Output, State  # type: ignore

from .config import app

NDIMS = 3

NO_RADIO_SELECT = 0
COUNT = 1
STATS = 2
MIN = 3
MAX = 4
MEDIAN = 5
MODE = 6
MEAN = 7
STD_DEV = 8


def make_dim_control(num_id: int, xy_str: str) -> dbc.Row:
    """Return a control box for managing/selecting a dimension."""
    width = "37.5em"

    return dbc.Row(
        style={"margin-top": "7rem"},
        children=[
            dbc.Col(
                children=[
                    daq.Slider(
                        id=f"bin-slider-{xy_str.lower()}-{num_id}",
                        min=1,
                        max=10,
                        value=5,
                        handleLabel={
                            "showCurrentValue": True,
                            "label": "BINS",
                            "style": {"width": "5rem"},
                        },
                        step=1,
                        size=width,
                    ),
                    dcc.Dropdown(
                        style={"width": width},
                        id=f"dropdown-{xy_str.lower()}-{num_id}",
                        placeholder=f"Select{' Additional' if num_id else ''}"
                        f" {xy_str.upper()} Dimension",
                        clearable=True,
                    ),
                ]
            ),
            dbc.Col(
                align="start",
                children=daq.BooleanSwitch(
                    style={"width": 55},
                    id=f"hide-switch-{xy_str.lower()}-{num_id}",
                    on=True,
                    label={"label": "Visible", "style": {"margin-bottom": 0}},
                    labelPosition="top",
                ),
            ),
        ],
    )


def layout() -> None:
    """Serve the layout to `app`."""
    app.title = "Heatmap Multiplexer"

    # Layout
    app.layout = html.Div(
        children=[
            html.H1("Heatmap Multiplexer"),
            dcc.Graph(id="heatmap-parent"),
            html.Div(
                children=[
                    html.Div(
                        style={
                            "text-align": "center",
                            "display": "block",
                            "margin-left": "auto",
                            "margin-right": "auto",
                            "width": "39rem",
                        },
                        children=[
                            html.Div("Data Coloring"),
                            # Count or Dimension
                            html.Div(
                                className="radio-group",
                                style={
                                    # "text-align": "center",
                                    "margin-bottom": "1rem",
                                },
                                children=dbc.RadioItems(
                                    id="color-count-or-stat-radios",
                                    className="btn-group",
                                    # style={"width": "500rem"},
                                    inputClassName="btn-check",
                                    labelClassName="btn btn-outline-primary fixed-width-button",
                                    labelCheckedClassName="active",
                                    options=[
                                        {
                                            "label": "count",
                                            "value": COUNT,
                                        },
                                        {
                                            "label": "dimensional statistic",
                                            "value": STATS,
                                        },
                                    ],
                                    value=COUNT,
                                ),
                            ),
                            # Dimension Coloring
                            dbc.Collapse(
                                id="color-collapse",
                                is_open=True,
                                # style={"width": "39rem"},
                                children=dbc.Card(
                                    html.Div(
                                        style={
                                            # "width": "37rem",
                                            "display": "block",
                                            "margin-left": "auto",
                                            "margin-right": "auto",
                                            # "width": "40%",
                                            "margin-top": "1rem",
                                            "margin-bottom": "1rem",
                                        },
                                        children=[
                                            dcc.Dropdown(
                                                style={"text-align": "center"},
                                                id="dropdown-color",
                                                placeholder="Select Dimension",
                                                clearable=False,
                                            ),
                                            html.Div(
                                                className="radio-group",
                                                style={"text-align": "center"},
                                                children=dbc.RadioItems(
                                                    id="color-stats-select-radios",
                                                    className="btn-group",
                                                    # style={"width": "500rem"},
                                                    inputClassName="btn-check",
                                                    labelClassName="btn btn-outline-primary",
                                                    labelCheckedClassName="active",
                                                    options=[
                                                        {
                                                            "label": "minimum",
                                                            "value": MIN,
                                                        },
                                                        {
                                                            "label": "maximum",
                                                            "value": MAX,
                                                        },
                                                        {
                                                            "label": "median",
                                                            "value": MEDIAN,
                                                        },
                                                        {
                                                            "label": "mode",
                                                            "value": MODE,
                                                        },
                                                        {
                                                            "label": "mean",
                                                            "value": MEAN,
                                                        },
                                                        {
                                                            "label": "standard deviation",
                                                            "value": STD_DEV,
                                                        },
                                                    ],
                                                ),
                                            ),
                                        ],
                                    ),
                                ),
                            ),
                        ],
                    ),
                ]
            ),
            html.Hr(style={"margin-top": "2em", "margin-bottom": "1em"}),
            html.H5("Select Dimensions"),
            dbc.Row(
                style={"margin-left": "2em", "margin-right": "2em"},
                children=[
                    dbc.Col(
                        # width=5,
                        children=[html.Div("Y Dimensions")]
                        + [dbc.Row(make_dim_control(i, "Y")) for i in range(NDIMS)],
                    ),
                    # html.Div(style={"width": "25px"}),
                    dbc.Col(
                        # width=5,
                        children=[html.Div("X Dimensions")]
                        + [dbc.Row(make_dim_control(i, "X")) for i in range(NDIMS)],
                    ),
                ],
            ),
            html.Hr(style={"margin-top": "4em", "margin-bottom": "1em"}),
            html.H5("Upload CSV File"),
            dcc.Upload(
                id="wbs-upload-xlsx",
                children=html.Div(["Drag and Drop or ", html.A("Select File")]),
                style={
                    "width": "94%",
                    "height": "5rem",
                    "lineHeight": "5rem",
                    "borderWidth": "1px",
                    "borderStyle": "dashed",
                    "borderRadius": "5px",
                    "textAlign": "center",
                    "margin-left": "2em",
                    "margin-right": "2em",
                },
                # Allow multiple files to be uploaded
                multiple=False,
                contents="",
            ),
            html.Div(style={"height": "5em"}),
        ]
    )


@app.callback(  # type: ignore[misc]
    [
        Output("color-collapse", "is_open"),
        Output("color-stats-select-radios", "value"),
        Output("dropdown-color", "value"),
    ],
    [Input("color-count-or-stat-radios", "value")],
    # [State("url", "pathname")],
    prevent_initial_callbacks=True,
)
def count_or_stats(value: str) -> Tuple[bool, int, str]:
    """Toggle the count-or-stats radio button & collapse box."""
    if value == COUNT:
        return False, NO_RADIO_SELECT, ""
    elif value == STATS:
        return True, NO_RADIO_SELECT, ""
    else:
        raise ValueError(f"Unrecognized value: {value}")


@app.callback(  # type: ignore[misc]
    [
        Output(f"dropdown-{'x' if i%2==0 else 'y'}-{i//2}", "options")
        for i in range(NDIMS * 2)
    ]
    + [Output("dropdown-color", "options")],
    Input("wbs-upload-xlsx", "contents")
    # [State("url", "pathname")],
)
def upload_csv(contents: str) -> List[List[Dict[str, str]]]:
    """Serve up the heatmap wrapped in a go.Figure instance."""
    try:
        base64_file = contents.split(",")[1]
    except IndexError:
        pass

    dimensions = ["aaa", "bbb", "ccc"]
    logging.info(f"Dimensions Available ({len(dimensions)}): {dimensions}")

    options_list = [
        {
            "label": dim,
            "value": dim,
        }
        for dim in dimensions
    ]

    return [options_list] * ((NDIMS * 2) + 1)


@app.callback(  # type: ignore[misc]
    Output("heatmap-parent", "figure"),
    [
        Input(f"dropdown-{'x' if i%2==0 else 'y'}-{i//2}", "value")
        for i in range(NDIMS * 2)
    ]
    + [Input("dropdown-color", "value"), Input("color-stats-select-radios", "value")]
    + [
        Input(f"hide-switch-{'x' if i%2==0 else 'y'}-{i//2}", "on")
        for i in range(NDIMS * 2)
    ],
    # [State("url", "pathname")],
)
def make_heatmap(*args_tuple: Union[str, bool, None]) -> go.Figure:
    """Serve up the heatmap wrapped in a go.Figure instance."""
    args = list(args_tuple)
    xys: List[Optional[str]] = args[: NDIMS * 2]  # type: ignore[assignment]
    args = args[NDIMS * 2 :]
    xdims = [a for i, a in enumerate(xys) if i % 2 == 0]
    logging.info(f"Selected X-Dimensions: {xdims}")
    ydims = [a for i, a in enumerate(xys) if i % 2 != 0]
    logging.info(f"Selected Y-Dimensions: {ydims}")

    zdim = args.pop(0)
    logging.info(f"Selected Z-Dimension: {zdim}")

    zstat = args.pop(0)
    logging.info(f"Selected Z-Dimension Statistic: {zstat}")

    xy_ons: List[bool] = args[: NDIMS * 2]  # type: ignore[assignment]
    args = args[NDIMS * 2 :]
    x_ons = [a for i, a in enumerate(xy_ons) if i % 2 == 0]
    logging.info(f"On/Off X-Dimensions: {xdims}")
    y_ons: List[bool] = [a for i, a in enumerate(xy_ons) if i % 2 != 0]
    logging.info(f"On/Off Y-Dimensions: {ydims}")

    def on_off_it(dims: List[Optional[str]], ons: List[bool]) -> Iterator[str]:
        for dim, is_on in zip(dims, ons):
            if is_on and dim:
                yield dim

    # zip & clear each xdims/ydims for ons
    xdims = list(on_off_it(xdims, x_ons))
    logging.info(f"Post-Filtered Selected X-Dimensions: {xdims}")
    ydims = list(on_off_it(ydims, y_ons))
    logging.info(f"Post-Filtered Selected Y-Dimensions: {ydims}")

    return go.Figure(
        data=go.Heatmap(
            z=[
                [1, None, 30, 50, 1],
                [20, 1, 60, 80, 30],
                [30, 60, 1, -10, 20],
            ],
            x=["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"],
            y=["Morning", "Afternoon", "Evening"],
            # hoverongaps=False,
        )
    )
