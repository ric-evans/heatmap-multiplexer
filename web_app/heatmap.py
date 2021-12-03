"""Handle Heatmap building."""


from copy import deepcopy
from typing import Callable, Dict, List, Optional, TypedDict

import pandas as pd  # type: ignore[import]

from .dimensions import Dim, Intersection, IntersectionMatrix


class HeatBrick(TypedDict):
    """Wrap a single Heatmap datum/element/brick."""

    z: float


StatsFunc = Callable[[List[float]], float]


class Heatmap:
    """Build and supply a heatmap."""

    def __init__(
        self,
        csv_path: str,
        x_dims: List[str],
        y_dims: List[str],
        z_func: StatsFunc = len,  # min, max, average, etc.
        bins: Optional[Dict[str, int]] = None,
    ) -> None:
        if not bins:
            bins = {}

        df: pd.DataFrame = pd.read_csv(csv_path)
        matrix = IntersectionMatrix(
            [Dim.from_pandas_df(x, df, bins.get(x)) for x in x_dims],
            [Dim.from_pandas_df(y, df, bins.get(y)) for y in y_dims],
        )
        self.heatmap = self._build(df, matrix, z_func)

    @staticmethod
    def _build(
        df: pd.DataFrame,
        matrix: IntersectionMatrix,
        z_func: StatsFunc,
    ) -> List[List[HeatBrick]]:
        """Build out the 2D heatmap."""

        def brick_it(inter: Intersection) -> HeatBrick:
            temp = deepcopy(df)

            for dimselect in inter.dimselections:
                # Categorical Dimension
                if isinstance(dimselect.catbin, str):
                    temp = temp.query(f"{dimselect.dim} == {dimselect.catbin}")
                # Numerical Dimension
                elif isinstance(dimselect.catbin, pd.Interval):
                    temp = temp.query(
                        f"{dimselect.dim} >= {dimselect.catbin.incl_low} and "
                        f"{dimselect.dim} < {dimselect.catbin.excl_high}"
                    )
                # Error!
                else:
                    raise ValueError(
                        f"DimSelection has invalid catbin type: {dimselect.dim=}, {dimselect.catbin=}"
                    )

            return {"z": z_func(df)}

        return [
            [brick_it(x_inter) for x_inter in matrix.matrix[y]]
            for y in range(len(matrix.matrix))
        ]
