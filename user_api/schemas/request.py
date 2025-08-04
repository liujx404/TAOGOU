from pydantic import BaseModel, field_validator, Field
import re


class LoginModel(BaseModel):
    # 限制手机号为字符串类型，且长度在合理范围内（11位国内手机号）
    mobile: str = Field(..., min_length=11, max_length=11, description="手机号必须为11位数字")
    code: str = Field(..., min_length=4, max_length=6, description="验证码长度为4-6位")

    @field_validator('mobile')
    def validate_mobile(cls, v):
        """验证手机号格式（以1开头的11位数字）"""
        # 正则表达式：以1开头，后跟10位数字
        pattern = r'^1[3-9]\d{9}$'
        if not re.match(pattern, v):
            raise ValueError('手机号格式不正确，必须是11位有效数字（以13-19开头）')
        return v


class UpdateUsernameModel(BaseModel):
    username: str

class UpdatePasswordModel(BaseModel):
    password: str = Field(..., min_length=6, max_length=20, description="密码长度为6-20位") 

