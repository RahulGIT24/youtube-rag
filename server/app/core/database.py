from sqlmodel import SQLModel, create_engine, Session
from .config import settings
from sqlalchemy.orm import DeclarativeBase

engine = create_engine(
    settings.DATABASE_URL,
    echo=settings.ENV == 'dev',
    pool_pre_ping=True
)

class Base(DeclarativeBase):
    pass

def get_session():
    with Session(engine) as session:
        yield session