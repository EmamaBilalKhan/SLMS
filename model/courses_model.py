from pydantic import BaseModel, Field

class Course(BaseModel):
    course_name: str = Field(..., min_length=5, max_length=15),
    description: str = Field(..., min_length=5, max_length=30),

class CreateCourse(Course):
    pass

class RegisterCourseRequest(BaseModel):
    course_id: str