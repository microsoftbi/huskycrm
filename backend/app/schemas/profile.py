from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class ProfileCreate(BaseModel):
    name: str
    profile_type: str = "standard"
    description: str | None = None


class ProfileUpdate(BaseModel):
    name: str | None = None
    profile_type: str | None = None
    description: str | None = None


class ProfileUserBrief(BaseModel):
    """轻量级用户信息 — 用于 Profile 详情中展示所属用户"""
    id: str
    username: str
    display_name: str | None = None
    email: str
    is_active: bool

    class Config:
        from_attributes = True


class ProfileOut(BaseModel):
    id: str
    name: str
    profile_type: str
    description: str | None = None
    is_system: bool
    user_count: int = 0
    users: list[ProfileUserBrief] = []
    created_at: datetime | None = None
    updated_at: datetime | None = None

    class Config:
        from_attributes = True


class ProfileBrief(BaseModel):
    """轻量级 — 用于下拉选择"""
    id: str
    name: str
    profile_type: str
    is_system: bool

    class Config:
        from_attributes = True