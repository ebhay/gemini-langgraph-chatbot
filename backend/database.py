from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from config import settings

# Configure engine with connection pooling
engine_args = {
    "connect_args": {"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {}
}

# Add connection pooling for non-SQLite databases
if "sqlite" not in settings.DATABASE_URL:
    engine_args.update({
        "pool_size": 10,
        "max_overflow": 20,
        "pool_pre_ping": True,  # Verify connections before using
        "pool_recycle": 3600,  # Recycle connections after 1 hour
    })

engine = create_engine(settings.DATABASE_URL, **engine_args)

SessionLocal = sessionmaker(bind=engine)

Base = declarative_base()