from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List

from tavily import TavilyClient

from backend.config import settings

tavily_client = TavilyClient(api_key=settings.TAVILY_API_KEY)


def _search_single_query(query: str, max_results: int) -> str:
    try:
        response = tavily_client.search(
            query=query,
            search_depth="advanced",
            max_results=max_results,
        )

        results = response.get("results", [])

        if not results:
            return f"Query: '{query}'\nNo results found."

        query_context = f"Query: '{query}'\nResults:\n"

        for res in results:
            query_context += (
                f"- Source: {res.get('url')}\n"
                f"  Content: {res.get('content')}\n"
            )

        return query_context

    except Exception as e:
        return f"Query: '{query}'\nError executing search: {str(e)}"


def perform_research(
    queries: List[str],
    max_results_per_query: int = settings.TAVILY_MAX_RESULTS,
) -> str:
    """
    Executes Tavily searches in parallel.
    """

    if not queries:
        return ""

    aggregated_results = []

    max_workers = min(len(queries), 10)

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {
            executor.submit(
                _search_single_query,
                query,
                max_results_per_query,
            ): query
            for query in queries
        }

        for future in as_completed(futures):
            aggregated_results.append(future.result())

    return "\n\n".join(aggregated_results)