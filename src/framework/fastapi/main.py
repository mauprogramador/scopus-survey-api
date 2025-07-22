from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

from src import __version__
from src.core.config.config import ENV, LIMITER, SECRET_KEY
from src.framework.fastapi.routes import router
from src.framework.fastapi.swagger import (
    CONTACT,
    DESCRIPTION,
    LICENSE,
    RESPONSES,
    TERMS_OF_SERVICE,
)
from src.framework.middleware import (
    ExceptionHandler,
    FlowGuardingMonitorMiddleware,
)

app = FastAPI(
    debug=ENV.debug,
    title="Scopus Survey API",
    summary="Web API for bibliographic survey of Scopus articles",
    description=DESCRIPTION,
    version=f"v{__version__}",
    docs_url="/",
    exception_handlers=ExceptionHandler().handlers,
    terms_of_service=TERMS_OF_SERVICE,
    contact=CONTACT,
    license_info=LICENSE,
    responses=RESPONSES,
    swagger_ui_parameters={"supportedSubmitMethods": []},
)
app.state.limiter = LIMITER

app.add_middleware(FlowGuardingMonitorMiddleware)

app.add_middleware(
    SessionMiddleware,
    secret_key=SECRET_KEY,
    max_age=None,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET"],
    allow_headers=["*"],
)

app.mount("/styles", StaticFiles(directory="web/static/css"))
app.mount("/images", StaticFiles(directory="web/static/img"))
app.mount("/scripts", StaticFiles(directory="web/static/js"))
app.mount("/svgs", StaticFiles(directory="web/static/svg"))
app.mount("/files", StaticFiles(directory="csv"))

app.include_router(router)
