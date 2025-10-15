from __future__ import annotations

from typing import List, Optional
from pydantic import BaseModel, Field, validator

from ..core.config import get_settings


class Article(BaseModel):
    title: Optional[str] = None
    author: Optional[str] = None
    source: Optional[str] = None
    description: Optional[str] = None
    content: Optional[str] = None
    pub_date: Optional[str] = Field(default=None, description="ISO date")
    url: Optional[str] = None
    photo_url: Optional[str] = None
    combined_text: Optional[str] = None


class ExtractRequest(BaseModel):
    domains: List[str] | None = None
    from_date: Optional[str] = Field(default=None, description="YYYY-MM-DD")

    @validator("domains", pre=True, always=True)
    def default_domains(cls, v):  # noqa: N805
        if v in (None, [], ""):
            return get_settings().default_domains_list
        return v


class AnalyzeRequest(BaseModel):
    text: Optional[str] = None
    texts: Optional[List[str]] = None
    articles: Optional[List[Article]] = None


class SendReportRequest(BaseModel):
    to: List[str]
    subject: Optional[str] = Field(default="News Analyzer Report")
    body: Optional[str] = Field(default="Please find the attached report.")
    attachments: Optional[List[str]] = Field(default=None)
