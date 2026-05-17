import os
from typing import List, Dict
from tavily import TavilyClient
from backend.config import settings

# Initialize the client using your config
tavily_client = TavilyClient(api_key=settings.TAVILY_API_KEY)


def perform_research(queries: List[str], max_results_per_query: int = settings.TAVILY_MAX_RESULTS) -> str:
    """
    Executes multiple search queries and compiles the results into a single context string.
    """
    aggregated_results = []

    for query in queries:
        try:
            # We use the search API to get context directly
            response = tavily_client.search(
                query=query,
                search_depth="advanced",
                max_results=max_results_per_query
            )

            results = response.get("results", [])
            if not results:
                aggregated_results.append(f"Query: '{query}'\nNo results found.")
                continue

            query_context = f"Query: '{query}'\nResults:\n"
            for res in results:
                query_context += f"- Source: {res.get('url')}\n  Content: {res.get('content')}\n"

            aggregated_results.append(query_context)

        except Exception as e:
            aggregated_results.append(f"Query: '{query}'\nError executing search: {str(e)}")

    return "\n\n".join(aggregated_results)