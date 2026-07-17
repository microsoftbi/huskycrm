from sqlalchemy import Column, Integer, String, Boolean, DateTime, func
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
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
