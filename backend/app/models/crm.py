from sqlalchemy import (
    Column, Integer, String, Text, Boolean, DateTime, ForeignKey, DECIMAL, Date, func
)
from sqlalchemy.orm import relationship
from app.database import Base


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    product_code = Column(String(100), unique=True, index=True)
    description = Column(Text)
    price = Column(DECIMAL(15, 2), default=0.0)
    cost = Column(DECIMAL(15, 2), default=0.0)
    category = Column(String(100))
    is_active = Column(Boolean, default=True)
    owner_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    owner = relationship("User")


class Account(Base):
    __tablename__ = "accounts"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    industry = Column(String(100))
    phone = Column(String(50))
    website = Column(String(255))
    email = Column(String(255))
    billing_street = Column(Text)
    billing_city = Column(String(100))
    billing_state = Column(String(100))
    billing_zip = Column(String(20))
    billing_country = Column(String(100))
    description = Column(Text)
    owner_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    owner = relationship("User")
    contacts = relationship("Contact", back_populates="account")


class Contact(Base):
    __tablename__ = "contacts"

    id = Column(Integer, primary_key=True, index=True)
    account_id = Column(Integer, ForeignKey("accounts.id"), index=True)
    first_name = Column(String(80), nullable=False)
    last_name = Column(String(80), nullable=False)
    email = Column(String(255), index=True)
    phone = Column(String(50))
    mobile_phone = Column(String(50))
    title = Column(String(255))
    department = Column(String(100))
    owner_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    account = relationship("Account", back_populates="contacts")
    owner = relationship("User")


class Stage(Base):
    __tablename__ = "stages"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    probability = Column(Integer, default=0)
    sort_order = Column(Integer, nullable=False)
    is_closed_won = Column(Boolean, default=False)
    is_closed_lost = Column(Boolean, default=False)

    opportunities = relationship("Opportunity", back_populates="stage")


class Opportunity(Base):
    __tablename__ = "opportunities"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    account_id = Column(Integer, ForeignKey("accounts.id"), index=True)
    stage_id = Column(Integer, ForeignKey("stages.id"), nullable=False)
    amount = Column(DECIMAL(15, 2), default=0.0)
    probability = Column(Integer, default=0)
    close_date = Column(Date)
    description = Column(Text)
    owner_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    account = relationship("Account")
    stage = relationship("Stage", back_populates="opportunities")
    owner = relationship("User")
    line_items = relationship("OpportunityProduct", back_populates="opportunity",
                              cascade="all, delete-orphan")


class OpportunityProduct(Base):
    """Line item joining an Opportunity with a Product."""
    __tablename__ = "opportunity_products"

    id = Column(Integer, primary_key=True, index=True)
    opportunity_id = Column(Integer, ForeignKey("opportunities.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    quantity = Column(Integer, default=1)
    unit_price = Column(DECIMAL(15, 2), default=0.0)
    total_price = Column(DECIMAL(15, 2), default=0.0)
    created_at = Column(DateTime, default=func.now())

    opportunity = relationship("Opportunity", back_populates="line_items")
    product = relationship("Product")
