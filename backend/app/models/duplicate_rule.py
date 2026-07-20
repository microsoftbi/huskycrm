from sqlalchemy import Column, String, Text, Boolean, DateTime, func
from app.database import Base
from app.utils.id_gen import generate_id


class DuplicateRule(Base):
    """Duplicate detection rule — defines matching fields for duplicate checking."""
    __tablename__ = "duplicate_rules"

    id = Column(String(36), primary_key=True, default=lambda: generate_id("dup_"))
    name = Column(String(255), nullable=False)
    object_type = Column(String(100), nullable=False, index=True, comment="Target object type: account/contact")
    is_active = Column(Boolean, default=True, index=True)
    matching_fields = Column(Text, nullable=False, comment="JSON array of field names to match, e.g. [\"name\", \"email\"]")
    created_at = Column(DateTime, default=func.now(), server_default=func.now())
    updated_at = Column(DateTime, default=func.now(), server_default=func.now(), onupdate=func.now())