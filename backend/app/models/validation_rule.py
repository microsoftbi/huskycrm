from sqlalchemy import Column, String, Text, Boolean, DateTime, func
from app.database import Base
from app.utils.id_gen import generate_id


class ValidationRule(Base):
    """Validation rule — conditions evaluated before record save, blocks save on match."""
    __tablename__ = "validation_rules"

    id = Column(String(36), primary_key=True, default=lambda: generate_id("val_"))
    name = Column(String(255), nullable=False)
    object_type = Column(String(100), nullable=False, index=True, comment="Target object type: account/contact/opportunity")
    is_active = Column(Boolean, default=True, index=True)
    condition_expression = Column(Text, nullable=False, comment="JSON array of conditions (same format as workflow conditions)")
    error_message = Column(String(500), nullable=False, comment="Error message shown when validation fails")
    created_at = Column(DateTime, default=func.now(), server_default=func.now())
    updated_at = Column(DateTime, default=func.now(), server_default=func.now(), onupdate=func.now())