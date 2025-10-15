"""Configuration management using environment variables."""
from __future__ import annotations

import os
from functools import lru_cache
from typing import List
from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    # Flask
    secret_key: str = Field(default_factory=lambda: os.getenv("SECRET_KEY", "dev-secret-key"))
    allowed_origins: str | list[str] = Field(default=os.getenv("ALLOWED_ORIGINS", "*"))
    log_level: str = Field(default=os.getenv("LOG_LEVEL", "INFO"))

    # Server
    host: str = Field(default=os.getenv("HOST", "0.0.0.0"))
    port: int = Field(default=int(os.getenv("PORT", "8000")))

    # News API
    api_key: str | None = Field(default=os.getenv("API_KEY"))
    url: str | None = Field(default=os.getenv("URL"))

    # MongoDB
    mongo_username: str | None = Field(default=os.getenv("MONGO_USERNAME"))
    mongo_password: str | None = Field(default=os.getenv("MONGO_PASSWORD"))
    db_name: str | None = Field(default=os.getenv("DB_NAME"))

    # Email
    email_user: str | None = Field(default=os.getenv("EMAIL_USER"))
    email_pass: str | None = Field(default=os.getenv("EMAIL_PASS"))

    # Analyzer
    analyzer_model: str = Field(default=os.getenv("ANALYZER_MODEL", "vader"))

    # Cache/Artifacts
    cache_csv_path: str = Field(default=os.getenv("CACHE_CSV_PATH", "assets/mean_polarity.csv"))

    # Defaults
    default_domains: str = Field(default=os.getenv("DEFAULT_DOMAINS", 
        "wsj.com,aljazeera.com,bbc.co.uk,techcrunch.com,nytimes.com,bloomberg.com,businessinsider.com,cbc.ca,cnbc.com,cnn.com,apnews.com,reuters.com,theguardian.com"))

    class Config:
        env_file = ".env"
        case_sensitive = False

    @property
    def default_domains_list(self) -> List[str]:
        raw = self.default_domains
        if isinstance(raw, list):
            return raw
        return [d.strip() for d in raw.split(",") if d.strip()]


@lru_cache()
def get_settings() -> Settings:
    return Settings()  # type: ignore[call-arg]
