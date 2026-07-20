from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from app.database import Base
from app.utils.id_gen import generate_id


class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=lambda: generate_id("user_"))
    username = Column(String(80), unique=True, nullable=False, index=True)
    email = Column(String(120), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    display_name = Column(String(120))
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    profile_id = Column(String(36), ForeignKey("profiles.id"), nullable=True, index=True)
    created_at = Column(DateTime, default=func.now(), server_default=func.now())
    updated_at = Column(DateTime, default=func.now(), server_default=func.now(), onupdate=func.now())

    profile = relationship("Profile", back_populates="users")
    events = relationship("Event", back_populates="owner", foreign_keys="Event.owner_id")
    tasks = relationship("Task", back_populates="assignee", foreign_keys="Task.assignee_id")
    leads = relationship("Lead", back_populates="owner", foreign_keys="Lead.owner_id")
    campaigns = relationship("Campaign", back_populates="owner", foreign_keys="Campaign.owner_id")


# Ensure Profile model is loaded into SQLAlchemy registry
from app.models.profile import Profile  # noqa: F401, E402