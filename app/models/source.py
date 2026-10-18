from datetime import timedelta
from sqlalchemy import (
    BigInteger,
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    Interval,
    Text,
    func,
    text,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from app.core.database import Base


class Source(Base):
    """
    Represents a specific job ingestion source for a company
    (e.g., a Greenhouse board, a Lever feed, or a custom HTML careers page).
    """
    __tablename__ = "sources"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    company_id = Column(
        BigInteger,
        ForeignKey("companies.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name = Column(Text, nullable=True)
    careers_url = Column(Text, nullable=False)
    adapter_id = Column(Text, nullable=False)  # e.g., 'greenhouse', 'lever', 'jsonld', 'html_config'
    config = Column(JSONB, nullable=False, default=dict, server_default=text("'{}'::jsonb"))
    detection = Column(JSONB, nullable=True)

    # Scheduling & Health Circuit Breaker
    enabled = Column(Boolean, nullable=False, default=True, server_default=text("true"))
    crawl_interval = Column(
        Interval,
        nullable=False,
        default=lambda: timedelta(hours=6),
        server_default=text("'6 hours'::interval"),
    )
    next_crawl_at = Column(DateTime(timezone=True), nullable=True)
    last_success_at = Column(DateTime(timezone=True), nullable=True)
    consecutive_failures = Column(Integer, nullable=False, default=0, server_default=text("0"))
    circuit_state = Column(
        Text,
        nullable=False,
        default="closed",
        server_default=text("'closed'"),
    )  # 'closed' | 'open' | 'half_open'
    circuit_until = Column(DateTime(timezone=True), nullable=True)
    strategy_risk = Column(
        Text,
        nullable=False,
        default="normal",
        server_default=text("'normal'"),
    )  # 'normal' | 'elevated'
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    # Partial index for fast scheduler polling of due sources
    __table_args__ = (
        Index(
            "idx_sources_due",
            "next_crawl_at",
            postgresql_where=text("enabled = true AND circuit_state != 'open'"),
        ),
    )

    # Relationships
    company = relationship("Company", back_populates="sources")
    crawl_runs = relationship("CrawlRun", back_populates="source", cascade="all, delete-orphan")
    raw_documents = relationship("RawDocument", back_populates="source", cascade="all, delete-orphan")
    jobs = relationship("Job", back_populates="source", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Source(id={self.id}, adapter='{self.adapter_id}', url='{self.careers_url}')>"
