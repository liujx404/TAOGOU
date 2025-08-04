from utils.single import SingletonMeta
import grpc
from services.protos import user_pb2_grpc, user_pb2
from .decroators import grpc_error_handeler

class UserStub:
    def __init__(self):
        self.user_service_addr = "localhost:5001"
    
    async def __aenter__(self):
        self.channel = grpc.aio.insecure_channel(self.user_service_addr)
        self.stub = user_pb2_grpc.UserStub(self.channel)
        return self.stub
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.channel.close()

class UserServiceClient(metaclass=SingletonMeta):

    @grpc_error_handeler
    async def get_or_create_userby_mobile(self, mobile: str):
        async with UserStub() as stub:
            request = user_pb2.MobileRequest(mobile=mobile)
            response = await stub.GetOrCreateUserByMobile(request)
            return response.user
        
    @grpc_error_handeler
    async def update_username(self, user_id: str, username: str):
        async with UserStub() as stub:
            request = user_pb2.UsernameRequest(id=user_id, username=username)
            await stub.UpdateUsername(request)

    @grpc_error_handeler
    async def update_password(self, user_id: str, password: str):
        async with UserStub() as stub:
            request = user_pb2.PasswordRequest(id=user_id, password=password)
            await stub.UpdatePassword(request)

    @grpc_error_handeler
    async def update_avatar(self, user_id: str, avatar: str):
        async with UserStub() as stub:
            request = user_pb2.AvatarRequest(id=user_id, avatar=avatar)
            await stub.UpdateAvatar(request)

    @grpc_error_handeler
    async def get_user_by_id(self, user_id: int):
        async with UserStub() as stub:
            request = user_pb2.UserIdRequest(id=user_id)
            response = await stub.GetUserById(request)
            return response.user
    
    @grpc_error_handeler
    async def get_user_by_mobile(self, mobile: str):
        async with UserStub() as stub:
            request = user_pb2.MobileRequest(mobile=mobile)
            response = await stub.GetUserByMobile(request)
            return response.user
    
    @grpc_error_handeler
    async def get_user_list(self, page: int = 1, page_size: int = 10):
        async with UserStub() as stub:
            request = user_pb2.PageRequest(page=page, page_size=page_size)
            response = await stub.GetUserList(request)
            return response.users
        
    @grpc_error_handeler
    async def verify_user(self, mobile: str, password: str):
        async with UserStub() as stub:
            request = user_pb2.VerifyUserRequest(mobile=mobile, password=password)
            response = await stub.VerifyUser(request)
            return response.user
