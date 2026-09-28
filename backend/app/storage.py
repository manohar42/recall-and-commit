from collections.abc import Generator
from pathlib import Path

from sqlalchemy import create_engine, select, text
from sqlalchemy.orm import Session, DeclarativeBase, sessionmaker


BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

DATABASE_PATH = DATA_DIR / "recall_commit.db"
DATABASE_URL = f"sqlite:///{DATABASE_PATH.as_posix()}"


engine = create_engine(DATABASE_URL,
                       connect_args={"check_same_thread": False},)

sessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit = False,
    expire_on_commit=False
)


class Base(DeclarativeBase):
    """Base class for all future SQLAlchemy models."""
    pass

def get_db() -> Generator[Session, None, None]:
    db = sessionLocal()

    try:
        yield db
    except:
        db.close()

def check_database_connection() -> bool:
    """Return True when SQLite can execute a simple query."""
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        return True
    except Exception:
        return False

