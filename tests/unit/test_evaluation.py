"""Unit tests for the LLM-as-a-Judge evaluation script."""

from unittest.mock import AsyncMock, MagicMock

import pytest

from src.gateway.models import InferenceResponse, TokenUsage
from tests.evaluation.evaluate_agent import PostEvaluator


@pytest.fixture
def mock_gateway():
    """Create a mock Inference Gateway for evaluation."""
    gateway = MagicMock()
    gateway.generate = AsyncMock(
        return_value=InferenceResponse(
            content="""
        {
          "clarity": 9,
          "tone": 8,
          "length": 9,
          "clarity_feedback": "Very clear and well-structured",
          "tone_feedback": "Professional and engaging",
          "length_feedback": "Appropriate length for LinkedIn",
          "overall_feedback": "Excellent post with good structure"
        }
        """,
            model="mock-model",
            usage=TokenUsage(prompt_tokens=200, completion_tokens=100, total_tokens=300),
        )
    )
    return gateway


@pytest.mark.asyncio
async def test_evaluate_post(mock_gateway):
    """Test post evaluation."""
    evaluator = PostEvaluator(gateway=mock_gateway, pass_threshold=8.0)

    content = "This is a test LinkedIn post about AI."
    topic = "artificial intelligence"

    evaluation = await evaluator.evaluate_post(content, topic)

    assert "clarity" in evaluation
    assert "tone" in evaluation
    assert "length" in evaluation
    assert "average_score" in evaluation
    assert "passed" in evaluation

    # Check that scores are in valid range
    assert 1 <= evaluation["clarity"] <= 10
    assert 1 <= evaluation["tone"] <= 10
    assert 1 <= evaluation["length"] <= 10


@pytest.mark.asyncio
async def test_evaluate_post_passing(mock_gateway):
    """Test that high-quality post passes evaluation."""
    evaluator = PostEvaluator(gateway=mock_gateway, pass_threshold=8.0)

    evaluation = await evaluator.evaluate_post("Test content", "test topic")

    # With scores of 9, 8, 9, average is 8.67, should pass
    assert evaluation["passed"] is True
    assert evaluation["average_score"] >= 8.0


@pytest.mark.asyncio
async def test_evaluate_post_failing():
    """Test that low-quality post fails evaluation."""
    gateway = MagicMock()
    gateway.generate = AsyncMock(
        return_value=InferenceResponse(
            content="""
        {
          "clarity": 6,
          "tone": 5,
          "length": 7,
          "clarity_feedback": "Somewhat unclear",
          "tone_feedback": "Tone could be more professional",
          "length_feedback": "Acceptable length",
          "overall_feedback": "Needs improvement"
        }
        """,
            model="mock-model",
            usage=TokenUsage(prompt_tokens=200, completion_tokens=100, total_tokens=300),
        )
    )

    evaluator = PostEvaluator(gateway=gateway, pass_threshold=8.0)
    evaluation = await evaluator.evaluate_post("Test content", "test topic")

    # With scores of 6, 5, 7, average is 6.0, should fail
    assert evaluation["passed"] is False
    assert evaluation["average_score"] < 8.0


def test_create_evaluation_prompt(mock_gateway):
    """Test evaluation prompt creation."""
    evaluator = PostEvaluator(gateway=mock_gateway)

    content = "Test post content"
    topic = "test topic"

    prompt = evaluator._create_evaluation_prompt(content, topic)

    assert "test topic" in prompt
    assert "Test post content" in prompt
    assert "CLARITY" in prompt
    assert "TONE" in prompt
    assert "LENGTH" in prompt
    assert "JSON" in prompt


def test_parse_evaluation_valid_json(mock_gateway):
    """Test parsing valid evaluation JSON."""
    evaluator = PostEvaluator(gateway=mock_gateway)

    response = """
    Some text before
    {
      "clarity": 8,
      "tone": 9,
      "length": 7,
      "clarity_feedback": "Good",
      "tone_feedback": "Great",
      "length_feedback": "Acceptable"
    }
    Some text after
    """

    evaluation = evaluator._parse_evaluation(response)

    assert evaluation["clarity"] == 8
    assert evaluation["tone"] == 9
    assert evaluation["length"] == 7


def test_parse_evaluation_invalid_json(mock_gateway):
    """Test parsing invalid evaluation response."""
    evaluator = PostEvaluator(gateway=mock_gateway)

    response = "This is not valid JSON"

    evaluation = evaluator._parse_evaluation(response)

    # Should return fallback scores
    assert "clarity" in evaluation
    assert "tone" in evaluation
    assert "length" in evaluation
    assert all(isinstance(evaluation[k], int) for k in ["clarity", "tone", "length"])
