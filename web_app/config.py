"""Config file."""

import logging
import os
from typing import TypedDict

import dash  # type: ignore
import dash_bootstrap_components as dbc  # type: ignore
import flask

CSV = "./data/used-data.csv"
CSV_META = "./data/used-data-meta.txt"
CSV_BACKUP = "./data/used-data-bkp.csv"
CSV_BACKUP_META = "./data/used-data-bkp-meta.txt"


NDIMS = 3


# --------------------------------------------------------------------------------------
# Set-up Dash server

app = dash.Dash(
    __name__,
    server=flask.Flask(__name__),
    external_stylesheets=[
        dbc.themes.BOOTSTRAP,
        "https://codepen.io/chriddyp/pen/bWLwgP.css",
    ],
)

# config
server = app.server
app.config.suppress_callback_exceptions = True
server.config.update(SECRET_KEY=os.urandom(12))


# --------------------------------------------------------------------------------------
# configure config_vars


class ConfigVarsTypedDict(TypedDict, total=False):
    """Global configuration-variable types."""

    WEB_SERVER_HOST: str
    WEB_SERVER_PORT: int


def get_config_vars() -> ConfigVarsTypedDict:
    """Get the global configuration variables."""
    config_vars: ConfigVarsTypedDict = {
        "WEB_SERVER_HOST": os.environ.get("WEB_SERVER_HOST", "localhost"),
        "WEB_SERVER_PORT": int(os.environ.get("WEB_SERVER_PORT", 8050)),
    }

    return config_vars


def log_config_vars() -> None:
    """Log the global configuration variables, key-value."""
    for key, val in get_config_vars().items():
        logging.info(f"{key}\t{val}\t({type(val).__name__})")
