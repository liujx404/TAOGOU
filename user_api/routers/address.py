from fastapi import APIRouter, Depends, HTTPException, Security, UploadFile
from fastapi.security import HTTPAuthorizationCredentials
from schemas.response import AddressModel, ResultModule, ResultEnum, AddressListModel
from schemas.request import CreateAddressModel, DeleteAddressModel, UpdateAddressModel
from utils.auth import AuthHandler
from services.address import AddressServiceClient
router = APIRouter(prefix="/address")

auth_handler = AuthHandler()
address_service_client = AddressServiceClient()

@router.post('/create')
async def create_address(data: CreateAddressModel, user_id=Depends(auth_handler.auth_access_dependency)):
    address = await address_service_client.create_address(
        user_id=user_id,
        realname=data.realname,
        mobile=data.mobile,
        region=data.region,
        detail=data.detail
    )
    # 将 protobuf 对象转换为字典以便 JSON 序列化
    return {
        "id": address.id,
        "realname": address.realname,
        "mobile": address.mobile,
        "region": address.region,
        "detail": address.detail
    }
                         
@router.delete('/delete', response_model=ResultModule)
async def delete_address(data: DeleteAddressModel, user_id=Depends(auth_handler.auth_access_dependency)):
    await address_service_client.delete_address(user_id=user_id, id=data.id)
    return ResultModule(result=ResultEnum.SUCCESS)


@router.put('/update', response_model=ResultModule)
async def update_address(data: UpdateAddressModel, user_id: int=Depends(auth_handler.auth_access_dependency)):
    await address_service_client.update_address(
        id=data.id,
        realname=data.realname,
        mobile=data.mobile,
        region=data.region,
        detail=data.detail,
        user_id=user_id,
    )
    return ResultModule(result=ResultEnum.SUCCESS)

@router.get('/detail/{id}', response_model=AddressModel)
async def update_address(id: str, user_id: int=Depends(auth_handler.auth_access_dependency)):
    address = await address_service_client.get_address_by_id(user_id, id)
    return {
        "id": address.id,
        "real_name": address.realname,
        "mobile": address.mobile,
        "region": address.region,
        "detail": address.detail
    }

# /address/list?page=1&size=20
@router.get('/list', response_model=AddressListModel)
async def update_address(page: int=1, size: int=10, user_id: int=Depends(auth_handler.auth_access_dependency)):
    addresses = await address_service_client.get_address_list(user_id, page=page, size=size)
    return {"addresses": addresses}
