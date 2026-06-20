import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import random
import os
from dotenv import load_dotenv
load_dotenv()

SMTP_SERVER = os.getenv("SMTP_SERVER")
SMTP_PORT = int(os.getenv("SMTP_PORT"))
SENDER_EMAIL = os.getenv("SENDER_EMAIL")
SENDER_PASSWORD = os.getenv("SENDER_PASSWORD")


def generate_otp():
    return str(random.randint(100000, 999999))


def send_otp_email(receiver_email):
    otp = generate_otp()

    subject = "Your OTP Verification Code"

    body = f"""
Hello,

Your OTP verification code is: {otp}

This OTP is valid for 5 minutes.

Do not share this OTP with anyone.
"""

    msg = MIMEMultipart()
    msg["From"] = SENDER_EMAIL
    msg["To"] = receiver_email
    msg["Subject"] = subject

    msg.attach(MIMEText(body, "plain"))

    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)

        server.sendmail(
            SENDER_EMAIL,
            receiver_email,
            msg.as_string()
        )

        server.quit()

        return otp

    except Exception as e:
        print("Email Error:", e)
        return None