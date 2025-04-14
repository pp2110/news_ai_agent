import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from app.core.state import NewsroomState
from app.api.models import Article
from typing import List
import json
import re

def extract_json_from_response(content: str) -> List[Article]:
    try:
        # First attempt: direct JSON parsing
        return json.loads(content)
    except json.JSONDecodeError:
        # Second attempt: find JSON array in content
        json_match = re.search(r'\[[\s\S]*\]', content)
        if json_match:
            try:
                return json.loads(json_match.group())
            except json.JSONDecodeError:
                pass
    
    # Final attempt: structured parsing
    articles = []
    current_article = {}
    
    for line in content.split('\n'):
        if '"title":' in line:
            if current_article and all(k in current_article for k in Article.__annotations__):
                articles.append(current_article)
            current_article = {}
        
        for field in Article.__annotations__:
            if f'"{field}":' in line:
                value = line.split(':', 1)[1].strip().strip('",')
                current_article[field] = value
    
    if current_article and all(k in current_article for k in Article.__annotations__):
        articles.append(current_article)
    
    return articles

def update_state(state: NewsroomState, updates: dict) -> NewsroomState:
    new_state = state.copy()
    for key, value in updates.items():
        new_state[key] = value
    return new_state