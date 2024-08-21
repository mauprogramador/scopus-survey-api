import uvicorn
from fastapi import FastAPI

from app.core.config.config import LOG, TOML
from app.framework.fastapi.config import CORS, FASTAPI, STATIC
from app.framework.fastapi.routes import router
from app.framework.middleware.tracing import TraceControl

app = FastAPI(**FASTAPI)

app.include_router(router)

for url, static in STATIC.items():
    app.mount(url, static)

app.add_middleware(**CORS)
app.add_middleware(TraceControl)


if __name__ == "__main__":
    LOG.info("Scopus API was initialized 🚀")
    uvicorn.run(**TOML.uvicorn)
