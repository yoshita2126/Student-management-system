from fastapi import (
    APIRouter,
    HTTPException,
    Depends
)

from fastapi.security import OAuth2PasswordBearer

from sqlalchemy.orm import Session

from models.student_model import (
    Student,
    UpdateStudent,
    StudentResponse
)

from database.dependency import get_db
from database.models import StudentDB

from core.security import verify_token
from core.roles import authorize_role

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="login"
)

# GET ALL STUDENTS
@router.get(
    "/students",
    response_model=list[StudentResponse]
)
def get_students(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):

    user = verify_token(token)

    if user is None:

        raise HTTPException(
            status_code=401,
            detail="Invalid token"
        )

    authorize_role(
        user["role"],
        ["student", "teacher", "admin"]
    )

    students = db.query(StudentDB).all()

    return students


# GET SINGLE STUDENT
@router.get(
    "/students/{student_id}",
    response_model=StudentResponse
)
def get_student(
    student_id: int,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):

    user = verify_token(token)

    if user is None:

        raise HTTPException(
            status_code=401,
            detail="Invalid token"
        )

    authorize_role(
        user["role"],
        ["student", "teacher", "admin"]
    )

    student = db.query(StudentDB).filter(
        StudentDB.id == student_id
    ).first()

    if student is None:

        raise HTTPException(
            status_code=404,
            detail="Student not found"
        )

    return student


# CREATE STUDENT
@router.post(
    "/students/{student_id}",
    response_model=StudentResponse
)
def create_student(
    student_id: int,
    student: Student,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):

    user = verify_token(token)

    if user is None:

        raise HTTPException(
            status_code=401,
            detail="Invalid token"
        )

    authorize_role(
        user["role"],
        ["teacher", "admin"]
    )

    existing_student = db.query(StudentDB).filter(
        StudentDB.id == student_id
    ).first()

    if existing_student:

        raise HTTPException(
            status_code=400,
            detail="Student already exists"
        )

    new_student = StudentDB(
        id=student_id,
        name=student.name,
        branch=student.branch,
        age=student.age,
        marks=student.marks
    )

    db.add(new_student)

    db.commit()

    db.refresh(new_student)

    return new_student


# PUT METHOD
@router.put(
    "/students/{student_id}",
    response_model=StudentResponse
)
def update_student(
    student_id: int,
    student: Student,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):

    user = verify_token(token)

    if user is None:

        raise HTTPException(
            status_code=401,
            detail="Invalid token"
        )

    authorize_role(
        user["role"],
        ["teacher", "admin"]
    )

    existing_student = db.query(StudentDB).filter(
        StudentDB.id == student_id
    ).first()

    if existing_student is None:

        raise HTTPException(
            status_code=404,
            detail="Student not found"
        )

    existing_student.name = student.name
    existing_student.branch = student.branch
    existing_student.age = student.age
    existing_student.marks = student.marks

    db.commit()

    db.refresh(existing_student)

    return existing_student


# PATCH METHOD
@router.patch(
    "/students/{student_id}",
    response_model=StudentResponse
)
def patch_student(
    student_id: int,
    student: UpdateStudent,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):

    user = verify_token(token)

    if user is None:

        raise HTTPException(
            status_code=401,
            detail="Invalid token"
        )

    existing_student = db.query(StudentDB).filter(
        StudentDB.id == student_id
    ).first()

    if existing_student is None:

        raise HTTPException(
            status_code=404,
            detail="Student not found"
        )

    # ADMIN
    if user["role"] == "admin":

        if student.name is not None:
            existing_student.name = student.name

        if student.branch is not None:
            existing_student.branch = student.branch

        if student.age is not None:
            existing_student.age = student.age

        if student.marks is not None:
            existing_student.marks = student.marks

        db.commit()

        db.refresh(existing_student)

        return existing_student

    # TEACHER
    elif user["role"] == "teacher":

        if (
            student.name is not None or
            student.branch is not None or
            student.age is not None
        ):

            raise HTTPException(
                status_code=403,
                detail="Teacher can update only marks"
            )

        if student.marks is not None:

            existing_student.marks = student.marks

            db.commit()

            db.refresh(existing_student)

            return existing_student

        raise HTTPException(
            status_code=400,
            detail="No marks provided"
        )

    else:

        raise HTTPException(
            status_code=403,
            detail="Students cannot update"
        )


# DELETE METHOD
@router.delete("/students/{student_id}")
def delete_student(
    student_id: int,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):

    user = verify_token(token)

    if user is None:

        raise HTTPException(
            status_code=401,
            detail="Invalid token"
        )

    authorize_role(
        user["role"],
        ["admin"]
    )

    existing_student = db.query(StudentDB).filter(
        StudentDB.id == student_id
    ).first()

    if existing_student is None:

        raise HTTPException(
            status_code=404,
            detail="Student not found"
        )

    db.delete(existing_student)

    db.commit()

    return {
        "message": "Student deleted successfully"
    }
@router.get("/test")
def test():
    return {"message": "working"}
@router.get("/dbtest")
def dbtest(
    db: Session = Depends(get_db)
):

    students = db.query(StudentDB).all()

    return students