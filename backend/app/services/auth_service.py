from uuid import UUID
from typing import Optional
import random
from datetime import datetime, timezone, timedelta
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.user import User
from app.models.otp import OTPVerification
from app.schemas.auth import RegistrationRequest, LoginRequest, ResetPasswordRequest
from app.core.security import hash_password, verify_password
from app.services.mail_service import send_otp_email

def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """Retrieve a user by their email address."""
    return db.query(User).filter(User.email == email.lower()).first()

def get_user_by_id(db: Session, user_id: UUID) -> Optional[User]:
    """Retrieve a user by their UUID."""
    return db.query(User).filter(User.id == user_id).first()

def register_user(db: Session, request: RegistrationRequest) -> User:
    """Validate uniqueness, hash password, create, and save a user."""
    existing_user = get_user_by_email(db, request.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email is already registered."
        )
    
    hashed_pwd = hash_password(request.password)
    db_user = User(
        name=request.name,
        email=request.email.lower(),
        password_hash=hashed_pwd
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def authenticate_user(db: Session, request: LoginRequest) -> User:
    """Verify credentials and return the authenticated user, or raise 401."""
    user = get_user_by_email(db, request.email)
    if not user or not verify_password(request.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user

def generate_otp(db: Session, email: str) -> str:
    """Generates a random 6-digit OTP, stores it in database, and sends it via email."""
    email_clean = email.lower().strip()
    
    # Check if user exists first
    user = get_user_by_email(db, email_clean)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No user registered with this email address."
        )

    # Generate 6-digit string OTP
    otp = f"{random.randint(100000, 999999)}"
    
    # Expiration set to 10 minutes from now (timezone-aware UTC)
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=10)
    
    otp_record = OTPVerification(
        email=email_clean,
        otp=otp,
        expires_at=expires_at,
        verified=False
    )
    db.add(otp_record)
    db.commit()
    
    # Send mail
    send_otp_email(email_clean, otp)
    return otp

def verify_and_reset_password(db: Session, request: ResetPasswordRequest) -> bool:
    """Verifies matching, unexpired, and unverified OTP, and updates user password."""
    email_clean = request.email.lower().strip()
    
    # Fetch the user
    user = get_user_by_email(db, email_clean)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No user registered with this email address."
        )

    # Fetch latest unverified, unexpired OTP for this email
    now = datetime.now(timezone.utc)
    otp_record = db.query(OTPVerification).filter(
        OTPVerification.email == email_clean,
        OTPVerification.otp == request.otp,
        OTPVerification.verified == False,
        OTPVerification.expires_at > now
    ).order_by(OTPVerification.created_at.desc()).first()
    
    if not otp_record:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired OTP."
        )
        
    # Mark OTP as verified
    otp_record.verified = True
    
    # Hash new password and update user record
    hashed_pwd = hash_password(request.new_password)
    user.password_hash = hashed_pwd
    
    db.commit()
    return True
