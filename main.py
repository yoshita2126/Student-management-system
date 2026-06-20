from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

from routers import auth
from routers import students

from database.connection import engine, sessionLocal
from database.models import Base

app = FastAPI()

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create Database Tables
Base.metadata.create_all(bind=engine)

with sessionLocal() as db:
    auth.seed_default_users(db)

# Templates Folder
templates = Jinja2Templates(directory="templates")


# HOME ROUTE - REDIRECT TO LOGIN
@app.get("/")
def home(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="login.html"
    )


# LOGIN PAGE ROUTE
@app.get("/login")
def login_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="login.html"
    )


# SIGNUP PAGE ROUTE
@app.get("/signup")
def signup_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="signup.html"
    )


# FORGOT PASSWORD PAGE ROUTE
@app.get("/forgot-password")
def forgot_password_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="forgot_password.html"
    )


# RESET PASSWORD PAGE ROUTE
@app.get("/reset-password")
def reset_password_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="reset_password.html"
    )


# DASHBOARD ROUTE
@app.get("/dashboard")
def dashboard(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="dashboard.html"
    )


# INCLUDE ROUTERS
app.include_router(auth.router)
app.include_router(students.router)
