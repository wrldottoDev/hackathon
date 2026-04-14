from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DATA_BASE_URL = "sqlite:///.bank.db"

engine = create_engine(
    DATA_BASE_URL,
    connect_args={"check_same_thread"}
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()