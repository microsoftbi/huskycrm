from sqlalchemy import Column, String, Boolean, DateTime, func
from app.database import Base
from app.utils.id_gen import generate_id


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(String(36), primary_key=True, default=lambda: generate_id("not_"))
    user_id = Column(String(36), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    message = Column(String, nullable=True)
    notification_type = Column(String(50), nullable=False)  # "workflow" | "system"
    reference_type = Column(String(80), nullable=True)
    reference_id = Column(String(36), nullable=True)
    is_read = Column(Boolean, default=False, index=True)
    created_at = Column(DateTime, default=func.now(), server_default=func.now())