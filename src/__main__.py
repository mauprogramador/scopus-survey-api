import cachecontrol  # pylint: disable=w0611 # noqa: F401
import fastapi  # pylint: disable=w0611 # noqa: F401
import pandas  # pylint: disable=w0611 # noqa: F401
import pydantic  # pylint: disable=w0611 # noqa: F401
import pydantic_settings  # pylint: disable=w0611 # noqa: F401
import requests  # pylint: disable=w0611 # noqa: F401
import slowapi  # pylint: disable=w0611 # noqa: F401
import thefuzz  # pylint: disable=w0611 # noqa: F401
import tqdm  # pylint: disable=w0611 # noqa: F401
import uvicorn

from src.adapters.presenters.html_response import TemplateBuilder
from src.core.config.config import (
    APP,
    DIRECTORY,
    ENV,
    HEADERS,
    LOG,
    SHUTDOWN_TIMEOUT,
)

if __name__ == "__main__":
    DIRECTORY.mkdir(parents=True, exist_ok=True)
    TemplateBuilder.load_translations()

    LOG.info("\033[33mScopus Survey API was initialized 🚀")
    LOG.debug(ENV.model_dump())

    uvicorn.run(
        app=APP,
        host=ENV.host,
        port=ENV.port,
        reload=ENV.reload,
        workers=ENV.workers,
        access_log=False,
        server_header=True,
        date_header=True,
        timeout_graceful_shutdown=SHUTDOWN_TIMEOUT,
        headers=HEADERS,
        use_colors=True,
    )
