from sqlalchemy import Column, String, DateTime, func
from app.database import Base
from app.utils.id_gen import generate_id


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(String(36), primary_key=True, default=lambda: generate_id("aud_"))
    object_type = Column(String(80), nullable=False, index=True)
    object_id = Column(String(36), nullable=False, index=True)
    field_name = Column(String(80), nullable=True)
    old_value = Column(String, nullable=True)
    new_value = Column(String, nullable=True)
    action = Column(String(20), nullable=False)  # "create" | "update" | "delete"
    user_id = Column(String(36), nullable=False, index=True)
    created_at = Column(DateTime, default=func.now())