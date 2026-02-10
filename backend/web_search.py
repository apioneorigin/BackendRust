"""
Web search providers for the Reality Transformer pipeline.

Supports:
  - tavily: Dedicated search API (~$0.005/search), returns structured LLM-ready results
  - llm: Built-in web search via Claude/OpenAI tools (more expensive, but integrated)

Usage:
    from web_search import tavily_search

    results = await tavily_search("NVIDIA market position 2025", max_results=5)
    # Returns list of {title, url, content, score}
"""

import os
from typing import Optional

import httpx
from logging_config import api_logger

TAVILY_API_KEY = os.getenv("TAVILY_API_KEY", "")
TAVILY_SEARCH_URL = "https://api.tavily.com/search"


async def tavily_search(
    query: str,
    *,
    max_results: int = 5,
    search_depth: str = "advanced",
    include_answer: bool = True,
) -> dict:
    """
    Search using Tavily API. Returns structured results optimized for LLM consumption.

    Args:
        query: Search query string
        max_results: Number of results (1-10)
        search_depth: "basic" (fast) or "advanced" (deeper extraction)
        include_answer: Include Tavily's AI-generated answer summary

    Returns:
        {
            "answer": "AI-generated summary of search results",
            "results": [{"title": ..., "url": ..., "content": ..., "score": ...}],
            "query": "original query"
        }
    """
    if not TAVILY_API_KEY:
        raise ValueError("TAVILY_API_KEY environment variable is not set")

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            TAVILY_SEARCH_URL,
            json={
                "api_key": TAVILY_API_KEY,
                "query": query,
                "max_results": max_results,
                "search_depth": search_depth,
                "include_answer": include_answer,
            },
        )

        if response.status_code != 200:
            api_logger.error(f"[TAVILY] API error: {response.status_code} - {response.text[:500]}")
            raise Exception(f"Tavily API error: {response.status_code}")

        data = response.json()

        return {
            "answer": data.get("answer", ""),
            "results": [
                {
                    "title": r.get("title", ""),
                    "url": r.get("url", ""),
                    "content": r.get("content", ""),
                    "score": r.get("score", 0),
                }
                for r in data.get("results", [])
            ],
            "query": query,
        }


async def tavily_multi_search(queries: list[str], max_results_per_query: int = 3) -> list[dict]:
    """
    Run multiple Tavily searches concurrently.

    Args:
        queries: List of search query strings
        max_results_per_query: Results per query

    Returns:
        List of search result dicts (same format as tavily_search)
    """
    import asyncio

    tasks = [
        tavily_search(q, max_results=max_results_per_query, search_depth="basic")
        for q in queries
    ]

    results = []
    for coro in asyncio.as_completed(tasks):
        try:
            result = await coro
            results.append(result)
        except Exception as e:
            api_logger.warning(f"[TAVILY] Search failed: {e}")

    return results


def format_tavily_for_llm(search_results: list[dict]) -> str:
    """
    Format Tavily search results into a context string for LLM prompts.

    Args:
        search_results: List of results from tavily_search or tavily_multi_search

    Returns:
        Formatted string ready to inject into LLM context
    """
    sections = []

    for sr in search_results:
        query = sr.get("query", "")
        answer = sr.get("answer", "")
        results = sr.get("results", [])

        section = f"=== Web Research: {query} ===\n"
        if answer:
            section += f"Summary: {answer}\n\n"

        for i, r in enumerate(results, 1):
            title = r.get("title", "")
            url = r.get("url", "")
            content = r.get("content", "")
            section += f"[{i}] {title}\n    {url}\n    {content[:500]}\n\n"

        sections.append(section)

    return "\n".join(sections)
