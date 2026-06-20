from datetime import datetime, timedelta
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import hashlib
import hmac
import os
import random
import smtplib
import string

from dotenv import load_dotenv
from jose import JWTError, jwt

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY", "change-this-secret-key")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

DEFAULT_USERS = {
    "admin": {
        "username": "admin",
        "email": "admin@example.com",
        "password": "admin123",
        "role": "admin",
    },
    "teacher": {
        "username": "teacher",
        "email": "teacher@example.com",
        "password": "teacher123",
        "role": "teacher",
    },
    "student": {
        "username": "student",
        "email": "student@example.com",
        "password": "student123",
        "role": "student",
    },
}

SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
SENDER_EMAIL = os.getenv("SENDER_EMAIL", "your_email@gmail.com")
SENDER_PASSWORD = os.getenv("SENDER_PASSWORD", "your_app_password")


def hash_password(password: str) -> str:
    salt = os.urandom(16)
    digest = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt,
        100_000,
    )
    return f"pbkdf2_sha256$100000${salt.hex()}${digest.hex()}"


def verify_password(plain_password: str, stored_password: str) -> bool:
    if not stored_password:
        return False

    # Existing demo accounts may already be stored as plain text.
    if not stored_password.startswith("pbkdf2_sha256$"):
        return hmac.compare_digest(plain_password, stored_password)

    try:
        _, iterations, salt_hex, digest_hex = stored_password.split("$", 3)
        digest = hashlib.pbkdf2_hmac(
            "sha256",
            plain_password.encode("utf-8"),
            bytes.fromhex(salt_hex),
            int(iterations),
        )
    except ValueError:
        return False

    return hmac.compare_digest(digest.hex(), digest_hex)


def generate_otp(length: int = 6) -> str:
    return "".join(random.choices(string.digits, k=length))


def send_otp_email(email: str, username: str, otp: str) -> bool:
    try:
        message = MIMEMultipart()
        message["From"] = SENDER_EMAIL
        message["To"] = email
        message["Subject"] = "Password Reset OTP"

        body = f"""
        <html>
            <body style="font-family: Arial, sans-serif;">
                <h2>Password Reset Request</h2>
                <p>Hello {username},</p>
                <p>You requested to reset your password. Use the OTP below:</p>
                <h1 style="color:#2196F3; letter-spacing:3px;">{otp}</h1>
                <p>This OTP is valid for 10 minutes.</p>
                <p>If you did not request this, please ignore this email.</p>
                <br>
                <p>Best Regards,<br>CRT Team</p>
            </body>
        </html>
        """

        message.attach(MIMEText(body, "html"))

        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.send_message(message)

        return True

    except Exception as exc:
        print("EMAIL ERROR:", exc)
        return False


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})

    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        role = payload.get("role")

        if username is None or role is None:
            return None

        return {
            "username": username,
            "role": role,
        }

    except JWTError:
        return None


if __name__ == "__main__":
    print("Generated OTP:", generate_otp())
