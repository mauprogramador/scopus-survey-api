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

from src.core.config.config import APP, ENV, LOG, SERVER

if __name__ == "__main__":
    SERVER.set(f"Uvicorn/{uvicorn.__version__}")
    LOG.info("\033[33mScopus Survey API was initialized 🚀")
    LOG.debug(ENV.model_dump())

    uvloop.install()
    uvicorn.run(
        app=APP,
        host=ENV.host,
        port=ENV.port,
        loop="uvloop",
        reload=ENV.reload,
        workers=ENV.workers,
        access_log=False,
        server_header=False,
        timeout_graceful_shutdown=5,
        use_colors=True,
    )
