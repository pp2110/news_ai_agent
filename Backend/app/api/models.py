from pydantic import BaseModel
from typing import List, Optional

class NewsRequest(BaseModel):
    topic: str

class Article(BaseModel):
    title: str
    url: str
    date: str
    content: str
    source: str

class NewsResponse(BaseModel):
    topic: str
    articles: List[Article]
    summary: Optional[str]
    status: str