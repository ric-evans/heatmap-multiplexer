"""Contains utilities for handling dimensions."""


from copy import deepcopy
from typing import List, Optional, Tuple, Union

Range = Tuple[float, float]
Cat = Union[str, Range]


class Dim:
    """Wraps a single dimension's metadata."""

    def __init__(self, name: str, cats: List[Cat]) -> None:
        self.cats = cats
        self.name = name

    def __eq__(self, other: object) -> bool:
        return (
            isinstance(other, Dim)
            and self.name == other.name
            and self.name == other.name
        )

    def __repr__(self) -> str:
        return f'Dim("{self.name}", #cats={len(self.cats)})'


class Intersection:
    """Wraps the intersection of n dimensions.."""

    def __init__(self, dimcats: Optional[List[Tuple[Dim, Cat]]] = None) -> None:
        if not dimcats:
            dimcats = []
        self.dimcats = dimcats

    def deepcopy_add_cat(self, dim: Dim, cat: Cat) -> "Intersection":
        """Deep-copy self then add the new dim-cat pair to the new Intersection."""
        new = deepcopy(self)
        new.dimcats.append((dim, cat))
        return new

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Intersection) and self.dimcats == other.dimcats

    def __repr__(self) -> str:
        return f"Intersection({self.dimcats})"


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

            for cat in dims_togo[0].cats:
                _recurse_build(
                    dims_togo[1:],
                    unfinished_intersection.deepcopy_add_cat(dims_togo[0], cat),
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
                num *= len(dim.cats)
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
