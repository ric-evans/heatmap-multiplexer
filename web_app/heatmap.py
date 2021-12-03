"""Handle Heatmap building."""


from copy import deepcopy
from typing import Callable, List, TypedDict

import pandas as pd  # type: ignore[import]

from .dimensions import Dim, Intersection, IntersectionMatrix, Range


class HeatBrick(TypedDict):
    """Wrap a single Heatmap datum/element/brick."""

    z: float


StatsFunc = Callable[[List[float]], float]


class Heatmap:
    """Build and supply a heatmap."""

    def __init__(
        self,
        csv_path: str,
        x_dims: List[Dim],
        y_dims: List[Dim],
        z_func: StatsFunc = len,  # min, max, average, etc.
    ) -> None:
        data: pd.DataFrame = pd.read_csv(csv_path)
        matrix = IntersectionMatrix(x_dims, y_dims)
        self.heatmap = self._build(data, matrix, z_func)

    @staticmethod
    def _build(
        data: pd.DataFrame,
        matrix: IntersectionMatrix,
        z_func: StatsFunc,
    ) -> List[List[HeatBrick]]:
        """Build out the 2D heatmap."""

        def brick_it(inter: Intersection) -> HeatBrick:
            temp = deepcopy(data)

            for dim, cat in inter.dimcats:
                # Categorical Dimension
                if isinstance(cat, str):
                    temp = temp.query(f"{dim} == {cat}")
                # Numerical Dimension
                elif isinstance(cat, Range):
                    temp = temp.query(
                        f"{dim} >= {cat.incl_low} and {dim} < {cat.excl_high}"
                    )
                # Error!
                else:
                    raise ValueError(f"Dim has invalid cat type: {dim=}, {cat=}")

            return {"z": z_func(data)}

        return [
            [brick_it(x_inter) for x_inter in matrix.matrix[y]]
            for y in range(len(matrix.matrix))
        ]
