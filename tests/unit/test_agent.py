"""Unit tests for the Marketing Agent."""

from datetime import datetime
from unittest.mock import AsyncMock, MagicMock

import pytest

from src.agents.marketing.agent import MarketingAgent
from src.agents.marketing.models import (
    GeneratedPost,
    GeneratePostRequest,
)
from src.agents.marketing.tools import (
    WebSearchResult,
    WebSearchTool,
)
from src.gateway.models import (
    InferenceResponse,
    TokenUsage,
)


@pytest.fixture
def mock_gateway():
    """Create a mock Inference Gateway."""
    gateway = MagicMock()
    gateway.generate = AsyncMock(
        return_value=InferenceResponse(
            content="This is a test LinkedIn post about AI and technology.",
            model="mock-model",
            usage=TokenUsage(prompt_tokens=100, completion_tokens=50, total_tokens=150),
        )
    )
    return gateway


@pytest.fixture
def mock_database():
    """Create a mock Vector Database."""
    database = MagicMock()
    database.add_document = MagicMock()
    database.get_all_documents = MagicMock(
        return_value={"ids": [], "documents": [], "metadatas": []}
    )
    return database


@pytest.fixture
def marketing_agent(mock_gateway, mock_database):
    """Create a Marketing Agent with mocked dependencies."""
    return MarketingAgent(gateway=mock_gateway, database=mock_database)


@pytest.mark.asyncio
async def test_web_search_tool():
    """Test WebSearchTool returns results."""
    tool = WebSearchTool()

    results = await tool.search("artificial intelligence")

    assert len(results) > 0
    assert all(isinstance(r, WebSearchResult) for r in results)
    assert all(r.title and r.snippet and r.url for r in results)


@pytest.mark.asyncio
async def test_generate_post(marketing_agent, mock_gateway):
    """Test post generation."""
    request = GeneratePostRequest(
        topic="artificial intelligence", tone="professional", max_length=500
    )

    post = await marketing_agent.generate_post(request)

    assert isinstance(post, GeneratedPost)
    assert post.topic == "artificial intelligence"
    assert post.tone == "professional"
    assert post.content is not None
    assert len(post.content) > 0
    assert post.usage.total_tokens > 0
    assert post.id is not None

    # Verify gateway was called
    mock_gateway.generate.assert_called_once()


@pytest.mark.asyncio
async def test_generate_post_saves_to_memory(marketing_agent, mock_database):
    """Test that generated posts are saved to ChromaDB."""
    request = GeneratePostRequest(topic="machine learning", tone="enthusiastic")

    post = await marketing_agent.generate_post(request)

    # Verify database was called
    mock_database.add_document.assert_called_once()

    # Check the call arguments
    call_args = mock_database.add_document.call_args
    assert call_args.kwargs["document_id"] == post.id
    assert "topic" in call_args.kwargs["metadata"]


@pytest.mark.asyncio
async def test_get_history_empty(marketing_agent, mock_database):
    """Test getting history when no posts exist."""
    mock_database.get_all_documents.return_value = {"ids": [], "documents": [], "metadatas": []}

    history = marketing_agent.get_history(limit=10)

    assert len(history) == 0


@pytest.mark.asyncio
async def test_get_history_with_posts(marketing_agent, mock_database):
    """Test getting history with existing posts."""
    mock_database.get_all_documents.return_value = {
        "ids": ["post-1", "post-2"],
        "documents": ["First post content", "Second post content"],
        "metadatas": [
            {
                "topic": "AI",
                "tone": "professional",
                "created_at": datetime.utcnow().isoformat(),
                "prompt_tokens": 100,
                "completion_tokens": 50,
                "total_tokens": 150,
            },
            {
                "topic": "ML",
                "tone": "casual",
                "created_at": datetime.utcnow().isoformat(),
                "prompt_tokens": 120,
                "completion_tokens": 60,
                "total_tokens": 180,
            },
        ],
    }

    history = marketing_agent.get_history(limit=10)

    assert len(history) == 2
    assert all(isinstance(post, GeneratedPost) for post in history)
    assert history[0].id == "post-1"
    assert history[1].id == "post-2"


def test_build_context(marketing_agent):
    """Test context building from search results."""
    search_results = [
        WebSearchResult(
            title="Test Title 1", snippet="Test snippet 1", url="https://example.com/1"
        ),
        WebSearchResult(
            title="Test Title 2", snippet="Test snippet 2", url="https://example.com/2"
        ),
    ]

    context = marketing_agent._build_context(search_results)

    assert "Test Title 1" in context
    assert "Test Title 2" in context
    assert "Test snippet 1" in context
    assert "Test snippet 2" in context
    assert "https://example.com/1" in context
    assert "https://example.com/2" in context


def test_create_prompt(marketing_agent):
    """Test prompt creation."""
    prompt = marketing_agent._create_prompt(
        topic="AI", context="Test context about AI", tone="professional", max_length=500
    )

    assert "AI" in prompt
    assert "Test context about AI" in prompt
    assert "professional" in prompt
    assert "500" in prompt
    assert "LinkedIn" in prompt
