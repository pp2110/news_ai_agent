import os
from typing import TypedDict, Sequence
import json
from duckduckgo_search import DDGS
from langgraph.graph import Graph, END
from langchain_core.messages import HumanMessage, AIMessage
from langchain_groq import ChatGroq
import dotenv
import re
# Load environment variables
dotenv.load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

class AgentState(TypedDict):
    topic: str
    search_results: list[dict]
    news_summary: str
    messages: Sequence[HumanMessage | AIMessage]

def search_news(state: AgentState) -> AgentState:
    """Search news using DuckDuckGo"""
    with DDGS() as ddgs:
        results = list(ddgs.news(
            keywords=state['topic'],
            max_results=15,
            timelimit='w'
        ))
    state['search_results'] = results
    return state


# def parse_news_summary(summary_str):
#     # Remove code block markers and strip whitespace
#     cleaned_str = summary_str.strip('`\n')
#     print(type(cleaned_str))
#     # Parse the JSON string
#     try:
#         # news_list = json.loads(cleaned_str)
#         news_list = json.loads(re.search(r'\[.*\]', cleaned_str, re.DOTALL).group())
#         return news_list
#     except json.JSONDecodeError as e:
#         # Fallback parsing if direct JSON parsing fails
#         print(f"JSON parsing error: {e}")
#         return []

def parse_news_summary(summary_str):
    try:
        # Use non-greedy match with multiline support
        news_list = json.loads(re.search(r'\[.*?\]', summary_str, re.DOTALL).group())
        return news_list
    except Exception as e:
        print(f"Parsing error: {e}")
        return []
    
def create_news_summary(state: AgentState) -> AgentState:
    """Generate news summary using Groq"""
    chat = ChatGroq(
        groq_api_key=GROQ_API_KEY, 
        model_name='llama3-8b-8192'
    )
    
    formatted_results = [
        {
            'title': result.get('title', ''),
            'body': result.get('body', ''),
            'url': result.get('url', ''),
            'date': result.get('date', ''),
            'image': result.get('image', '')
        }
        for result in state['search_results']
    ]
    
    prompt = f"""Create a top 10 news highlights for the topic: {state['topic']}
    Based on these search results: {json.dumps(formatted_results)}
    Return a JSON in the following JSON format:
    [
        {{
            "headline": "News headline",
            "summary": "Brief summary of the news",
            "source": "Source name",
            "url": "Article URL",
            "image_url": "Image URL for the article"
        }}
    ]
    Ensure the response is a valid JSON array following this structure.
    Just give me the list and no any extra text to be added"""
    
    response = chat.invoke(prompt)
    state["news_summary"] = json.dumps(parse_news_summary(response.content))
    return state

def create_workflow():
    """Create and configure the workflow graph"""
    workflow = Graph()
    workflow.set_entry_point("search")
    workflow.add_node("search", search_news)
    workflow.add_node("summarize", create_news_summary)
    workflow.add_edge("search", "summarize")
    workflow.add_edge("summarize", END)
    return workflow.compile()

def run_news_agent(topic: str):
    """Execute the news agent workflow"""
    state = AgentState(
        topic=topic,
        search_results=[],
        news_summary=[],
        messages=[]
    )
    workflow = create_workflow()
    final_state = workflow.invoke(state)
    return final_state