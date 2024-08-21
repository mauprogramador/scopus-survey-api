import uvicorn
from fastapi import FastAPI

from app.core.config.config import LOG, TOML
from app.framework.fastapi.config import CORS, FASTAPI, STATIC
from app.framework.fastapi.routes import router
from app.framework.middleware import (
    RedirectNotFoundRoutes,
    TraceExceptionControl,
)
from app.utils.access_qrcode import ShowAccessQRCode

app = FastAPI(**FASTAPI)

app.include_router(router)

for url, static in STATIC.items():
    app.mount(url, static)

app.add_middleware(**CORS)
app.add_middleware(RedirectNotFoundRoutes)
app.add_middleware(TraceExceptionControl)


if __name__ == "__main__":
    LOG.info("Scopus Searcher API was initialized 🚀")
    ShowAccessQRCode(TOML.port)
    uvicorn.run(**TOML.uvicorn)
