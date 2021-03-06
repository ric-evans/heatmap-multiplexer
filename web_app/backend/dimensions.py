"""Contains utilities for handling dimensions."""


import logging
import math
from copy import deepcopy
from typing import Any, List, Optional, Tuple, TypedDict, Union

import numpy as np  # type: ignore[import]
import pandas as pd  # type: ignore[import]

CatBin = Union[str, pd.Interval]


def analyze_data_type(data_list: List[Any]) -> Tuple[List[Any], bool]:
    """Look at the data, remove any null-like values, sort, and tell if it's numerical."""

    def is_nullish(val: Any) -> bool:
        if isinstance(val, str):
            return not bool(val) or str.isspace(val)
        if isinstance(val, float):
            return math.isnan(val)
        return False

    uniques = sorted({e for e in data_list if not is_nullish(e)})
    is_numerical = isinstance(uniques[0], (float, int))  # sorted, so only need first
    return uniques, is_numerical


class Dim:
    """Wraps a single dimension's metadata."""

    def __init__(
        self,
        name: str,
        catbins: List[CatBin],
        is_10pow: bool = False,
        is_discrete: bool = True,
    ) -> None:
        self.catbins = catbins
        self.name = name
        self.is_10pow = is_10pow

        if all(isinstance(c, pd.Interval) for c in catbins):
            self.is_numerical = True
            self.is_discrete = is_discrete
        elif all(isinstance(c, str) for c in catbins):
            self.is_numerical = False
            self.is_discrete = True
        else:
            raise ValueError(f"Dim has invalid catbin type(s): {name=}, {catbins=}")

    def __eq__(self, other: object) -> bool:
        return (
            isinstance(other, Dim)
            and self.name == other.name
            and self.catbins == other.catbins
        )

    def __repr__(self) -> str:
        return f'Dim("{self.name}", #catbins={len(self.catbins)})'

    @staticmethod
    def from_pandas_df(
        name: str, df: pd.DataFrame, num_bins: Optional[int] = None
    ) -> "Dim":
        """Factory from a pandas dataframe.

        All intervals are left-inclusive: [a,b)
        """
        is_10pow = False

        def sturges_rule() -> int:
            """Use Sturges??? Rule, calculated by cardinality of set."""
            return int(np.ceil(np.log2(len(df[name])) + 1))

        def get_cut(num: int) -> List[pd.Interval]:
            # print(max(values))
            # print(min(values))
            return list(
                pd.cut(
                    np.linspace(min(unique_values), max(unique_values), num=num),
                    num,
                    include_lowest=True,
                    right=False,
                )
            )

        def dist(one: int, two: int) -> float:
            """Get the "distance" between the two, calculated by degree of similarity."""
            return max(one, two) / min(one, two)
            # return np.abs(one - two)  # type: ignore[no-any-return]

        class TenPowException(Exception):
            """Raise when 10-Pow algo fails."""

        def get_10pow() -> List[pd.Interval]:
            logging.info(f"10^N Binning ({name})...")
            sturges = sturges_rule()
            # get starting power by rounding up "largest" value to nearest power of 10
            largest_value = max(np.abs(max(unique_values)), np.abs(min(unique_values)))
            power = int(np.ceil(np.log10(largest_value)))
            prev = None
            for power_offset in range(7):  # 7; think: low-range high-value; 2000, 2001
                width = 10 ** (power - power_offset)
                temp = list(
                    pd.interval_range(
                        start=(min(unique_values) // width) * width,  # 5278 -> 5000
                        end=max(unique_values) + width,  # 6001 -> 7000
                        freq=width,
                        closed="left",
                    )
                )
                logging.debug(f"{sturges} vs {len(temp)} ({dist(len(temp), sturges)})")
                # if new dist is now greater than last, use last
                if prev and dist(len(temp), sturges) > dist(len(prev), sturges):
                    return prev
                prev = temp
            raise TenPowException()

        def is_discrete_by_binning(num: int) -> bool:
            """If pd.cut() places multiple values in the same bin, then it's not discrete."""
            print(pd.cut(unique_values, num, include_lowest=True, right=False))
            return (
                len(pd.cut(unique_values, num, include_lowest=True, right=False)) <= num
            )

        # get a sorted unique list w/o nan values
        unique_values, is_numerical = analyze_data_type(df[name].tolist())
        # Numerical
        if is_numerical:
            # use default # of bins
            if not num_bins:
                catbins = get_cut(sturges_rule())
            # use 10-pow calculated bins
            elif num_bins == -1:
                try:
                    catbins = get_10pow()
                    is_10pow = True  # only mark true if this algo works
                except TenPowException:
                    catbins = get_cut(sturges_rule())
            # use given # of bins
            else:
                catbins = get_cut(num_bins)
            # Did the binning make this data effectively discrete?
            is_discrete = is_discrete_by_binning(len(catbins))
        # Categorical
        else:
            catbins = unique_values
            is_discrete = True

        logging.info(f"Cat-Bins: {catbins}")
        return Dim(name, catbins, is_10pow, is_discrete)


class DimSelection:
    """A pairing of a Dim and a category/bin."""

    def __init__(self, dim: Dim, catbin: CatBin, is_x: bool) -> None:
        self.dim = dim
        self.catbin = catbin
        self.is_x = is_x

    def __eq__(self, other: object) -> bool:
        return (
            isinstance(other, DimSelection)
            and self.dim == other.dim
            and self.catbin == other.catbin
            and self.is_x == other.is_x
        )

    def get_pandas_query(self) -> str:
        """Get the pandas-style query string."""
        if self.dim.is_numerical:
            return (
                f"{self.dim.name} {'>=' if self.catbin.closed_left else '>'} "  # type: ignore[union-attr]
                f"{self.catbin.left} and "
                f"{self.dim.name} {'<=' if self.catbin.closed_right else '<'} "
                f"{self.catbin.right}"
            )

        return f'{self.dim.name} == "{self.catbin}"'

    def __repr__(self) -> str:
        """Get repr string."""
        return f"DimSelection({self.dim=}, {self.catbin=}, {self.is_x=})"


class Intersection:
    """Wraps the intersection of n dimensions.."""

    def __init__(self, dimselections: Optional[List[DimSelection]] = None) -> None:
        if not dimselections:
            dimselections = []
        self.dimselections = dimselections

    def deepcopy_add_dimselection(self, dimselection: DimSelection) -> "Intersection":
        """Deep-copy self then add the new DimSelection to a new Intersection."""
        new = deepcopy(self)
        new.dimselections.append(dimselection)
        return new

    def __eq__(self, other: object) -> bool:
        return (
            isinstance(other, Intersection)
            and self.dimselections == other.dimselections
        )

    def __repr__(self) -> str:
        return f"Intersection({self.dimselections})"


# ---------------------------------------------------------------------------------------


def super_len(dims: List[Dim]) -> int:
    num = 1
    for dim in dims:
        num *= len(dim.catbins)
    return num


class IntersectionMatrixBuildException(Exception):
    """ "Raise when the IntersectionMatrix cannot be built correctly."""


class IntersectionMatrix:
    """Contains the 2D matrix of category combinations (intersections of multiple dimensions)."""

    def __init__(self, x_dims: List[Dim], y_dims: List[Dim]) -> None:
        self.matrix = self._build(x_dims, y_dims)

    @staticmethod
    def _build_list(x_dims: List[Dim], y_dims: List[Dim]) -> List[Intersection]:
        """Build out the 1D Intersection list."""
        the_list: List[Intersection] = []

        class DimXY(TypedDict):  # pylint:disable=missing-class-docstring
            dim: Dim
            is_x: bool

        def _recurse_build(
            dims_togo: List[DimXY],
            unfinished_intersection: Optional[Intersection] = None,
        ) -> None:
            if not unfinished_intersection:
                unfinished_intersection = Intersection()

            if not dims_togo:
                # intersection IS finished
                the_list.append(unfinished_intersection)
                return

            for catbin in dims_togo[0]["dim"].catbins:
                _recurse_build(
                    dims_togo[1:],
                    unfinished_intersection.deepcopy_add_dimselection(
                        DimSelection(dims_togo[0]["dim"], catbin, dims_togo[0]["is_x"])
                    ),
                )

        y_dimxys: List[DimXY] = [{"dim": d, "is_x": False} for d in y_dims]
        x_dimxys: List[DimXY] = [{"dim": d, "is_x": True} for d in x_dims]
        _recurse_build(y_dimxys + x_dimxys)
        return the_list

    @staticmethod
    def _build(x_dims: List[Dim], y_dims: List[Dim]) -> List[List[Intersection]]:
        """Build out the 2D Intersection matrix."""
        # pylint:disable=invalid-name
        x, y = 0, 0

        x_range, y_range = range(super_len(x_dims)), range(super_len(y_dims))
        matrix: List[List[Intersection]] = [
            [Intersection() for x in x_range] for y in y_range
        ]

        for intersection in IntersectionMatrix._build_list(x_dims, y_dims):
            if x == len(matrix[0]):
                x = 0
                y += 1
            matrix[y][x] = intersection
            x += 1

        if x != len(matrix[0]) and y != len(matrix) - 1:
            raise IntersectionMatrixBuildException(
                f"{len(matrix[0])}x{len(matrix)} matrix did not complete, "
                f"last element: ({x=},{y=})"
            )

        return matrix
