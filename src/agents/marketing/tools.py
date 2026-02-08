"""Marketing Agent Tools.

This module implements the tools available to the Marketing Agent.
"""

import logging

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class WebSearchResult(BaseModel):
    """Result from a web search.

    Attributes:
        title: Title of the search result.
        snippet: Brief snippet of the content.
        url: URL of the source.
    """

    title: str = Field(..., description="Title of the search result")
    snippet: str = Field(..., description="Brief snippet of the content")
    url: str = Field(..., description="URL of the source")


class WebSearchTool:
    """Simulated web search tool for the Marketing Agent.

    This tool simulates searching the web for information about a topic.
    In production, this would integrate with real search APIs.
    """

    name: str = "web_search"
    description: str = "Search the web for information about a specific topic"

    def __init__(self):
        """Initialize the web search tool."""
        logger.info("WebSearchTool initialized (simulated mode)")

    async def search(self, query: str) -> list[WebSearchResult]:
        """Perform a simulated web search.

        Args:
            query: The search query.

        Returns:
            List of search results with titles, snippets, and URLs.
        """
        logger.info(f"WebSearchTool: Searching for '{query}'")

        # Simulated search results based on the query
        results = self._get_mock_results(query)

        logger.info(f"WebSearchTool: Found {len(results)} results")
        return results

    def _get_mock_results(self, query: str) -> list[WebSearchResult]:
        """Generate mock search results.

        Args:
            query: The search query.

        Returns:
            List of mock search results.
        """
        # Create contextually relevant mock data
        return [
            WebSearchResult(
                title=f"Understanding {query}: A Comprehensive Guide",
                snippet=(
                    f"{query} is revolutionizing the industry with innovative approaches "
                    "and cutting-edge technologies. Recent developments show significant "
                    "growth and adoption across multiple sectors."
                ),
                url=f"https://example.com/guide-{query.replace(' ', '-').lower()}",
            ),
            WebSearchResult(
                title=f"Top 10 Trends in {query} for 2026",
                snippet=(
                    f"The landscape of {query} is evolving rapidly. Industry experts "
                    "predict major advancements in the coming months, with key players "
                    "investing heavily in research and development."
                ),
                url=f"https://example.com/trends-{query.replace(' ', '-').lower()}",
            ),
            WebSearchResult(
                title=f"How {query} is Transforming Business Operations",
                snippet=(
                    f"Companies are leveraging {query} to streamline workflows, "
                    "improve efficiency, and drive innovation. Case studies demonstrate "
                    "ROI improvements of up to 40% in early adopters."
                ),
                url=f"https://example.com/business-{query.replace(' ', '-').lower()}",
            ),
        ]

    def get_tool_description(self) -> dict[str, str]:
        """Get the tool description for agent configuration.

        Returns:
            Dictionary with tool name and description.
        """
        return {"name": self.name, "description": self.description}
