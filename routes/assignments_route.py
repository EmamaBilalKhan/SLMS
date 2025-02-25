from bson import ObjectId
from fastapi import APIRouter
from model.assignments_model import CreateAssignment
from fastapi.exceptions import HTTPException
from utils.jwt_auth import decode_token
from fastapi.requests import Request
from fastapi import Depends
from fastapi.responses import JSONResponse
from crud.assigments_crud import create_new_assignment, submit_new_assignment, grade_submission, get_all_assignments, get_all_submissions
from schema.assignment_schema import get_assignment_collection
from model.submissions_model import CreateSubmissions, GradeSubmissions
from schema.submission_schema import get_submissions_collection

router = APIRouter(prefix="/assignments", tags=["assignments"])
assignment_collection = get_assignment_collection()
submissions_collection = get_submissions_collection()

def create_assignment_middleware(request: Request):
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
            raise HTTPException(status_code=403,detail="Only Teacher or Admin can create an assignment")

        return user_id

    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)


def submit_assignment_middleware(request: Request):
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
            raise HTTPException(status_code=403, detail="Only Student can submit an assignment")

        return user_id

    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)

def validate_assignment_id(assignment_id: str):
        try:
            if not ObjectId.is_valid(assignment_id):
                raise HTTPException(status_code=400, detail="Invalid assignment ID format")

            assignment = assignment_collection.find_one({"_id": ObjectId(assignment_id)}, {"_id": 1})
            if assignment is None:
                raise HTTPException(status_code=404, detail="Assignment does not exist")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Internal Server Error: {e}")

def grade_assignment_middleware(request: Request):
    auth_header = request.headers.get("Authorization")

    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid Authorization header")

    token = auth_header.split("Bearer ")[1].strip()

    try:
        decoded_token = decode_token(token)
        sub_data = decoded_token.get("sub", {})
        user_id = sub_data.get("id")
        user_role = sub_data.get("role")

        if user_role != "Teacher":
            raise HTTPException(status_code=403, detail="Only Teacher can grade an assignment")

        return user_id
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)



def validate_submission_id(submission_id: str):
    try:
        if not ObjectId.is_valid(submission_id):
            raise HTTPException(status_code=400, detail="Invalid submission ID format")
        document = submissions_collection.find_one({"_id": ObjectId(submission_id)}, {"_id": 1})
        if document is None:
            raise HTTPException(status_code=404, detail="Submission does not exist")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {e}")


@router.get("/get-assignments")
def get_assignments():
    response = get_all_assignments()
    if "error" in response:
        return JSONResponse(content=response, status_code=500)
    return JSONResponse(content={"assignments": response}, status_code=200)

@router.post("/create-assignment", dependencies=[Depends(create_assignment_middleware)])
def create_assignment(assignment : CreateAssignment):
    assignment = assignment.model_dump()
    response = create_new_assignment(assignment)
    if "error" in response:
        return JSONResponse(content=response, status_code=400)

    return JSONResponse(content=response, status_code=201)

@router.post("/submit-assignment")
def submit_assignment(submitted_assignment: CreateSubmissions, student_id: str = Depends(submit_assignment_middleware)):
    try:
        submitted_assignment = submitted_assignment.model_dump()
        validate_assignment_id(submitted_assignment["assignment_id"])
        submitted_assignment["student_id"] = student_id
        if submitted_assignment["grade"] is None:
            submitted_assignment["grade"] = None
        response = submit_new_assignment(submitted_assignment)
        if "error" in response:
            return JSONResponse(content=response, status_code=400)
        return JSONResponse(content=response, status_code=201)
    except HTTPException as e:
        return JSONResponse(content=e.detail, status_code=e.status_code)
    except Exception as e:
        return JSONResponse(content=str(e), status_code=500)

@router.put("/grade-assignment")
def grade_assignment(graded_submission: GradeSubmissions, teacher_id: str = Depends(grade_assignment_middleware)):
    try:
        graded_submission = graded_submission.model_dump()
        validate_submission_id(graded_submission["submission_id"])
        graded_submission["teacher_id"] = teacher_id
        response = grade_submission(graded_submission)
        if "error" in response:
            return JSONResponse(content=response, status_code=400)
        return JSONResponse(content=response, status_code=200)
    except HTTPException as e:
        return JSONResponse(content=e.detail, status_code=e.status_code)
    except Exception as e:
        return JSONResponse(content=str(e), status_code=500)

@router.get("/get-submissions", dependencies=[Depends(grade_assignment_middleware)])
def get_submissions():
    try:
        response = get_all_submissions()
        return JSONResponse(content={"submissions": response}, status_code=200)
    except HTTPException as e:
        return JSONResponse(content=e.detail, status_code=e.status_code)
    except Exception as e:
        return JSONResponse(content=str(e), status_code=500)
