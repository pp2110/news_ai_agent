from fastapi import APIRouter, HTTPException
from .agent import run_news_agent
from pydantic import BaseModel

router = APIRouter()

class NewsRequest(BaseModel):
    topic: str

@router.post("/news")
async def get_news_summary(request: NewsRequest):
    try:
        result = run_news_agent(request.topic)
        print(request.topic)
        return {
            "topic": request.topic,
            "search_results": result.get('search_results', []),
            "news_summary": result.get('news_summary', '')
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))