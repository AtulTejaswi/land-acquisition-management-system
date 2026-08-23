from pydantic import BaseModel
from typing import Optional
import uuid


class LoginRequest(BaseModel):
    email: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: "UserResponse"


class RefreshRequest(BaseModel):
    refresh_token: str


class ForgotPasswordRequest(BaseModel):
    email: str


class ForgotPasswordResponse(BaseModel):
    message: str
    otp: Optional[str] = None  # In demo mode, show OTP


class UserResponse(BaseModel):
    id: uuid.UUID
    full_name: str
    email: str
    phone: str
    role_name: str
    state_id: Optional[uuid.UUID] = None
    state_name: Optional[str] = None
    district_id: Optional[uuid.UUID] = None
    district_name: Optional[str] = None
    agency_name: Optional[str] = None
    is_active: bool

    class Config:
        from_attributes = True


class UserCreate(BaseModel):
    full_name: str
    email: str
    phone: str
    password: str
    role_id: uuid.UUID
    state_id: Optional[uuid.UUID] = None
    district_id: Optional[uuid.UUID] = None
    agency_name: Optional[str] = None


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    role_id: Optional[uuid.UUID] = None
    state_id: Optional[uuid.UUID] = None
    district_id: Optional[uuid.UUID] = None
    agency_name: Optional[str] = None
    is_active: Optional[bool] = None


# Avoid circular import
TokenResponse.model_rebuild()
