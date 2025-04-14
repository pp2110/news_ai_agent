import os
from typing import TypedDict, Annotated
import json
from langchain_community.tools import DuckDuckGoSearchResults as DDGS
from langchain_community.utilities import DuckDuckGoSearchAPIWrapper
from langgraph.graph import Graph,StateGraph, END
from langchain_core.messages import HumanMessage, AIMessage
from langchain_groq import ChatGroq
import dotenv
from IPython.display import Image
import re
import operator
from langchain_core.messages import AnyMessage
# Load environment variables
dotenv.load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

wrapper = DuckDuckGoSearchAPIWrapper(time="w", max_results=15)
tool = DDGS(backend="news",api_wrapper=wrapper)
print(type(tool))
print(tool.name)

class AgentState(TypedDict):
    topic: str
    search_results: list[dict]
    news_summary: str
    messages: Annotated[list[AnyMessage], operator.add]

class Agent:
    def __init__(self,model,tools):
        graph = StateGraph(AgentState)
        graph.add_node("llm",self.search_news)
        graph.add_node("search_news",self.take_action)
        graph.add_node("news_reporter",self.news_reporter)
        graph.set_entry_point("llm")
        graph.add_conditional_edges(
            "llm",
            self.have_news,
            {True: "news_reporter",False: "search_news"}
        )
        graph.add_edge("search_news","llm")
        graph.add_edge("news_reporter",END)
#         graph.add_conditional_edges(
#             "news_editor",
#             self.exist_action,
#             {True: "news_reporter",False:END}
#         )
        self.graph = graph.compile()
        self.tools = {t.name: t for t in tools}
        self.model = model.bind_tools(tools)
    
    def have_news(self, state: AgentState) -> bool:
        print("Inside condition Result is ",bool(state['search_results']))
        return bool(state['search_results'])  
    
    def news_reporter(self,state: AgentState) -> AgentState:
    # """Search news using DuckDuckGo"""
        print("inside news reporter")

        # Check if search_results are empty
        if not state['search_results']:
            print("No search results found. Returning empty news summary.")
            state['news_summary'] = "No relevant news found."
            return state

        prompt = f"""You are an innovative and dynamic {state['topic']} news reporter.
        Based on the following search results, generate a news summary:

        {json.dumps(state['search_results'], indent=2)}

        Provide your response in the proper JSON format:
        {{
            "title": "News headline",
            "summary": "Brief summary of the news",
            "source": "Source name",
            "url": "Article URL",
            "image_url": "Image URL for the article"
        }}"""

        results = self.model.invoke(prompt)
        print("news reporter output", results)
        
        state['news_summary'] = results
        return state

    
    def search_news(self,state: AgentState) -> AgentState:
    # """Search news using DuckDuckGo"""
        print("inside search news")
        prompt = f"You have to go to web search and have to find out top 10 latest news for the \"{state['topic']}\""
        results = self.model.invoke(prompt)
        print("search news output",results)
        state['messages'].append(results)
        return state

    def take_action(self,state: AgentState) -> AgentState:
        tool_calls = state['messages'][-1].tool_calls
        results = []
        
        for t in tool_calls:
            print(f"calling {t}")
            result = self.tools[t['name']].invoke(t['args'])
            print(f"Result from tool: {result}")  # Debugging output
            
            # Ensure tool result is in list form and properly structured
            if isinstance(result, list):
                results.extend(result)  # Append all results
            else:
                results.append(result)  # Ensure single result is added
        
        print("Back to model")
        print(results)
        state['search_results'] = results
        return state


model = ChatGroq(
        groq_api_key=GROQ_API_KEY, 
        model_name='llama3-8b-8192'
    )
abot = Agent(model=model,tools=[tool])

result = abot.graph.invoke({
    "topic": "deepseek",
    "search_results": [],
    "news_summary": "",
    "messages": []
})
print(result)
    # with DDGS() as ddgs:
    #     results = list(ddgs.news(
    #         keywords=state['topic'],
    #         max_results=15,
    #         timelimit='w'
    #     ))
    # state['search_results'] = results
    # return state


# # def parse_news_summary(summary_str):
# #     # Remove code block markers and strip whitespace
# #     cleaned_str = summary_str.strip('`\n')
# #     print(type(cleaned_str))
# #     # Parse the JSON string
# #     try:
# #         # news_list = json.loads(cleaned_str)
# #         news_list = json.loads(re.search(r'\[.*\]', cleaned_str, re.DOTALL).group())
# #         return news_list
# #     except json.JSONDecodeError as e:
# #         # Fallback parsing if direct JSON parsing fails
# #         print(f"JSON parsing error: {e}")
# #         return []

# def parse_news_summary(summary_str):
#     try:
#         # Use non-greedy match with multiline support
#         news_list = json.loads(re.search(r'\[.*?\]', summary_str, re.DOTALL).group())
#         return news_list
#     except Exception as e:
#         print(f"Parsing error: {e}")
#         return []
    
# def create_news_summary(state: AgentState) -> AgentState:
#     """Generate news summary using Groq"""
#     chat = ChatGroq(
#         groq_api_key=GROQ_API_KEY, 
#         model_name='llama3-8b-8192'
#     )
    
#     formatted_results = [
#         {
#             'title': result.get('title', ''),
#             'body': result.get('body', ''),
#             'url': result.get('url', ''),
#             'date': result.get('date', ''),
#             'image': result.get('image', '')
#         }
#         for result in state['search_results']
#     ]
    
#     prompt = f"""Create a top 10 news highlights for the topic: {state['topic']}
#     Based on these search results: {json.dumps(formatted_results)}
#     Return a JSON in the following JSON format:
#     [
#         {{
#             "headline": "News headline",
#             "summary": "Brief summary of the news",
#             "source": "Source name",
#             "url": "Article URL",
#             "image_url": "Image URL for the article"
#         }}
#     ]
#     Ensure the response is a valid JSON array following this structure.
#     Just give me the list and no any extra text to be added"""
    
#     response = chat.invoke(prompt)
#     state["news_summary"] = json.dumps(parse_news_summary(response.content))
#     return state

# def create_workflow():
#     """Create and configure the workflow graph"""
#     workflow = Graph()
#     workflow.set_entry_point("search")
#     workflow.add_node("search", search_news)
#     workflow.add_node("summarize", create_news_summary)
#     workflow.add_edge("search", "summarize")
#     workflow.add_edge("summarize", END)
#     return workflow.compile()

# def run_news_agent(topic: str):
#     """Execute the news agent workflow"""
#     state = AgentState(
#         topic=topic,
#         search_results=[],
#         news_summary=[],
#         messages=[]
#     )
#     workflow = create_workflow()
#     final_state = workflow.invoke(state)
#     return final_state