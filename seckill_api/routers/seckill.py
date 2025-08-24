from fastapi import APIRouter, Depends, HTTPException
from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
from sqlalchemy import select
from models.seckill import Seckill
from schemas.response import SeckillListSchema, SeckillSchema
from hooks.dependence import get_db_session
from models import AsyncSession
router = APIRouter(
    prefix="/seckill",
    tags=["seckill"],
)

# @router.get("/ing", response_model=SeckillListSchema)
# async def get_ing_seckills(request: Request, page: int = 1, size: int = 10):
#     async with request.state.session.begin():
#         # 秒杀中： start_time <= now <= end_time
#         now = datetime.now()
#         stmt = select(Seckill).where(Seckill.start_time <= now, Seckill.end_time >= now).order_by(Seckill.create_time.desc()).limit(size).offset((page - 1) * size)
#         result = await request.state.session.execute(stmt)
#         rows = result.scalars()
#         return {"seckills": rows}

# @router.get("/will", response_model=SeckillListSchema)
# async def get_will_seckills(request: Request, page: int = 1, size: int = 10):
#     async with request.state.session.begin():
#         # 即将开始： now < start_time
#         now = datetime.now()
#         stmt = select(Seckill).where(Seckill.start_time > now).order_by(Seckill.create_time.desc()).limit(size).offset((page - 1) * size)
#         result = await request.state.session.execute(stmt)
#         rows = result.scalars()
#         return {"seckills": rows}

@router.get("/ing", response_model=SeckillListSchema)
async def get_ing_seckills(session: AsyncSession = Depends(get_db_session), page: int = 1, size: int = 10):
    async with session.begin():
        # 秒杀中： start_time <= now <= end_time
        now = datetime.now()
        stmt = select(Seckill).where(Seckill.start_time <= now, Seckill.end_time >= now).order_by(Seckill.create_time.desc()).limit(size).offset((page - 1) * size)
        result = await session.execute(stmt)
        rows = result.scalars()
        return {"seckills": rows}

@router.get("/will", response_model=SeckillListSchema)
async def get_will_seckills(session: AsyncSession = Depends(get_db_session), page: int = 1, size: int = 10):
    async with session.begin():
        # 即将开始： now < start_time
        now = datetime.now()
        stmt = select(Seckill).where(Seckill.start_time > now).order_by(Seckill.create_time.desc()).limit(size).offset((page - 1) * size)
        result = await session.execute(stmt)
        rows = result.scalars()
        return {"seckills": rows}
    
@router.get("/detail/{seckill_id}", response_model=SeckillSchema)
async def get_seckill_detail(seckill_id: int, session: AsyncSession = Depends(get_db_session)):
    print(seckill_id)
    async with session.begin():
        result = await session.execute(select(Seckill).where(Seckill.id == seckill_id))
        seckill = result.scalar()
        if not seckill:
            raise HTTPException(status_code=404, detail="Seckill not found")
        return seckill
