from utils.single import SingletonMeta
import grpc
from services.protos import address_pb2_grpc, address_pb2
from .decroators import grpc_error_handeler
from utils.tll_consul import TLLConsul

tllconsul = TLLConsul()
class AddressStub:
    def __init__(self):
        pass

    @property
    def user_service_addr(self):
        """获取用户服务地址"""
        host, port = tllconsul.get_one_user_service_address()
        return f"{host}:{port}"
    
    async def __aenter__(self):
        self.channel = grpc.aio.insecure_channel(self.user_service_addr)
        self.stub = address_pb2_grpc.AddressStub(self.channel)
        return self.stub
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.channel.close()


class AddressServiceClient(metaclass=SingletonMeta):

    @grpc_error_handeler
    async def create_address(
        self,
        user_id: int,
        realname: str,
        mobile: str,
        region: str,
        detail: str
    ):
        async with AddressStub() as stub:
            request = address_pb2.CreateAddressRequest(
                user_id=user_id,
                realname=realname,
                mobile=mobile,
                region=region,
                detail=detail
            )
            response = await stub.CreateAddress(request)
            return response.address
        
    @grpc_error_handeler
    async def update_address(
        self,
        id: str, 
        user_id: int,
        realname: str,
        mobile: str,
        region: str,
        detail: str
    ):
        async with AddressStub() as stub:
            request = address_pb2.UpdateAddressRequest(
                id=id,
                user_id=user_id,
                realname=realname,
                mobile=mobile,
                region=region,
                detail=detail
            )
            await stub.UpdateAddress(request)

    @grpc_error_handeler
    async def delete_address(self, user_id: int, id: str):
        async with AddressStub() as stub:
            request = address_pb2.DeleteAddressRequest(
                user_id=user_id,
                id=id
            )
            await stub.DeleteAddress(request)

    @grpc_error_handeler
    async def get_address_by_id(self, user_id: int, id: str):
        async with AddressStub() as stub:
            request = address_pb2.AddressIdRequest(
                user_id=user_id,
                id=id
            )
            response = await stub.GetAddressById(request)
            return response.address
        
    @grpc_error_handeler    
    async def get_address_list(self, user_id: int, page: int=1, size: int=10):
        async with AddressStub() as stub:
            request = address_pb2.AddressListRequest(
                user_id=user_id,
                page=page,
                size=size
            )
            response = await stub.GetAddressList(request)
            return response.addresses


    
    


