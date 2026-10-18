from sqlalchemy import (
    BigInteger,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    SmallInteger,
    String,
    Text,
    UniqueConstraint,
    func,
    text,
)
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, TSVECTOR
from sqlalchemy.orm import relationship

from app.core.database import Base


class Job(Base):
    """
    Canonical job listing table.
    Stores normalized fields, SHA-256 content_hash (for update detection),
    dedupe_key (for cross-posting deduplication), and lifecycle state.
    """
    __tablename__ = "jobs"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    source_id = Column(
        BigInteger,
        ForeignKey("sources.id", ondelete="CASCADE"),
        nullable=False,
    )
    company_id = Column(
        BigInteger,
        ForeignKey("companies.id", ondelete="CASCADE"),
        nullable=False,
    )
    external_id = Column(Text, nullable=False)

    # Core Content
    title = Column(Text, nullable=False)
    title_normalized = Column(Text, nullable=False)
    description_html = Column(Text, nullable=True)
    description_text = Column(Text, nullable=True)
    department = Column(Text, nullable=True)

    # Normalized Taxonomy & Classification
    employment_type = Column(
        Text,
        nullable=True,
        default="unknown",
        server_default=text("'unknown'"),
    )  # 'full_time' | 'part_time' | 'contract' | 'intern' | 'other' | 'unknown'
    workplace_type = Column(
        Text,
        nullable=True,
        default="unknown",
        server_default=text("'unknown'"),
    )  # 'onsite' | 'hybrid' | 'remote' | 'unknown'
    seniority = Column(
        Text,
        nullable=True,
        default="unknown",
        server_default=text("'unknown'"),
    )  # 'intern' | 'junior' | 'mid' | 'senior' | 'staff' | 'principal' | 'unknown'
    experience_min_years = Column(SmallInteger, nullable=True)
    experience_max_years = Column(SmallInteger, nullable=True)

    # Structured Locations & Compensation
    locations = Column(JSONB, nullable=True, default=list, server_default=text("'[]'::jsonb"))
    country_codes = Column(ARRAY(Text), nullable=True)
    salary_min = Column(Numeric, nullable=True)
    salary_max = Column(Numeric, nullable=True)
    salary_currency = Column(String(3), nullable=True)
    salary_period = Column(Text, nullable=True)

    # Links & Timestamps
    apply_url = Column(Text, nullable=False)
    canonical_url = Column(Text, nullable=True)
    posted_at = Column(DateTime(timezone=True), nullable=True)
    source_updated_at = Column(DateTime(timezone=True), nullable=True)
    first_seen_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    last_seen_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    last_changed_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    closed_at = Column(DateTime(timezone=True), nullable=True)

    # Lifecycle & Fingerprinting
    status = Column(
        Text,
        nullable=False,
        default="active",
        server_default=text("'active'"),
    )  # 'active' | 'missing' | 'closed' | 'expired' | 'archived'
    missed_crawl_count = Column(SmallInteger, nullable=False, default=0, server_default=text("0"))
    content_hash = Column(String(64), nullable=False)
    dedupe_key = Column(Text, nullable=True)
    canonical_job_id = Column(
        BigInteger,
        ForeignKey("jobs.id", ondelete="SET NULL"),
        nullable=True,
    )

    # Provenance & Search
    quality_score = Column(Float, nullable=False, default=1.0, server_default=text("1.0"))
    extraction_method = Column(Text, nullable=False, default="api", server_default=text("'api'"))
    parser_version = Column(Text, nullable=False, default="1.0.0", server_default=text("'1.0.0'"))
    raw_document_id = Column(
        BigInteger,
        ForeignKey("raw_documents.id", ondelete="SET NULL"),
        nullable=True,
    )
    extra = Column(JSONB, nullable=True, default=dict, server_default=text("'{}'::jsonb"))
    search_vector = Column(TSVECTOR, nullable=True)

    __table_args__ = (
        UniqueConstraint("source_id", "external_id", name="uq_source_external_id"),
        Index(
            "idx_jobs_active_listing",
            text("posted_at DESC NULLS LAST"),
            text("id DESC"),
            postgresql_where=text("status = 'active'"),
        ),
        Index("idx_jobs_search_vector", "search_vector", postgresql_using="gin"),
        Index("idx_jobs_country_codes", "country_codes", postgresql_using="gin"),
        Index("idx_jobs_company_status", "company_id", "status"),
        Index("idx_jobs_dedupe_key", "dedupe_key"),
        Index("idx_jobs_lifecycle_sweep", "source_id", "status"),
    )

    # Relationships
    source = relationship("Source", back_populates="jobs")
    company = relationship("Company", back_populates="jobs")
    raw_document = relationship("RawDocument")
    versions = relationship("JobVersion", back_populates="job", cascade="all, delete-orphan")
    canonical_job = relationship("Job", remote_side=[id])

    def __repr__(self) -> str:
        return f"<Job(id={self.id}, external_id='{self.external_id}', title='{self.title}', status='{self.status}')>"


class JobVersion(Base):
    """
    Immutable historical snapshot created whenever a Job's content_hash changes.
    Tracks what fields changed across time.
    """
    __tablename__ = "job_versions"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    job_id = Column(
        BigInteger,
        ForeignKey("jobs.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    version = Column(Integer, nullable=False)
    content_hash = Column(String(64), nullable=False)
    snapshot = Column(JSONB, nullable=False)
    changed_fields = Column(ARRAY(Text), nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    __table_args__ = (
        UniqueConstraint("job_id", "version", name="uq_job_version"),
    )

    # Relationships
    job = relationship("Job", back_populates="versions")

    def __repr__(self) -> str:
        return f"<JobVersion(job_id={self.job_id}, version={self.version}, hash='{self.content_hash[:10]}...')>"