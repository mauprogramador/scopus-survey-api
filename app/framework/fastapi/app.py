from fastapi import FastAPI

from app.framework.fastapi.config import CORS, FASTAPI, STATIC
from app.framework.fastapi.routes import router
from app.framework.middleware import (
    RedirectNotFoundRoutes,
    TraceExceptionControl,
)

app = FastAPI(**FASTAPI)

app.include_router(router)

for url, static in STATIC.items():
    app.mount(url, static)

app.add_middleware(**CORS)
app.add_middleware(RedirectNotFoundRoutes)
app.add_middleware(TraceExceptionControl)
