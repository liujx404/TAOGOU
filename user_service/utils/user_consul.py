import consul
from .single import SingletonMeta
import uuid
import socket
import fcntl
import struct
from loguru import logger
from typing import Tuple


def get_zerotier_ip(interface: str = "zt0") -> str:
    """获取指定 ZeroTier 虚拟网卡的 IP 地址"""
    try:
        # 创建套接字
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # 通过 IO 控制获取网卡 IP（仅 Linux 有效）
        ip_addr = fcntl.ioctl(
            s.fileno(),
            0x8915,  # SIOCGIFADDR 命令，获取网卡地址
            struct.pack('256s', interface.encode('utf-8')[:15])
        )
        # 解析 IP 地址
        return socket.inet_ntoa(ip_addr[20:24])
    except Exception as e:
        # 若指定网卡不存在或获取失败，返回默认逻辑的 IP
        logger.error(f"获取 ZeroTier IP 失败，使用默认逻辑: {e}")
        # log --- IGNORE ---
        return get_default_ip()

def get_default_ip() -> str:
    """原逻辑：获取访问 8.8.8.8 所用的 IP"""
    socket_ip = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        socket_ip.connect(("8.8.8.8", 80))
        return socket_ip.getsockname()[0]
    finally:
        socket_ip.close()

def get_ip_and_port() -> Tuple[str, int]:
    # 优先获取 ZeroTier 网卡的 IP（您的 ZeroTier 网卡名称是 "ztaw4kaxwe"）
    ip = get_zerotier_ip(interface="ztaw4kaxwe")
    
    # 端口获取逻辑不变（随机可用端口）
    socket_port = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        socket_port.bind(("", 0))
        _, port = socket_port.getsockname()
        return ip, port
    finally:
        socket_port.close()


class UserConsul(metaclass=SingletonMeta):
    def __init__(self):
        self.client = consul.Consul(host="11.11.11.130", port=8500)
        self.user_service_id = uuid.uuid4().hex
    def register_service(self, ip: str = None, port: int = None):
        logger.info(f"注册服务，IP: {ip}, Port: {port}")
        self.client.agent.service.register(
            name="user_service",
            service_id=self.user_service_id ,
            address=ip,
            port=port,
            tags=["user_service", "grpc"],
            check=consul.Check.tcp(host=ip, port=port, interval="10s")
        )
        logger.info("服务注册到Consul成功")
    
    def unregister_service(self):
        if self.user_service_id:
            self.client.agent.service.deregister(self.user_service_id)
            logger.info("服务注销成功")
        else:
            logger.warning("没有注册的服务 ID，无法注销服务")
