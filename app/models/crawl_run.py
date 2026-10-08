import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship

from app.database import Base


class CrawlRun(Base):
    __tablename__ = 'crawl_runs'

    id = Column(Integer, primary_key=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False)
    status = Column(String, nullable=False)  # 'success', 'failed', 'partial'
    jobs_found = Column(Integer, default=0)
    jobs_added = Column(Integer, default=0)
    jobs_updated = Column(Integer, default=0)
    error_message = Column(Text, nullable=True)
    started_at = Column(DateTime, default=datetime.datetime.utcnow)
    ended_at = Column(DateTime, nullable=True)

    company = relationship("Company", back_populates="crawl_runs")