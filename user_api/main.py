from fastapi import FastAPI
from hooks.lifespan import lifespan
from loguru import logger
from hooks.middlewares import log_middleware
from starlette.middleware.base import BaseHTTPMiddleware
from routers import user, address
from settings import SERVER_PORT
app = FastAPI(lifespan=lifespan)
app.add_middleware(BaseHTTPMiddleware, log_middleware)
app.include_router(user.router)
app.include_router(address.router)

@app.get("/")
async def root():
    logger.info("rizhi")
    return {"message": "Hello World"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "user_api"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=SERVER_PORT)
    