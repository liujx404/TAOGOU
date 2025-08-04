from functools import wraps
from fastapi import HTTPException
from utils.status_code import get_http_code
import grpc


def grpc_error_handeler(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            result = await func(*args, **kwargs)    
            return result
        except grpc.RpcError as e:
            raise HTTPException(status=get_http_code(e.code()), detail=e.details())
    return wrapper