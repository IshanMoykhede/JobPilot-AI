from uuid import UUID
from typing import Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.user import User
from app.schemas.auth import RegistrationRequest, LoginRequest
from app.core.security import hash_password, verify_password

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
