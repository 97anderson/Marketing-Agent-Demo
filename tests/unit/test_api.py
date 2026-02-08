"""Unit tests for the FastAPI application."""

from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from src.agents.marketing.api import app
from src.agents.marketing.models import GeneratedPost
from src.gateway.models import TokenUsage


@pytest.fixture
def mock_agent():
    """Create a mock Marketing Agent."""
    agent = MagicMock()

    # Mock generate_post
    agent.generate_post = AsyncMock(return_value=GeneratedPost(
        id="test-post-id",
        topic="test topic",
        content="This is a test LinkedIn post.",
        tone="professional",
        usage=TokenUsage(
            prompt_tokens=100,
            completion_tokens=50,
            total_tokens=150
        ),
        created_at=datetime.utcnow()
    ))

    # Mock get_history
    agent.get_history = MagicMock(return_value=[
        GeneratedPost(
            id="post-1",
            topic="topic 1",
            content="Content 1",
            tone="professional",
            usage=TokenUsage(
                prompt_tokens=100,
                completion_tokens=50,
                total_tokens=150
            ),
            created_at=datetime.utcnow()
        )
    ])

    return agent


@pytest.fixture
def client(mock_agent):
    """Create a test client with mocked agent."""
    with patch("src.agents.marketing.api.agent", mock_agent):
        with TestClient(app) as client:
            yield client


def test_root_endpoint(client):
    """Test the root endpoint."""
    response = client.get("/")

    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "version" in data


def test_health_check(client):
    """Test the health check endpoint."""
    response = client.get("/health")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "service" in data
    assert "environment" in data


def test_generate_post_endpoint(client, mock_agent):
    """Test the generate post endpoint."""
    request_data = {
        "topic": "artificial intelligence",
        "tone": "professional",
        "max_length": 500
    }

    response = client.post("/generate", json=request_data)

    assert response.status_code == 201
    data = response.json()

    assert "post" in data
    assert data["post"]["topic"] == "test topic"
    assert data["post"]["content"] is not None
    assert "usage" in data["post"]

    # Verify mock was called
    mock_agent.generate_post.assert_called_once()


def test_generate_post_invalid_data(client):
    """Test generate post with invalid data."""
    request_data = {
        "topic": "",  # Empty topic should fail validation
        "tone": "professional"
    }

    response = client.post("/generate", json=request_data)

    # Should return validation error
    assert response.status_code == 422


def test_get_history_endpoint(client, mock_agent):
    """Test the get history endpoint."""
    response = client.get("/history?limit=10")

    assert response.status_code == 200
    data = response.json()

    assert "posts" in data
    assert "total" in data
    assert len(data["posts"]) > 0

    # Verify mock was called
    mock_agent.get_history.assert_called_once_with(limit=10)


def test_metrics_endpoint(client, mock_agent):
    """Test the metrics endpoint."""
    response = client.get("/metrics")

    assert response.status_code == 200
    data = response.json()

    assert "total_posts_generated" in data
    assert "total_tokens_used" in data
    assert "status" in data


def test_generate_post_error_handling(client, mock_agent):
    """Test error handling in generate post."""
    # Make the mock raise an exception
    mock_agent.generate_post.side_effect = Exception("Test error")

    request_data = {
        "topic": "test topic",
        "tone": "professional"
    }

    response = client.post("/generate", json=request_data)

    assert response.status_code == 500
    data = response.json()
    assert "detail" in data
