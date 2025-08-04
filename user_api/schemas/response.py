from pydantic import BaseModel
from enum import Enum

class ResultEnum(Enum):
    SUCCESS = 1
    FAILURE = 2

class ResultModule(BaseModel):
    result: ResultEnum = ResultEnum.SUCCESS

class UserModel(BaseModel):
    id: int
    mobile: str
    username: str
    avatar: str
    is_active: bool
    is_staff: bool

class LoginedModel(BaseModel):
    user: UserModel
    access_token: str
    refresh_token: str