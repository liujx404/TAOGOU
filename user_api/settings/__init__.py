from datetime import timedelta


JWT_SECRET_KEY = "asdasfsfgtgdfgqfdcda"
JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=2)
JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=15)

ALIYUN_OSS_ENDPOINT = "https://oss-cn-hangzhou.aliyuncs.com"
ALIYUN_OSS_BUCKET = "taogoumy"
ALIYUN_OSS_REGION = "cn-hangzhou"
ALIYUN_OSS_DOMAIN = f"https://{ALIYUN_OSS_BUCKET}.oss-{ALIYUN_OSS_REGION}.aliyuncs.com"

GRPC_SERVICE_NAMES = ['user_api', 'user_service']
CONSUL_HOST = "11.11.11.130"
CONSUL_HTTP_PORT = 8500
CONSUL_DNS_PORT = 8600  

SERVER_PORT = 8000