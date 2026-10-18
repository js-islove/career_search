from sqlalchemy import (
    BigInteger,
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


class Task(Base):
    """
    PostgreSQL-backed background task queue table.
    Workers claim tasks atomically using SELECT ... FOR UPDATE SKIP LOCKED.
    """
    __tablename__ = "tasks"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    type = Column(Text, nullable=False)  # 'DISCOVER' | 'FETCH_DETAIL' | 'REPARSE' | 'SWEEP'
    source_id = Column(
        BigInteger,
        ForeignKey("sources.id", ondelete="CASCADE"),
        nullable=True,
    )
    payload = Column(JSONB, nullable=False, default=dict, server_default=text("'{}'::jsonb"))
    status = Column(
        Text,
        nullable=False,
        default="pending",
        server_default=text("'pending'"),
    )  # 'pending' | 'running' | 'done' | 'failed' | 'dead'
    run_after = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    attempts = Column(Integer, nullable=False, default=0, server_default=text("0"))
    max_attempts = Column(Integer, nullable=False, default=5, server_default=text("5"))
    locked_by = Column(Text, nullable=True)
    locked_at = Column(DateTime(timezone=True), nullable=True)
    dedupe_key = Column(Text, nullable=True)
    last_error = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    finished_at = Column(DateTime(timezone=True), nullable=True)

    __table_args__ = (
        Index(
            "idx_tasks_queue",
            "run_after",
            "id",
            postgresql_where=text("status = 'pending'"),
        ),
        Index(
            "uq_task_pending_dedupe",
            "dedupe_key",
            unique=True,
            postgresql_where=text("status IN ('pending', 'running')"),
        ),
    )

    # Relationships
    source = relationship("Source")

    def __repr__(self) -> str:
        return f"<Task(id={self.id}, type='{self.type}', status='{self.status}', attempts={self.attempts})>"
