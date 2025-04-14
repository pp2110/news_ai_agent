import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from typing import TypedDict, List, Literal, Optional
from app.api.models import Article

class NewsroomState(TypedDict):
    topic: str
    searched_articles: List[Article]
    reported_articles: List[Article]
    edited_articles: List[Article]
    final_articles: List[Article]
    summary: Optional[str]
    current_stage: Literal["search", "report", "edit", "summarize", "review"]
    error: Optional[str]

def create_initial_state(topic: str) -> NewsroomState:
    print("into create_initial_state with topic:",topic)
    print("Completed create_initial_state with topic:",topic)
    print("="*50)
    return {
        "topic": topic,
        "searched_articles": [],
        "reported_articles": [],
        "edited_articles": [],
        "final_articles": [],
        "summary": None,
        "current_stage": "search",
        "error": None
    }