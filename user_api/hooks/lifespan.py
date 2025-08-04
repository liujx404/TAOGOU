from contextlib import asynccontextmanager
from fastapi import FastAPI
from loguru import logger
from utils.cache import TLLRedis

@asynccontextmanager
async def lifespan(app:FastAPI):
    #logger.remove()
    logger.add("logs/file.log", rotation="500 MB", enqueue=True, level="INFO")
    yield
    await TLLRedis().close()