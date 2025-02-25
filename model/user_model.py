from pydantic import BaseModel, Field, EmailStr
from enum import Enum

class UserRole(str, Enum):
    Teacher = "Teacher",
    Student = "Student"
    Admin = "Admin"

class User(BaseModel):
    username: str = Field(..., min_length=8, max_length=15)
    email : EmailStr
    password: str = Field(..., min_length=8, max_length=15, description="Password must be at least 8 characters long, and must contain 1 Uppercase character, 1 lowercase character, 1 number and 1 special character")
    role: UserRole
    is_verified: bool = False

class CreateUser(User):
    pass

class LoginUser(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=15)

