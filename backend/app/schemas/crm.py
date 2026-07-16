from pydantic import BaseModel
from datetime import datetime, date
from typing import Optional, Any


class AccountBase(BaseModel):
    name: str
    industry: Optional[str] = None
    phone: Optional[str] = None
    website: Optional[str] = None
    email: Optional[str] = None
    billing_street: Optional[str] = None
    billing_city: Optional[str] = None
    billing_state: Optional[str] = None
    billing_zip: Optional[str] = None
    billing_country: Optional[str] = None
    description: Optional[str] = None
    owner_id: Optional[int] = None


class AccountCreate(AccountBase):
    pass


class AccountUpdate(AccountBase):
    name: Optional[str] = None


class AccountOut(AccountBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ContactBase(BaseModel):
    first_name: str
    last_name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    mobile_phone: Optional[str] = None
    title: Optional[str] = None
    department: Optional[str] = None
    account_id: Optional[int] = None
    owner_id: Optional[int] = None


class ContactCreate(ContactBase):
    pass


class ContactUpdate(ContactBase):
    first_name: Optional[str] = None
    last_name: Optional[str] = None


class ContactOut(ContactBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class StageOut(BaseModel):
    id: int
    name: str
    probability: int
    sort_order: int
    is_closed_won: bool
    is_closed_lost: bool

    class Config:
        from_attributes = True


class OpportunityBase(BaseModel):
    name: str
    account_id: Optional[int] = None
    stage_id: int
    amount: Optional[float] = 0.0
    probability: Optional[int] = 0
    close_date: Optional[date] = None
    description: Optional[str] = None
    owner_id: Optional[int] = None


class OpportunityCreate(OpportunityBase):
    pass


class OpportunityUpdate(BaseModel):
    name: Optional[str] = None
    account_id: Optional[int] = None
    stage_id: Optional[int] = None
    amount: Optional[float] = None
    probability: Optional[int] = None
    close_date: Optional[date] = None
    description: Optional[str] = None
    owner_id: Optional[int] = None


class OpportunityProductBase(BaseModel):
    product_id: int
    quantity: int = 1
    unit_price: float = 0.0
    total_price: float = 0.0


class OpportunityProductCreate(OpportunityProductBase):
    pass


class OpportunityProductOut(OpportunityProductBase):
    id: int
    opportunity_id: int
    created_at: datetime

    class Config:
        from_attributes = True


class OpportunityOut(OpportunityBase):
    id: int
    created_at: datetime
    updated_at: datetime
    line_items: list[OpportunityProductOut] = []

    class Config:
        from_attributes = True


class PipelineStageData(BaseModel):
    stage: StageOut
    opportunities: list[OpportunityOut]
    total_amount: float
    count: int


class PipelineOut(BaseModel):
    stages: list[PipelineStageData]


class ProductBase(BaseModel):
    name: str
    product_code: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = 0.0
    cost: Optional[float] = 0.0
    category: Optional[str] = None
    is_active: Optional[bool] = True
    owner_id: Optional[int] = None


class ProductCreate(ProductBase):
    pass


class ProductUpdate(ProductBase):
    name: Optional[str] = None


class ProductOut(ProductBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PaginatedResponse(BaseModel):
    total: int
    page: int
    page_size: int
    items: list[Any]
