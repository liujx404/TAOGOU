from fastapi.requests import Request
from loguru import logger
from fastapi.responses import JSONResponse

async def log_middleware(request: Request, call_next):
    try:
        response = await call_next(request)
        await logger.complete()
        return response
    except Exception as e:
        logger.exception("发送异常了：")
        return JSONResponse(content={"detail": "服务器内部错"}, status_code = 500)