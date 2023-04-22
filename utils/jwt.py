from datetime import timedelta, datetime
from jose import jwt

from core.settings import JWT_CONFIG


# Generating JWT access token
def create_access_token(username: str):
    access_token_expires = timedelta(minutes=JWT_CONFIG['ACCESS_TOKEN_EXPIRE_MINUTES'])
    access_token_data = {"sub": username, "exp": datetime.utcnow() + access_token_expires}
    access_token = jwt.encode(access_token_data, JWT_CONFIG['SECRET_KEY'], algorithm=JWT_CONFIG['ALGORITHM'])
    return access_token

