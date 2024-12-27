from os.path import exists
from os import mkdir

import cachecontrol  # pylint: disable=w0611 # noqa: F401
import dotenv  # pylint: disable=w0611 # noqa: F401
import fastapi  # pylint: disable=w0611 # noqa: F401
import pandas  # pylint: disable=w0611 # noqa: F401
import qrcode  # pylint: disable=w0611 # noqa: F401
import requests  # pylint: disable=w0611 # noqa: F401
import thefuzz  # pylint: disable=w0611 # noqa: F401
import toml  # pylint: disable=w0611 # noqa: F401
import tqdm  # pylint: disable=w0611 # noqa: F401
import uvicorn

from app.core.config.config import DIRECTORY, LOG, TOML_ENV


if __name__ == "__main__":
    if not exists(DIRECTORY):
        mkdir(DIRECTORY)

    LOG.info("Scopus Survey API was initialized 🚀")
    uvicorn.run(**TOML_ENV.uvicorn)
