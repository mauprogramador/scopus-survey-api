from fastapi import FastAPI

from app.api.middleware import TraceControl
from app.api.routes import router
from app.api.swagger import FASTAPI
from app.core.config import CORS, STATIC
from app.utils.logger import Logger

app = FastAPI(**FASTAPI)

app.include_router(router)

for url, static in STATIC.items():
    app.mount(url, static)

app.add_middleware(**CORS)
app.add_middleware(TraceControl)


Logger.info('\033[33mScopus API was initialized 🚀\033[m')
