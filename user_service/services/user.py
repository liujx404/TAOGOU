from protos import user_pb2, user_pb2_grpc
from models import AsyncSessionFactory
from models.user import User
import sqlalchemy
import grpc
from sqlalchemy import select

class UserServicer(user_pb2_grpc.UserServicer):
    
    async def CreateUser(self, request: user_pb2.CreateUserRequest, context, session):  
        mobile = request.mobile
        try:  
            async with session.begin():
                user = User(mobile=mobile)
                session.add(user)   
            session.refresh(user)
            response = user_pb2.UserInfoResponse(user=user.to_dict())
            return response
        except sqlalchemy.exc.IntegrityError:
            context.set_code(grpc.StatusCode.ALREADY_EXISTS)
            context.set_details('该手机号已经存在！')


    async def GetUserById(self, request: user_pb2.IdRequest, context, session):
        try:
            async with session.begin():
                user_id = request.id
                query = await session.execute(select(User).where(User.id==user_id))
                user = query.scalar()
                if not user:
                    context.set_code(grpc.StatusCode.NOT_FOUND)
                    context.set_details('该用户不存在！')
                else:
                    response = user_pb2.UserInfoResponse(user=user.to_dict())
                    return response
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details('服务器错误！')

    async def GetUserByMobile(self, request: user_pb2.MobileRequest, context, session):
        try:
            async with session.begin():
                mobile = request.mobile
                query = await session.execute(select(User).where(User.mobile==mobile))
                #(User,) => User
                user = query.scalar()
                if not user:
                    context.set_code(grpc.StatusCode.NOT_FOUND)
                    context.set_details("该用户不存在！")
                else:
                    response = user_pb2.UserInfoResponse(user=user.to_dict())
                    return response
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details("服务器错误")

    def UpdateUserAvatar(self, request, context):
        pass
    def UpdateUsername(self, request, context):
        pass
    def UpdatePassword(self, request, context):
        pass
    def GetUserList(self, request, context):
        pass
    def VerifyUser(self, request, context):
        pass
