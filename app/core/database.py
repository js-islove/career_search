from contextlib import contextmanager
from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker, Session

from app.core.config import settings

# SQLite compatibility arguments for local tests
connect_args = {}
if settings.DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

# 1. Create the database engine with connection pooling and health pre-ping
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    connect_args=connect_args,
)

# 2. Session factory bound to our engine
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 3. Base class for all SQLAlchemy ORM models
Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """
    FastAPI dependency that provides a database session per HTTP request.
    Usage:
        @app.get("/items")
        def read_items(db: Session = Depends(get_db)):
            ...
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@contextmanager
def get_db_session() -> Generator[Session, None, None]:
    """
    Context manager for background tasks and ETL scripts.
    Auto-commits on success and rolls back on error.
    Usage:
        with get_db_session() as db:
            db.add(job)
    """
    session: Session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()

