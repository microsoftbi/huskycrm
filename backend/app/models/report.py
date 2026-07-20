from sqlalchemy import (
    Column, Integer, String, Text, DateTime, ForeignKey, func
)
from sqlalchemy.orm import relationship
from app.database import Base
from app.utils.id_gen import generate_id


class Report(Base):
    """Saved report definition."""
    __tablename__ = "reports"

    id = Column(String(36), primary_key=True, default=lambda: generate_id("rpt_"))
    name = Column(String(255), nullable=False)
    object_type = Column(String(120), nullable=False)    # "account", "contact", "opportunity", or custom API name
    report_type = Column(String(50), default="tabular")  # "tabular", "summary"
    filters = Column(Text)                               # JSON
    grouping = Column(Text)                              # JSON
    aggregations = Column(Text)                          # JSON
    columns = Column(Text)                               # JSON: field names to display
    owner_id = Column(String(36), ForeignKey("users.id"))
    created_at = Column(DateTime, default=func.now(), server_default=func.now())
    updated_at = Column(DateTime, default=func.now(), server_default=func.now(), onupdate=func.now())

    owner = relationship("User")


class Dashboard(Base):
    """Dashboard definition with multiple report tiles."""
    __tablename__ = "dashboards"

    id = Column(String(36), primary_key=True, default=lambda: generate_id("dsb_"))
    name = Column(String(255), nullable=False)
    owner_id = Column(String(36), ForeignKey("users.id"))
    layout = Column(Text)                                # JSON: grid layout
    created_at = Column(DateTime, default=func.now(), server_default=func.now())
    updated_at = Column(DateTime, default=func.now(), server_default=func.now(), onupdate=func.now())

    owner = relationship("User")
    components = relationship("DashboardComponent", back_populates="dashboard",
                              cascade="all, delete-orphan")


class DashboardComponent(Base):
    """A chart/table tile within a dashboard."""
    __tablename__ = "dashboard_components"

    id = Column(String(36), primary_key=True, default=lambda: generate_id("dsc_"))
    dashboard_id = Column(String(36), ForeignKey("dashboards.id"), nullable=False)
    report_id = Column(String(36), ForeignKey("reports.id"))
    title = Column(String(255))
    chart_type = Column(String(50), default="table")     # "table", "bar", "line", "pie", "metric"
    position_x = Column(Integer, default=0)
    position_y = Column(Integer, default=0)
    width = Column(Integer, default=4)
    height = Column(Integer, default=3)

    dashboard = relationship("Dashboard", back_populates="components")
    report = relationship("Report")