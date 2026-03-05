from pydantic import BaseModel, HttpUrl
from typing import List, Optional

class SummarizeRequest(BaseModel):
    url: str
    length: str = "medium" # short, medium, long

class MetadataResponse(BaseModel):
    title: str
    author: str
    date: str

class SentimentResponse(BaseModel):
    label: str
    score: float

class SummarizeResponse(BaseModel):
    metadata: MetadataResponse
    summary_paragraph: str
    summary_bullets: List[str]
    sentiment: SentimentResponse
    original_length: int
    summary_length: int
