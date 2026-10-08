import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, UniqueConstraint
from sqlalchemy.orm import relationship

from app.database import Base


class Company(Base):
    __tablename__ = 'companies'

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    careers_url = Column(String, nullable=False)

    jobs = relationship("Job", back_populates="company", cascade="all, delete-orphan")
    crawl_runs = relationship("CrawlRun", back_populates="company", cascade="all, delete-orphan")