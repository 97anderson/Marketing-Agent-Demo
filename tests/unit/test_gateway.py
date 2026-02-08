"""Unit tests for the Inference Gateway."""

from unittest.mock import patch

import pytest

from src.gateway.inference_gateway import InferenceGateway, MockModel
from src.gateway.models import InferenceRequest, InferenceResponse, TokenUsage


@pytest.mark.asyncio
async def test_mock_model_generate():
    """Test MockModel generates valid responses."""
    model = MockModel()

    request = InferenceRequest(
        prompt="Test prompt", model="mock-model", temperature=0.7, max_tokens=500
    )

    response = await model.generate(request)

    assert isinstance(response, InferenceResponse)
    assert response.content is not None
    assert len(response.content) > 0
    assert response.model == "mock-model"
    assert isinstance(response.usage, TokenUsage)
    assert response.usage.total_tokens > 0


@pytest.mark.asyncio
async def test_mock_model_token_calculation():
    """Test MockModel calculates tokens correctly."""
    model = MockModel()

    prompt = "This is a test prompt with several words"
    request = InferenceRequest(prompt=prompt, model="mock-model")

    response = await model.generate(request)

    # Token count should be roughly 2x word count
    expected_prompt_tokens = len(prompt.split()) * 2
    assert response.usage.prompt_tokens == expected_prompt_tokens
    assert response.usage.completion_tokens > 0
    assert response.usage.total_tokens == (
        response.usage.prompt_tokens + response.usage.completion_tokens
    )


@pytest.mark.asyncio
async def test_inference_gateway_with_mock():
    """Test InferenceGateway works with mock model."""
    gateway = InferenceGateway(use_mock=True)

    response = await gateway.generate(
        prompt="Generate a test post", model="gpt-3.5-turbo", temperature=0.7, max_tokens=500
    )

    assert isinstance(response, InferenceResponse)
    assert response.content is not None
    assert response.usage.total_tokens > 0


@pytest.mark.asyncio
async def test_inference_gateway_with_metadata():
    """Test InferenceGateway preserves metadata."""
    gateway = InferenceGateway(use_mock=True)

    metadata = {"agent": "test_agent", "topic": "testing"}

    response = await gateway.generate(prompt="Test prompt", metadata=metadata)

    assert response.metadata == metadata


@pytest.mark.asyncio
async def test_inference_gateway_from_settings():
    """Test InferenceGateway can be created from settings."""
    with patch("src.gateway.inference_gateway.get_settings") as mock_settings:
        mock_settings.return_value.use_mock_model = True
        mock_settings.return_value.openai_api_key = "test-key"

        gateway = InferenceGateway.from_settings()

        assert gateway.use_mock is True
        assert isinstance(gateway.model, MockModel)


def test_openai_model_requires_api_key():
    """Test OpenAIModel raises error without API key."""
    # Should raise ValueError when trying to use real model without key
    # This is caught in the __init__
    with pytest.raises(ValueError):
        InferenceGateway(use_mock=False, api_key=None)
