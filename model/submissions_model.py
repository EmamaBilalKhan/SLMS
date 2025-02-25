from pydantic import Field, BaseModel
from typing import Optional

class Submissions(BaseModel):
    assignment_id: str = Field(..., max_length=24),
    student_id: str = Field(...,max_length=24),
    grade: Optional[str] = None
    file_url: str

class CreateSubmissions(Submissions):
    pass

class UpdateSubmissions(BaseModel):
    grade : str = Field(..., min_length=1, max_length=4)
    submission_id: str = Field(..., max_length=24)

class GradeSubmissions(UpdateSubmissions):
    pass

