"""Dash HTML-ish layout."""

import base64
import logging
from typing import Any, Dict, List, Tuple, Union

import dash_bootstrap_components as dbc  # type: ignore[import]
import dash_daq as daq  # type: ignore[import]
import visdcc  # type: ignore[import]
from dash import dcc, html  # type: ignore
from dash.dependencies import Input, Output, State  # type: ignore

from . import backend
from . import dash_utils as du
from .config import CSV, CSV_META, NDIMS, app


def make_dim_control(num_id: int, xy_str: str) -> dbc.Row:
    """Return a control box for managing/selecting a dimension."""
    dropdown_width = 45  # rem
    bin_btns_sum_width = 19  # rem

    return dbc.Row(
        style={"margin-top": "7rem"},
        children=[
            dbc.Col(
                children=[
                    dbc.Row(
                        children=[
                            dbc.Col(
                                style={"align-self": "flex-end"},
                                children=daq.Slider(  # pylint:disable=not-callable
                                    id=f"bin-slider-{xy_str.lower()}-{num_id}",
                                    min=2,  # the bin defaulting algo is only defined >=2
                                    max=20,
                                    value=0,
                                    handleLabel=du.slider_handle_label(True),
                                    step=1,
                                    size=(dropdown_width - bin_btns_sum_width - 2) * 10,
                                    disabled=False,
                                    labelPosition="bottom",
                                ),
                            ),
                            dbc.Col(
                                className="radio-group",
                                style={
                                    "width": f"{bin_btns_sum_width}rem",
                                    "padding": 0,
                                },
                                children=html.Div(
                                    id=f"bin-radios-parent-{xy_str.lower()}-{num_id}",
                                    children=dbc.RadioItems(
                                        id=f"bin-radios-{xy_str.lower()}-{num_id}",
                                        className="btn-group",
                                        inputClassName="btn-check",
                                        labelClassName="btn btn-outline-primary",
                                        labelCheckedClassName="active",
                                        options=[
                                            {
                                                "label": "manual",
                                                "value": du.BinRadioOptions.MANUAL.value,
                                            },
                                            {
                                                "label": "auto-manual",
                                                "value": du.BinRadioOptions.RESET.value,
                                            },
                                            {
                                                "label": "smart bins",
                                                "value": du.BinRadioOptions.TENPOW.value,
                                            },
                                        ],
                                        value=du.BinRadioOptions.MANUAL.value,
                                    ),
                                ),
                            ),
                        ]
                    ),
                    dbc.Row(
                        dcc.Dropdown(
                            style={"width": f"{dropdown_width}rem"},
                            id=f"dropdown-{xy_str.lower()}-{num_id}",
                            placeholder=f"Select{' Additional' if num_id else ''}"
                            f" {xy_str.upper()} Dimension",
                            clearable=True,
                        ),
                    ),
                ]
            ),
            dbc.Col(
                # align="start",
                # width=1,
                children=daq.BooleanSwitch(  # pylint:disable=not-callable
                    id=f"hide-switch-{xy_str.lower()}-{num_id}",
                    on=True,
                    label={"label": "Visible", "style": {"margin-bottom": 0}},
                    labelPosition="top",
                ),
                style={"align-self": "flex-end", "margin-left": 5, "width": "5rem"},
            ),
            dbc.Col(
                # align="start",
                style={"height": "5rem", "align-self": "flex-end", "padding": 0},
                children=[
                    dbc.Button(
                        id=id_,
                        children=arrow if not disabled else "-",
                        style={
                            "width": "3rem",
                            "padding": "0",
                            "margin": 0,
                            # "margin-left": 5,
                            # "padding-left": "0",
                            # "padding-right": "0",
                            "line-height": 0,
                            "font-size": "3rem",
                            "margin-top": "1.3rem",
                            # "border": 0,
                            # "margin-right": "1rem",
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
            # JS calls for refreshing page
            visdcc.Run_js("refresh-for-new-csv"),  # pylint: disable=E1101
            #
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
                        style={
                            "border-width": 1,
                            "border-style": "dashed",
                            "padding-left": "4rem",
                            "padding-right": "4rem",
                            "padding-bottom": "4rem",
                        },
                    ),
                    html.Div(style={"width": "1rem"}),  # space between columns
                    # dbc.Col(),
                    dbc.Col(
                        # width=5,
                        children=[html.Div("X Dimensions")]
                        + [dbc.Row(make_dim_control(i, "X")) for i in range(NDIMS)],
                        style={
                            "border-width": 1,
                            "border-style": "dashed",
                            "padding-left": "4rem",
                            "padding-right": "4rem",
                            "padding-bottom": "4rem",
                        },
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
        ],
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
    + [Output("dropdown-color", "options"), Output("refresh-for-new-csv", "run")],
    [Input("wbs-upload-xlsx", "contents"), Input("wbs-upload-xlsx", "filename")]
    # [State("url", "pathname")],
)
def upload_csv(contents: str, filename: str) -> Tuple[Union[List[Dict[str, str]], str]]:
    """Serve up the heatmap wrapped in a go.Figure instance."""
    try:
        base64_file = contents.split(",")[1]
        decrypted = base64.b64decode(base64_file).decode("utf-8")
        with open(CSV, "w") as f:
            f.write(decrypted)
        with open(CSV_META, "w") as f:
            f.write(filename)
    except IndexError:
        pass

    df, _ = du.get_csv_df()
    logging.info(f"Dimensions Available ({len(df.columns)}): {df.columns}")

    options = [
        {
            "label": dim,
            "value": dim,
        }
        for dim in df.columns
    ]

    if du.triggered() == "wbs-upload-xlsx.contents":
        return tuple([du.no_update] * ((NDIMS * 2) + 1) + ["location.reload();"])  # type: ignore[return-value]
    else:
        return tuple([options] * ((NDIMS * 2) + 1) + [du.no_update])  # type: ignore[return-value]


@app.callback(  # type: ignore[misc]
    [Output("heatmap-parent", "figure")]
    + [Output(f"dropdown-x-{i}", "value") for i in range(NDIMS)]
    + [Output(f"bin-slider-x-{i}", "value") for i in range(NDIMS)]
    + [Output(f"bin-radios-x-{i}", "value") for i in range(NDIMS)]
    + [Output(f"bin-slider-x-{i}", "disabled") for i in range(NDIMS)]
    + [Output(f"bin-radios-parent-x-{i}", "hidden") for i in range(NDIMS)]
    + [Output(f"bin-slider-x-{i}", "handleLabel") for i in range(NDIMS)]
    + [Output(f"dropdown-y-{i}", "value") for i in range(NDIMS)]
    + [Output(f"bin-slider-y-{i}", "value") for i in range(NDIMS)]
    + [Output(f"bin-radios-y-{i}", "value") for i in range(NDIMS)]
    + [Output(f"bin-slider-y-{i}", "disabled") for i in range(NDIMS)]
    + [Output(f"bin-radios-parent-y-{i}", "hidden") for i in range(NDIMS)]
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
    ]
    + [
        Input(f"bin-radios-{'x' if i%2==0 else 'y'}-{i//2}", "value")
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
    logging.warning(du.triggered())

    args = list(args_tuple)
    xys: List[str] = [a if a else "" for a in args[: NDIMS * 2]]  # type: ignore[misc]
    args = args[NDIMS * 2 :]

    zdim: str = args.pop(0)  # type: ignore[assignment]
    logging.info(f"Selected Z-Dimension: {zdim}")
    z_stat_value: int = args.pop(0)  # type: ignore[assignment]
    logging.info(f"Selected Z-Dimension Statistic: {z_stat_value}")

    # get ons
    xy_ons: List[bool] = args[: NDIMS * 2]  # type: ignore[assignment]
    args = args[NDIMS * 2 :]

    # get bins
    xy_bins: List[int] = args[: NDIMS * 2]  # type: ignore[assignment]
    args = args[NDIMS * 2 :]

    # ups & downs -- we'll detect these using context since only one thing happens per callback
    args = args[NDIMS * 2 :]
    args = args[NDIMS * 2 :]

    # bin radios
    xy_bin_radios: List[int] = args[: NDIMS * 2]  # type: ignore[assignment]
    args = args[NDIMS * 2 :]

    # (STATES)

    # disabled bins
    xy_disabled_bins: List[bool] = args[: NDIMS * 2]  # type: ignore[assignment]
    args = args[NDIMS * 2 :]

    # # Aggregate # #

    # zip & clear each xdims/ydims for ons
    x_from_dash = du.DimControlUtils.from_dash(
        [a for i, a in enumerate(xys) if i % 2 == 0],
        [a for i, a in enumerate(xy_ons) if i % 2 == 0],
        [a for i, a in enumerate(xy_bins) if i % 2 == 0],
        [a for i, a in enumerate(xy_disabled_bins) if i % 2 == 0],
        [a for i, a in enumerate(xy_bin_radios) if i % 2 == 0],
        True,
    )
    du.DimControlUtils.log_dims(x_from_dash, "From_dash Selected X-Dimensions")
    y_from_dash = du.DimControlUtils.from_dash(
        [a for i, a in enumerate(xys) if i % 2 != 0],
        [a for i, a in enumerate(xy_ons) if i % 2 != 0],
        [a for i, a in enumerate(xy_bins) if i % 2 != 0],
        [a for i, a in enumerate(xy_disabled_bins) if i % 2 != 0],
        [a for i, a in enumerate(xy_bin_radios) if i % 2 != 0],
        False,
    )
    du.DimControlUtils.log_dims(y_from_dash, "From_dash Selected Y-Dimensions")

    # # DATA TIME # #

    x_to_backend = du.DimControlUtils.to_backend(x_from_dash)
    du.DimControlUtils.log_dims(x_to_backend, "Post-Filtered Selected X-Dimensions")
    y_to_backend = du.DimControlUtils.to_backend(y_from_dash)
    du.DimControlUtils.log_dims(y_to_backend, "Post-Filtered Selected Y-Dimensions")

    df, title = du.get_csv_df()
    hmap = backend.heatmap.Heatmap(
        df,
        [d["name"] for d in x_to_backend],
        [d["name"] for d in y_to_backend],
        z_stat=du.get_z_stat(z_stat_value, zdim),
        bins={d["name"]: d["bins"] for d in x_to_backend + y_to_backend if d["bins"]},
    )

    # # Transform Heatmap for Front-End # #

    x_to_dash = list(du.DimControlUtils.to_dash(x_from_dash, hmap.x_dims, x_to_backend))
    du.DimControlUtils.log_dims(
        x_to_dash, "To_dash X-Dimensions (vs From_dash)", x_from_dash
    )
    y_to_dash = list(du.DimControlUtils.to_dash(y_from_dash, hmap.y_dims, y_to_backend))
    du.DimControlUtils.log_dims(
        y_to_dash, "To_dash Y-Dimensions (vs From_dash)", y_from_dash
    )

    return tuple(
        [du.DimControlUtils.make_fig(hmap, df, title)]
        #
        + [x["name"] for x in x_to_dash]
        + [x["bins"] for x in x_to_dash]  # bin value
        + [x["bin_radio"] for x in x_to_dash]
        + [not x["is_numerical"] for x in x_to_dash]  # bin disabled
        + [not x["is_numerical"] for x in x_to_dash]  # bin radio hidden
        + [du.slider_handle_label(x["is_numerical"]) for x in x_to_dash]
        #
        + [y["name"] for y in y_to_dash]
        + [y["bins"] for y in y_to_dash]  # bin value
        + [y["bin_radio"] for y in y_to_dash]
        + [not y["is_numerical"] for y in y_to_dash]  # bin disabled
        + [not y["is_numerical"] for y in y_to_dash]  # bin radio hidden
        + [du.slider_handle_label(y["is_numerical"]) for y in y_to_dash]
    )
