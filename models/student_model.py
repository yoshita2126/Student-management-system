from pydantic import BaseModel
from typing import Optional

class Student(BaseModel):

    name: str
    branch: str
    age: int
    marks: int


class UpdateStudent(BaseModel):

    name: Optional[str] = None
    branch: Optional[str] = None
    age: Optional[int] = None
    marks: Optional[int] = None


class StudentResponse(BaseModel):

    id: int
    name: str
    branch: str
    age: int
    marks: int

    class Config:
        from_attributes = True