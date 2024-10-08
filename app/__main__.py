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

from app.core.config.config import LOG, TOML_ENV
from app.utils.access_qrcode import ShowAccessQRCode

if __name__ == "__main__":
    LOG.info("Scopus Survey API was initialized 🚀")
    ShowAccessQRCode(TOML_ENV.host, TOML_ENV.port)
    uvicorn.run(**TOML_ENV.uvicorn)
