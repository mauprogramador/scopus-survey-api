from os.path import exists
from os import mkdir

import cachecontrol  # pylint: disable=w0611 # noqa: F401
import fastapi  # pylint: disable=w0611 # noqa: F401
import pandas  # pylint: disable=w0611 # noqa: F401
import requests  # pylint: disable=w0611 # noqa: F401
import thefuzz  # pylint: disable=w0611 # noqa: F401
import tqdm  # pylint: disable=w0611 # noqa: F401
import ratelimit  # pylint: disable=w0611 # noqa: F401
import pydantic  # pylint: disable=w0611 # noqa: F401
import pydantic_settings  # pylint: disable=w0611 # noqa: F401
import uvicorn

from app.core.config.config import LOG, ENV, APP, DIRECTORY


if __name__ == "__main__":
    if not exists(DIRECTORY):
        mkdir(DIRECTORY)

    LOG.info("\033[33mScopus Survey API was initialized 🚀")
    LOG.debug(ENV.model_dump())

    # Set headers | Remove Security Middleware
    uvicorn.run(
        app=APP,
        host=ENV.host,
        port=ENV.port,
        reload=ENV.reload,
        workers=ENV.workers,
        access_log=False,
        server_header=True,
        date_header=True,
        timeout_graceful_shutdown=5,
        use_colors=True,
    )
