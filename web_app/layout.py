"""Dash HTML-ish layout."""

import logging
from typing import Dict, List, Tuple

import dash_bootstrap_components as dbc  # type: ignore[import]
import plotly.graph_objects as go  # type: ignore[import]
from dash import dcc  # type: ignore
from dash import html
from dash.dependencies import Input, Output, State  # type: ignore

from .config import app

NDIMS = 3


def layout() -> None:
    """Serve the layout to `app`."""
    app.title = "Heatmap Multiplexer"

    # Layout
    app.layout = html.Div(
        children=[
            html.H1("Heatmap Multiplexer"),
            dcc.Graph(id="heatmap-parent"),
            html.H4("Select Dimensions"),
            dbc.Row(
                children=[
                    dbc.Col(
                        children=[
                            dbc.Row(
                                dcc.Dropdown(
                                    id=f"dropdown-y-{i}",
                                    placeholder=f"Select{' Additional' if i else ''} Y Dimension",
                                    clearable=True,
                                )
                            )
                            for i in range(NDIMS)
                        ]
                    ),
                    dbc.Col(
                        children=[
                            dbc.Row(
                                dcc.Dropdown(
                                    id=f"dropdown-x-{i}",
                                    placeholder=f"Select{' Additional' if i else ''} X Dimension",
                                    clearable=True,
                                )
                            )
                            for i in range(NDIMS)
                        ]
                    ),
                ],
            ),
            html.Hr(style={"margin-top": "4em", "margin-bottom": "1em"}),
            html.H4("Upload CSV File"),
            dcc.Upload(
                id="wbs-upload-xlsx",
                children=html.Div(["Drag and Drop or ", html.A("Select File")]),
                style={
                    "width": "100%",
                    "height": "5rem",
                    "lineHeight": "5rem",
                    "borderWidth": "1px",
                    "borderStyle": "dashed",
                    "borderRadius": "5px",
                    "textAlign": "center",
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
        Output(f"dropdown-{'x' if i%2==0 else 'y'}-{i//2}", "options")
        for i in range(NDIMS * 2)
    ],
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

    options_lists = [
        [
            {
                "label": dim,
                "value": dim,
            }
            for dim in dimensions
        ]
        for i in range(NDIMS * 2)
    ]

    return options_lists


@app.callback(  # type: ignore[misc]
    Output("heatmap-parent", "figure"),
    [
        Input(f"dropdown-{'x' if i%2==0 else 'y'}-{i//2}", "value")
        for i in range(NDIMS * 2)
    ],
    # [State("url", "pathname")],
)
def make_heatmap(*args: str) -> go.Figure:
    """Serve up the heatmap wrapped in a go.Figure instance."""
    xdims = [a for i, a in enumerate(args) if i % 2 == 0]
    logging.info(f"Selected X-Dimensions: {xdims}")
    ydims = [a for i, a in enumerate(args) if i % 2 != 0]
    logging.info(f"Selected Y-Dimensions: {ydims}")

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
