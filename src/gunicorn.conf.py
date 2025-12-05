import aiohttp  # pylint: disable=w0611 # noqa: F401
import aiohttp_retry  # pylint: disable=w0611 # noqa: F401
import aiolimiter  # pylint: disable=w0611 # noqa: F401
import fastapi  # pylint: disable=w0611 # noqa: F401
import gunicorn  # pylint: disable=w0611 # noqa: F401
import itsdangerous  # pylint: disable=w0611 # noqa: F401
import pandas  # pylint: disable=w0611 # noqa: F401
import pydantic  # pylint: disable=w0611 # noqa: F401
import pydantic_settings  # pylint: disable=w0611 # noqa: F401
import slowapi  # pylint: disable=w0611 # noqa: F401
import thefuzz  # pylint: disable=w0611 # noqa: F401
import uvicorn  # pylint: disable=w0611 # noqa: F401
import uvicorn_worker  # pylint: disable=w0611 # noqa: F401
import uvloop  # pylint: disable=w0611 # noqa: F401
from gunicorn.arbiter import Arbiter

from src.core.config.config import APP, ENV, LOG, SERVER

SERVER.set(f"Gunicorn/{gunicorn.__version__}")


def when_ready_hook(_: Arbiter) -> None:
    LOG.info("\033[33mScopus Survey API was initialized 🚀")
    LOG.debug(ENV.model_dump())
    LOG.info(
        f"Gunicorn running at\033[37;1m http://localhost:{ENV.port}"
        "\033[m (Press CTRL+C to quit)"
    )


# pylint: disable=C0103
wsgi_app = APP
reload = False
bind = f"0.0.0.0:{ENV.port}"
workers = 4
worker_class = "uvicorn_worker.UvicornWorker"
timeout = 120
keepalive = 5
accesslog = "-"
errorlog = "-"
loglevel = "info"
access_log_format = None
logger_class = "src.utils.logging._CustomGunicornLogger"
raw_env = ["PROGRESS_BAR=False"]
when_ready = when_ready_hook
