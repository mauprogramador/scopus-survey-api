import contextlib

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from src import __version__
from src.adapters.presenters.jinja_response import build_all_templates
from src.core.config.config import DIRECTORY, ENV, LIMITER
from src.core.domain.translations import load_translations
from src.framework.fastapi.routes import favicon_router, router
from src.framework.fastapi.swagger import (
    APP_DESCRIPTION,
    CONTACT,
    LICENSE,
    RESPONSES,
    TERMS_OF_SERVICE,
)
from src.framework.middleware import (
    HANDLERS,
    FlowGuardingMonitorMiddleware,
    ProxyForwardedResolverMiddleware,
)
from src.utils import logger


@contextlib.asynccontextmanager
async def lifespan(app: FastAPI):  # pylint: disable=W0621,W0613
    DIRECTORY.mkdir(parents=True, exist_ok=True)
    build_all_templates(*load_translations())

    if ENV.host == "0.0.0.0":
        logger.localhost(ENV.port)

    yield


app = FastAPI(
    debug=ENV.debug,
    title="Scopus Survey API",
    summary="Web API for bibliographic survey of Scopus articles",
    description=APP_DESCRIPTION,
    version=f"v{__version__}",
    docs_url="/",
    exception_handlers=HANDLERS,
    lifespan=lifespan,
    terms_of_service=TERMS_OF_SERVICE,
    contact=CONTACT,
    license_info=LICENSE,
    responses=RESPONSES,
    swagger_ui_parameters={"supportedSubmitMethods": []},
)
app.state.limiter = LIMITER


app.add_middleware(ProxyForwardedResolverMiddleware)
app.add_middleware(FlowGuardingMonitorMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["GET"],
    allow_headers=["*"],
)

app.mount("/styles", StaticFiles(directory="web/static/css"), name="styles")
app.mount("/scripts", StaticFiles(directory="web/static/js"), name="scripts")
app.mount("/libs", StaticFiles(directory="web/static/lib"), name="libs")
app.mount("/fonts", StaticFiles(directory="web/static/font"), name="fonts")
app.mount("/images", StaticFiles(directory="web/static/img"), name="images")
app.mount("/svgs", StaticFiles(directory="web/static/svg"), name="svgs")

app.include_router(router)
app.include_router(favicon_router)
