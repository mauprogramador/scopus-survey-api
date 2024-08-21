from contextlib import asynccontextmanager
from shutil import rmtree

from fastapi import FastAPI

from app.core.config.config import DIRECTORY, LOG


@asynccontextmanager
async def lifespan(_: FastAPI):
    yield
    LOG.info("Cleaning up the Temporary Directory")
    rmtree(DIRECTORY)
