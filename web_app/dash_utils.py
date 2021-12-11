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
    return


def slider_handle_label(use_bins: bool) -> Dict[str, Any]:
    """Get the slider handle label dict."""
    return {
        "showCurrentValue": True,
        "label": "BINS" if use_bins else "CATEGORIES",
        "style": {"width": "6rem"},
    }


# --------------------------------------------------------------------------------------


Z_STAT_FUNCS = {
    StatsRadioOptions.MIN.value: min,
    StatsRadioOptions.MAX.value: max,
    StatsRadioOptions.MEDIAN.value: st.median,
    StatsRadioOptions.MODE.value: st.mode,
    StatsRadioOptions.MEAN.value: st.mean,
    StatsRadioOptions.STD_DEV.value: st.stdev,
}


def get_z_stat(z_stat_value: int, zdim: str) -> Optional[heatmap.ZStat]:
    """Get the heatmap.ZStat dict from args."""
    if z_stat_value and zdim:
        return {"dim_name": zdim, "stats_func": Z_STAT_FUNCS[z_stat_value]}  # type: ignore[typeddict-item]
    return None


class DimControls(TypedDict, total=False):  # pylint:disable=C0115
    name: str
    on: bool
    bins: int
    is_numerical: bool


class DimControlUtils:
    """Utils for creating/managing DimControls."""

    @staticmethod
    def log_dims(
        dim_ctrls: List[DimControls],
        header: str,
        zipped_dims: Optional[List[DimControls]] = None,
    ) -> None:
        """Log the list(s) of dim controls."""
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

    @staticmethod
    def from_dash(
        dim_names: List[str],
        ons: List[bool],
        bins: List[int],
        disableds: List[bool],
        is_x: bool,
    ) -> List[DimControls]:
        """Get the original list with augmenting as needed."""

        def is_new_dropdown_value(i: int) -> bool:
            return bool(triggered() == f"dropdown-{'x' if is_x else'y'}-{i}.value")

        originals: List[DimControls] = []
        for i, zipped in enumerate(zip(dim_names, ons, bins, disableds)):
            originals.append(
                {
                    "name": zipped[0],
                    "on": zipped[1],
                    "bins": 0 if is_new_dropdown_value(i) else zipped[2],
                    "is_numerical": not zipped[3],
                }
            )

        m = re.match(
            fr"^(?P<updown>up|down)-{'x' if is_x else'y'}-(?P<num_id>\d+)\.n_clicks$",
            triggered(),
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
                ValueError(f"Could not detect up/down button trigger: {triggered()}")

        return originals

    @staticmethod
    def to_backend(
        dims_original: List[DimControls],
    ) -> List[DimControls]:
        """Get the to_backend list for Dash."""
        return [d for d in deepcopy(dims_original) if d["name"] and d["on"]]

    @staticmethod
    def to_dash(
        dims_original: List[DimControls],
        dim_heatmap: List[dimensions.Dim],
        dims_to_backend: List[DimControls],
    ) -> Iterator[DimControls]:
        """Get the outgoing list for Dash."""
        i = -1
        for dim_ctrl in dims_original:
            # Was this data even heatmapped?
            if dim_ctrl not in dims_to_backend:
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

    @staticmethod
    def make_fig(hmap: heatmap.Heatmap, df: pd.DataFrame) -> go.Figure:
        """Make go.Figure with the heatmap."""
        xs_bin0 = [d.catbins[0] for d in hmap.x_dims]
        ys_bin0 = [d.catbins[0] for d in hmap.y_dims]

        def make_hover(brick: heatmap.HeatBrick) -> str:
            string = f"{brick['z']} <br>"
            for (key, val), low in zip(
                brick["intersection"].items(), ys_bin0 + xs_bin0
            ):
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

        return fig
