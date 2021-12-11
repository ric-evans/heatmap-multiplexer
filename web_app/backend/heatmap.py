"""Handle Heatmap building."""


import math
from copy import deepcopy
from typing import Callable, Dict, List, Optional, TypedDict

import pandas as pd  # type: ignore[import]

from .dimensions import Dim, Intersection, IntersectionMatrix

StatFunc = Callable[[List[float]], float]


class HeatBrick(TypedDict):
    """Wrap a single Heatmap datum/element/brick."""

    z: Optional[float]
    intersection: Dict[str, str]


class ZStat(TypedDict):
    """Wrap a dimension and its statistical function."""

    dim_name: str
    stats_func: StatFunc


class Heatmap:
    """Build and supply a heatmap."""

    def __init__(
        self,
        df: pd.DataFrame,
        x_dim_names: List[str],
        y_dim_names: List[str],
        z_stat: Optional[ZStat] = None,  # Ex: {'dim_name': 'Score', 'stats_func': min}
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
        # pylint:disable=invalid-name

        def brick_it(inter: Intersection) -> HeatBrick:
            temp = deepcopy(df)
            for dimselect in inter.dimselections:
                temp = temp.query(dimselect.get_pandas_query())

            z = None
            if z_stat:
                # Ex: [0, 1, 3, 2.5, 3] or ['apple', 'lemon', 'lemon']
                z_list = list(temp[z_stat["dim_name"]])
                if z_list:
                    # apply some function to it, like average or a lambda
                    z = z_stat["stats_func"](z_list)
                    if math.isnan(z):
                        z = None
            else:
                if len(temp):  # Does length=0 make sense here? Maybe, but leave as None
                    z = len(temp)

            return {
                "z": z,
                "intersection": {ds.dim.name: ds.catbin for ds in inter.dimselections},
            }

        return [
            [brick_it(x_inter) for x_inter in matrix.matrix[y]]
            for y in range(len(matrix.matrix))
        ]
