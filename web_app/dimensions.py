"""Contains utilities for handling dimensions."""


import math
from copy import deepcopy
from typing import Any, List, Optional, Union

import numpy as np  # type: ignore[import]
import pandas as pd  # type: ignore[import]

CatBin = Union[str, pd.Interval]


class Dim:
    """Wraps a single dimension's metadata."""

    def __init__(self, name: str, catbins: List[CatBin]) -> None:
        self.catbins = catbins
        self.name = name

        if all(isinstance(c, pd.Interval) for c in catbins):
            self.is_numerical = True
        elif all(isinstance(c, str) for c in catbins):
            self.is_numerical = False
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
        """Factory from a pandas dataframe."""

        def is_nullish(val: Any) -> bool:
            if isinstance(val, str):
                return not bool(val) or str.isspace(val)
            if isinstance(val, float):
                return math.isnan(val)
            return False

        # get a sorted unique list w/o nan values
        values = sorted({e for e in df[name].tolist() if not is_nullish(e)})
        print(values)
        if isinstance(values[0], (float, int)):
            if not num_bins:
                # use Sturges’ Rule
                num_bins = int(np.ceil(np.log2(len(df[name])) + 1))
            catbins = list(
                pd.cut(
                    np.linspace(min(values), max(values), num=num_bins),
                    num_bins,
                    include_lowest=True,
                )
            )
        else:
            catbins = values
        print(catbins)
        return Dim(name, catbins)


class DimSelection:
    """A pairing of a Dim and a category/bin."""

    def __init__(self, dim: Dim, catbin: CatBin) -> None:
        self.dim = dim
        self.catbin = catbin

    def __eq__(self, other: object) -> bool:
        return (
            isinstance(other, DimSelection)
            and self.dim == other.dim
            and self.catbin == other.catbin
        )

    def get_pandas_query(self) -> str:
        """Get the pandas-style query string."""
        if self.dim.is_numerical:
            return (
                f"{self.dim.name} > {self.catbin.left} and "  # type: ignore[union-attr]
                f"{self.dim.name} <= {self.catbin.right}"
            )

        return f'{self.dim.name} == "{self.catbin}"'


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


class IntersectionMatrixBuildException(Exception):
    """ "Raise when the IntersectionMatrix cannot be built correctly."""


class IntersectionMatrix:
    """Contains the 2D matrix of category combinations (intersections of multiple dimensions)."""

    def __init__(self, x_dims: List[Dim], y_dims: List[Dim]) -> None:
        self.matrix = self._build(x_dims, y_dims)

    @staticmethod
    def _build_list(dims: List[Dim]) -> List[Intersection]:
        """Build out the 1D Intersection list."""
        the_list: List[Intersection] = []

        def _recurse_build(
            dims_togo: List[Dim],
            unfinished_intersection: Optional[Intersection] = None,
        ) -> None:
            if not unfinished_intersection:
                unfinished_intersection = Intersection()

            if not dims_togo:
                # intersection IS finished
                the_list.append(unfinished_intersection)
                return

            for catbin in dims_togo[0].catbins:
                _recurse_build(
                    dims_togo[1:],
                    unfinished_intersection.deepcopy_add_dimselection(
                        DimSelection(dims_togo[0], catbin)
                    ),
                )

        _recurse_build(dims)
        return the_list

    @staticmethod
    def _build(x_dims: List[Dim], y_dims: List[Dim]) -> List[List[Intersection]]:
        """Build out the 2D Intersection matrix."""
        # pylint:disable=invalid-name
        x, y = 0, 0

        def super_len(dims: List[Dim]) -> int:
            num = 1
            for dim in dims:
                num *= len(dim.catbins)
            return num

        x_range, y_range = range(super_len(x_dims)), range(super_len(y_dims))
        matrix: List[List[Intersection]] = [
            [Intersection() for x in x_range] for y in y_range
        ]

        for intersection in IntersectionMatrix._build_list(y_dims + x_dims):
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
