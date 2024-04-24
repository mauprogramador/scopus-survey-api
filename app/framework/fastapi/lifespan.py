from contextlib import asynccontextmanager
from shutil import rmtree

from fastapi import FastAPI

from app.core.config import DIRECTORY
from app.utils.logger import Logger


@asynccontextmanager
async def lifespan(_: FastAPI):
    yield
    Logger.info('Cleaning up the Temporary Directory')
    rmtree(DIRECTORY)
