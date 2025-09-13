from tavily import TavilyClient
import streamlit as st
from langchain.tools import tool
# Init Tavily client (make sure TAVILY_API_KEY is in st.secrets or env)
tavily = TavilyClient(api_key=st.secrets["TAVILY_API_KEY"])
from datetime import datetime

@tool
def fetch_salary_trends():
    """
    Use Tavily to fetch current salary increment / trend info.
    """
    query = f"Current salary increment trends for the given industry in the given location, India as of {datetime.now()} for the given candidate's expperiecne and skills."
    results = tavily.search(query=query, max_results=3)
    
    # Collect snippets
    trend_info = "\n".join([r["content"] for r in results["results"]])
    return trend_info if trend_info else "No live salary trend data found."
