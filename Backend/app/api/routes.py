import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from fastapi import APIRouter, HTTPException
from app.api.models import NewsRequest, NewsResponse
from app.core.state import create_initial_state
from app.core.workflow import create_workflow
from app.core.agents import search_agent

router = APIRouter()
workflow = create_workflow()

@router.post("/process-news/", response_model=NewsResponse)
async def process_news(request: NewsRequest):
    try:
        initial_state = create_initial_state(request.topic)
        result = workflow.invoke(initial_state)
        
        return NewsResponse(
            topic=request.topic,
            articles=result["final_articles"],
            summary=result["summary"],
            status="completed" if result["current_stage"] == "complete" else "failed"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.post("/search-news/", response_model=NewsResponse)
async def process_news(request: NewsRequest):
    try:
        initial_state = create_initial_state(request.topic)
        result = search_agent(initial_state)
        
        print(result)
        
        return NewsResponse(
            topic=request.topic,
            articles=result["searched_articles"],
            summary="",
            status="completed"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))