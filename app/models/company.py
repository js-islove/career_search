from sqlalchemy import BigInteger, Column, DateTime, Text, func
from sqlalchemy.orm import relationship

from app.core.database import Base


class Company(Base):
    """Represents an organization whose job openings we track."""
    __tablename__ = "companies"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    name = Column(Text, nullable=False)
    slug = Column(Text, unique=True, nullable=False, index=True)
    website = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    # Relationships
    sources = relationship("Source", back_populates="company", cascade="all, delete-orphan")
    jobs = relationship("Job", back_populates="company", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Company(id={self.id}, slug='{self.slug}', name='{self.name}')>"