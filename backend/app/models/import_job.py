from sqlalchemy import Column, String, Integer, DateTime, func
from app.database import Base
from app.utils.id_gen import generate_id


class ImportJob(Base):
    __tablename__ = "import_jobs"

    id = Column(String(36), primary_key=True, default=lambda: generate_id("imp_"))
    object_type = Column(String(80), nullable=False)
    filename = Column(String(255), nullable=False)
    total_rows = Column(Integer, default=0)
    success_rows = Column(Integer, default=0)
    error_rows = Column(Integer, default=0)
    errors = Column(String, nullable=True)
    status = Column(String(20), default="pending")  # pending | processing | completed | failed
    created_by = Column(String(36), nullable=False)
    created_at = Column(DateTime, default=func.now())