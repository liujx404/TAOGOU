from protos.address_pb2_grpc import AddressServicer
from protos import address_pb2
from sqlalchemy import select, update, delete
from fastapi import APIRouter, Depends, HTTPException
import grpc
from models.user import User
from models.address import Address
from google.protobuf import empty_pb2

class AddressServicer(AddressServicer):
    
    async def CreateAddress(self, request: address_pb2.CreateAddressRequest, context, session):
        async with session.begin():
            user_id = request.user_id
            realname = request.realname
            mobile = request.mobile
            region = request.region
            detail = request.detail
            try:
                address = Address(
                    user_id=user_id,
                    realname=realname,
                    mobile=mobile,
                    region=region,
                    detail=detail
                )
                session.add(address)
            except Exception as e:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details(f"用户不存在")
        response = address_pb2.AddressResponse(address=address.to_dict())
        return response

    async def UpdateAddress(self, request: address_pb2.UpdateAddressRequest, context, session):
        async with session.begin():
            id = request.id
            realname = request.realname
            mobile = request.mobile
            region = request.region
            detail = request.detail
            user_id = request.user_id
            result = await session.execute(update(Address).where(Address.id == id, Address.user_id == user_id).values(
                realname=realname,
                mobile=mobile,
                region=region,
                detail=detail
            ))
            rowcount = result.rowcount
            if rowcount == 0:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details(f'ID{id}不存在或不属于用户{user_id}')
        return empty_pb2.Empty()
    
    async def DeleteAddress(self, request: address_pb2.DeleteAddressRequest, context, session):
        async with session.begin():
            id = request.id
            user_id = request.user_id
            result = await session.execute(delete(Address).where(Address.id == id, Address.user_id == user_id))
            rowcount = result.rowcount
            if rowcount == 0:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details(f'ID{id}不存在或不属于用户{user_id}')
        return empty_pb2.Empty()
    
    async def GetAddressById(self, request: address_pb2.AddressIdRequest, context, session):
        async with session.begin():
            id = request.id
            query = await session.execute(select(Address).where(Address.id == id))
            address = query.scalar()
            return address_pb2.AddressResponse(address=address.to_dict()) if address else context.set_code(grpc.StatusCode.NOT_FOUND) and context.set_details(f'ID{id}不存在！')

    async def GetAddressList(self, request: address_pb2.AddressListRequest, context, session):
        async with session.begin():
            user_id = request.user_id
            page = request.page
            size = request.size
            offset = (page - 1) * size
            result = await session.execute(select(Address).where(Address.user_id==user_id).limit(size).offset(offset))
            rows = result.scalars()
        addresses = []
        for row in rows:
            addresses.append(row.to_dict())
        return address_pb2.AddressListResponse(addresses=addresses)