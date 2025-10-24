# backend/app/database.py
from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base, Session

# SQLite DB file will live next to this file (backend/app/app.db)
DATABASE_URL = "sqlite:///./app.db"

# For SQLite with SQLAlchemy in single-process dev, disable same_thread check
engine = create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}
)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()


def init_db() -> None:
    """
    Create database tables. Call this at application startup.
    Models must import Base from this module and subclass it.
    """
    # Import models here if they are in a separate file so they are registered with Base
    # (avoid circular import at module import time in main.py: import only inside function)
    try:
        # If models.py exists, import it so Base.metadata has tables to create
        import backend.app.models  # noqa: F401
    except Exception:
        # models may not exist yet during step-by-step setup — that's ok.
        pass

    Base.metadata.create_all(bind=engine)


# Dependency to get DB session in path operations
def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
