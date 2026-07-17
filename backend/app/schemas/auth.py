from pydantic import BaseModel, EmailStr
from datetime import datetime


class UserRegister(BaseModel):
    username: str
    email: str
    password: str
    display_name: str | None = None


class UserLogin(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshRequest(BaseModel):
    refresh_token: str


class UserOut(BaseModel):
    id: str
    username: str
    email: str
    display_name: str | None = None
    is_active: bool
    is_superuser: bool
    created_at: datetime | None = None
    updated_at: datetime | None = None

    class Config:
        from_attributes = True


class ProfileUpdate(BaseModel):
    display_name: str | None = None
    email: str | None = None


class PasswordChange(BaseModel):
    current_password: str
    new_password: str
    confirm_password: str


class UserTerritoryOut(BaseModel):
    territory_id: str
    territory_name: str
    territory_code: str | None = None
    territory_type: str
    role: str
    manager_name: str | None = None
    manager_username: str | None = None
