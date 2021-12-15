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
from .config import CSV, CSV_BACKUP, CSV_BACKUP_META, CSV_META

ITS_A_FILLER_NAME_HACK = "<IT'S-A-FILLER>"

DOT_WIDTH = 3
SOLID_LINE_WIDTH = 3


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


def get_csv_df() -> Tuple[pd.DataFrame, str]:
    """Read the csv and return the DataFrame."""
    try:
        df = pd.read_csv(CSV, skipinitialspace=True)
        title = open(CSV_META).readlines()[-1].strip()
    except FileNotFoundError:
        df = pd.read_csv(CSV_BACKUP, skipinitialspace=True)
        title = open(CSV_BACKUP_META).readlines()[-1].strip()

    return df, title


def slider_handle_label(is_numerical: bool, is_ten_pow: bool = False) -> Dict[str, Any]:
    """Get the slider handle label dict."""
    if is_numerical:
        label = "BINS"
        if is_ten_pow:
            label = "SMART BINS"
    else:
        label = "CATEGORIES"
    return {
        "showCurrentValue": True,
        "label": label,
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


class DimControls(TypedDict):
    """Wraps dimension-related components that are grouped in the front-end."""

    name: str
    on: bool
    original_bins: int
    bins: int  # bins after tweaking per radio option
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
                if isinstance(dim_ctrl["name"], type(no_update))
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
                return -1, BinRadioOptions.TENPOW.value
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
                    "original_bins": zipped[2],
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
                        "original_bins": dim_ctrl["original_bins"],
                        "is_numerical": dim_ctrl["is_numerical"],
                        "bin_radio": dim_ctrl["bin_radio"],
                    }
                elif not dim_ctrl["on"]:
                    yield {
                        "name": dim_ctrl["name"],
                        "on": dim_ctrl["on"],
                        "bins": dim_ctrl["original_bins"],  # no want 0 or -1 b/c radio
                        "original_bins": dim_ctrl["original_bins"],
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
                "original_bins": dim_ctrl["original_bins"],
                "is_numerical": dim_heatmap[i].is_numerical,
                "bin_radio": dim_ctrl["bin_radio"],
            }


class HeatmapFigureFactory:
    """Static factory class for building the Dash Heatmap."""

    @staticmethod
    def make_fig(
        hmap: backend.heatmap.Heatmap, df: pd.DataFrame, title: str, add_lines: bool
    ) -> go.Figure:
        """Make go.Figure with the heatmap."""
        add_lines = add_lines and (len(hmap.y_dims) > 1 or len(hmap.x_dims) > 1)

        x_fillers: List[str] = []
        y_fillers: List[str] = []
        if add_lines:
            hmap.heatmap, x_fillers, y_fillers = HeatmapFigureFactory._add_fillers(hmap)

        x_tix, y_tix, z_data, z_text = HeatmapFigureFactory._format_xyz(
            {
                "df": df,
                "yxs_bin0": [d.catbins[0] for d in hmap.y_dims + hmap.x_dims],
                "yxs_10powdisc": [
                    d.is_10pow and d.is_discrete for d in hmap.y_dims + hmap.x_dims
                ],
            },
            hmap,
            add_lines,
            x_fillers,
            y_fillers,
        )
        fig = go.Figure(
            layout=go.Layout(title=title, autosize=False),
            data=go.Heatmap(
                z=z_data,
                x=x_tix,
                y=y_tix,
                # hoverongaps=False,
                hoverinfo="text",
                text=z_text,
            ),
        )

        # Format the Axes
        for func, title_text in [
            (fig.update_yaxes, " — ".join(d.name.upper() for d in hmap.y_dims)),
            (fig.update_xaxes, " — ".join(d.name.upper() for d in hmap.x_dims)),
        ]:
            func(
                # type="linear",  # may be unnecessary -> plotly auto-detects
                title={"text": title_text},
                # showgrid=True, # True by default
                # tickmode="linear",  # puts ticks/labels/grid-lines on every axis val
                # ticklabeloverflow="allow",  # put label even if it overlaps stuff
                ticklen=50,  # px length of tick line
                ticks="outside",  # draw tick outside of axis
                tickson="boundaries",  # draw ticks/grid-lines between blocks
                zeroline=False,  # unnecessary
                # showticklabels=False,
                # showspikes=True,
                spikemode="toaxis",  # draw spike (dropline) to the axis (across or marker on axis)
                spikesnap="cursor",
                # showline=True,
                spikedash="solid",
                spikethickness=1,
                # secondary_y=True,
            )

        # Add dots to empty bricks
        fig.add_trace(
            HeatmapFigureFactory._add_non_dots(hmap, add_lines, z_data, x_tix, y_tix)
        )

        # Add the reference lines
        if add_lines:
            for trace in HeatmapFigureFactory._add_reference_lines(
                hmap, x_tix, y_tix, x_fillers, y_fillers
            ):
                fig.add_trace(trace)

        return fig

    class DataSetCache(TypedDict):
        """A local store for commonly accessed dataset things."""

        df: pd.DataFrame
        yxs_bin0: List[backend.dimensions.CatBin]
        yxs_10powdisc: List[bool]

    @staticmethod
    def _add_fillers(
        hmap: backend.heatmap.Heatmap,
    ) -> Tuple[List[List[backend.heatmap.HeatBrick]], List[str], List[str]]:
        """Add the filler bricks to separate the data hierarchically."""
        # First add x-fillers
        with_x_fillers: List[List[backend.heatmap.HeatBrick]] = []
        x_fillers: List[str] = []
        for r, row in enumerate(hmap.heatmap):
            new_row: List[backend.heatmap.HeatBrick] = []
            for i, brick in enumerate(row):
                if hmap.x_dims:
                    if i % len(hmap.x_dims[-1].catbins) == 0 and i:
                        # HACK: unique simple labels
                        x_filler_i = i // len(hmap.x_dims[-1].catbins) - 1
                        if r == 0:  # only add row for first
                            x_fillers.append(" " * (len(x_fillers) + 1))
                        # Add filler
                        new_row.append(
                            {
                                "z": None,
                                "intersection": [
                                    {
                                        "name": ITS_A_FILLER_NAME_HACK,
                                        # HACK: unique simple labels
                                        "catbin": x_fillers[x_filler_i],
                                        "is_x": True,
                                    }
                                ],
                            }
                        )
                new_row.append(brick)
            with_x_fillers.append(new_row)
        # Next, add y-fillers
        # This has to be separate b/c the rows change length above
        with_xy_fillers: List[List[backend.heatmap.HeatBrick]] = []
        y_fillers: List[str] = []
        for r, row in enumerate(with_x_fillers):
            if r and r % len(hmap.y_dims[-1].catbins) == 0:
                # HACK: unique simple labels
                # y_filler_i = (r // len(hmap.y_dims[-1].catbins)) - 1
                # if r == 0:  # only add row for first
                y_fillers.append(" " * (len(y_fillers) + 1))
                # Add filler
                with_xy_fillers.append(
                    [
                        {
                            "z": None,
                            "intersection": [
                                {
                                    "name": ITS_A_FILLER_NAME_HACK,
                                    # HACK: unique simple labels
                                    "catbin": y_fillers[-1],
                                    "is_x": False,
                                }
                            ],
                        }
                    ]
                    * len(row)
                )
            with_xy_fillers.append(row)
        return with_xy_fillers, x_fillers, y_fillers

    @staticmethod
    def _format_xyz(
        datacache: DataSetCache,
        hmap: backend.heatmap.Heatmap,
        add_lines: bool,
        x_fillers: List[str],
        y_fillers: List[str],
    ) -> Tuple[List[str], List[str], List[List[Optional[float]]], List[List[str]]]:
        """Get the x, y, and z data (and hover text) for the heatmap."""

        def join(strings: List[str]) -> str:
            if len(strings) == 1:
                return strings[0]
            tags = {0: "<b>", 1: "("}
            end_tags = {0: "</b>", 1: ")"}
            return " ".join(
                f"{tags[i%2]}{s}{end_tags[i%2]}" for i, s in enumerate(strings)
            )

        x_tix = [
            col["intersection"][0]["catbin"]  # HACK: unique simple labels
            if col["intersection"]
            and col["intersection"][0]["name"] == ITS_A_FILLER_NAME_HACK
            else join(HeatmapFigureFactory._stringer(datacache, col, "x", short=True))
            for col in hmap.heatmap[0]
        ]
        y_tix = [
            row[0]["intersection"][0]["catbin"]  # HACK: unique simple labels
            if row[0]["intersection"]
            and row[0]["intersection"][0]["name"] == ITS_A_FILLER_NAME_HACK
            else join(
                HeatmapFigureFactory._stringer(datacache, row[0], "y", short=True)
            )
            for row in hmap.heatmap
        ]
        if add_lines:
            # add border ticks & border filler data
            if x_fillers:
                x_tix = [x_fillers[-1] + " "] + x_tix + [x_fillers[-1] + (" " * 2)]
            else:
                x_tix = [" "] + x_tix + [" " * 2]
            if y_fillers:
                y_tix = [y_fillers[-1] + " "] + y_tix + [y_fillers[-1] + (" " * 2)]
            else:
                y_tix = [" "] + y_tix + [" " * 2]
            border_brick: backend.heatmap.HeatBrick = {
                "z": None,
                "intersection": [
                    {"name": ITS_A_FILLER_NAME_HACK, "catbin": "", "is_x": False}
                ],
            }
            z_data: List[List[Optional[float]]] = [
                [brick["z"] for brick in [border_brick] + row + [border_brick]]
                for row in [[border_brick] * len(hmap.heatmap[0])]
                + hmap.heatmap
                + [[border_brick] * len(hmap.heatmap[0])]
            ]
            z_text = [
                [
                    "<br>".join(
                        [str(brick["z"])]
                        + HeatmapFigureFactory._stringer(datacache, brick)
                    )
                    if brick["intersection"]
                    and brick["intersection"][0]["name"] != ITS_A_FILLER_NAME_HACK
                    else ""
                    for brick in [border_brick] + row + [border_brick]
                ]
                for row in [[border_brick] * len(hmap.heatmap[0])]
                + hmap.heatmap
                + [[border_brick] * len(hmap.heatmap[0])]
            ]
        else:
            z_data = [[brick["z"] for brick in row] for row in hmap.heatmap]
            z_text = [
                [
                    "<br>".join(
                        [str(brick["z"])]
                        + HeatmapFigureFactory._stringer(datacache, brick)
                    )
                    for brick in row
                ]
                for row in hmap.heatmap
            ]
        return x_tix, y_tix, z_data, z_text

    @staticmethod
    def _stringer(
        datacache: DataSetCache,
        brick: backend.heatmap.HeatBrick,
        only: str = "",
        short: bool = False,
    ) -> List[str]:
        """Make strings from the HeatBrick."""
        strings = []
        for hb_inter, bin0, tenpowdisc in zip(
            brick["intersection"], datacache["yxs_bin0"], datacache["yxs_10powdisc"]
        ):
            if only == "x" and not hb_inter["is_x"]:
                continue
            elif only == "y" and hb_inter["is_x"]:
                continue
            #  Is this a numerical interval?
            if isinstance(hb_inter["catbin"], pd.Interval):
                # set the lowest bound to the min for open-lefts
                if hb_inter["catbin"].open_left and hb_inter["catbin"] == bin0:
                    l_brac = "["
                    left = datacache["df"][hb_inter["name"]].min()
                else:
                    l_brac = "[" if hb_inter["catbin"].closed_left else "("
                    left = hb_inter["catbin"].left
                r_brac = "]" if hb_inter["catbin"].closed_right else ")"
                right = hb_inter["catbin"].right

                if tenpowdisc and short:
                    strings.append(f"{left}")
                elif tenpowdisc:  # is this a 10^N and discrete value?
                    strings.append(f"{hb_inter['name']}: {left}")
                elif short:  # short format
                    if l_brac == "[" and r_brac == ")":
                        strings.append(f"{left}+")
                    else:
                        strings.append(f"{left}-{right}")
                else:  # long format
                    strings.append(
                        f"{hb_inter['name']}: {l_brac}{left:5.2f}, {right:5.2f}{r_brac}"
                    )
            # Okay, then this is categorical.
            else:
                if short:  # short format
                    strings.append(f"{hb_inter['catbin']}")
                else:  # long format
                    strings.append(f"{hb_inter['name']}: {hb_inter['catbin']}")
        return strings

    @staticmethod
    def _add_non_dots(
        hmap: backend.heatmap.Heatmap,
        add_lines: bool,
        z_data: List[List[Optional[float]]],
        x_tix: List[str],
        y_tix: List[str],
    ) -> go.Scatter:
        """Get Scatter plot of dots on each 'None' brick."""
        none_dots = []
        for r, row in enumerate(z_data):
            if add_lines:
                # skip borders
                if (not r) or r == len(z_data) - 1:
                    continue
                # skip dividers
                if hmap.y_dims and r % (len(hmap.y_dims[-1].catbins) + 1) == 0:
                    continue
            for i, data in enumerate(row):
                if add_lines:
                    # skip borders
                    if (not i) or i == len(row) - 1:
                        continue
                    # skip dividers
                    if hmap.x_dims and i % (len(hmap.x_dims[-1].catbins) + 1) == 0:
                        continue
                if data is None:
                    none_dots.append((x_tix[i], y_tix[r]))
        return go.Scatter(
            x=[n[0] for n in none_dots],
            y=[n[1] for n in none_dots],
            showlegend=False,
            mode="markers",
            marker=dict(color="black", size=DOT_WIDTH),
            hoverinfo="skip",  # just do whatever heatmap does
        )

    @staticmethod
    def _add_reference_lines(
        hmap: backend.heatmap.Heatmap,
        x_tix: List[str],
        y_tix: List[str],
        x_fillers: List[str],
        y_fillers: List[str],
    ) -> List[go.Trace]:
        """Get traces of lines to be added as reference lines: dividers & borders."""
        traces = []
        # border lines
        for x_coord in [x_tix[0], x_tix[-1]]:
            traces.append(
                go.Scatter(
                    x=[
                        x_coord,
                        x_coord,
                    ],
                    y=[
                        y_tix[0],
                        y_tix[-1],
                    ],
                    mode="lines",
                    line=go.scatter.Line(color="black", width=SOLID_LINE_WIDTH),
                    showlegend=False,
                    hoverinfo="none",
                )
            )
        for y_coord in [y_tix[0], y_tix[-1]]:
            traces.append(
                go.Scatter(
                    x=[
                        x_tix[0],
                        x_tix[-1],
                    ],
                    y=[
                        y_coord,
                        y_coord,
                    ],
                    mode="lines",
                    line=go.scatter.Line(color="black", width=SOLID_LINE_WIDTH),
                    showlegend=False,
                    hoverinfo="none",
                )
            )
        # dividers
        for i, x_coord in enumerate(x_fillers, start=1):
            if not hmap.x_dims or len(hmap.x_dims) <= 1:
                # this check isn't necessary since x_fillers only for 2+ dims
                break
            elif len(hmap.x_dims) == 2:
                width, dash = SOLID_LINE_WIDTH, "solid"
            else:  # 3+ dims
                width, dash = SOLID_LINE_WIDTH / 2, "dash"
                if i % len(hmap.x_dims[-2].catbins) == 0:
                    width, dash = SOLID_LINE_WIDTH, "solid"
            traces.append(
                go.Scatter(
                    x=[
                        x_coord,
                        x_coord,
                    ],
                    y=[
                        y_tix[0],
                        y_tix[-1],
                    ],
                    mode="lines",
                    line=go.scatter.Line(dash=dash, color="black", width=width),
                    showlegend=False,
                    hoverinfo="none",
                )
            )
        for i, y_coord in enumerate(y_fillers, start=1):
            if not hmap.y_dims or len(hmap.y_dims) <= 1:
                # this check isn't necessary since y_fillers only for 2+ dims
                break
            elif len(hmap.y_dims) == 2:
                width, dash = SOLID_LINE_WIDTH, "solid"
            else:  # 3+ dims
                width, dash = SOLID_LINE_WIDTH / 2, "dash"
                if i % len(hmap.y_dims[-2].catbins) == 0:
                    width, dash = SOLID_LINE_WIDTH, "solid"
            traces.append(
                go.Scatter(
                    x=[
                        x_tix[0],
                        x_tix[-1],
                    ],
                    y=[
                        y_coord,
                        y_coord,
                    ],
                    mode="lines",
                    line=go.scatter.Line(dash=dash, color="black", width=width),
                    showlegend=False,
                    hoverinfo="none",
                )
            )
        return traces
