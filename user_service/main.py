import grpc
from protos import user_pb2_grpc
from services.user import UserServicer
import asyncio
from services.interceptors import UserInterceptor
async def main():
    server = grpc.aio.server(interceptors=[UserInterceptor()])
    user_pb2_grpc.add_UserServicer_to_server(UserServicer(), server)
    server.add_insecure_port("0.0.0.0:5001")
    await server.start()
    print("grpc服务器已启动。。。")
    await server.wait_for_termination()

if __name__ == '__main__':
    asyncio.run(main())