"""Dash HTML-ish layout."""

import logging
import statistics as st
from copy import deepcopy
from typing import Any, Dict, Iterator, List, Optional, Tuple, Union

import dash_bootstrap_components as dbc  # type: ignore[import]
import dash_daq as daq  # type: ignore[import]
import pandas as pd
import plotly.graph_objects as go  # type: ignore[import]
from dash import dcc, html, no_update  # type: ignore
from dash.dependencies import Input, Output, State  # type: ignore

from . import dimensions, heatmap
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


def get_zstat_func(stat_value: int) -> heatmap.StatFunc:
    """Map the stat value to its function."""
    return {  # type: ignore[return-value]
        MIN: min,
        MAX: max,
        MEDIAN: st.median,
        MODE: st.mode,
        MEAN: st.mean,
        STD_DEV: st.stdev,
    }[stat_value]


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
                        value=0,
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
    [Output("heatmap-parent", "figure")]
    + [Output(f"bin-slider-x-{i}", "value") for i in range(NDIMS)]
    + [Output(f"bin-slider-x-{i}", "disabled") for i in range(NDIMS)]
    + [Output(f"bin-slider-y-{i}", "value") for i in range(NDIMS)]
    + [Output(f"bin-slider-y-{i}", "disabled") for i in range(NDIMS)],
    [
        Input(f"dropdown-{'x' if i%2==0 else 'y'}-{i//2}", "value")
        for i in range(NDIMS * 2)
    ]
    + [Input("dropdown-color", "value"), Input("color-stats-select-radios", "value")]
    + [
        Input(f"hide-switch-{'x' if i%2==0 else 'y'}-{i//2}", "on")
        for i in range(NDIMS * 2)
    ]
    + [
        Input(f"bin-slider-{'x' if i%2==0 else 'y'}-{i//2}", "value")
        for i in range(NDIMS * 2)
    ],
    # [State("url", "pathname")],
)
def make_heatmap(*args_tuple: Union[str, bool, int, None]) -> Tuple[Any, ...]:
    """Serve up the heatmap wrapped in a go.Figure instance."""
    args = list(args_tuple)
    xys: List[Optional[str]] = args[: NDIMS * 2]  # type: ignore[assignment]
    args = args[NDIMS * 2 :]

    zdim: str = args.pop(0)  # type: ignore[assignment]
    logging.info(f"Selected Z-Dimension: {zdim}")
    z_stat_value: int = args.pop(0)  # type: ignore[assignment]
    logging.info(f"Selected Z-Dimension Statistic: {z_stat_value}")
    z_stat: Optional[heatmap.ZStat] = None
    if z_stat_value and zdim:
        z_stat = {"dim_name": zdim, "stats_func": get_zstat_func(z_stat_value)}

    # get ons
    xy_ons: List[bool] = args[: NDIMS * 2]  # type: ignore[assignment]
    args = args[NDIMS * 2 :]

    # get bins
    xy_bins: List[int] = args[: NDIMS * 2]  # type: ignore[assignment]
    args = args[NDIMS * 2 :]

    # # Aggregate # #

    def do_include_dim(dim_name: Optional[str], dim_on: bool) -> bool:
        return bool(dim_name and dim_on)

    def filter_them(
        dim_names: List[Optional[str]], ons: List[bool], bins: List[int]
    ) -> Tuple[List[Tuple[str, bool, int]], List[Tuple[Optional[str], bool, int]]]:
        originals = list(zip(dim_names, ons, bins))
        return list(filter(lambda d: do_include_dim(d[0], d[1]), deepcopy(originals))), originals  # type: ignore[arg-type]

    # zip & clear each xdims/ydims for ons
    x_dims, x_dims_original = filter_them(
        [a for i, a in enumerate(xys) if i % 2 == 0],
        [a for i, a in enumerate(xy_ons) if i % 2 == 0],
        [a for i, a in enumerate(xy_bins) if i % 2 == 0],
    )
    logging.info(f"Original Selected X-Dimensions: {x_dims_original}")
    logging.info(f"Post-Filtered Selected X-Dimensions: {x_dims}")
    y_dims, y_dims_original = filter_them(
        [a for i, a in enumerate(xys) if i % 2 != 0],
        [a for i, a in enumerate(xy_ons) if i % 2 != 0],
        [a for i, a in enumerate(xy_bins) if i % 2 != 0],
    )
    logging.info(f"Original Selected Y-Dimensions: {y_dims_original}")
    logging.info(f"Post-Filtered Selected Y-Dimensions: {y_dims}")

    # # DATA TIME # #

    hmap = heatmap.Heatmap(
        pd.DataFrame(),
        [d[0] for d in x_dims],
        [d[0] for d in y_dims],
        z_stat=z_stat,
        bins={d[0]: d[2] for d in x_dims + y_dims if d[2]},
    )

    # # Transform Heatmap for Front-End # #

    def outgoing(
        dims_original: List[Tuple[Optional[str], bool, int]],
        dim_heatmap: List[dimensions.Dim],
    ) -> Iterator[Tuple[int, bool]]:
        i = -1
        for name, on, nbins in dims_original:
            if not do_include_dim(name, on):
                yield no_update, no_update
                continue
            i += 1
            if nbins == len(dim_heatmap[i].catbins):
                yield no_update, not dim_heatmap[i].is_numerical
            else:
                yield len(dim_heatmap[i].catbins), not dim_heatmap[i].is_numerical

    x_outgoing = list(outgoing(x_dims_original, hmap.x_dims))
    logging.info(f"Outgoing X-Dimensions: {list(zip(x_outgoing,x_dims_original))}")
    y_outgoing = list(outgoing(y_dims_original, hmap.y_dims))
    logging.info(f"Outgoing Y-Dimensions: {list(zip(y_outgoing, y_dims_original))}")
    assert len(x_outgoing) == len(x_dims_original)
    assert len(y_outgoing) == len(y_dims_original)

    fig = go.Figure(
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

    return tuple(
        [fig]
        + [x[0] for x in x_outgoing]  # selection
        + [x[1] for x in x_outgoing]  # disabled
        + [y[0] for y in y_outgoing]  # selection
        + [y[1] for y in y_outgoing]  # disabled
    )
