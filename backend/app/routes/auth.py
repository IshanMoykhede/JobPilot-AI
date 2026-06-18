from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.auth import RegistrationRequest, LoginRequest, AuthResponse, CurrentUserResponse
from app.services import auth_service
from app.core.security import create_access_token
from app.dependencies.auth import get_current_user
from app.models.user import User

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", status_code=status.HTTP_201_CREATED, response_model=CurrentUserResponse)
def register(request: RegistrationRequest, db: Session = Depends(get_db)):
    """Register a new user, verifying email uniqueness and hashing the password."""
    user = auth_service.register_user(db, request)
    return user

@router.post("/login", response_model=AuthResponse)
def login(request: LoginRequest, db: Session = Depends(get_db)):
    """Authenticate credentials and return a Bearer access token."""
    user = auth_service.authenticate_user(db, request)
    access_token = create_access_token(data={"sub": str(user.id)})
    return AuthResponse(access_token=access_token, token_type="bearer")

@router.get("/me", response_model=CurrentUserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    """Retrieve details of the currently authenticated user using their JWT."""
    return current_user
