from . import Base
import string
import random
from sqlalchemy import Column, Integer, String, Boolean, DateTime


def generate_username():
    #猫猫98729
    code = "".join(random.sample(string.digits, 6))
    return "猫猫" + code


class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    mobile = Column(String(20), unique=True, index=True)
    username = Column(String(20), default=generate_username)
    password = Column(String(300), nullable=True)
    avatar = Column(string(200), nullable=True)
    is_activate = Column(Boolean, default=True)
    is_staff = Column(Boolean, default=False)
    last_login = Column(DateTime, nullable=True)