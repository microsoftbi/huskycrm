from sqlalchemy import Column, String, Boolean, Text, DateTime, func
from app.database import Base
from app.utils.id_gen import generate_id


class Profile(Base):
    """用户配置 — 定义权限集合"""
    __tablename__ = "profiles"

    id = Column(String(36), primary_key=True, default=lambda: generate_id("prof_"))
    name = Column(String(120), unique=True, nullable=False, index=True)
    profile_type = Column(String(50), nullable=False, default="standard")  # admin / standard / readonly
    description = Column(Text)
    is_system = Column(Boolean, default=False)  # 系统预设，不可删除
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())