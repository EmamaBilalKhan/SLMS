from fastapi.requests import Request
from bson import ObjectId
from fastapi.exceptions import HTTPException
from starlette.responses import JSONResponse
from crud.progress_crud import get_student_progress
from utils.jwt_auth import decode_token
from fastapi import APIRouter, Depends
from schema.submission_schema import get_submissions_collection

router = APIRouter(prefix="/progress", tags=["progress"])

submissions_collection = get_submissions_collection()

def validate_progress_middleware(request: Request):
    auth_header = request.headers.get("Authorization")

    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid Authorization header")

    token = auth_header.split("Bearer ")[1].strip()

    try:
        decoded_token = decode_token(token)
        sub_data = decoded_token.get("sub", {})
        user_role = sub_data.get("role")

        if user_role not in ["Teacher", "Student"]:
            raise HTTPException(status_code=403, detail="Only Teacher or student can access this route")

    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)

def validate_student_id(student_id: str):
        if not ObjectId.is_valid(student_id):
            raise HTTPException(status_code=400, detail="Invalid student ID format")
        response = submissions_collection.find_one({"student_id": student_id}, {"_id": 1})
        if response is None:
            raise HTTPException(status_code=404, detail="No submissions exist against this student")

@router.get("/{student_id}", dependencies=[Depends(validate_progress_middleware), Depends(validate_student_id)])
def get_progress(student_id: str):
    try:
        response = get_student_progress(student_id)
        return JSONResponse(status_code=200, content=response)
    except HTTPException as e:
        return JSONResponse(content=e.detail, status_code=e.status_code)
    except Exception as e:
        return JSONResponse(content=str(e), status_code=500)
