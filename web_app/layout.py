"""Dash HTML-ish layout."""

import base64
import logging
import statistics as st
from copy import deepcopy
from typing import Any, Dict, Iterator, List, Optional, Tuple, TypedDict, Union, cast

import dash_bootstrap_components as dbc  # type: ignore[import]
import dash_daq as daq  # type: ignore[import]
import pandas as pd  # type: ignore[import]
import plotly.graph_objects as go  # type: ignore[import]
from dash import callback_context, dcc, html, no_update  # type: ignore
from dash.dependencies import Input, Output, State  # type: ignore

from . import dimensions, heatmap
from .config import app

CSV = "./used-data.csv"
CSV_BACKUP = "./used-data-bkp.csv"

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


def triggered() -> str:
    """Return the component that triggered the callback.

    https://dash.plotly.com/advanced-callbacks
    """
    trig = callback_context.triggered[0]["prop_id"]
    return cast(str, trig)


def get_csv_df() -> pd.DataFrame:
    """Read the csv and return the DataFrame."""
    try:
        return pd.read_csv(CSV, skipinitialspace=True)
    except FileNotFoundError:
        return pd.read_csv(CSV_BACKUP, skipinitialspace=True)


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


def slider_handle_label(use_bins: bool) -> Dict[str, Any]:
    """Get the slider handle label dict."""
    return {
        "showCurrentValue": True,
        "label": "BINS" if use_bins else "CATEGORIES",
        "style": {"width": "6rem"},
    }


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
                        min=2,  # the bin defaulting algo is only defined >=2
                        max=10,
                        value=0,
                        handleLabel=slider_handle_label(True),
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
            dcc.Loading(
                dcc.Graph(id="heatmap-parent"),
                fullscreen=True,
                style={"background": "rgba(255,255,255,0.5)"},  # float atop all
                type="graph",
            ),
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
        decrypted = base64.b64decode(base64_file).decode("utf-8")
        with open(CSV, "w") as f:
            f.write(decrypted)
    except IndexError:
        pass

    df = get_csv_df()
    logging.info(f"Dimensions Available ({len(df.columns)}): {df.columns}")

    options = [
        {
            "label": dim,
            "value": dim,
        }
        for dim in df.columns
    ]

    return [options] * ((NDIMS * 2) + 1)


@app.callback(  # type: ignore[misc]
    [Output("heatmap-parent", "figure")]
    + [Output(f"bin-slider-x-{i}", "value") for i in range(NDIMS)]
    + [Output(f"bin-slider-x-{i}", "disabled") for i in range(NDIMS)]
    + [Output(f"bin-slider-x-{i}", "handleLabel") for i in range(NDIMS)]
    + [Output(f"bin-slider-y-{i}", "value") for i in range(NDIMS)]
    + [Output(f"bin-slider-y-{i}", "disabled") for i in range(NDIMS)]
    + [Output(f"bin-slider-y-{i}", "handleLabel") for i in range(NDIMS)],
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
    xys: List[str] = [a if a else "" for a in args[: NDIMS * 2]]  # type: ignore[misc]
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

    class DimControls(TypedDict, total=False):  # pylint:disable=C0115
        name: str
        on: bool
        bins: int
        is_numerical: bool

    def log_dims(
        dim_ctrls: List[DimControls],
        header: str,
        zipped_dims: Optional[List[DimControls]] = None,
    ) -> None:
        if zipped_dims:
            assert len(dim_ctrls) == len(zipped_dims)
        for i, dim_ctrl in enumerate(dim_ctrls):
            log_name = (
                "<no-update>"
                if type(dim_ctrl["name"]) == type(no_update)
                else f"\"{dim_ctrl['name']}\""
            )
            logging.info(f"{header}: {log_name}")
            # logging.info(f"{dim_ctrl}")
            for key, val in dim_ctrl.items():
                logging.debug(f"{key}:{val}")
            if zipped_dims:
                logging.debug(f"- - - -")
                for key, val in zipped_dims[i].items():
                    logging.debug(f"{key}:{val}")

    def do_include_dim(dim_ctrl: DimControls) -> bool:
        return bool(dim_ctrl["name"] and dim_ctrl["on"])

    def originals_and_incoming(
        dim_names: List[str], ons: List[bool], bins: List[int], is_x: bool
    ) -> Tuple[List[DimControls], List[DimControls]]:
        def do_reset_bin(i: int) -> bool:
            return bool(triggered() == f"dropdown-{'x' if is_x else'y'}-{i}.value")

        originals: List[DimControls] = [
            {"name": o[0], "on": o[1], "bins": 0 if do_reset_bin(i) else o[2]}
            for i, o in enumerate(zip(dim_names, ons, bins))
        ]
        return originals, [d for d in deepcopy(originals) if do_include_dim(d)]

    # zip & clear each xdims/ydims for ons
    x_originals, x_incoming = originals_and_incoming(
        [a for i, a in enumerate(xys) if i % 2 == 0],
        [a for i, a in enumerate(xy_ons) if i % 2 == 0],
        [a for i, a in enumerate(xy_bins) if i % 2 == 0],
        True,
    )
    log_dims(x_originals, "Original Selected X-Dimensions")
    log_dims(x_incoming, "Post-Filtered Selected X-Dimensions")
    y_originals, y_incoming = originals_and_incoming(
        [a for i, a in enumerate(xys) if i % 2 != 0],
        [a for i, a in enumerate(xy_ons) if i % 2 != 0],
        [a for i, a in enumerate(xy_bins) if i % 2 != 0],
        False,
    )
    log_dims(y_originals, "Original Selected Y-Dimensions")
    log_dims(y_incoming, "Post-Filtered Selected Y-Dimensions")

    # # DATA TIME # #

    hmap = heatmap.Heatmap(
        get_csv_df(),
        [d["name"] for d in x_incoming],
        [d["name"] for d in y_incoming],
        z_stat=z_stat,
        bins={d["name"]: d["bins"] for d in x_incoming + y_incoming if d["bins"]},
    )

    # # Transform Heatmap for Front-End # #

    def outgoing(
        dims_original: List[DimControls], dim_heatmap: List[dimensions.Dim]
    ) -> Iterator[DimControls]:
        i = -1
        for dim_ctrl in dims_original:
            if not do_include_dim(dim_ctrl):
                if not dim_ctrl["name"]:
                    yield {
                        "name": no_update,
                        "on": True,
                        "bins": 0,
                        "is_numerical": no_update,
                    }
                elif not dim_ctrl["bins"]:
                    yield {
                        "name": no_update,
                        "on": no_update,
                        "bins": no_update,
                        "is_numerical": no_update,
                    }
                continue
            i += 1
            yield {
                "name": no_update,
                "on": no_update,
                # always return bins b/c might be overridden
                "bins": len(dim_heatmap[i].catbins),
                "is_numerical": dim_heatmap[i].is_numerical,
            }

    x_outgoing = list(outgoing(x_originals, hmap.x_dims))
    log_dims(x_outgoing, "Outgoing X-Dimensions (vs Originals)", x_originals)
    y_outgoing = list(outgoing(y_originals, hmap.y_dims))
    log_dims(y_outgoing, "Outgoing Y-Dimensions (vs Originals)", y_originals)

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
        + [x["bins"] for x in x_outgoing]  # bin value
        + [not x["is_numerical"] for x in x_outgoing]  # bin disabled
        + [slider_handle_label(x["is_numerical"]) for x in x_outgoing]
        + [y["bins"] for y in y_outgoing]  # bin value
        + [not y["is_numerical"] for y in y_outgoing]  # bin disabled
        + [slider_handle_label(y["is_numerical"]) for y in y_outgoing]
    )
