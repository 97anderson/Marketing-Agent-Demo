"""Tests for the multi-agent workflow components."""

import pytest

from src.agents.marketing.critique_agent import CritiqueAgent
from src.agents.marketing.multi_agent_flow import MultiAgentFlow
from src.agents.marketing.planner_agent import PlannerAgent
from src.agents.marketing.writer_agent import WriterAgent
from src.gateway.inference_gateway import InferenceGateway


@pytest.fixture
def mock_gateway():
    """Create a mock gateway for testing."""
    return InferenceGateway(use_mock=True)


@pytest.fixture
def planner_agent(mock_gateway):
    """Create a PlannerAgent instance."""
    return PlannerAgent(mock_gateway)


@pytest.fixture
def writer_agent(mock_gateway):
    """Create a WriterAgent instance."""
    return WriterAgent(mock_gateway)


@pytest.fixture
def critique_agent(mock_gateway):
    """Create a CritiqueAgent instance."""
    return CritiqueAgent(mock_gateway, pass_threshold=8.0)


@pytest.fixture
def multi_agent_flow(mock_gateway):
    """Create a MultiAgentFlow instance."""
    return MultiAgentFlow(
        gateway=mock_gateway,
        critique_threshold=8.0,
        max_rewrites=2,
    )


class TestPlannerAgent:
    """Tests for PlannerAgent."""

    @pytest.mark.asyncio
    async def test_create_outline(self, planner_agent):
        """Test outline creation."""
        outline = await planner_agent.create_outline(
            topic="AI in healthcare",
            context="AI is transforming healthcare diagnostics...",
            tone="professional",
            max_length=500,
        )

        assert isinstance(outline, str)
        assert len(outline) > 0
        # Mock should return outline-like content
        assert "linkedin" in outline.lower() or "post" in outline.lower()

    @pytest.mark.asyncio
    async def test_create_outline_with_brand(self, planner_agent):
        """Test outline creation with brand voice."""
        brand_voice = "Brand Voice: Professional, data-driven, innovative"

        outline = await planner_agent.create_outline(
            topic="AI in healthcare",
            context="AI research shows...",
            brand_voice=brand_voice,
            tone="professional",
            max_length=500,
        )

        assert isinstance(outline, str)
        assert len(outline) > 0


class TestWriterAgent:
    """Tests for WriterAgent."""

    @pytest.mark.asyncio
    async def test_write_post(self, writer_agent):
        """Test post writing."""
        outline = "1. Hook: AI revolution\n2. Points: Benefits\n3. CTA: Learn more"

        content = await writer_agent.write_post(
            topic="AI in healthcare",
            outline=outline,
            tone="professional",
            max_length=500,
        )

        assert isinstance(content, str)
        assert len(content) > 0

    @pytest.mark.asyncio
    async def test_write_post_with_brand(self, writer_agent):
        """Test post writing with brand voice."""
        outline = "1. Hook\n2. Body\n3. CTA"
        brand_voice = "Brand Voice: Innovative, professional"

        content = await writer_agent.write_post(
            topic="AI in healthcare",
            outline=outline,
            brand_voice=brand_voice,
            tone="professional",
            max_length=500,
        )

        assert isinstance(content, str)
        assert len(content) > 0

    @pytest.mark.asyncio
    async def test_rewrite_post(self, writer_agent):
        """Test post rewriting with critique feedback."""
        outline = "1. Hook\n2. Body\n3. CTA"
        feedback = "The post needs more specific examples and data."

        content = await writer_agent.write_post(
            topic="AI in healthcare",
            outline=outline,
            tone="professional",
            max_length=500,
            is_rewrite=True,
            critique_feedback=feedback,
        )

        assert isinstance(content, str)
        assert len(content) > 0


class TestCritiqueAgent:
    """Tests for CritiqueAgent."""

    @pytest.mark.asyncio
    async def test_evaluate_post(self, critique_agent):
        """Test post evaluation."""
        content = """
        🚀 Exciting developments in AI healthcare!

        Machine learning is revolutionizing diagnostics...

        What's your experience with AI in healthcare?

        #AIHealthcare #Innovation #FutureTech
        """

        approved, feedback, score = await critique_agent.evaluate_post(
            content=content,
            topic="AI in healthcare",
            tone="professional",
        )

        assert isinstance(approved, bool)
        assert isinstance(feedback, str)
        assert isinstance(score, (int, float))
        assert 0 <= score <= 10

    @pytest.mark.asyncio
    async def test_evaluate_with_brand(self, critique_agent):
        """Test evaluation with brand guidelines."""
        content = "AI is transforming healthcare. #AI #Tech"
        brand_voice = "Brand Voice: Use #HealthTech and #Innovation hashtags"

        approved, feedback, score = await critique_agent.evaluate_post(
            content=content,
            topic="AI in healthcare",
            brand_voice=brand_voice,
            tone="professional",
        )

        assert isinstance(approved, bool)
        assert isinstance(score, (int, float))
        # If not using required hashtags, should have feedback
        if not approved:
            assert len(feedback) > 0


class TestMultiAgentFlow:
    """Tests for MultiAgentFlow orchestrator."""

    @pytest.mark.asyncio
    async def test_generate_post(self, multi_agent_flow):
        """Test complete multi-agent workflow."""
        result = await multi_agent_flow.generate_post(
            topic="The future of remote work",
            context="Remote work trends show...",
            tone="professional",
            max_length=500,
        )

        assert "content" in result
        assert "outline" in result
        assert "iterations" in result
        assert "final_score" in result
        assert "workflow_summary" in result

        assert isinstance(result["content"], str)
        assert len(result["content"]) > 0
        assert result["iterations"] >= 1
        assert 0 <= result["final_score"] <= 10

    @pytest.mark.asyncio
    async def test_generate_post_with_brand(self, multi_agent_flow):
        """Test multi-agent workflow with brand voice."""
        brand_voice = "Brand Voice: Professional, data-driven. Use #TechInnovation"

        result = await multi_agent_flow.generate_post(
            topic="Cloud computing trends",
            context="Cloud adoption is growing...",
            brand_voice=brand_voice,
            tone="professional",
            max_length=500,
        )

        assert "content" in result
        assert result["iterations"] >= 1
        assert isinstance(result["approved"], bool)

    @pytest.mark.asyncio
    async def test_max_rewrites_limit(self, mock_gateway):
        """Test that max rewrites limit is enforced."""
        # Create flow with low threshold to force rewrites
        flow = MultiAgentFlow(
            gateway=mock_gateway,
            critique_threshold=9.5,  # Very high threshold
            max_rewrites=1,  # Only 1 rewrite allowed
        )

        result = await flow.generate_post(
            topic="Test topic",
            context="Test context",
            tone="professional",
            max_length=500,
        )

        # Should stop after max iterations even if not approved
        assert result["iterations"] <= 2  # 1 initial + 1 rewrite
        assert "content" in result


class TestAgentIntegration:
    """Integration tests for agent collaboration."""

    @pytest.mark.asyncio
    async def test_agents_communicate(self, planner_agent, writer_agent, critique_agent):
        """Test that agents can work together in sequence."""
        # Step 1: Planner creates outline
        outline = await planner_agent.create_outline(
            topic="Test topic",
            context="Test context",
            tone="professional",
            max_length=500,
        )
        assert len(outline) > 0

        # Step 2: Writer uses outline
        content = await writer_agent.write_post(
            topic="Test topic",
            outline=outline,
            tone="professional",
            max_length=500,
        )
        assert len(content) > 0

        # Step 3: Critique evaluates
        approved, feedback, score = await critique_agent.evaluate_post(
            content=content,
            topic="Test topic",
            tone="professional",
        )
        assert isinstance(approved, bool)
        assert isinstance(score, (int, float))
