from fastapi import APIRouter, Depends, HTTPException, Security, UploadFile
from fastapi.security import HTTPAuthorizationCredentials
import string 
import random
import aiohttp  # 导入异步 HTTP 库
from schemas.response import ResultModule, ResultEnum, LoginedModel, UserModel, UpdatedAvatarModel
from utils.cache import TLLRedis
from schemas.request import LoginModel, UpdateUsernameModel, UpdatePasswordModel
from utils.auth import AuthHandler
from services.user import UserServiceClient
from utils.alyoss import oss_upload_image
from fastapi import status
router = APIRouter(prefix="/user")
ttl_redis = TLLRedis()
auth_handler = AuthHandler()
user_service_client = UserServiceClient()   

@router.get('/smscode/{mobile}', response_model=ResultModule)
async def get_smscode(mobile: str):

    code = "".join(random.sample(string.digits, 4))
    body = {'name': '推送助手', 'code': code, 'targets': mobile}
    
    # async with aiohttp.ClientSession() as session:  # 创建异步会话
    #     try:
    #         async with session.post(
    #             url='https://push.spug.cc/send/nbONk8gy6Kj34gXG',
    #             json=body  
    #         ) as response:
    #             push_result = await response.json()
    #             print(f"推送结果: {push_result}")
                
    #     except Exception as e:
    #         return ResultModule(result=ResultEnum.FAILURE)

    print(code)
    await ttl_redis.set_sms_code(mobile, code)
    return ResultModule(result=ResultEnum.SUCCESS)

@router.post('/login', response_model=LoginedModel)
async def login(data: LoginModel):
    mobile = data.mobile
    code = data.code 
    cached_code = await ttl_redis.get_sms_code(mobile)
    print(cached_code)
    if code != cached_code:
        raise HTTPException(status_code=400, detail="验证码错误")
    #连接rpc服务
    user = await user_service_client.get_or_create_userby_mobile(mobile)
    if not user:
        raise HTTPException(status_code=404, detail="用户未找到或创建失败")
    #生成token
    tokens = auth_handler.encode_login_token(user.id)
    return {
        'user': user,
        'access_token': tokens['access_token'],
        'refresh_token': tokens['refresh_token']
    }


@router.post('/access/token')
async def access_token_view(user_id: int = Depends(auth_handler.auth_access_dependency)):
    return {"detail": "access token验证成功！", 'user_id': user_id}

@router.get('/refresh/token')
async def refresh_token_view(user_id: int = Depends(auth_handler.auth_refresh_dependency)):
    access_token = auth_handler.encode_update_token(user_id)
    return access_token

@router.put('/update/username', response_model=ResultModule)
async def update_username(data: UpdateUsernameModel, user_id: int = Depends(auth_handler.auth_access_dependency), response_model=ResultModule):
    username = data.username
    await user_service_client.update_username(user_id, username)
    return ResultModule()

@router.put('/update/password', response_model=ResultModule)
async def update_password(data: UpdatePasswordModel, user_id: int = Depends(auth_handler.auth_access_dependency)):
    password = data.password
    await user_service_client.update_password(user_id, password)
    return ResultModule()

@router.get('mine', response_model=UserModel)
async def get_user_info(user_id: int = Depends(auth_handler.auth_access_dependency)):
    user = await user_service_client.get_user_by_id(user_id)
    return user

@router.put('/update/avatar', response_model=UpdatedAvatarModel)
async def update_avatar(file: UploadFile, user_id: int = Depends(auth_handler.auth_access_dependency)):
    file_url = await oss_upload_image(file)
    if not file_url:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="头像上传失败")
    await user_service_client.update_avatar(user_id, file_url)
    return UpdatedAvatarModel(file_url=file_url)