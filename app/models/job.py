import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship

from app.database import Base


class Job(Base):
    __tablename__ = 'jobs'

    id = Column(Integer, primary_key=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False)

    # Core Data
    title = Column(String, nullable=False)
    url = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    location = Column(String, nullable=True)
    department = Column(String, nullable=True)
    employment_type = Column(String, nullable=True)
    source_job_id = Column(String, nullable=True)

    # Pipeline Metadata
    fingerprint = Column(String, unique=True, nullable=False)  # e.g., SHA-256 of (Company URL + Job ID)
    content_hash = Column(String, nullable=False)              # e.g., SHA-256 of (Title + Location + Desc)
    status = Column(String, default="active")                  # 'active' or 'inactive'

    # Timestamps
    first_seen_at = Column(DateTime, default=datetime.datetime.utcnow)
    last_seen_at = Column(DateTime, default=datetime.datetime.utcnow)

    company = relationship("Company", back_populates="jobs")