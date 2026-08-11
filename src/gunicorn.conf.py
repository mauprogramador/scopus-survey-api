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
from uvicorn_worker import UvicornWorker

from src.infra.config.config import APP, ENV, SERVER
from src.infra.utils import logger


SERVER.set(f"Gunicorn/{gunicorn.__version__}")


def when_ready_hook(_: Arbiter) -> None:
    logger.info("\033[33mScopus Survey API was initialized 🚀")
    logger.debug(env_config=ENV)
    logger.gunicorn_running(ENV.port)


# pylint: disable=C0103
wsgi_app = APP
reload = False
bind = f"0.0.0.0:{ENV.port}"
workers = 4
worker_class = f"{UvicornWorker.__module__}.{UvicornWorker.__qualname__}"
timeout = 120
keepalive = 5
accesslog = "-"
errorlog = "-"
loglevel = "info"
access_log_format = None
logger_class = (
    f"{logger.ProdLogger.__module__}.{logger.ProdLogger.__qualname__}"
)
raw_env = ["PROGRESS_BAR=False"]
when_ready = when_ready_hook
