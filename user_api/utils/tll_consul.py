import consul
from .single import SingletonMeta
import uuid
import socket
import fcntl
import struct
from loguru import logger
from typing import Tuple
import settings
from dns import asyncresolver, rdatatype
from typing import Dict, List


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

class ServiceAddress:
    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port
        self.count = 0

    def increment_count(self):
        self.count += 1

    def __str__(self):
        return f"{self.ip}:{self.port}"

    def __repr__(self):
        return f"ServiceAddress(ip={self.ip}, port={self.port})"

class LoadBalancer:
    def __init__(self, addresses: list[Dict[str, str|int]] = None):
        self.addresses: List[ServiceAddress] = []
        if addresses:
            self.init_addresses(addresses)
    
    def init_addresses(self, addresses: list[Dict[str, str|int]]):
        self.addresses.clear()
        for addr in addresses:
            self.addresses.append(ServiceAddress(host=addr["host"], port=addr["port"]))

    def get_least_used(self) -> Tuple[str|None, int|None]:
        if not self.addresses:
            raise Exception("No service addresses available")
        least_used = min(self.addresses, key=lambda addr: addr.count)
        least_used.increment_count()
        return least_used.host, least_used.port

class TLLConsul(metaclass=SingletonMeta):
    def __init__(self):
        self.consul_host = settings.CONSUL_HOST
        self.consul_port = settings.CONSUL_HTTP_PORT
        self.consul_dns_port = settings.CONSUL_DNS_PORT
        self.client = consul.Consul(host=self.consul_host, port=self.consul_port)
        self.user_service_id = uuid.uuid4().hex
        self.user_service_lb = LoadBalancer()

    def register_service(self):
        ip, _ = get_ip_and_port()
        port = settings.SERVER_PORT
        logger.info(f"注册服务，IP: {ip}, Port: {port}")
        self.client.agent.service.register(
            name="user_api",
            service_id=self.user_service_id ,
            address=ip,
            port=port,
            tags=["user_api"],
            check={
                "http": f"http://{ip}:{port}/health",
                "interval": "10s"
            }
        )
        logger.info("服务注册到Consul成功")
        return self.user_service_id
    
    def unregister_service(self):
        if self.user_service_id:
            self.client.agent.service.deregister(self.user_service_id)
            logger.info("服务注销成功")
        else:
            logger.warning("没有注册的服务 ID，无法注销服务")
        
    async def fetch_service_addresses(self):
        """从 Consul DNS 获取服务地址"""
        resolver = asyncresolver.Resolver()
        resolver.nameservers = [self.consul_host]
        resolver.port = self.consul_dns_port
        try:
            response_ip = await resolver.resolve(
                f"user_service.service.consul",
                rdtype=rdatatype.A
            )
            response_port = await resolver.resolve(
                f"user_service.service.consul",
                rdtype=rdatatype.SRV
            )
            ips = [str(rdata) for rdata in response_ip]
            ports = [rdata.port for rdata in response_port]
            addresses = [f"{{ip:{ip}, port:{port}}}" for ip, port in zip(ips, ports)]
            self.user_service_lb.init_addresses(addresses)
        except Exception as e:
            logger.error(f"获取服务地址失败: {e}")

    def get_one_user_service_address(self) -> ServiceAddress:
        """获取一个用户服务地址"""
        return self.user_service_lb.get_least_used()
    
if __name__ == "__main__":
    tll_consul = TLLConsul()
    tll_consul.register_service()
    import asyncio
    asyncio.run(tll_consul.fetch_service_addresses())
    addr = tll_consul.get_one_user_service_address()
    print(addr)
