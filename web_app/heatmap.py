"""Handle Heatmap building."""


from copy import deepcopy
from typing import Callable, Dict, List, Optional, TypedDict

import pandas as pd  # type: ignore[import]

from .dimensions import Dim, Intersection, IntersectionMatrix


class HeatBrick(TypedDict):
    """Wrap a single Heatmap datum/element/brick."""

    z: float
    intersection: Dict[str, str]


class ZStat(TypedDict):
    """Wrap a dimension and its statistical function."""

    dim_name: str
    stats_func: Callable[[List[float]], float]


class Heatmap:
    """Build and supply a heatmap."""

    def __init__(
        self,
        df: pd.DataFrame,
        x_dim_names: List[str],
        y_dim_names: List[str],
        z_stat: Optional[ZStat] = None,  # Ex: {'Score': min}, {'Time': max}, etc.
        bins: Optional[Dict[str, int]] = None,
    ) -> None:
        if not bins:
            bins = {}

        self.x_dims = [Dim.from_pandas_df(x, df, bins.get(x)) for x in x_dim_names]
        self.y_dims = [Dim.from_pandas_df(y, df, bins.get(y)) for y in y_dim_names]
        matrix = IntersectionMatrix(self.x_dims, self.y_dims)

        self.heatmap = self._build(df, matrix, z_stat)

    @staticmethod
    def _build(
        df: pd.DataFrame, matrix: IntersectionMatrix, z_stat: Optional[ZStat]
    ) -> List[List[HeatBrick]]:
        """Build out the 2D heatmap."""

        def brick_it(inter: Intersection) -> HeatBrick:
            temp = deepcopy(df)

            for dimselect in inter.dimselections:
                temp = temp.query(dimselect.get_numpy_query())

            if z_stat:
                # Ex: [0, 1, 3, 2.5, 3] or ['apple', 'lemon', 'lemon']
                z_series = temp[z_stat["dim_name"]]
                # apply some function to it, like average or a lambda
                z = z_stat["stats_func"](z_series)  # pylint:disable=invalid-name
            else:
                z = len(df)  # pylint:disable=invalid-name

            return {
                "z": z,
                "intersection": {
                    ds.dim.name: str(ds.catbin) for ds in inter.dimselections
                },
            }

        return [
            [brick_it(x_inter) for x_inter in matrix.matrix[y]]
            for y in range(len(matrix.matrix))
        ]
