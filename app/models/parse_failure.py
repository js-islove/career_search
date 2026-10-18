from sqlalchemy import BigInteger, Column, DateTime, ForeignKey, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from app.core.database import Base


class ParseFailure(Base):
    """
    Quarantine table for individual job entries that failed parsing or validation.
    Isolates bad records so a single malformed job posting never crashes an entire crawl run.
    """
    __tablename__ = "parse_failures"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    source_id = Column(
        BigInteger,
        ForeignKey("sources.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    raw_document_id = Column(
        BigInteger,
        ForeignKey("raw_documents.id", ondelete="SET NULL"),
        nullable=True,
    )
    external_id = Column(Text, nullable=True)
    reason = Column(Text, nullable=False)
    details = Column(JSONB, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    # Relationships
    source = relationship("Source")
    raw_document = relationship("RawDocument")

    def __repr__(self) -> str:
        return f"<ParseFailure(id={self.id}, source_id={self.source_id}, reason='{self.reason}')>"
