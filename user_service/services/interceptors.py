from grpc_interceptor.server import AsyncServerInterceptor
import grpc
from typing import Any, Callable, Callable
from models import AsyncSessionFactory
from grpc_interceptor.exceptions import GrpcException

class UserInterceptor(AsyncServerInterceptor):
    async def intercept(
        self,
        method: Callable,
        request_or_iterator: Any,
        context: grpc.ServicerContext,
        method_name: str,
    ) -> Any:
        session = AsyncSessionFactory()
        try:
            response = await method(request_or_iterator, context, session)
            return response
        except GrpcException as e:
            await context.set_code(e.status_code)
            await context.set_details(e.details)
        finally:
            await session.close()
        