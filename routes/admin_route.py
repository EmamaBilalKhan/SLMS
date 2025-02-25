from fastapi.requests import Request
from fastapi.exceptions import HTTPException
from fastapi import APIRouter, Depends
from starlette.responses import JSONResponse
from utils.jwt_auth import decode_token
from crud.admin_crud import get_all_users
router = APIRouter(prefix="/admin", tags=["admin"])

def validate_admin_middleware(request: Request):
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return JSONResponse(status_code=401, content={"message": "Missing or invalid Authorization header"})

    token = auth_header.split("Bearer ")[1].strip()
    try:
        decoded_token = decode_token(token)
        sub_data = decoded_token.get("sub")
        user_role = sub_data.get("role")
        if user_role != "Admin":
            raise HTTPException(status_code=403, detail="Only Admin can access this route")

    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)


@router.get("/")
def get_admin():
    return {"message": "Hello from Admin Route"}


@router.get("/users", dependencies=[Depends(validate_admin_middleware)])
def get_users():
    try:
        response = get_all_users()
        if "error" in response:
            return JSONResponse(status_code=500, content=response)
        return JSONResponse(status_code=200, content=response)
    except HTTPException as e:
        return JSONResponse(content=e.detail, status_code=e.status_code)
    except Exception as e:
        return JSONResponse(content=str(e), status_code=500)