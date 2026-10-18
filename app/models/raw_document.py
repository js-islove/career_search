from sqlalchemy import (
    BigInteger,
    Column,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    LargeBinary,
    String,
    Text,
    func,
)
from sqlalchemy.orm import relationship

from app.core.database import Base


class RawDocument(Base):
    """
    Immutable store of raw HTTP payloads fetched during crawling.
    Payloads are stored compressed (gzip) alongside their SHA-256 hash
    so historical listings can be reparsed offline without re-fetching.
    """
    __tablename__ = "raw_documents"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    crawl_run_id = Column(
        BigInteger,
        ForeignKey("crawl_runs.id", ondelete="SET NULL"),
        nullable=True,
    )
    source_id = Column(
        BigInteger,
        ForeignKey("sources.id", ondelete="CASCADE"),
        nullable=False,
    )
    url = Column(Text, nullable=False)
    http_status = Column(Integer, nullable=False)
    content_type = Column(Text, nullable=True)
    body_compressed = Column(LargeBinary, nullable=False)  # gzip-compressed bytes (BYTEA)
    body_sha256 = Column(String(64), nullable=False)
    fetched_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    kind = Column(Text, nullable=False)  # 'listing' | 'detail' | 'api'

    __table_args__ = (
        Index("idx_raw_docs_sha", "body_sha256"),
    )

    # Relationships
    crawl_run = relationship("CrawlRun", back_populates="raw_documents")
    source = relationship("Source", back_populates="raw_documents")

    def __repr__(self) -> str:
        return f"<RawDocument(id={self.id}, kind='{self.kind}', status={self.http_status}, sha256='{self.body_sha256[:10]}...')>"
