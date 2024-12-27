from fastapi import FastAPI

from app.framework.fastapi.config import (
    CORS,
    FASTAPI,
    SESSION,
    STATIC,
    RATE_LIMIT,
)
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
app.add_middleware(**SESSION)
app.add_middleware(**RATE_LIMIT)
app.add_middleware(RedirectNotFoundRoutes)
app.add_middleware(TraceExceptionControl)
