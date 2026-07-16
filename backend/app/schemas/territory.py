from pydantic import BaseModel
from datetime import datetime
from typing import Optional


# ── Territory ────────────────────────────────────────────────────────

class TerritoryBase(BaseModel):
    name: str
    code: Optional[str] = None
    territory_type: Optional[str] = "region"
    parent_id: Optional[int] = None
    description: Optional[str] = None
    is_active: Optional[bool] = True
    owner_id: Optional[int] = None


class TerritoryCreate(TerritoryBase):
    pass


class TerritoryUpdate(BaseModel):
    name: Optional[str] = None
    code: Optional[str] = None
    territory_type: Optional[str] = None
    parent_id: Optional[int] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None
    owner_id: Optional[int] = None


class TerritoryOut(TerritoryBase):
    id: int
    created_at: datetime
    updated_at: datetime
    children: list["TerritoryOut"] = []
    member_count: int = 0
    account_count: int = 0
    product_count: int = 0

    class Config:
        from_attributes = True


class TerritoryTreeNode(BaseModel):
    id: int
    name: str
    code: Optional[str] = None
    territory_type: str = "region"
    parent_id: Optional[int] = None
    children: list["TerritoryTreeNode"] = []


# ── Territory Member ─────────────────────────────────────────────────

class TerritoryMemberOut(BaseModel):
    id: int
    territory_id: int
    user_id: int
    role: str
    username: Optional[str] = None
    display_name: Optional[str] = None
    assigned_at: datetime

    class Config:
        from_attributes = True


class TerritoryMemberCreate(BaseModel):
    user_id: int
    role: str = "member"


# ── Territory Account ────────────────────────────────────────────────

class TerritoryAccountOut(BaseModel):
    id: int
    territory_id: int
    account_id: int
    account_name: Optional[str] = None
    assigned_at: datetime

    class Config:
        from_attributes = True


class TerritoryAccountCreate(BaseModel):
    account_id: int


# ── Territory Product ────────────────────────────────────────────────

class TerritoryProductOut(BaseModel):
    id: int
    territory_id: int
    product_id: int
    price: Optional[float] = None
    is_active: bool = True
    product_name: Optional[str] = None
    product_code: Optional[str] = None
    default_price: Optional[float] = None

    class Config:
        from_attributes = True


class TerritoryProductCreate(BaseModel):
    product_id: int
    price: Optional[float] = None


class TerritoryProductUpdate(BaseModel):
    price: Optional[float] = None
    is_active: Optional[bool] = None
