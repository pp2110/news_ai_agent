import os
from typing import TypedDict, Sequence, List, Dict, Optional
import json
from langgraph.graph import Graph, END
from langchain_core.messages import HumanMessage, AIMessage
from langchain_groq import ChatGroq
from langchain.tools import Tool
from langchain.agents import AgentExecutor, create_structured_chat_agent
from datetime import datetime, timedelta
from gnews import GNews
import dotenv
import re
from pydantic import BaseModel, Field

# Load environment variables
dotenv.load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

class AgentState(TypedDict):
    topic: str
    search_results: list[dict]
    news_summary: str
    reporter_content: str
    final_content: str
    messages: Sequence[HumanMessage | AIMessage]

class NewsSearchInput(BaseModel):
    """Input schema for news search"""
    query: str = Field(..., description="The search query for news articles")
    max_results: int = Field(default=15, description="Maximum number of results to return")

class NewsSearchTool:
    """News search tool using Google News API"""
    
    def __init__(self):
        self.google_news = GNews(
            language='en',
            country='US',
            period='7d',
            max_results=15,
            exclude_websites=['reddit.com', 'youtube.com']
        )
    
    def search(self, query: str) -> List[Dict]:
        """Search news using Google News API"""
        try:
            results = self.google_news.get_news(query)
            return [
                {
                    'title': article.get('title', ''),
                    'body': article.get('description', ''),
                    'url': article.get('url', ''),
                    'date': article.get('published date', ''),
                    'image': article.get('image', ''),
                    'publisher': article.get('publisher', {}).get('name', '')
                }
                for article in results
            ]
        except Exception as e:
            print(f"Google News search error: {e}")
            return []

def setup_tools() -> List[Tool]:
    """Set up tools for the agent"""
    news_tool = NewsSearchTool()
    
    return [
        Tool(
            name="search_news",
            description="Search for recent news articles on a specific topic",
            func=news_tool.search,
            args_schema=NewsSearchInput
        )
    ]

def setup_agent(tools: List[Tool]) -> AgentExecutor:
    """Set up the agent with tools"""
    llm = ChatGroq(
        groq_api_key=GROQ_API_KEY,
        model_name='llama3-8b-8192',
        temperature=0.7
    )
    
    agent = create_structured_chat_agent(llm, tools, """You are a news research assistant. Your task is to:
    1. Search for relevant news using the search_news tool
    2. Analyze and summarize the findings
    3. Present the information in a clear and organized way
    Remember to:
    - Use the search_news tool effectively
    - Focus on recent and relevant information
    - Provide accurate summaries
    """)
    
    return AgentExecutor(agent=agent, tools=tools, verbose=True)

def process_with_agent(state: AgentState) -> AgentState:
    """Process news search using agent"""
    tools = setup_tools()
    agent_executor = setup_agent(tools)
    
    # Create the agent task
    task = f"""Research and collect news articles about {state['topic']}. 
    Follow these steps:
    1. Search for relevant news articles
    2. Collect and organize the results
    3. Return the results in a structured format
    
    Return the information in this format:
    [
        {{
            "headline": "News headline",
            "summary": "Brief summary",
            "source": "Source name",
            "url": "Article URL",
            "image_url": "Image URL"
        }}
    ]"""
    
    # Execute agent
    result = agent_executor.invoke({"input": task})
    state["search_results"] = json.loads(result["output"])
    return state

def news_reporter(state: AgentState) -> AgentState:
    """Generate detailed news report using Groq"""
    chat = ChatGroq(
        groq_api_key=GROQ_API_KEY,
        model_name='llama3-8b-8192'
    )
    
    reporter_prompt = f"""You are an innovative and dynamic {state['topic']} news reporter, dedicated to transforming traditional news delivery into an engaging and enriching experience. Drawing from diverse and credible sources, you provide unbiased interpretations, ensuring readers gain quick access to accurate, insightful, and comprehensive information.

Based on these news items, create a comprehensive news report:
{json.dumps(state['search_results'], indent=2)}

Create a well-structured report that includes:
1. An engaging introduction
2. Detailed coverage of major developments
3. Analysis of trends and implications
4. Supporting quotes and data where relevant
5. A conclusion that ties everything together

Format the report in markdown for better readability."""

    response = chat.invoke(reporter_prompt)
    state["reporter_content"] = response.content
    return state

def news_editor(state: AgentState) -> AgentState:
    """Edit and refine the news report using Groq"""
    chat = ChatGroq(
        groq_api_key=GROQ_API_KEY,
        model_name='llama3-8b-8192'
    )
    
    editor_prompt = f"""You are a meticulous and creative News Editor with a keen eye for detail. Your role is to refine and elevate news articles while ensuring clarity, accuracy, and impartiality.

Please review and edit the following news report:

{state['reporter_content']}

Focus on:
1. Improving clarity and flow
2. Enhancing readability
3. Ensuring factual accuracy
4. Maintaining consistent tone
5. Adding necessary context where needed
6. Optimizing structure and organization

Return the edited version in markdown format."""

    response = chat.invoke(editor_prompt)
    state["final_content"] = response.content
    return state

def create_workflow():
    """Create and configure the workflow graph"""
    workflow = Graph()
    
    # Set the entry point
    workflow.set_entry_point("search")
    
    # Add nodes
    workflow.add_node("search", process_with_agent)
    workflow.add_node("reporter", news_reporter)
    workflow.add_node("editor", news_editor)
    
    # Add edges
    workflow.add_edge("search", "reporter")
    workflow.add_edge("reporter", "editor")
    workflow.add_edge("editor", END)
    
    return workflow.compile()

def run_news_agent(topic: str):
    """Execute the news agent workflow"""
    state = AgentState(
        topic=topic,
        search_results=[],
        news_summary="",
        reporter_content="",
        final_content="",
        messages=[]
    )
    workflow = create_workflow()
    final_state = workflow.invoke(state)
    return final_state