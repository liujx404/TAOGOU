from fastapi import APIRouter, Depends, HTTPException
from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
from sqlalchemy import select, update
from models.seckill import Seckill
from schemas.response import SeckillListSchema, SeckillSchema
from schemas.request import BuySchema, AddStockSchema
from hooks.dependence import get_db_session
from models import AsyncSession
from schemas.response import SeckillListSchema, SeckillSchema
from hooks.dependence import get_db_session
from models import AsyncSession
from utils.auth import AuthHandler  
from schemas.request import BuySchema
from models.order import Order, OrderStatusEnum
from alipay import AliPay
import settings
import aiofiles

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



authHandler = AuthHandler()
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

@router.post('/lock')
async def mysql_lock(session: AsyncSession = Depends(get_db_session)):
    # 悲观锁实现
    # async with session.begin():
    #     seckill_id = 1959267158206709760
    #     result = await session.execute(select(Seckill).where(Seckill.id == seckill_id).with_for_update())
    #     seckill = result.scalar()
    #     if not seckill:
    #         raise HTTPException(status_code=404, detail="Seckill not found")
    #     seckill.stock -= 1
    #     await session.commit()
    #     return {"message": "Stock decremented", "remaining_stock": seckill.stock}
    
    # 乐观锁实现
    async with session.begin():
        seckill_id = 1959267158206709760
        result = await session.execute(select(Seckill).where(Seckill.id == seckill_id))
        seckill = result.scalar()
        seckill.stock -= 1
    return {"message": "Stock decremented", "remaining_stock": seckill.stock}

@router.post("/buy")
async def buy(data: BuySchema, session: AsyncSession = Depends(get_db_session), user_id: int = Depends(authHandler.auth_access_dependency)):

    # 异步读取文件
    async with aiofiles.open('keys/app_private.key', mode='r') as f:
        app_private_key_string = await f.read()
    async with aiofiles.open('keys/alipay_public.pem', mode='r') as f:
        alipay_public_key_string = await f.read()
    # with open('keys/app_private.key', mode='r') as f:
    #     app_private_key_string = f.read()
    # with open('keys/alipay_public.pem', mode='r') as f:
    #     alipay_public_key_string = f.read()

    alipay = AliPay(
        appid=settings.ALIPAY_APP_ID,
        # app_notify_url="http://www.example.com/notify",  # 默认回调 url
        app_notify_url="http://318621gs38qz.vicp.fun/seckill/alipay/notify",
        app_private_key_string=app_private_key_string,
        # 支付宝的公钥，验证支付宝回传消息使用，不是你自己的公钥,
        alipay_public_key_string=alipay_public_key_string,
        sign_type="RSA2",  # RSA 或者 RSA2
        # 沙箱环境需要设置debug=True
        debug=True,  # 默认 False
        verbose=True,  # 输出调试数据
    )
    
    order_string = alipay.api_alipay_trade_app_pay(
        out_trade_no=order.id,
        total_amount=float(order.amount),
        subject=seckill.commodity.title
     )
    
    seckill_id = data.seckill_id
    count = data.count
    address = data.address
    
    async with session.begin():
        result = await session.execute(select(Order).where(Order.user_id == user_id, Order.seckill_id == seckill_id))
        order = result.scalar()
        if order:
            raise HTTPException(status_code=400, detail="You have already placed an order for this seckill item.")
        
        seckill_result = await session.execute(select(Seckill).where(Seckill.id == seckill_id).with_for_update())
        seckill = seckill_result.scalar()
        if not seckill:
            raise HTTPException(status_code=404, detail="Seckill not found")
        if seckill.stock < count:
            raise HTTPException(status_code=400, detail="Insufficient stock")
        # 更新库存
        await session.execute(update(Seckill).where(Seckill.id == seckill_id).values(stock=Seckill.stock - count))
        
    async with session.begin():
        order = Order(
            user_id=user_id,
            seckill_id=seckill_id,
            count=count,
            amount=seckill.sk_price * count,
            address=address,
            status=OrderStatusEnum.UNPAYED
        )
        session.add(order)
    
    return {"message": "Order placed successfully", "order_id": order.id, "order_string": order_string}
        
@router.post("/addstock/{seckill_id}")
async def add_stock(seckill_id: int, request: AddStockSchema, session: AsyncSession = Depends(get_db_session)):
    async with session.begin():
        result = await session.execute(select(Seckill).where(Seckill.id == seckill_id).with_for_update())
        seckill = result.scalar()
        if not seckill:
            raise HTTPException(status_code=404, detail="Seckill not found")
        seckill.stock += request.amount
    return {"message": "Stock added", "new_stock": seckill.stock}

@router.get('/detail/{seckill_id}')
async def get_seckill_detail(seckill_id: int, session: AsyncSession = Depends(get_db_session)):
    async with session.begin():
        result = await session.execute(select(Seckill).where(Seckill.id == seckill_id))
        seckill = result.scalar()
        if not seckill:
            raise HTTPException(status_code=404, detail="Seckill not found")
        return seckill

