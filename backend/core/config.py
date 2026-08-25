import os
from dotenv import load_dotenv
from pathlib import Path

env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)


class Settings:
    PROJECT_NAME: str = 'SOKOLOV EVGENIY'
    PROJECT_VERSION: str = "1.0.0"

    POSTGRES_USER: str = os.getenv('POSTGRES_USER')
    POSTGRES_PASSWORD: str = os.getenv('POSTGRES_PASSWORD')
    POSTGRES_SERVER: str = os.getenv('POSTGRES_SERVER')
    POSTGRES_PORT: str = os.getenv('POSTGRES_PORT')
    POSTGRES_DB: str = os.getenv('POSTGRES_DB')
    DATABASE_URL: str = f'postgresql://{POSTGRES_USER}:' \
                        f'{POSTGRES_PASSWORD}@{POSTGRES_SERVER}:{POSTGRES_PORT}/{POSTGRES_DB}'

    REFRESH_TOKEN_EXPIRE_DAYS = 1
    ACCESS_TOKEN_EXPIRE_MINUTES = 30
    ALGORITHM: str = 'HS256'
    SECRET_KEY: str = os.getenv("SECRET_KEY")

    TEST_USER_EMAIL = 'test@example.com'


settings = Settings()
