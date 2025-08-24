from contextlib import asynccontextmanager
from fastapi import FastAPI
from loguru import logger
from utils.cache import TLLRedis
import consul
import uuid
from typing import Tuple
import socket
import fcntl
import struct
from utils.tll_consul import TLLConsul

client = consul.Consul(host="11.11.11.130", port=8500)
tll_consul = TLLConsul()

@asynccontextmanager
async def lifespan(app:FastAPI):
    #logger.remove()
    logger.add("logs/file.log", rotation="500 MB", enqueue=True, level="INFO")
    from settings import SERVER_PORT
    tll_consul.register_service()
    yield
    tll_consul.unregister_service()
    await TLLRedis().close()