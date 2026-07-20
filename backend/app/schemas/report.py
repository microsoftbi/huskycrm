from pydantic import BaseModel, field_validator
from datetime import datetime
from typing import Optional, Any
import json


class ReportBase(BaseModel):
    name: str
    object_type: str
    report_type: str = "tabular"
    filters: Optional[list[dict]] = None
    grouping: Optional[list[str]] = None
    aggregations: Optional[list[dict]] = None
    columns: Optional[list[str]] = None


class ReportCreate(ReportBase):
    pass


class ReportUpdate(BaseModel):
    name: Optional[str] = None
    filters: Optional[list[dict]] = None
    grouping: Optional[list[str]] = None
    aggregations: Optional[list[dict]] = None
    columns: Optional[list[str]] = None


class ReportOut(ReportBase):
    id: str
    owner_id: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    @field_validator("filters", "grouping", "aggregations", "columns", mode="before")
    @classmethod
    def parse_json_fields(cls, v):
        if isinstance(v, str):
            try:
                return json.loads(v)
            except (json.JSONDecodeError, TypeError):
                return None
        return v

    class Config:
        from_attributes = True


class ReportResult(BaseModel):
    columns: list[str]
    rows: list[list[Any]]
    total: int


class DashboardComponentBase(BaseModel):
    report_id: Optional[str] = None
    title: str
    chart_type: str = "table"
    position_x: int = 0
    position_y: int = 0
    width: int = 4
    height: int = 3


class DashboardComponentOut(DashboardComponentBase):
    id: str
    dashboard_id: str

    class Config:
        from_attributes = True


class DashboardBase(BaseModel):
    name: str


class DashboardCreate(DashboardBase):
    pass


class DashboardOut(DashboardBase):
    id: str
    owner_id: Optional[str] = None
    components: list[DashboardComponentOut] = []
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True