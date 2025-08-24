from . import Base
from sqlalchemy import Column, Integer, String, ForeignKey, BigInteger
from sqlalchemy.orm import relationship
import uuid
from sqlalchemy_serializer import SerializerMixin
from .user import User
def get_generated_id():
    return uuid.uuid4().hex

class Address(Base, SerializerMixin):
    __tablename__ = 'address'
    serialize_only = ('id', 'realname', 'mobile', 'region', 'detail')
    id = Column(String(32), primary_key=True, default=get_generated_id)
    realname = Column(String(20))
    mobile = Column(String(20))
    region = Column(String(100))
    detail = Column(String(200))

    user_id = Column(BigInteger, ForeignKey('user.id'))
    user = relationship(User, backref='addresses')