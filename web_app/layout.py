"""Dash HTML-ish layout."""

import dash_bootstrap_components as dbc  # type: ignore[import]
from dash import dcc  # type: ignore
from dash import html  # type: ignore

from .config import app


def layout() -> None:
    """Serve the layout to `app`."""
    app.title = "Heatmap Multiplexer"

    # Layout
    app.layout = html.Div()
