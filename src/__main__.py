import aiohttp  # pylint: disable=w0611 # noqa: F401
import aiohttp_retry  # pylint: disable=w0611 # noqa: F401
import aiolimiter  # pylint: disable=w0611 # noqa: F401
import fastapi  # pylint: disable=w0611 # noqa: F401
import itsdangerous  # pylint: disable=w0611 # noqa: F401
import pandas  # pylint: disable=w0611 # noqa: F401
import pydantic  # pylint: disable=w0611 # noqa: F401
import pydantic_settings  # pylint: disable=w0611 # noqa: F401
import slowapi  # pylint: disable=w0611 # noqa: F401
import thefuzz  # pylint: disable=w0611 # noqa: F401
import tqdm  # pylint: disable=w0611 # noqa: F401
import uvicorn
import uvloop

from src.infra.config.config import APP, ENV, SERVER
from src.infra.utils import logger


if __name__ == "__main__":
    SERVER.set(f"Uvicorn/{uvicorn.__version__}")
    logger.info("\033[33mScopus Survey API was initialized 🚀")
    logger.debug(env_config=ENV)

    uvloop.install()
    uvicorn.run(
        app=APP,
        host=ENV.host,
        port=ENV.port,
        loop="uvloop",
        reload=ENV.reload,
        workers=ENV.workers,
        log_config=logger.UVICORN_LOGGING_CONFIG,
        access_log=False,
        server_header=False,
        timeout_graceful_shutdown=5,
        use_colors=True,
    )
