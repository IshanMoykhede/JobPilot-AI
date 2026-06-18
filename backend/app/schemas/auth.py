from uuid import UUID
from pydantic import BaseModel, Field

class RegistrationRequest(BaseModel):
    name: str
    email: str = Field(..., pattern=r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")
    password: str

class LoginRequest(BaseModel):
    email: str = Field(..., pattern=r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")
    password: str

class AuthResponse(BaseModel):
    access_token: str
    token_type: str

class CurrentUserResponse(BaseModel):
    id: UUID
    name: str
    email: str

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "name": "Jane Doe",
                "email": "jane.doe@example.com"
            }
        }
