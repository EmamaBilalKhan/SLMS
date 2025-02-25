from datetime import timedelta, datetime
import jwt
import os
import uuid
from fastapi import HTTPException
ACCESS_TOKEN_EXPIRY = 3600

def create_access_token(user_data: dict, expiry: timedelta = None, refresh: bool = False):
    payload = {}
    payload["sub"] = user_data

    if expiry is None:
        expiry = timedelta(seconds=ACCESS_TOKEN_EXPIRY)

    payload["exp"] = datetime.now() + expiry
    payload["jti"] = str(uuid.uuid4())
    payload["refresh"] = refresh
    token = jwt.encode(
        payload= payload,
        key = os.environ.get("JWT_SECRET"),
        algorithm = os.environ.get("JWT_ALGORITHM"),
    )

    return token

def check_refresh_token(token: str):
    try:
        payload = jwt.decode(token, key = os.environ.get("JWT_SECRET"), algorithm = os.environ.get("JWT_ALGORITHM"))
        if not payload.get("refresh"):
            raise HTTPException(status_code=403, detail="Invalid token type")

        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.PyJWTError:
        raise HTTPException(status_code=403, detail="Invalid token")

def decode_token(token: str):
        if not token:
            raise HTTPException(status_code=401, detail="Missing or invalid access token")
        try:
            payload = jwt.decode(token, key = os.environ.get("JWT_SECRET"), algorithm = os.environ.get("JWT_ALGORITHM"))
            if payload.get("refresh"):
                raise HTTPException(status_code=403, detail="Invalid token type")
            return payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Token has expired")
        except jwt.PyJWTError:
            raise HTTPException(status_code=403, detail="Invalid token")