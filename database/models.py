from sqlalchemy import Column, DateTime, Integer, String
from database.connection import Base

class StudentDB(Base):
    __tablename__ = "students"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    branch = Column(String)
    age = Column(Integer)
    marks = Column(Integer)


class UserDB(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    password = Column(String)
    role = Column(String, default="student")


class PasswordResetOTPDB(Base):
    __tablename__ = "password_reset_otps"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    otp = Column(String)
    expires_at = Column(DateTime)
