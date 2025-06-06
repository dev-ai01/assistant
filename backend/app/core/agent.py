import requests
import html
import re
import json
import trafilatura
from typing import Optional, Any, Dict, List
import logging
from langchain_openai import ChatOpenAI
import os
from dotenv import load_dotenv, find_dotenv
from groq import Groq
from app.core.tools import search_serper, extract_json_block, map_to_schema, summarize_text, scrape_and_clean, summarize_or_filter_json, json_to_docx
from openai import OpenAI
from typing import TypedDict, List, Dict, Optional
from langgraph.graph import StateGraph

load_dotenv(find_dotenv())


class AgentState(TypedDict):
    query: str
    urls: Optional[List[str]]
    scraped_texts: Optional[List[str]]
    summaries: Optional[List[str]]
    mapped_results: Optional[List[Dict[str, Any]]]

def search_node(state: AgentState) -> AgentState:
    """Search for URLs based on the query."""
    try:
        urls = search_serper(state["query"], SERPER_API_KEY)
        return {**state, "urls": urls}
    except Exception as e:
        logging.error(f"Search node failed: {e}")
        return state

def scrape_node(state: AgentState) -> AgentState:
    """Scrape and clean text from each URL."""
    if not state.get("urls"):
        return state
    scraped_texts = [scrape_and_clean(url) for url in state["urls"]]
    return {**state, "scraped_texts": scraped_texts}

def summarize_node(state: AgentState) -> AgentState:
    """Summarize each scraped text."""
    if not state.get("scraped_texts"):
        return state

    combined_text = "\n\n".join(state["scraped_texts"])
    summary = summarize_text(combined_text, state["query"])
    return {**state, "summaries": [summary]} 

def map_to_schema_node(state: AgentState) -> AgentState:
    """Map each summary to a structured schema."""
    if not state.get("summaries"):
        return state

    summary = state["summaries"][0]
    mapped = map_to_schema(summary, state["query"])
    return {**state, "mapped_results": [mapped]}

# def extract_json_node(state: AgentState) -> AgentState:
#     """Extract JSON block from each mapped result."""
#     if not state.get("mapped_results"):
#         return state
#     final_json = {"results": [extract_json_block(res) for res in state["mapped_results"]]}
#     return {**state, "final_json": final_json}


def summarize_filter_node(state: AgentState) -> AgentState:
    """
    Summarizes or filters the final_json in the state based on the original query.
    """
    if not state.get("final_json"):
        return state

    user_query = state["query"]
    summarized_json = summarize_or_filter_json(
        state["final_json"],
        user_query,
        summarize=True,
        model="meta-llama/llama-guard-4-12b"
    )
    return {**state, "filtered_json": summarized_json}

def run_agent(query: str) -> Dict[str, Any]:
    """Run the sequential agent pipeline."""
    workflow = StateGraph(AgentState)
    workflow.add_node("search", search_node)
    workflow.add_node("scrape", scrape_node)
    workflow.add_node("summarize", summarize_node)
    workflow.add_node("map_to_schema", map_to_schema_node)
    # workflow.add_node("extract_json", extract_json_node)
    # workflow.add_node("summarize_json", summarize_filter_node)
    workflow.add_edge("search", "scrape")
    workflow.add_edge("scrape", "summarize")
    workflow.add_edge("summarize", "map_to_schema")
    # workflow.add_edge("map_to_schema", "extract_json")
    # workflow.add_edge("extract_json", "summarize_json")
    workflow.set_entry_point("search")
    workflow.set_finish_point("map_to_schema")

    app = workflow.compile()
    state = {"query": query}
    result = app.invoke(state)
    if result:
        file_name = f"{query.replace(' ', '_')}.docx"
        file_path = os.path.join("app", "static", "reports", file_name)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        json_to_docx(result, query, file_path)
        return result
    else:
        return {
            "data": None,
            "docx_link": None
        }


# if __name__ == "__main__":

#     user_query = "recent fundings of openai and gemini"
#     try:
#         result = run_agent(user_query)
#         if not result:
#             print("No results to display.")
#         else:
#             json_to_docx(result, user_query, "report2.docx")
#             print(f"[INFO]: Saved the docx successfully!")
#     except Exception as e:
#         print(f"Error: {e}")

