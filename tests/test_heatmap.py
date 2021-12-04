"""Tests for heatmap.py"""

import os
import statistics as st
import sys

import pandas as pd  # type: ignore[import]

sys.path.append(".")
from web_app.heatmap import Heatmap  # noqa: E402

CSV = os.path.join(os.path.dirname(__file__), "data.csv")


def test_00_heatmap() -> None:
    """Test Heatmap."""
    df = pd.read_csv(CSV, skipinitialspace=True)
    assert Heatmap(df, [], []).heatmap == [[{"intersection": {}, "z": 10}]]


def test_01_heatmap_just_defaults() -> None:
    """Test Heatmap."""
    df = pd.read_csv(CSV, skipinitialspace=True)
    assert Heatmap(df, ["age"], []).heatmap == [
        [
            {"z": 4, "intersection": {"age": "(21.965, 28.8]"}},
            {"z": 2, "intersection": {"age": "(28.8, 35.6]"}},
            {"z": 1, "intersection": {"age": "(35.6, 42.4]"}},
            {"z": None, "intersection": {"age": "(42.4, 49.2]"}},
            {"z": 2, "intersection": {"age": "(49.2, 56.0]"}},
        ]
    ]
    assert Heatmap(df, [], ["age"]).heatmap == [
        [{"z": 4, "intersection": {"age": "(21.965, 28.8]"}}],
        [{"z": 2, "intersection": {"age": "(28.8, 35.6]"}}],
        [{"z": 1, "intersection": {"age": "(35.6, 42.4]"}}],
        [{"z": None, "intersection": {"age": "(42.4, 49.2]"}}],
        [{"z": 2, "intersection": {"age": "(49.2, 56.0]"}}],
    ]
    assert Heatmap(df, ["sex"], []).heatmap == [
        [{"z": 3, "intersection": {"sex": "F"}}, {"z": 6, "intersection": {"sex": "M"}}]
    ]
    assert Heatmap(df, ["sex"], ["age"]).heatmap == [
        [
            {"intersection": {"age": "(21.965, 28.8]", "sex": "F"}, "z": 2},
            {"intersection": {"age": "(21.965, 28.8]", "sex": "M"}, "z": 1},
        ],
        [
            {"intersection": {"age": "(28.8, 35.6]", "sex": "F"}, "z": 1},
            {"intersection": {"age": "(28.8, 35.6]", "sex": "M"}, "z": 1},
        ],
        [
            {"intersection": {"age": "(35.6, 42.4]", "sex": "F"}, "z": None},
            {"intersection": {"age": "(35.6, 42.4]", "sex": "M"}, "z": 1},
        ],
        [
            {"intersection": {"age": "(42.4, 49.2]", "sex": "F"}, "z": None},
            {"intersection": {"age": "(42.4, 49.2]", "sex": "M"}, "z": None},
        ],
        [
            {"intersection": {"age": "(49.2, 56.0]", "sex": "F"}, "z": None},
            {"intersection": {"age": "(49.2, 56.0]", "sex": "M"}, "z": 2},
        ],
    ]
    assert Heatmap(df, ["sex", "age"], ["fav_food"]).heatmap == [
        [
            {
                "intersection": {
                    "age": "(21.965, 28.8]",
                    "fav_food": "burger",
                    "sex": "F",
                },
                "z": 2,
            },
            {
                "intersection": {
                    "age": "(28.8, 35.6]",
                    "fav_food": "burger",
                    "sex": "F",
                },
                "z": None,
            },
            {
                "intersection": {
                    "age": "(35.6, 42.4]",
                    "fav_food": "burger",
                    "sex": "F",
                },
                "z": None,
            },
            {
                "intersection": {
                    "age": "(42.4, 49.2]",
                    "fav_food": "burger",
                    "sex": "F",
                },
                "z": None,
            },
            {
                "intersection": {
                    "age": "(49.2, 56.0]",
                    "fav_food": "burger",
                    "sex": "F",
                },
                "z": None,
            },
            {
                "intersection": {
                    "age": "(21.965, 28.8]",
                    "fav_food": "burger",
                    "sex": "M",
                },
                "z": None,
            },
            {
                "intersection": {
                    "age": "(28.8, 35.6]",
                    "fav_food": "burger",
                    "sex": "M",
                },
                "z": None,
            },
            {
                "intersection": {
                    "age": "(35.6, 42.4]",
                    "fav_food": "burger",
                    "sex": "M",
                },
                "z": None,
            },
            {
                "intersection": {
                    "age": "(42.4, 49.2]",
                    "fav_food": "burger",
                    "sex": "M",
                },
                "z": None,
            },
            {
                "intersection": {
                    "age": "(49.2, 56.0]",
                    "fav_food": "burger",
                    "sex": "M",
                },
                "z": 1,
            },
        ],
        [
            {
                "intersection": {
                    "age": "(21.965, 28.8]",
                    "fav_food": "pizza",
                    "sex": "F",
                },
                "z": None,
            },
            {
                "intersection": {
                    "age": "(28.8, 35.6]",
                    "fav_food": "pizza",
                    "sex": "F",
                },
                "z": None,
            },
            {
                "intersection": {
                    "age": "(35.6, 42.4]",
                    "fav_food": "pizza",
                    "sex": "F",
                },
                "z": None,
            },
            {
                "intersection": {
                    "age": "(42.4, 49.2]",
                    "fav_food": "pizza",
                    "sex": "F",
                },
                "z": None,
            },
            {
                "intersection": {
                    "age": "(49.2, 56.0]",
                    "fav_food": "pizza",
                    "sex": "F",
                },
                "z": None,
            },
            {
                "intersection": {
                    "age": "(21.965, 28.8]",
                    "fav_food": "pizza",
                    "sex": "M",
                },
                "z": 1,
            },
            {
                "intersection": {
                    "age": "(28.8, 35.6]",
                    "fav_food": "pizza",
                    "sex": "M",
                },
                "z": 1,
            },
            {
                "intersection": {
                    "age": "(35.6, 42.4]",
                    "fav_food": "pizza",
                    "sex": "M",
                },
                "z": 1,
            },
            {
                "intersection": {
                    "age": "(42.4, 49.2]",
                    "fav_food": "pizza",
                    "sex": "M",
                },
                "z": None,
            },
            {
                "intersection": {
                    "age": "(49.2, 56.0]",
                    "fav_food": "pizza",
                    "sex": "M",
                },
                "z": 1,
            },
        ],
        [
            {
                "intersection": {
                    "age": "(21.965, 28.8]",
                    "fav_food": "quinoa",
                    "sex": "F",
                },
                "z": None,
            },
            {
                "intersection": {
                    "age": "(28.8, 35.6]",
                    "fav_food": "quinoa",
                    "sex": "F",
                },
                "z": None,
            },
            {
                "intersection": {
                    "age": "(35.6, 42.4]",
                    "fav_food": "quinoa",
                    "sex": "F",
                },
                "z": None,
            },
            {
                "intersection": {
                    "age": "(42.4, 49.2]",
                    "fav_food": "quinoa",
                    "sex": "F",
                },
                "z": None,
            },
            {
                "intersection": {
                    "age": "(49.2, 56.0]",
                    "fav_food": "quinoa",
                    "sex": "F",
                },
                "z": None,
            },
            {
                "intersection": {
                    "age": "(21.965, 28.8]",
                    "fav_food": "quinoa",
                    "sex": "M",
                },
                "z": None,
            },
            {
                "intersection": {
                    "age": "(28.8, 35.6]",
                    "fav_food": "quinoa",
                    "sex": "M",
                },
                "z": None,
            },
            {
                "intersection": {
                    "age": "(35.6, 42.4]",
                    "fav_food": "quinoa",
                    "sex": "M",
                },
                "z": None,
            },
            {
                "intersection": {
                    "age": "(42.4, 49.2]",
                    "fav_food": "quinoa",
                    "sex": "M",
                },
                "z": None,
            },
            {
                "intersection": {
                    "age": "(49.2, 56.0]",
                    "fav_food": "quinoa",
                    "sex": "M",
                },
                "z": None,
            },
        ],
    ]


def test_02_heatmap_bins() -> None:
    """Test Heatmap."""
    df = pd.read_csv(CSV, skipinitialspace=True)
    assert Heatmap(df, ["age"], [], bins={"age": 2}).heatmap == [
        [
            {"intersection": {"age": "(21.965, 39.0]"}, "z": 6},
            {"intersection": {"age": "(39.0, 56.0]"}, "z": 3},
        ]
    ]
    assert Heatmap(df, ["age"], [], bins={"age": 10}).heatmap == [
        [
            {"intersection": {"age": "(21.965, 25.4]"}, "z": 4},
            {"intersection": {"age": "(25.4, 28.8]"}, "z": None},
            {"intersection": {"age": "(28.8, 32.2]"}, "z": 1},
            {"intersection": {"age": "(32.2, 35.6]"}, "z": 1},
            {"intersection": {"age": "(35.6, 39.0]"}, "z": None},
            {"intersection": {"age": "(39.0, 42.4]"}, "z": 1},
            {"intersection": {"age": "(42.4, 45.8]"}, "z": None},
            {"intersection": {"age": "(45.8, 49.2]"}, "z": None},
            {"intersection": {"age": "(49.2, 52.6]"}, "z": None},
            {"intersection": {"age": "(52.6, 56.0]"}, "z": 2},
        ]
    ]


def test_03_heatmap_zstat() -> None:
    """Test Heatmap."""
    df = pd.read_csv(CSV, skipinitialspace=True)
    assert Heatmap(
        df, ["age"], [], z_stat={"dim_name": "score", "stats_func": st.mean}
    ).heatmap == [
        [
            {"intersection": {"age": "(21.965, 28.8]"}, "z": 80.67750000000001},
            {"intersection": {"age": "(28.8, 35.6]"}, "z": 28.9},
            {"intersection": {"age": "(35.6, 42.4]"}, "z": None},
            {"intersection": {"age": "(42.4, 49.2]"}, "z": None},
            {"intersection": {"age": "(49.2, 56.0]"}, "z": 22.8},
        ]
    ]
