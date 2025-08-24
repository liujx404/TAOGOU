import grpc
from protos import user_pb2_grpc, address_pb2_grpc
from services.user import UserServicer
import asyncio
from services.interceptors import UserInterceptor
from services.address import AddressServicer
import consul
import uuid
import socket
from typing import Tuple
from loguru import logger
import socket
import fcntl
import struct
from typing import Tuple
from utils.user_consul import UserConsul

user_consul = UserConsul()
async def main():
    server = grpc.aio.server(interceptors=[UserInterceptor()])
    user_pb2_grpc.add_UserServicer_to_server(UserServicer(), server)
    address_pb2_grpc.add_AddressServicer_to_server(AddressServicer(), server)
    ip, port = user_consul.register_service()  # 获取 IP 和端口
    logger.info(f"服务将运行在 {ip}:{port}")
    server.add_insecure_port(f"0.0.0.0:{port}")  # Use the port from get_ip_and_port

    user_consul.register_service(ip, port)
    await server.start()
    logger.info("grpc服务器已启动。。。")
    
    try:
        await server.wait_for_termination()
    except KeyboardInterrupt:
        print("接收到关闭信号，正在优雅关闭服务器...")
    finally:
        user_consul.unregister_service()
        # 优雅关闭服务器
        await server.stop(grace=5.0)
        logger.info("grpc服务器已优雅关闭。")

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("接收到关闭信号，正在优雅关闭服务器...")    