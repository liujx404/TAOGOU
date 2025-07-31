from . import Base
import string
import random
from sqlalchemy import Column, BigInteger, String, Boolean, DateTime
from utils.snowflake.snowflake import Snowflake
from settings import DATACENTER_ID, WORDER_ID
from sqlalchemy_serializer import SerializerMixin


snowflake = Snowflake(DATACENTER_ID, WORDER_ID)

def generate_snow_flake_id():
    new_id = snowflake.get_id()
    return new_id

def generate_username():
    #猫猫98729
    code = "".join(random.sample(string.digits, 6))
    return "猫猫" + code


class User(Base, SerializerMixin):
    __tablename__ = 'user'
    #serialize_only = ('id', 'mobile')
    serialize_rules = ('-password',)
    id = Column(BigInteger, primary_key=True, default=generate_snow_flake_id)
    mobile = Column(String(20), unique=True, index=True)
    username = Column(String(20), default=generate_username)
    password = Column(String(300), nullable=True)
    avatar = Column(String(200), nullable=True)
    is_active = Column(Boolean, default=True)
    is_staff = Column(Boolean, default=False)
    last_login = Column(DateTime, nullable=True)