import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from app.config import settings
from app.core.state import NewsroomState
from app.utils.helpers import extract_json_from_response,update_state
from typing import Dict, List, Optional,Literal
from typing import TypedDict,Annotated
from langgraph.graph import StateGraph, END
from langchain_core.messages import AIMessage
from langchain_community.tools import DuckDuckGoSearchResults as DDGS
from langchain_community.utilities import DuckDuckGoSearchAPIWrapper
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage
import json
from langchain_core.pydantic_v1 import BaseModel,Field
import os
import dotenv
import re
from datetime import datetime, timedelta

wrapper = DuckDuckGoSearchAPIWrapper(time="w", max_results=15)
search_tool = DDGS(backend="news",api_wrapper=wrapper)
print(type(search_tool))
print(search_tool.name)

model = ChatGroq(
        groq_api_key= settings.GROQ_API_KEY,
        model_name='llama3-8b-8192'
    )

def search_agent(state: NewsroomState) -> NewsroomState:
    """News Retrieval Search Agent"""
    print("in Search Agent with topic", state['topic'])
    search_prompt = f"""You are a News Retrieval Search Agent.
    Search for articles related to: {state['topic']}
    
    Requirements:
    - Minimum 10 high-quality articles
    - Filter out: off-topic, low-quality sources, duplicates, opinion pieces
    - Focus on factual reporting
    
    Return ONLY a JSON array of articles in this exact format:
    [
        {{
            "title": "Article Title",
            
            "url": "https://...",
            "date": "YYYY-MM-DD",
            "content": "Article body...",
            "source": "Source Name"
        }}
    ]"""
    
    try:
        search_results = search_tool.run(f"{state['topic']}")
        print("Search results: ",search_results)
        response = model.invoke([HumanMessage(content=f"{search_prompt}\n\nSearch results:\n{search_results}")])
        print("Search response: ",response)
        articles = extract_json_from_response(response.content)
        
        print("Out of Search Agent")
        if not articles:
            return update_state(state, {
                "error": "No valid articles found",
                "searched_articles": []
            })
        
        return update_state(state, {
            "searched_articles": articles,
            "current_stage": "report",
            "error": None
        })
    except Exception as e:
        return update_state(state, {
            "error": f"Search failed: {str(e)}",
            "searched_articles": []
        })

def reporter_agent(state: NewsroomState) -> NewsroomState:
    """News Reporter Agent"""
    if not state['searched_articles']:
        return update_state(state, {"error": "No articles to report on"})
    
    reporter_prompt = """You are a skilled News Reporter. Transform this article into an engaging, 
    unbiased story while maintaining accuracy.
    
    Focus on:
    - Clear and concise writing
    - Engaging narrative structure
    - Factual accuracy
    - Balanced perspective
    
    Return ONLY a JSON array with a single article in this exact format:
    [
        {
            "title": "Original title - keep it",
            "url": "Original URL - keep it",
            "date": "Original date - keep it",
            "content": "Your rewritten content here...",
            "source": "Original source - keep it"
        }
    ]"""
    
    try:
        reported_articles = []
        for article in state['searched_articles']:
            response = model.invoke([
                HumanMessage(content=f"{reporter_prompt}\n\nArticle:\n{json.dumps([article], ensure_ascii=False)}")
            ])
            
            processed_articles = extract_json_from_response(response.content)
            if processed_articles:
                reported_articles.extend(processed_articles)
        
        if not reported_articles:
            return update_state(state, {
                "error": "No articles were successfully processed",
                "reported_articles": []
            })
        
        return update_state(state, {
            "reported_articles": reported_articles,
            "current_stage": "edit",
            "error": None
        })
    except Exception as e:
        return update_state(state, {
            "error": f"Reporting failed: {str(e)}",
            "reported_articles": []
        })

def editor_agent(state: NewsroomState) -> NewsroomState:
    """News Editor Agent"""
    if not state['reported_articles']:
        return update_state(state, {"error": "No articles to edit"})
    
    editor_prompt = """You are a meticulous News Editor. Review and refine these articles for:
    - Clarity and readability
    - Logical structure
    - Grammatical accuracy
    - Consistent style
    - Engaging headlines
    
    Return ONLY a JSON array with a single article in this exact format:
    [
        {
            "title": "Original title - keep it",
            "url": "Original URL - keep it",
            "date": "Original date - keep it",
            "content": "Your edited content here...",
            "source": "Original source - keep it"
        }
    ]"""
    
    try:
        edited_articles = []
        for article in state['reported_articles']:
            response = model.invoke([
                HumanMessage(content=f"{editor_prompt}\n\nArticle:\n{json.dumps([article], ensure_ascii=False)}")
            ])
            
            edited_article = extract_json_from_response(response.content)
            if edited_article:
                edited_articles.extend(edited_article)
        
        if not edited_articles:
            return update_state(state, {
                "error": "No articles were successfully edited",
                "edited_articles": []
            })
        
        return update_state(state, {
            "edited_articles": edited_articles,
            "current_stage": "summarize",
            "error": None
        })
    except Exception as e:
        return update_state(state, {
            "error": f"Editing failed: {str(e)}",
            "edited_articles": []
        })
        
def summarizer_agent(state: NewsroomState) -> NewsroomState:
    """News Summarizer Agent"""
    if not state['edited_articles']:
        return update_state(state, {"error": "No articles to summarize"})
    
    summarizer_prompt = """You are an expert News Summarizer. Create a comprehensive summary of all the provided articles. Just provide summarized content only—don't start your response with "Here is your content" or "Here is your summarized content."

Give the summary in **three sections**:

## 3-Point Summary (Make this heading 2 by adding ## at the start)
- Start content below to the topic add "-" at the end of each bullet point
- Start each bullet point on a **new line**.  
- This summary should be **eye-catching**, providing an **overview** of major updates and incidents from the past week.  

## Interesting Facts (Make this heading 2 by adding ## at the start)
- Start content below to the topic add "-" at the end of each bullet point   
- Start each bullet point on a **new line**.  
- This section should include **interesting and unusual events** that happened in an **unexpected or intriguing** manner.  

## Detailed Summary \n (Make this heading 2 by adding ## at the start)
Write this section in **2-3 paragraphs** below the heading.  
- The summary should be written in a **blog-style format** (800-1000 words).  
- It should **cover all news updates** and major developments from the past week.  

### **Requirements:**  
- Synthesize **key information** from all articles.  
- Identify **main themes and trends**.  
- Include **important statistics and data**.  
- Maintain **objectivity**.  

Return the summary in **Markdown format**, ensuring each bullet point appears on a new line.  """
    
    try:
        # Combine all articles for context
        combined_articles = "\n\n".join([
            f"Title: {article['title']}\nContent: {article['content']}"
            for article in state['edited_articles']
        ])
        
        response = model.invoke([
            HumanMessage(content=f"{summarizer_prompt}\n\nArticles:\n{combined_articles}")
        ])
        
        summary = response.content.strip()
        
        if not summary:
            return update_state(state, {
                "error": "Failed to generate summary",
                "summary": None
            })
        
        return update_state(state, {
            "summary": summary,
            "current_stage": "review",
            "error": None
        })
    except Exception as e:
        return update_state(state, {
            "error": f"Summarization failed: {str(e)}",
            "summary": None
        })
        
def newsroom_editor(state: NewsroomState) -> NewsroomState:
    """Newsroom Editor - Final Review"""
    if state.get('error'):
        print("⚠️ Error detected - Redirecting to search stage")
        return update_state(state, {"current_stage": "search"})

    if state.get('current_stage') == "review" and state.get('edited_articles') and state.get('summary'):
        review_prompt = """You are the Chief Newsroom Editor. Review the articles and summary for:
        - Minimum 10 articles requirement
        - Source credibility
        - Content quality and insight
        - Writing style and engagement
        - Summary comprehensiveness and accuracy
        
        You MUST return a JSON object in this exact format:
        {
            "decision": "approve",  # or "reject"
            "reason": "Specific reason for decision",
            "stage": "search"  # or "report" or "edit" or "summarize"
        }"""

        try:
            response = model.invoke([
                HumanMessage(content=f"{review_prompt}\n\nArticles:\n{json.dumps(state['edited_articles'], ensure_ascii=False)}\n\nSummary:\n{state['summary']}")
            ])
            
            # Extract JSON from response
            feedback_match = re.search(r'\{[\s\S]*\}', response.content)
            if feedback_match:
                feedback = json.loads(feedback_match.group())
            else:
                raise json.JSONDecodeError("No valid JSON found", response.content, 0)
            
            print(f"📋 Editor's Decision: {feedback['decision']}")
            print(f"📝 Reason: {feedback['reason']}")
            
            if feedback['decision'] == 'approve':
                print("✅ Articles and summary approved - Workflow complete")
                return update_state(state, {
                    "final_articles": state["edited_articles"],
                    "current_stage": "complete"
                })
            
            print(f"🔄 Content needs revision - Redirecting to {feedback['stage']} stage")
            return update_state(state, {"current_stage": feedback['stage']})
            
        except (json.JSONDecodeError, KeyError) as e:
            print(f"⚠️ Invalid editor response: {str(e)} - Defaulting to edit stage")
            return update_state(state, {"current_stage": "edit"})

    return state