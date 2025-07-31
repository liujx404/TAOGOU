MYSQL_HOST = "11.11.11.45"
MYSQL_PORT = 3306
MYSQL_USER = "root"
MYSQL_PASSWORD = "123"
MYSQL_DATABASE = "tll_user_db"

DB_URI = f"mysql+asyncmy://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}?charset=utf8mb4"


# 这个地方后续部署到服务器删， 可以用读取环境变量的形式
DATACENTER_ID = 0
WORDER_ID = 0