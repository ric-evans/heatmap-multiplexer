"""Utils for the front-end."""


import enum
import logging
import re
import statistics as st
from copy import deepcopy
from typing import Any, Dict, Iterator, List, Optional, Tuple, TypedDict, cast

import pandas as pd  # type: ignore[import]
import plotly.graph_objects as go  # type: ignore[import]
from dash import callback_context, no_update  # type: ignore

from . import backend
from .config import CSV, CSV_BACKUP, NDIMS


@enum.unique
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


@enum.unique
class BinRadioOptions(enum.Enum):
    """Stores option values for the bin radio buttons."""

    RESET = -1
    NO_RADIO_SELECT = 0
    MANUAL = 1
    TENPOW = 2


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


def get_z_stat(z_stat_value: int, zdim: str) -> Optional[backend.heatmap.ZStat]:
    """Get the heatmap.ZStat dict from args."""
    if z_stat_value and zdim:
        return {"dim_name": zdim, "stats_func": Z_STAT_FUNCS[z_stat_value]}  # type: ignore[typeddict-item]
    return None


class DimControls(TypedDict, total=False):  # pylint:disable=C0115
    name: str
    on: bool
    bins: int
    is_numerical: bool
    bin_radio: int


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
        names: List[str],
        ons: List[bool],
        bins: List[int],
        disableds: List[bool],
        bin_radios: List[int],
        is_x: bool,
    ) -> List[DimControls]:
        """Get the from_dash list with augmenting as needed."""

        def get_bin(i: int, b_val: int, radio: int) -> Tuple[int, int]:
            # is new dropdown value?
            if triggered() == f"dropdown-{'x' if is_x else'y'}-{i}.value":
                return 0, BinRadioOptions.MANUAL.value
            # just now adjusted the slider
            elif triggered() == f"bin-slider-{'x' if is_x else'y'}-{i}.value":
                return b_val, BinRadioOptions.MANUAL.value
            # is reset option on?
            elif radio == BinRadioOptions.RESET.value:
                return 0, BinRadioOptions.MANUAL.value
            # # is manual option on?
            # elif radio == BinRadioOptions.MANUAL.value:
            #     return 0, radio
            # is 10^n option on? (just now or otherwise)
            elif radio == BinRadioOptions.TENPOW.value:
                return -1, radio
            else:
                return b_val, radio

        from_dash: List[DimControls] = []
        for i, zipped in enumerate(zip(names, ons, bins, disableds, bin_radios)):
            bins_val, radio_val = get_bin(i, zipped[2], zipped[4])
            from_dash.append(
                {
                    "name": zipped[0],
                    "on": zipped[1],
                    "bins": bins_val,
                    "is_numerical": not zipped[3],
                    "bin_radio": radio_val,
                }
            )

        m = re.match(
            fr"^(?P<updown>up|down)-{'x' if is_x else'y'}-(?P<num_id>\d+)\.n_clicks$",
            triggered(),
        )
        if m:
            num_id = int(m.groupdict()["num_id"])
            if m.groupdict()["updown"] == "up":
                from_dash.insert(num_id - 1, from_dash.pop(num_id))
                logging.info(
                    f"Moving Up {'x' if is_x else'y'} #{num_id} to #{num_id - 1}"
                )
            elif m.groupdict()["updown"] == "down":
                from_dash.insert(num_id + 1, from_dash.pop(num_id))
                logging.info(
                    f"Moving Down {'x' if is_x else'y'} #{num_id} to #{num_id + 1}"
                )
            else:
                ValueError(f"Could not detect up/down button trigger: {triggered()}")

        return from_dash

    @staticmethod
    def to_backend(dims_from_dash: List[DimControls]) -> List[DimControls]:
        """Get the to_backend list for Dash."""
        return [d for d in deepcopy(dims_from_dash) if d["name"] and d["on"]]

    @staticmethod
    def to_dash(
        dims_from_dash: List[DimControls],
        dim_heatmap: List[backend.dimensions.Dim],
        dims_to_backend: List[DimControls],
    ) -> Iterator[DimControls]:
        """Get the to_dash list for Dash."""
        i = -1
        for dim_ctrl in dims_from_dash:
            # Was this data even heatmapped?
            if dim_ctrl not in dims_to_backend:
                if not dim_ctrl["name"]:
                    yield {
                        "name": dim_ctrl["name"],
                        "on": True,  # reset empty dim to on
                        "bins": 0,  # reset empty dim to 0
                        "is_numerical": dim_ctrl["is_numerical"],
                        "bin_radio": dim_ctrl["bin_radio"],
                    }
                elif not dim_ctrl["on"]:
                    yield {
                        "name": dim_ctrl["name"],
                        "on": dim_ctrl["on"],
                        "bins": dim_ctrl["bins"],
                        "is_numerical": dim_ctrl["is_numerical"],
                        "bin_radio": dim_ctrl["bin_radio"],
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
                "bin_radio": dim_ctrl["bin_radio"],
            }

    @staticmethod
    def make_fig(hmap: backend.heatmap.Heatmap, df: pd.DataFrame) -> go.Figure:
        """Make go.Figure with the heatmap."""
        xs_bin0 = [d.catbins[0] for d in hmap.x_dims]
        ys_bin0 = [d.catbins[0] for d in hmap.y_dims]

        def stringer(brick: backend.heatmap.HeatBrick, only: str = "") -> List[str]:
            strings = []
            for hb_inter, bin0 in zip(brick["intersection"], ys_bin0 + xs_bin0):
                if only == "x" and not hb_inter["is_x"]:
                    continue
                elif only == "y" and hb_inter["is_x"]:
                    continue
                #  Ex: (left, right]
                if isinstance(hb_inter["catbin"], pd.Interval):
                    # set the lowest bound to the min
                    if hb_inter["catbin"].open_left and hb_inter["catbin"] == bin0:
                        l_brac = "["
                        left = df[hb_inter["name"]].min()
                    else:
                        l_brac = "[" if hb_inter["catbin"].closed_left else "("
                        left = hb_inter["catbin"].left
                    r_brac = "]" if hb_inter["catbin"].closed_right else ")"
                    right = hb_inter["catbin"].right
                    strings.append(
                        f"{hb_inter['name']}:{l_brac}{left:5.2f}, {right:5.2f}{r_brac}"
                    )
                else:
                    strings.append(f"{hb_inter['name']}:{hb_inter['catbin']}")
            return strings

        fig = go.Figure(
            data=go.Heatmap(
                z=[[brick["z"] for brick in row] for row in hmap.heatmap],
                x=[" | ".join(stringer(col, "x")) for col in hmap.heatmap[0]],
                y=[" | ".join(stringer(row[0], "y")) for row in hmap.heatmap],
                # hoverongaps=False,
                hoverinfo="text",
                text=[
                    ["<br>".join([str(brick["z"])] + stringer(brick)) for brick in row]
                    for row in hmap.heatmap
                ],
            )
        )

        return fig
