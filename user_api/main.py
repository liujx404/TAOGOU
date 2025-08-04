from fastapi import FastAPI
from hooks.lifespan import lifespan
from loguru import logger
from hooks.middlewares import log_middleware
from starlette.middleware.base import BaseHTTPMiddleware
from routers import user


app = FastAPI(lifespan=lifespan)
app.add_middleware(BaseHTTPMiddleware, log_middleware)
app.include_router(user.router)

@app.get("/")
async def root():
    logger.info("rizhi")
    return {"message": "Hello World"}
