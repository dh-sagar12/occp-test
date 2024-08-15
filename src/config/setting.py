"""
Base app configurations.
"""

import os

from pydantic_settings import BaseSettings




class Settings(BaseSettings):
    """Base settings."""

    DB_PORT: int = os.getenv("POSTGRES_PORT")
    DB_HOST: str = os.getenv("POSTGRES_HOST")
    DB_NAME: str = os.getenv("POSTGRES_DB")
    DB_USER: str = os.getenv("POSTGRES_USER")
    DB_PASS: str = os.getenv("POSTGRES_PASSWORD")

    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM")
    JWT_SECRET: str = os.getenv("JWT_SECRET")
    ACCESS_TOKEN_EXPIRES_AT: int = os.getenv("ACCESS_TOKEN_EXPIRES_AT")
    REFRESH_TOKEN_EXPIRES_AT: int = os.getenv("REFRESH_TOKEN_EXPIRES_AT")


settings = Settings()
