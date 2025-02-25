from fastapi.requests import Request
from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from fastapi.exceptions import HTTPException
from model.courses_model import CreateCourse, RegisterCourseRequest
from crud.course_crud import create_course, get_all_courses, register_new_course
from utils.jwt_auth import decode_token
from bson import ObjectId
from schema.courses_schema import get_courses_collection
from schema.student_course_schema import get_student_course_collection
student_course_collection = get_student_course_collection()
course_collection = get_courses_collection()

router = APIRouter(prefix="/courses", tags=["Courses"])

def create_course_middleware(request: Request):
    auth_header = request.headers.get("Authorization")

    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid Authorization header")

    token = auth_header.split("Bearer ")[1].strip()

    try:
        decoded_token = decode_token(token)
        sub_data = decoded_token.get("sub", {})
        user_id = sub_data.get("id")
        user_role = sub_data.get("role")

        if user_role not in ["Teacher", "Admin"]:
            raise HTTPException(status_code=403,detail="Only Teacher or Admin can create a course")

        return user_id

    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)


def register_course_middleware(request: Request):
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid Authorization header")

    token = auth_header.split("Bearer ")[1].strip()

    try:
        decoded_token = decode_token(token)
        sub_data = decoded_token.get("sub", {})
        user_id = sub_data.get("id")
        user_role = sub_data.get("role")

        if user_role != "Student":
            raise HTTPException(status_code=403, detail="Only Student can register a course")

        return user_id

    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)

def validate_course_register(course_id: str):
    try:
        if not ObjectId.is_valid(course_id):
            raise HTTPException(status_code=400, detail="Invalid course ID format")

        document = course_collection.find_one({"_id": ObjectId(course_id)},{ "_id": 1})
        if document is None:
            raise HTTPException(status_code=404, detail="Course does not exist")
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {e}")



@router.post("/create-course")
def create_new_course(course: CreateCourse, user_id: str = Depends(create_course_middleware)):
    try:
        course = course.model_dump()
        course["teacherID"] = user_id
        response = create_course(course)

        if "error" in response:
            return JSONResponse(content=response, status_code=400)

        return JSONResponse(content=response, status_code=201)
    except HTTPException as e:
        return JSONResponse(content=e.detail, status_code=e.status_code)
    except Exception as e:
        return JSONResponse(content=str(e), status_code=500)

@router.get("/get-courses")
def get_courses():
    try:
        response = get_all_courses()
        if "error" in response:
            return JSONResponse(content=response, status_code=500)

        return JSONResponse(content={"courses":response}, status_code=200)
    except HTTPException as e:
        return JSONResponse(content=e.detail, status_code=e.status_code)
    except Exception as e:
        return JSONResponse(content=str(e), status_code=500)


@router.post("/register-course")
def register_course(
        course_id: RegisterCourseRequest,
        student_id: str = Depends(register_course_middleware)
):
    try:
        course_id = course_id.model_dump()
        validate_course_register(course_id["course_id"])
        response = register_new_course({"course_id": course_id["course_id"], "student_id": student_id})

        if "error" in response:
            return JSONResponse(content=response, status_code=400)

        return JSONResponse(content=response, status_code=201)
    except HTTPException as e:
        return JSONResponse(content=e.detail, status_code=e.status_code)
    except Exception as e:
        return JSONResponse(content=str(e), status_code=500)




