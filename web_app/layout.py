"""Dash HTML-ish layout."""

import base64
import logging
import re
from copy import deepcopy
from typing import Any, Dict, Iterator, List, Optional, Tuple, TypedDict, Union

import dash_bootstrap_components as dbc  # type: ignore[import]
import dash_daq as daq  # type: ignore[import]
import pandas as pd  # type: ignore[import]
import plotly.graph_objects as go  # type: ignore[import]
from dash import dcc, html, no_update  # type: ignore
from dash.dependencies import Input, Output, State  # type: ignore

from . import dash_utils as du
from . import dimensions, heatmap
from .config import CSV, NDIMS, app


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
                        handleLabel=du.slider_handle_label(True),
                        step=1,
                        size=width,
                        disabled=False,
                    ),
                    # TODO- add auto-10^x trigger
                    #  (0.0s, 0.1s, 0.2s, ...), (0s, 1s, 2s, ...), (0s, 10s, 20s, ...), etc.
                    #  start at top & decrease, until about equal with default #bins
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
                width=1,
                children=daq.BooleanSwitch(
                    # style={"width": 55},
                    id=f"hide-switch-{xy_str.lower()}-{num_id}",
                    on=True,
                    label={"label": "Visible", "style": {"margin-bottom": 0}},
                    labelPosition="top",
                ),
            ),
            dbc.Col(
                align="start",
                style={"height": "5rem"},
                children=[
                    dbc.Button(
                        id=id_,
                        children=arrow if not disabled else "-",
                        style={
                            "width": "4rem",
                            "padding": "0",
                            # "padding-left": "0",
                            # "padding-right": "0",
                            "line-height": 0,
                            "font-size": "3.5rem",
                            "margin-top": "1.3rem",
                            # "border": 0,
                            "margin-right": "1rem",
                        },
                        disabled=disabled,
                        # color="none",
                        outline=True,
                    )
                    for id_, arrow, disabled in [
                        (f"up-{xy_str.lower()}-{num_id}", "▲", num_id == 0),
                        (f"down-{xy_str.lower()}-{num_id}", "▼", num_id == NDIMS - 1),
                    ]
                ],
            ),
        ],
    )


def layout() -> None:
    """Serve the layout to `app`."""
    app.title = "Heatmap Multiplexer"

    # Layout
    app.layout = html.Div(
        children=[
            html.H1("Heatmap Multiplexer", style={"margin-bottom": 0}),
            dcc.Loading(
                dcc.Graph(
                    id="heatmap-parent",
                    style={"height": "70rem"},
                ),
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
                                            "value": du.StatsRadioOptions.COUNT.value,
                                        },
                                        {
                                            "label": "dimensional statistic",
                                            "value": du.StatsRadioOptions.STATS.value,
                                        },
                                    ],
                                    value=du.StatsRadioOptions.COUNT.value,
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
                                                            "value": du.StatsRadioOptions.MIN.value,
                                                        },
                                                        {
                                                            "label": "maximum",
                                                            "value": du.StatsRadioOptions.MAX.value,
                                                        },
                                                        {
                                                            "label": "median",
                                                            "value": du.StatsRadioOptions.MEDIAN.value,
                                                        },
                                                        {
                                                            "label": "mode",
                                                            "value": du.StatsRadioOptions.MODE.value,
                                                        },
                                                        {
                                                            "label": "mean",
                                                            "value": du.StatsRadioOptions.MEAN.value,
                                                        },
                                                        {
                                                            "label": "standard deviation",
                                                            "value": du.StatsRadioOptions.STD_DEV.value,
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
    if value == du.StatsRadioOptions.COUNT.value:
        return False, du.StatsRadioOptions.NO_RADIO_SELECT.value, ""
    elif value == du.StatsRadioOptions.STATS.value:
        return True, du.StatsRadioOptions.NO_RADIO_SELECT.value, ""
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

    df = du.get_csv_df()
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
    + [Output(f"dropdown-x-{i}", "value") for i in range(NDIMS)]
    + [Output(f"bin-slider-x-{i}", "value") for i in range(NDIMS)]
    + [Output(f"bin-slider-x-{i}", "disabled") for i in range(NDIMS)]
    + [Output(f"bin-slider-x-{i}", "handleLabel") for i in range(NDIMS)]
    + [Output(f"dropdown-y-{i}", "value") for i in range(NDIMS)]
    + [Output(f"bin-slider-y-{i}", "value") for i in range(NDIMS)]
    + [Output(f"bin-slider-y-{i}", "disabled") for i in range(NDIMS)]
    + [Output(f"bin-slider-y-{i}", "handleLabel") for i in range(NDIMS)],
    # Inputs
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
    ]
    + [
        Input(f"up-{'x' if i%2==0 else 'y'}-{i//2}", "n_clicks")
        for i in range(NDIMS * 2)
    ]
    + [
        Input(f"down-{'x' if i%2==0 else 'y'}-{i//2}", "n_clicks")
        for i in range(NDIMS * 2)
    ],
    # States
    [
        State(f"bin-slider-{'x' if i%2==0 else 'y'}-{i//2}", "disabled")
        for i in range(NDIMS * 2)
    ],
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
        z_stat = {"dim_name": zdim, "stats_func": du.get_zstat_func(z_stat_value)}

    # get ons
    xy_ons: List[bool] = args[: NDIMS * 2]  # type: ignore[assignment]
    args = args[NDIMS * 2 :]

    # get bins
    xy_bins: List[int] = args[: NDIMS * 2]  # type: ignore[assignment]
    args = args[NDIMS * 2 :]

    # ups & downs -- we'll detect these using context since only one thing happens per callback
    args = args[NDIMS * 2 :]
    args = args[NDIMS * 2 :]

    # (STATES)

    # disabled bins
    xy_disabled_bins: List[bool] = args[: NDIMS * 2]  # type: ignore[assignment]
    args = args[NDIMS * 2 :]
    print(xy_disabled_bins)

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
                logging.debug("- - - -")
                for key, val in zipped_dims[i].items():
                    logging.debug(f"{key}:{val}")

    def originals(
        dim_names: List[str],
        ons: List[bool],
        bins: List[int],
        disableds: List[bool],
        is_x: bool,
    ) -> List[DimControls]:
        def is_new_dropdown_value(i: int) -> bool:
            return bool(du.triggered() == f"dropdown-{'x' if is_x else'y'}-{i}.value")

        originals: List[DimControls] = []
        for i, o in enumerate(zip(dim_names, ons, bins, disableds)):
            originals.append(
                {
                    "name": o[0],
                    "on": o[1],
                    "bins": 0 if is_new_dropdown_value(i) else o[2],
                    "is_numerical": not o[3],
                }
            )

        m = re.match(
            fr"^(?P<updown>up|down)-{'x' if is_x else'y'}-(?P<num_id>\d+)\.n_clicks$",
            du.triggered(),
        )
        if m:
            num_id = int(m.groupdict()["num_id"])
            if m.groupdict()["updown"] == "up":
                originals.insert(num_id - 1, originals.pop(num_id))
                logging.info(
                    f"Moving Up {'x' if is_x else'y'} #{num_id} to #{num_id - 1}"
                )
            elif m.groupdict()["updown"] == "down":
                originals.insert(num_id + 1, originals.pop(num_id))
                logging.info(
                    f"Moving Down {'x' if is_x else'y'} #{num_id} to #{num_id + 1}"
                )
            else:
                ValueError(f"Could not detect up/down button trigger: {du.triggered()}")

        return originals

    # zip & clear each xdims/ydims for ons
    x_originals = originals(
        [a for i, a in enumerate(xys) if i % 2 == 0],
        [a for i, a in enumerate(xy_ons) if i % 2 == 0],
        [a for i, a in enumerate(xy_bins) if i % 2 == 0],
        [a for i, a in enumerate(xy_disabled_bins) if i % 2 == 0],
        True,
    )
    log_dims(x_originals, "Original Selected X-Dimensions")
    y_originals = originals(
        [a for i, a in enumerate(xys) if i % 2 != 0],
        [a for i, a in enumerate(xy_ons) if i % 2 != 0],
        [a for i, a in enumerate(xy_bins) if i % 2 != 0],
        [a for i, a in enumerate(xy_disabled_bins) if i % 2 != 0],
        False,
    )
    log_dims(y_originals, "Original Selected Y-Dimensions")

    # # DATA TIME # #

    x_incoming = [d for d in deepcopy(x_originals) if d["name"] and d["on"]]
    log_dims(x_incoming, "Post-Filtered Selected X-Dimensions")
    y_incoming = [d for d in deepcopy(y_originals) if d["name"] and d["on"]]
    log_dims(y_incoming, "Post-Filtered Selected Y-Dimensions")

    df = du.get_csv_df()
    hmap = heatmap.Heatmap(
        df,
        [d["name"] for d in x_incoming],
        [d["name"] for d in y_incoming],
        z_stat=z_stat,
        bins={d["name"]: d["bins"] for d in x_incoming + y_incoming if d["bins"]},
    )

    # # Transform Heatmap for Front-End # #

    def outgoing(
        dims_original: List[DimControls],
        dim_heatmap: List[dimensions.Dim],
        dims_incoming: List[DimControls],
    ) -> Iterator[DimControls]:
        i = -1
        for dim_ctrl in dims_original:
            # Was this data even heatmapped?
            if dim_ctrl not in dims_incoming:
                if not dim_ctrl["name"]:
                    yield {
                        "name": dim_ctrl["name"],
                        "on": True,  # reset empty dim to on
                        "bins": 0,  # reset empty dim to 0
                        "is_numerical": dim_ctrl["is_numerical"],
                    }
                elif not dim_ctrl["bins"]:
                    yield {
                        "name": dim_ctrl["name"],
                        "on": dim_ctrl["on"],
                        "bins": dim_ctrl["bins"],
                        "is_numerical": dim_ctrl["is_numerical"],
                    }
                else:
                    raise ValueError(
                        f"Dim Control was excluded for unknown reason: {dim_ctrl}"
                    )
                continue
            # Update if heatmap overrode values
            i += 1
            yield {
                "name": dim_ctrl["name"],
                "on": dim_ctrl["on"],
                # always return bins b/c might be overridden
                "bins": len(dim_heatmap[i].catbins),
                "is_numerical": dim_heatmap[i].is_numerical,
            }

    x_outgoing = list(outgoing(x_originals, hmap.x_dims, x_incoming))
    log_dims(x_outgoing, "Outgoing X-Dimensions (vs Originals)", x_originals)
    y_outgoing = list(outgoing(y_originals, hmap.y_dims, y_incoming))
    log_dims(y_outgoing, "Outgoing Y-Dimensions (vs Originals)", y_originals)

    xs_bin0 = [d.catbins[0] for d in hmap.x_dims]
    ys_bin0 = [d.catbins[0] for d in hmap.y_dims]

    def make_hover(brick: heatmap.HeatBrick) -> str:
        string = f"{brick['z']} <br>"
        for (key, val), low in zip(brick["intersection"].items(), ys_bin0 + xs_bin0):
            #  (left, right]
            print(low)
            if isinstance(val, pd.Interval):
                bracket, left = "(", val.left
                if val == low:
                    bracket, left = "[", df[key].min()
                string += f"{key}: {bracket}{left:.2f}, {val.right:.2f}] <br>"
            else:
                string += f"{key}: {val} <br>"
        return string

    fig = go.Figure(
        data=go.Heatmap(
            z=[[brick["z"] for brick in row] for row in hmap.heatmap],
            # x=["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"],
            # y=["Morning", "Afternoon", "Evening"],
            # hoverongaps=False,
            hoverinfo="text",
            text=[[make_hover(brick) for brick in row] for row in hmap.heatmap],
        )
    )

    return tuple(
        [fig]
        + [x["name"] for x in x_outgoing]
        + [x["bins"] for x in x_outgoing]  # bin value
        + [not x["is_numerical"] for x in x_outgoing]  # bin disabled
        + [du.slider_handle_label(x["is_numerical"]) for x in x_outgoing]
        + [y["name"] for y in y_outgoing]
        + [y["bins"] for y in y_outgoing]  # bin value
        + [not y["is_numerical"] for y in y_outgoing]  # bin disabled
        + [du.slider_handle_label(y["is_numerical"]) for y in y_outgoing]
    )
