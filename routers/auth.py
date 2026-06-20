from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, Form, HTTPException, Request, status
from fastapi.responses import RedirectResponse
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.templating import Jinja2Templates
from sqlalchemy import or_
from sqlalchemy.orm import Session

from core.security import (
    DEFAULT_USERS,
    create_access_token,
    generate_otp,
    hash_password,
    send_otp_email,
    verify_password,
)
from database.dependency import get_db
from database.models import PasswordResetOTPDB, UserDB

router = APIRouter()
templates = Jinja2Templates(directory="templates")


def seed_default_users(db: Session):
    for user in DEFAULT_USERS.values():
        existing_user = db.query(UserDB).filter(UserDB.username == user["username"]).first()

        if existing_user:
            continue

        db.add(
            UserDB(
                username=user["username"],
                email=user["email"],
                password=hash_password(user["password"]),
                role=user["role"],
            )
        )

    db.commit()


def get_user_by_username_or_email(db: Session, username_or_email: str):
    return (
        db.query(UserDB)
        .filter(
            or_(
                UserDB.username == username_or_email,
                UserDB.email == username_or_email,
            )
        )
        .first()
    )


@router.post("/login")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    user = get_user_by_username_or_email(db, form_data.username)

    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username/email or password",
        )

    access_token = create_access_token(
        data={
            "sub": user.username,
            "role": user.role,
        }
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
    }


@router.get("/signup")
def signup_get(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="signup.html",
        context={"request": request},
    )


@router.post("/signup")
def signup_post(
    request: Request,
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    role: str = Form("student"),
    db: Session = Depends(get_db),
):
    username = username.strip()
    email = email.strip().lower()
    role = role if role in {"student", "teacher", "admin"} else "student"

    existing_user = (
        db.query(UserDB)
        .filter(
            or_(
                UserDB.username == username,
                UserDB.email == email,
            )
        )
        .first()
    )

    if existing_user:
        field = "Username" if existing_user.username == username else "Email"
        return templates.TemplateResponse(
            request=request,
            name="signup.html",
            context={
                "request": request,
                "error": f"{field} already registered",
            },
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    db.add(
        UserDB(
            username=username,
            email=email,
            password=hash_password(password),
            role=role,
        )
    )
    db.commit()

    return RedirectResponse(
        url="/",
        status_code=status.HTTP_303_SEE_OTHER,
    )


@router.get("/forgot-password")
def forgot_password_get(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="forgot_password.html",
        context={"request": request},
    )


@router.post("/forgot-password")
def forgot_password_post(
    request: Request,
    email: str = Form(...),
    db: Session = Depends(get_db),
):
    email = email.strip().lower()
    user = db.query(UserDB).filter(UserDB.email == email).first()

    if not user:
        return templates.TemplateResponse(
            request=request,
            name="forgot_password.html",
            context={
                "request": request,
                "error": "Email is not registered",
            },
            status_code=status.HTTP_404_NOT_FOUND,
        )

    otp = generate_otp()
    sent = send_otp_email(
        email=user.email,
        username=user.username,
        otp=otp,
    )

    if not sent:
        return templates.TemplateResponse(
            request=request,
            name="forgot_password.html",
            context={
                "request": request,
                "error": "OTP email failed. Check SMTP settings in .env.",
            },
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    db.query(PasswordResetOTPDB).filter(PasswordResetOTPDB.user_id == user.id).delete()
    db.add(
        PasswordResetOTPDB(
            user_id=user.id,
            otp=otp,
            expires_at=datetime.utcnow() + timedelta(minutes=10),
        )
    )
    db.commit()

    return templates.TemplateResponse(
        request=request,
        name="reset_password.html",
        context={
            "request": request,
            "email": user.email,
            "message": "OTP sent successfully",
        },
    )


@router.get("/reset-password")
def reset_password_get(
    request: Request,
    email: str = "",
):
    return templates.TemplateResponse(
        request=request,
        name="reset_password.html",
        context={
            "request": request,
            "email": email,
        },
    )


@router.post("/forgot-password")
def forgot_password_post(
    request: Request,
    email: str = Form(...),
    db: Session = Depends(get_db),
):
    try:
        email = email.strip().lower()

        user = db.query(UserDB).filter(UserDB.email == email).first()

        if not user:
            return templates.TemplateResponse(
                request=request,
                name="forgot_password.html",
                context={
                    "request": request,
                    "error": "Email is not registered",
                },
                status_code=404,
            )

        otp = generate_otp()

        # save OTP
        db.query(PasswordResetOTPDB).filter(
            PasswordResetOTPDB.user_id == user.id
        ).delete()

        db.add(
            PasswordResetOTPDB(
                user_id=user.id,
                otp=otp,
                expires_at=datetime.utcnow() + timedelta(minutes=10),
            )
        )

        db.commit()

        # send email
        sent = send_otp_email(
            email=user.email,
            username=user.username,
            otp=otp,
        )

        if not sent:
            return templates.TemplateResponse(
                request=request,
                name="forgot_password.html",
                context={
                    "request": request,
                    "error": "Failed to send OTP email",
                },
            )

        # open reset password page
        return templates.TemplateResponse(
            request=request,
            name="reset_password.html",
            context={
                "request": request,
                "email": user.email,
                "message": "OTP sent successfully",
            },
        )

    except Exception as e:
        return templates.TemplateResponse(
            request=request,
            name="forgot_password.html",
            context={
                "request": request,
                "error": f"Server Error: {str(e)}",
            },
        )


@router.post("/reset-password")
def reset_password_post(
    request: Request,
    email: str = Form(...),
    otp: str = Form(...),
    new_password: str = Form(...),
    confirm_password: str = Form(...),
    db: Session = Depends(get_db),
):
    try:
        email = email.strip().lower()
        otp = otp.strip()

        # Validate passwords match
        if new_password != confirm_password:
            return templates.TemplateResponse(
                request=request,
                name="reset_password.html",
                context={
                    "request": request,
                    "email": email,
                    "error": "Passwords do not match",
                },
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        # Validate password strength (minimum 6 characters)
        if len(new_password) < 6:
            return templates.TemplateResponse(
                request=request,
                name="reset_password.html",
                context={
                    "request": request,
                    "email": email,
                    "error": "Password must be at least 6 characters",
                },
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        # Find user by email
        user = db.query(UserDB).filter(UserDB.email == email).first()
        if not user:
            return templates.TemplateResponse(
                request=request,
                name="reset_password.html",
                context={
                    "request": request,
                    "email": email,
                    "error": "User not found",
                },
                status_code=status.HTTP_404_NOT_FOUND,
            )

        # Check OTP exists and is valid
        otp_record = (
            db.query(PasswordResetOTPDB)
            .filter(PasswordResetOTPDB.user_id == user.id)
            .first()
        )

        if not otp_record:
            return templates.TemplateResponse(
                request=request,
                name="reset_password.html",
                context={
                    "request": request,
                    "email": email,
                    "error": "OTP not found. Please request a new OTP",
                },
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        # Check OTP expiration
        if datetime.utcnow() > otp_record.expires_at:
            db.delete(otp_record)
            db.commit()
            return templates.TemplateResponse(
                request=request,
                name="reset_password.html",
                context={
                    "request": request,
                    "email": email,
                    "error": "OTP has expired. Please request a new one",
                },
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        # Verify OTP
        if otp_record.otp != otp:
            return templates.TemplateResponse(
                request=request,
                name="reset_password.html",
                context={
                    "request": request,
                    "email": email,
                    "error": "Invalid OTP",
                },
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        # Update password
        user.password = hash_password(new_password)

        # Delete used OTP
        db.delete(otp_record)
        db.commit()

        return templates.TemplateResponse(
            request=request,
            name="password_reset_success.html",
            context={
                "request": request,
                "email": email,
                "message": "Password reset successfully",
            },
        )

    except Exception as e:
        return templates.TemplateResponse(
            request=request,
            name="reset_password.html",
            context={
                "request": request,
                "email": email,
                "error": f"Server Error: {str(e)}",
            },
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )