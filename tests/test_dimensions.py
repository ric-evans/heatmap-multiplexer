"""Tests for dimensions.py"""

import sys
from typing import List

sys.path.append(".")
from web_app.dimensions import Dim, Intersection, IntersectionMatrix  # noqa: E402


def test_00_intersection_matrix_null() -> None:
    """Test IntersectionMatrix w/ no dimensions -> empty 1x1."""
    assert IntersectionMatrix([], []).matrix == [[Intersection()]]


def test_01_intersection_matrix_no_x() -> None:
    """Test IntersectionMatrix w/ no x-dim(s) -> 1xN."""
    # pylint:disable=invalid-name

    # Y's:
    a = Dim("A", ["A0", "A1"])
    b = Dim("B", ["B0", "B1", "B2"])

    matrix = [
        [Intersection([(a, a.cats[0]), (b, b.cats[0])])],
        [Intersection([(a, a.cats[0]), (b, b.cats[1])])],
        [Intersection([(a, a.cats[0]), (b, b.cats[2])])],
        [Intersection([(a, a.cats[1]), (b, b.cats[0])])],
        [Intersection([(a, a.cats[1]), (b, b.cats[1])])],
        [Intersection([(a, a.cats[1]), (b, b.cats[2])])],
    ]

    assert IntersectionMatrix([], [a, b]).matrix == matrix


def test_02_intersection_matrix_no_y() -> None:
    """Test IntersectionMatrix w/ no y-dim(s) -> Nx1."""
    # pylint:disable=invalid-name

    # X's
    c = Dim("C", ["C0", "C1", "C2", "C3"])
    d = Dim("D", ["D0", "D1"])

    matrix = [
        [
            Intersection([(c, c.cats[0]), (d, d.cats[0])]),
            Intersection([(c, c.cats[0]), (d, d.cats[1])]),
            Intersection([(c, c.cats[1]), (d, d.cats[0])]),
            Intersection([(c, c.cats[1]), (d, d.cats[1])]),
            Intersection([(c, c.cats[2]), (d, d.cats[0])]),
            Intersection([(c, c.cats[2]), (d, d.cats[1])]),
            Intersection([(c, c.cats[3]), (d, d.cats[0])]),
            Intersection([(c, c.cats[3]), (d, d.cats[1])]),
        ]
    ]

    assert IntersectionMatrix([c, d], []).matrix == matrix


def test_03_intersection_matrix_1d_x() -> None:
    """Test IntersectionMatrix w/ 1 x-dim -> nxN."""
    # pylint:disable=invalid-name

    # X's
    d = Dim("D", ["D0", "D1"])
    # Y's:
    a = Dim("A", ["A0", "A1"])
    b = Dim("B", ["B0", "B1", "B2"])

    matrix = [
        [
            Intersection([(a, a.cats[0]), (b, b.cats[0]), (d, d.cats[0])]),
            Intersection([(a, a.cats[0]), (b, b.cats[0]), (d, d.cats[1])]),
        ],
        [
            Intersection([(a, a.cats[0]), (b, b.cats[1]), (d, d.cats[0])]),
            Intersection([(a, a.cats[0]), (b, b.cats[1]), (d, d.cats[1])]),
        ],
        [
            Intersection([(a, a.cats[0]), (b, b.cats[2]), (d, d.cats[0])]),
            Intersection([(a, a.cats[0]), (b, b.cats[2]), (d, d.cats[1])]),
        ],
        [
            Intersection([(a, a.cats[1]), (b, b.cats[0]), (d, d.cats[0])]),
            Intersection([(a, a.cats[1]), (b, b.cats[0]), (d, d.cats[1])]),
        ],
        [
            Intersection([(a, a.cats[1]), (b, b.cats[1]), (d, d.cats[0])]),
            Intersection([(a, a.cats[1]), (b, b.cats[1]), (d, d.cats[1])]),
        ],
        [
            Intersection([(a, a.cats[1]), (b, b.cats[2]), (d, d.cats[0])]),
            Intersection([(a, a.cats[1]), (b, b.cats[2]), (d, d.cats[1])]),
        ],
    ]

    assert IntersectionMatrix([d], [a, b]).matrix == matrix


def test_04_intersection_matrix_1d_y() -> None:
    """Test IntersectionMatrix w/ 1 y-dim -> Nxn."""
    # pylint:disable=invalid-name

    # X's
    c = Dim("C", ["C0", "C1", "C2", "C3"])
    d = Dim("D", ["D0", "D1"])
    # Y's:
    a = Dim("A", ["A0", "A1"])

    matrix = [
        [
            Intersection([(a, a.cats[0]), (c, c.cats[0]), (d, d.cats[0])]),
            Intersection([(a, a.cats[0]), (c, c.cats[0]), (d, d.cats[1])]),
            Intersection([(a, a.cats[0]), (c, c.cats[1]), (d, d.cats[0])]),
            Intersection([(a, a.cats[0]), (c, c.cats[1]), (d, d.cats[1])]),
            Intersection([(a, a.cats[0]), (c, c.cats[2]), (d, d.cats[0])]),
            Intersection([(a, a.cats[0]), (c, c.cats[2]), (d, d.cats[1])]),
            Intersection([(a, a.cats[0]), (c, c.cats[3]), (d, d.cats[0])]),
            Intersection([(a, a.cats[0]), (c, c.cats[3]), (d, d.cats[1])]),
        ],
        [
            Intersection([(a, a.cats[1]), (c, c.cats[0]), (d, d.cats[0])]),
            Intersection([(a, a.cats[1]), (c, c.cats[0]), (d, d.cats[1])]),
            Intersection([(a, a.cats[1]), (c, c.cats[1]), (d, d.cats[0])]),
            Intersection([(a, a.cats[1]), (c, c.cats[1]), (d, d.cats[1])]),
            Intersection([(a, a.cats[1]), (c, c.cats[2]), (d, d.cats[0])]),
            Intersection([(a, a.cats[1]), (c, c.cats[2]), (d, d.cats[1])]),
            Intersection([(a, a.cats[1]), (c, c.cats[3]), (d, d.cats[0])]),
            Intersection([(a, a.cats[1]), (c, c.cats[3]), (d, d.cats[1])]),
        ],
    ]

    assert IntersectionMatrix([c, d], [a]).matrix == matrix


def test_05_intersection_matrix_1d_x_1d_y_vanilla_heatmap() -> None:
    """Test IntersectionMatrix w/ 1 x-dim and 1 y-dim -> nxn."""
    # pylint:disable=invalid-name

    # X's
    c = Dim("C", ["C0", "C1", "C2", "C3"])
    # Y's:
    a = Dim("A", ["A0", "A1"])

    matrix = [
        [
            Intersection([(a, a.cats[0]), (c, c.cats[0])]),
            Intersection([(a, a.cats[0]), (c, c.cats[1])]),
            Intersection([(a, a.cats[0]), (c, c.cats[2])]),
            Intersection([(a, a.cats[0]), (c, c.cats[3])]),
        ],
        [
            Intersection([(a, a.cats[1]), (c, c.cats[0])]),
            Intersection([(a, a.cats[1]), (c, c.cats[1])]),
            Intersection([(a, a.cats[1]), (c, c.cats[2])]),
            Intersection([(a, a.cats[1]), (c, c.cats[3])]),
        ],
    ]

    assert IntersectionMatrix([c], [a]).matrix == matrix


def test_06_intersection_matrix_multi_x_multi_y() -> None:
    """Test IntersectionMatrix w/ multi x-dims and y-dims -> NxN."""
    # pylint:disable=invalid-name

    # (2x3) x (4x2)
    # X's
    c = Dim("C", ["C0", "C1", "C2", "C3"])
    d = Dim("D", ["D0", "D1"])
    # Y's:
    a = Dim("A", ["A0", "A1"])
    b = Dim("B", ["B0", "B1", "B2"])

    matrix: List[List[Intersection]] = [
        # 1st Y-Chunk
        # # 1st Y-Row
        [
            Intersection(
                [(a, a.cats[0]), (b, b.cats[0]), (c, c.cats[0]), (d, d.cats[0])]
            ),
            Intersection(
                [(a, a.cats[0]), (b, b.cats[0]), (c, c.cats[0]), (d, d.cats[1])]
            ),
            Intersection(
                [(a, a.cats[0]), (b, b.cats[0]), (c, c.cats[1]), (d, d.cats[0])]
            ),
            Intersection(
                [(a, a.cats[0]), (b, b.cats[0]), (c, c.cats[1]), (d, d.cats[1])]
            ),
            Intersection(
                [(a, a.cats[0]), (b, b.cats[0]), (c, c.cats[2]), (d, d.cats[0])]
            ),
            Intersection(
                [(a, a.cats[0]), (b, b.cats[0]), (c, c.cats[2]), (d, d.cats[1])]
            ),
            Intersection(
                [(a, a.cats[0]), (b, b.cats[0]), (c, c.cats[3]), (d, d.cats[0])]
            ),
            Intersection(
                [(a, a.cats[0]), (b, b.cats[0]), (c, c.cats[3]), (d, d.cats[1])]
            ),
        ],
        # # 2nd Y-Row
        [
            Intersection(
                [(a, a.cats[0]), (b, b.cats[1]), (c, c.cats[0]), (d, d.cats[0])]
            ),
            Intersection(
                [(a, a.cats[0]), (b, b.cats[1]), (c, c.cats[0]), (d, d.cats[1])]
            ),
            Intersection(
                [(a, a.cats[0]), (b, b.cats[1]), (c, c.cats[1]), (d, d.cats[0])]
            ),
            Intersection(
                [(a, a.cats[0]), (b, b.cats[1]), (c, c.cats[1]), (d, d.cats[1])]
            ),
            Intersection(
                [(a, a.cats[0]), (b, b.cats[1]), (c, c.cats[2]), (d, d.cats[0])]
            ),
            Intersection(
                [(a, a.cats[0]), (b, b.cats[1]), (c, c.cats[2]), (d, d.cats[1])]
            ),
            Intersection(
                [(a, a.cats[0]), (b, b.cats[1]), (c, c.cats[3]), (d, d.cats[0])]
            ),
            Intersection(
                [(a, a.cats[0]), (b, b.cats[1]), (c, c.cats[3]), (d, d.cats[1])]
            ),
        ],
        # # 3rd Y-Row
        [
            Intersection(
                [(a, a.cats[0]), (b, b.cats[2]), (c, c.cats[0]), (d, d.cats[0])]
            ),
            Intersection(
                [(a, a.cats[0]), (b, b.cats[2]), (c, c.cats[0]), (d, d.cats[1])]
            ),
            Intersection(
                [(a, a.cats[0]), (b, b.cats[2]), (c, c.cats[1]), (d, d.cats[0])]
            ),
            Intersection(
                [(a, a.cats[0]), (b, b.cats[2]), (c, c.cats[1]), (d, d.cats[1])]
            ),
            Intersection(
                [(a, a.cats[0]), (b, b.cats[2]), (c, c.cats[2]), (d, d.cats[0])]
            ),
            Intersection(
                [(a, a.cats[0]), (b, b.cats[2]), (c, c.cats[2]), (d, d.cats[1])]
            ),
            Intersection(
                [(a, a.cats[0]), (b, b.cats[2]), (c, c.cats[3]), (d, d.cats[0])]
            ),
            Intersection(
                [(a, a.cats[0]), (b, b.cats[2]), (c, c.cats[3]), (d, d.cats[1])]
            ),
        ],
        # 2nd Y-Chunk
        # # 1st Y-Row
        [
            Intersection(
                [(a, a.cats[1]), (b, b.cats[0]), (c, c.cats[0]), (d, d.cats[0])]
            ),
            Intersection(
                [(a, a.cats[1]), (b, b.cats[0]), (c, c.cats[0]), (d, d.cats[1])]
            ),
            Intersection(
                [(a, a.cats[1]), (b, b.cats[0]), (c, c.cats[1]), (d, d.cats[0])]
            ),
            Intersection(
                [(a, a.cats[1]), (b, b.cats[0]), (c, c.cats[1]), (d, d.cats[1])]
            ),
            Intersection(
                [(a, a.cats[1]), (b, b.cats[0]), (c, c.cats[2]), (d, d.cats[0])]
            ),
            Intersection(
                [(a, a.cats[1]), (b, b.cats[0]), (c, c.cats[2]), (d, d.cats[1])]
            ),
            Intersection(
                [(a, a.cats[1]), (b, b.cats[0]), (c, c.cats[3]), (d, d.cats[0])]
            ),
            Intersection(
                [(a, a.cats[1]), (b, b.cats[0]), (c, c.cats[3]), (d, d.cats[1])]
            ),
        ],
        # # 2nd Y-Row
        [
            Intersection(
                [(a, a.cats[1]), (b, b.cats[1]), (c, c.cats[0]), (d, d.cats[0])]
            ),
            Intersection(
                [(a, a.cats[1]), (b, b.cats[1]), (c, c.cats[0]), (d, d.cats[1])]
            ),
            Intersection(
                [(a, a.cats[1]), (b, b.cats[1]), (c, c.cats[1]), (d, d.cats[0])]
            ),
            Intersection(
                [(a, a.cats[1]), (b, b.cats[1]), (c, c.cats[1]), (d, d.cats[1])]
            ),
            Intersection(
                [(a, a.cats[1]), (b, b.cats[1]), (c, c.cats[2]), (d, d.cats[0])]
            ),
            Intersection(
                [(a, a.cats[1]), (b, b.cats[1]), (c, c.cats[2]), (d, d.cats[1])]
            ),
            Intersection(
                [(a, a.cats[1]), (b, b.cats[1]), (c, c.cats[3]), (d, d.cats[0])]
            ),
            Intersection(
                [(a, a.cats[1]), (b, b.cats[1]), (c, c.cats[3]), (d, d.cats[1])]
            ),
        ],
        # # 3rd Y-Row
        [
            Intersection(
                [(a, a.cats[1]), (b, b.cats[2]), (c, c.cats[0]), (d, d.cats[0])]
            ),
            Intersection(
                [(a, a.cats[1]), (b, b.cats[2]), (c, c.cats[0]), (d, d.cats[1])]
            ),
            Intersection(
                [(a, a.cats[1]), (b, b.cats[2]), (c, c.cats[1]), (d, d.cats[0])]
            ),
            Intersection(
                [(a, a.cats[1]), (b, b.cats[2]), (c, c.cats[1]), (d, d.cats[1])]
            ),
            Intersection(
                [(a, a.cats[1]), (b, b.cats[2]), (c, c.cats[2]), (d, d.cats[0])]
            ),
            Intersection(
                [(a, a.cats[1]), (b, b.cats[2]), (c, c.cats[2]), (d, d.cats[1])]
            ),
            Intersection(
                [(a, a.cats[1]), (b, b.cats[2]), (c, c.cats[3]), (d, d.cats[0])]
            ),
            Intersection(
                [(a, a.cats[1]), (b, b.cats[2]), (c, c.cats[3]), (d, d.cats[1])]
            ),
        ],
    ]

    out = IntersectionMatrix([c, d], [a, b]).matrix
    for i, row in enumerate(out):
        assert matrix[i] == row

    assert matrix == out
