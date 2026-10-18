from sqlalchemy import (
    BigInteger,
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    Text,
    func,
    text,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from app.core.database import Base


class CrawlRun(Base):
    """
    Execution audit trail for a single crawl run of a Source.
    Tracks metrics (found, new, updated, unchanged, closed), completeness, and errors.
    """
    __tablename__ = "crawl_runs"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    source_id = Column(
        BigInteger,
        ForeignKey("sources.id", ondelete="CASCADE"),
        nullable=False,
    )
    started_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    finished_at = Column(DateTime(timezone=True), nullable=True)

    # 'running' | 'succeeded' | 'partial' | 'failed' | 'quarantined'
    status = Column(Text, nullable=False, default="running", server_default=text("'running'"))
    is_complete = Column(Boolean, nullable=False, default=False, server_default=text("false"))

    # Run counters
    refs_found = Column(Integer, nullable=False, default=0, server_default=text("0"))
    jobs_new = Column(Integer, nullable=False, default=0, server_default=text("0"))
    jobs_updated = Column(Integer, nullable=False, default=0, server_default=text("0"))
    jobs_unchanged = Column(Integer, nullable=False, default=0, server_default=text("0"))
    jobs_closed = Column(Integer, nullable=False, default=0, server_default=text("0"))
    parse_failures = Column(Integer, nullable=False, default=0, server_default=text("0"))
    http_errors = Column(Integer, nullable=False, default=0, server_default=text("0"))

    adapter_version = Column(Text, nullable=False, default="1.0.0", server_default=text("'1.0.0'"))
    error = Column(Text, nullable=True)
    stats = Column(JSONB, nullable=True)

    __table_args__ = (
        Index("idx_crawl_runs_source_started", "source_id", text("started_at DESC")),
    )

    # Relationships
    source = relationship("Source", back_populates="crawl_runs")
    raw_documents = relationship("RawDocument", back_populates="crawl_run")

    def __repr__(self) -> str:
        return (
            f"<CrawlRun(id={self.id}, source_id={self.source_id}, "
            f"status='{self.status}', new={self.jobs_new}, updated={self.jobs_updated})>"
        )