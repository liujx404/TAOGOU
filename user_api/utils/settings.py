from datetime import timedelta


JWT_SECRET_KEY = "asdasfsfgtgdfgqfdcda"
JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=2)
JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=15)