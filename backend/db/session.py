from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from typing import Generator

from core.config import settings

SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# если нужна sqlite
SQLALCHEMY_DATABASE_URL = "sqlite:///./sql_app.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)


SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# задел на будущее
def get_db() -> Generator:
    """
    во время тестирования переопределяем этот 'get_db' для подключения к другой БД.
    Чтоб не засорять основную базу данных.
    Также создали зависимость get_db, которая позволяет предоставлять соединение с БД для каждого запроса.
    """
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()
