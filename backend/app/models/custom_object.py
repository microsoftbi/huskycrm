from sqlalchemy import (
    Column, Integer, String, Text, Boolean, DateTime, ForeignKey, func
)
from sqlalchemy.orm import relationship
from app.database import Base
from app.utils.id_gen import generate_id


class CustomObjectDef(Base):
    """
    Defines a custom object type (like a Salesforce custom object).
    Each definition corresponds to a dynamically created SQLite table.
    """
    __tablename__ = "custom_object_defs"

    id = Column(String(36), primary_key=True, default=lambda: generate_id("cod_"))
    api_name = Column(String(120), unique=True, nullable=False, index=True)  # e.g. "custom_invoice"
    label = Column(String(255), nullable=False)                               # e.g. "发票"
    plural_label = Column(String(255))
    description = Column(Text)
    table_name = Column(String(120), unique=True, nullable=False)              # e.g. "obj_1"
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now(), server_default=func.now())
    updated_at = Column(DateTime, default=func.now(), server_default=func.now(), onupdate=func.now())

    fields = relationship("CustomFieldDef", back_populates="custom_object",
                          cascade="all, delete-orphan",
                          order_by="CustomFieldDef.display_order",
                          foreign_keys="CustomFieldDef.object_id")


class CustomFieldDef(Base):
    """
    Defines a field on a custom object.
    Each field becomes a column in the dynamic table.
    """
    __tablename__ = "custom_field_defs"

    id = Column(String(36), primary_key=True, default=lambda: generate_id("cfd_"))
    object_id = Column(String(36), ForeignKey("custom_object_defs.id"), nullable=False)
    api_name = Column(String(120), nullable=False)       # e.g. "amount"
    label = Column(String(255), nullable=False)           # e.g. "金额"
    field_type = Column(String(50), nullable=False)       # text, number, date, picklist, boolean, textarea, email, phone, url, lookup
    is_required = Column(Boolean, default=False)
    is_unique = Column(Boolean, default=False)
    default_value = Column(Text)
    max_length = Column(Integer)
    picklist_values = Column(Text)                       # JSON array for picklist options
    precision_total = Column(Integer)                    # for number type: total digits
    precision_scale = Column(Integer)                    # for number type: decimal places
    lookup_object_id = Column(String(36), ForeignKey("custom_object_defs.id"))
    display_order = Column(Integer, default=0)
    created_at = Column(DateTime, default=func.now(), server_default=func.now())
    updated_at = Column(DateTime, default=func.now(), server_default=func.now(), onupdate=func.now())

    custom_object = relationship("CustomObjectDef", back_populates="fields",
                                  foreign_keys=[object_id])
    lookup_object = relationship("CustomObjectDef", foreign_keys=[lookup_object_id])