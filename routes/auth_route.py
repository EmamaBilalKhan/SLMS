from fastapi import Depends
from fastapi.requests import Request
from starlette.responses import JSONResponse
from fastapi import APIRouter, Body
from model.user_model import CreateUser, LoginUser
from crud.auth_crud import create_user, login_user
from utils.password_manager import hash_password
from utils.jwt_auth import create_access_token, check_refresh_token
from datetime import timedelta
from crud.auth_crud import verify_user_email
from fastapi.exceptions import HTTPException
from utils.jwt_auth import decode_token

router = APIRouter(prefix="/auth", tags=["AUTH"])

def verify_email_middleware(request: Request):
    auth_header = request.headers.get("Authorization")

    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid Authorization header")

    token = auth_header.split("Bearer ")[1].strip()

    try:
        decoded_token = decode_token(token)
        sub_data = decoded_token.get("sub", {})
        user_id = sub_data.get("id")
        return user_id

    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)

@router.get("/")
def root():
    return {"message": "Hello from Users API"}

@router.post("/register")
def register(user: CreateUser):
    try:
        user = user.model_dump()
        user["password"] = hash_password(user["password"]).decode("utf-8")
        response = create_user(user)
        if "error" in response.keys():
            return JSONResponse(content=response, status_code=400)
        else:
            return JSONResponse(content=response, status_code=201)
    except HTTPException as e:
        return JSONResponse(content=e.detail, status_code=e.status_code)
    except Exception as e:
        return JSONResponse(content=str(e), status_code=500)

@router.post("/login")
def login(user: LoginUser):
    try:
        user = user.model_dump()
        result = login_user(user["email"], user["password"])
        if "client_error" in result.keys():
            return JSONResponse(content=result, status_code=400)
        if "error" in result.keys():
            return JSONResponse(content=result, status_code=500)
        else:
            access_token = create_access_token(
                user_data={"id": result["_id"], "role": result["role"]},
            )
            refresh_token = create_access_token(
                user_data={"id": result["_id"], "role": result["role"]},
                refresh=True,
                expiry = timedelta(days=1)
            )
            response = JSONResponse(content={"message": "successful login","is_verified": result["is_verified"], "access_token": access_token.decode(encoding="utf-8"), "refresh_token": refresh_token.decode(encoding="utf-8") ,"user_role":result["role"], "userID": result["_id"]}, status_code=200)
            return response
    except HTTPException as e:
        return JSONResponse(content=e.detail, status_code=e.status_code)
    except Exception as e:
        return JSONResponse(content=str(e), status_code=500)

@router.post("/refresh")
def refresh(refresh_token: str = Body(...,embed=True)):
    try:
        payload = check_refresh_token(refresh_token)
        access_token = create_access_token(user_data= payload["sub"], refresh=False)
        user_role = payload["sub"]["role"]
        user_id = payload["sub"]["id"]
        response = JSONResponse(content={"message": "successful refresh","user_id": user_id,"access_token": access_token.decode(encoding="utf-8"), "user_role": user_role}, status_code=200)
        return response
    except HTTPException as e:
        return JSONResponse(status_code=e.status_code, content={"error":e.detail})

@router.post("/verify-email")
def verify_email(code: str = Body(embed=True),user_id: str = Depends(verify_email_middleware)):
    response = verify_user_email(user_id, code)
    if "error" in response.keys():
        return JSONResponse(content=response, status_code=500)
    else:
        return JSONResponse(content=response, status_code=200)


@router.get("/logout")
def logout():
    return JSONResponse(content={"message": "successful logout"}, status_code=200)
