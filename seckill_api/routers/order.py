
from user_api.utils import auth
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from hooks.dependence import get_db_session
from models.order import Order
from sqlalchemy import select
from schemas.response import OrderListSchema
auth_handler = auth.AuthHandler()

router = APIRouter(
    prefix="/order",
    tags=["order"], 
    dependencies=[Depends(auth_handler.auth_access_dependency)]
)

@router.get("/list", response_model=OrderListSchema)
async def order_list(
    page: int = 1 , 
    size: int = 10, 
    user_id: int = Depends(auth_handler.auth_access_dependency), 
    session: AsyncSession = Depends(get_db_session)
    ):
    async with session.begin():
        offset = (page - 1) * size
        result = await session.execute(
            select(Order).where(Order.user_id == user_id).order_by(Order.create_time.desc()).limit(size).offset(offset)
        )
        orders = result.scalars().all()
        return {"orders": orders}