import os.path
import oss2
from fastapi import HTTPException, status, UploadFile
import settings
import uuid
from asgiref.sync import sync_to_async
from loguru import logger

async def oss_upload_image(file: UploadFile, max_size: int = 1024*1024) -> str|None:
    if file.size > max_size:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File size exceeds the maximum limit of {max_size} bytes"
        )
    extension = os.path.splitext(file.filename)[1].lower()
    if extension not in ['.jpg', '.jpeg', '.png', '.gif']:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unsupported file type. Only .jpg, .jpeg, .png, .gif are allowed."
        )
    access_key_id = os.environ['ALIBABA_CLOUD_ACCESS_KEY_ID']
    access_key_secret = os.environ['ALIBABA_CLOUD_ACCESS_KEY_SECRET']

    # 使用环境变量中获取的RAM用户访问密钥配置访问凭证
    auth = oss2.AuthV4(access_key_id, access_key_secret)
    # 填写Bucket所在地域对应的Endpoint。以华东1（杭州）为例，Endpoint填写为https://oss-cn-hangzhou.aliyuncs.com。
    # yourBucketName填写存储空间名称。
    bucket = oss2.Bucket(auth, settings.ALIYUN_OSS_ENDPOINT, settings.ALIYUN_OSS_BUCKET, region=settings.ALIYUN_OSS_REGION)

    filename = f"{uuid.uuid4()}{extension}"
    filedata = await file.read()
    async_put_object = sync_to_async(bucket.put_object)
    result = await async_put_object(key=filename, data=filedata)
    if result.status == 200:
        domain = f"{settings.ALIYUN_OSS_DOMAIN}/{filename}"
        return domain
    else: 
        # requests -> response.text
        logger.error(result.resp.text)
        return None