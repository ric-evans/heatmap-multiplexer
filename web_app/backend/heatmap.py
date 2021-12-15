"""Handle Heatmap building."""


import concurrent.futures
import logging
import math
from typing import Callable, Dict, List, Optional, Tuple, TypedDict

import pandas as pd  # type: ignore[import]

from .dimensions import CatBin, Dim, Intersection, IntersectionMatrix

StatFunc = Callable[[List[float]], float]


class HeatBrickIntersection(TypedDict):
    """Wrap Heat Brick intersection."""

    name: str
    catbin: CatBin
    is_x: bool


class HeatBrick(TypedDict):
    """Wrap a single Heatmap datum/element/brick."""

    z: Optional[float]
    intersection: List[HeatBrickIntersection]


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
        logging.info("Building Heatmap...")

        def brick_it(inter: Intersection) -> HeatBrick:
            temp = df
            for dimselect in inter.dimselections:
                temp = temp.query(dimselect.get_pandas_query(), inplace=False)

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
                "intersection": [
                    {"name": ds.dim.name, "catbin": ds.catbin, "is_x": ds.is_x}
                    for ds in inter.dimselections
                ],
            }

        def do_row(
            matrix_row: List[Intersection], i: int
        ) -> Tuple[int, List[HeatBrick]]:
            return i, [brick_it(x_inter) for x_inter in matrix_row]

        if len(matrix.matrix) >= 64 or len(matrix.matrix[0]) >= 64:
            base: List[List[HeatBrick]] = [[] for y in range(len(matrix.matrix))]
            file_workers: List[concurrent.futures.Future] = []  # type: ignore[type-arg]
            # spawn
            with concurrent.futures.ThreadPoolExecutor() as pool:
                for i, matrix_row in enumerate(matrix.matrix):
                    file_workers.append(pool.submit(do_row, matrix_row, i))
            # retrieve
            for worker in concurrent.futures.as_completed(file_workers):
                i, row = worker.result()
                base[i] = row
            return base
        else:
            return [
                [brick_it(x_inter) for x_inter in matrix.matrix[y]]
                for y in range(len(matrix.matrix))
            ]
