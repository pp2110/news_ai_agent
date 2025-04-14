import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from langgraph.graph import StateGraph, END
from app.core.agents import (
    search_agent, reporter_agent, editor_agent, 
    summarizer_agent, newsroom_editor
)
from app.core.state import NewsroomState

def create_workflow():
    print("into Create Workflow")
    workflow = StateGraph(NewsroomState)
    
    # Add nodes
    workflow.add_node("search", search_agent)
    workflow.add_node("report", reporter_agent)
    workflow.add_node("edit", editor_agent)
    workflow.add_node("summarize", summarizer_agent)
    workflow.add_node("newsroom_editor", newsroom_editor)
    
    workflow.set_entry_point("newsroom_editor")
    
    # Add edges
    workflow.add_conditional_edges(
        "newsroom_editor",
        lambda x: x["current_stage"],
        {
            "search": "search",
            "report": "report",
            "edit": "edit",
            "summarize": "summarize",
            "complete": END
        }
    )
    
    workflow.add_edge("search", "newsroom_editor")
    workflow.add_edge("report", "newsroom_editor")
    workflow.add_edge("edit", "newsroom_editor")
    workflow.add_edge("summarize", "newsroom_editor")
    print("Completed Create Workflow")
    print("="*50)
    return workflow.compile()