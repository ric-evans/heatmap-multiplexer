"""Utils for the front-end."""

import base64
import enum
import logging
import re
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
from .config import CSV, CSV_BACKUP, app


class StatsRadioOptions(enum.Enum):
    """Stores option values for the "statistics" radio buttons."""

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
    """Map the stat option value to its function."""
    return {  # type: ignore[return-value]
        StatsRadioOptions.MIN.value: min,
        StatsRadioOptions.MAX.value: max,
        StatsRadioOptions.MEDIAN.value: st.median,
        StatsRadioOptions.MODE.value: st.mode,
        StatsRadioOptions.MEAN.value: st.mean,
        StatsRadioOptions.STD_DEV.value: st.stdev,
    }[stat_value]


def slider_handle_label(use_bins: bool) -> Dict[str, Any]:
    """Get the slider handle label dict."""
    return {
        "showCurrentValue": True,
        "label": "BINS" if use_bins else "CATEGORIES",
        "style": {"width": "6rem"},
    }
