from pydantic import BaseModel, Field

class Assignment(BaseModel):
    title : str = Field(...,min_length=5,max_length=10)
    description : str = Field(...,min_length=8,max_length=30)
    course_id : str = Field(..., max_length=24)
    due_date : str

class CreateAssignment(Assignment):
    pass