# Forgot Password with OTP Email Feature

## Overview
This application now includes a complete forgot password flow with OTP (One-Time Password) sent to the user's registered email address.

## Features
- **Forgot Password Page** (`/forgot-password`) - Users can request password reset
- **OTP Verification** - One-time password sent to registered email
- **Password Reset** - Users can reset their password with valid OTP
- **OTP Expiration** - OTP is valid for 10 minutes only
- **Email Notifications** - Beautiful HTML emails with OTP sent to users

## Setup Instructions

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Email Settings
Copy the `.env.example` file to `.env`:
```bash
cp .env.example .env
```

Edit `.env` and add your email configuration:
```
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SENDER_EMAIL=your_email@gmail.com
SENDER_PASSWORD=your_app_password
```

### 3. Gmail Configuration (if using Gmail)
1. Enable 2-Factor Authentication on your Gmail account
2. Generate an App Password: https://myaccount.google.com/apppasswords
3. Select "Mail" and "Windows Computer" (or your device)
4. Google will generate a 16-character password
5. Use this password in the `.env` file as `SENDER_PASSWORD`

### 4. Update Signup Form
The signup form now requires:
- Username
- Email Address (for password recovery)
- Password
- Account Type (Student/Teacher/Admin)

## How It Works

### User Flow
1. User clicks **"Forgot Password?"** on the home page
2. User enters their registered email address
3. System generates a 6-digit OTP and sends it via email
4. User receives email with OTP (valid for 10 minutes)
5. User navigates to reset page and enters:
   - OTP from email
   - New password
   - Confirm password
6. System verifies OTP and updates password
7. User sees success message and can login with new password

### OTP Details
- **Length**: 6 digits
- **Validity**: 10 minutes from generation
- **Storage**: In-memory (temporary) - will reset on app restart
- **Security**: Used once, automatically cleared after verification

## Routes

### Authentication Routes
- `GET /` - Home page
- `GET /signup` - Signup form
- `POST /signup` - Create new account
- `POST /login` - Login (OAuth2 PasswordRequestForm)
- `GET /forgot-password` - Forgot password page
- `POST /forgot-password` - Send OTP to email
- `GET /reset-password` - Reset password page with OTP verification
- `POST /reset-password` - Verify OTP and reset password

## File Structure
```
d:\crt\
├── main.py                          # Main FastAPI application
├── core/
│   └── security.py                  # Security, OTP, and email functions
├── routers/
│   └── auth.py                      # Authentication routes (signup, login, forgot password)
├── database/
│   ├── connection.py                # Database connection
│   └── models.py                    # Database models (includes new UserDB model)
├── templates/
│   ├── index.html                   # Home page
│   ├── signup.html                  # Signup form (updated with email field)
│   ├── forgot_password.html         # Forgot password page
│   ├── reset_password.html          # Reset password page with OTP verification
│   └── password_reset_success.html  # Success confirmation page
├── .env.example                     # Environment variables template
├── requirements.txt                 # Python dependencies
└── README.md                        # This file
```

## Database Model Updates

### UserDB Model
```python
class UserDB(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    password = Column(String)
    role = Column(String, default="student")
```

## Security Features
✓ Email validation
✓ OTP expiration (10 minutes)
✓ One-time use OTP
✓ Password strength indicators
✓ Confirmation password matching
✓ Email doesn't reveal if account exists (for security)
✓ Session-based OTP storage

## Error Handling
- Invalid email format
- Email not found (generic message for security)
- Expired OTP
- Invalid OTP
- Password mismatch
- Email sending failures

## Testing the Feature

### Test Users
Default users with email:
- **Admin**: admin@example.com / password: admin123
- **Teacher**: teacher@example.com / password: teacher123
- **Student**: student@example.com / password: student123

### Manual Testing
1. Add `.env` file with Gmail configuration
2. Start the application: `python -m uvicorn main:app --reload`
3. Go to `http://localhost:8000`
4. Click "Forgot Password?"
5. Enter a test user email
6. Check the email for OTP
7. Enter OTP and new password
8. Verify successful reset

## Notes
- OTP storage is in-memory and will be cleared when the application restarts
- For production, consider using a database for OTP storage with additional logging
- Email credentials should never be committed to version control
- The `.env` file is environment-specific and should be created locally
- For production, consider using a third-party email service like SendGrid, Mailgun, etc.

## Troubleshooting

### "Failed to send OTP"
- Check if `.env` file exists with valid credentials
- Verify SMTP settings are correct
- Check internet connection
- For Gmail: ensure "Less secure app access" is enabled or use App Password

### "User not found"
- Verify the email is registered
- Check email spelling
- Note: The system doesn't reveal if an email exists for security

### OTP Expired
- OTP is valid for 10 minutes
- Click "Request New OTP" to get a new one
- Note: Each new OTP invalidates the previous one

## Future Enhancements
- Store OTP in database with expiration timestamps
- Add email verification during signup
- Implement rate limiting for OTP requests
- Add phone number verification as alternative
- Implement 2-factor authentication
- Add OTP retry limits
- Add email change functionality
