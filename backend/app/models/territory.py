from sqlalchemy import (
    Column, Integer, String, Text, Boolean, DateTime, ForeignKey, DECIMAL, func, UniqueConstraint
)
from sqlalchemy.orm import relationship
from app.database import Base
from app.utils.id_gen import generate_id


class Territory(Base):
    __tablename__ = "territories"

    id = Column(String(36), primary_key=True, default=lambda: generate_id("terr_"))
    name = Column(String(255), nullable=False, index=True)
    code = Column(String(100), index=True)
    territory_type = Column(String(50), default="region")
    parent_id = Column(String(36), ForeignKey("territories.id"))
    description = Column(Text)
    is_active = Column(Boolean, default=True)
    owner_id = Column(String(36), ForeignKey("users.id"))
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    parent = relationship("Territory", remote_side=[id], back_populates="children")
    children = relationship("Territory", back_populates="parent", cascade="all, delete-orphan")
    owner = relationship("User")


class TerritoryMember(Base):
    __tablename__ = "territory_members"
    __table_args__ = (UniqueConstraint("territory_id", "user_id"),)

    id = Column(String(36), primary_key=True, default=lambda: generate_id("tmem_"))
    territory_id = Column(String(36), ForeignKey("territories.id"), nullable=False)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    role = Column(String(50), default="member")
    assigned_at = Column(DateTime, default=func.now())

    territory = relationship("Territory")
    user = relationship("User")


class TerritoryAccount(Base):
    __tablename__ = "territory_accounts"
    __table_args__ = (UniqueConstraint("territory_id", "account_id"),)

    id = Column(String(36), primary_key=True, default=lambda: generate_id("tacc_"))
    territory_id = Column(String(36), ForeignKey("territories.id"), nullable=False)
    account_id = Column(String(36), ForeignKey("accounts.id"), nullable=False)
    assigned_at = Column(DateTime, default=func.now())

    territory = relationship("Territory")
    account = relationship("Account")


class TerritoryProduct(Base):
    __tablename__ = "territory_products"
    __table_args__ = (UniqueConstraint("territory_id", "product_id"),)

    id = Column(String(36), primary_key=True, default=lambda: generate_id("tprod_"))
    territory_id = Column(String(36), ForeignKey("territories.id"), nullable=False)
    product_id = Column(String(36), ForeignKey("products.id"), nullable=False)
    price = Column(DECIMAL(15, 2))  # null = use product default price
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())

    territory = relationship("Territory")
    product = relationship("Product")
