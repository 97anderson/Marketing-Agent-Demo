"""Inference Gateway Implementation.

This module provides a unified interface for routing LLM calls with observability.
It supports both mock models (for testing) and real models (OpenAI).
"""

import logging
import time
from abc import ABC, abstractmethod

from langchain.schema import HumanMessage
from langchain_openai import ChatOpenAI

from src.gateway.models import (
    InferenceRequest,
    InferenceResponse,
    TokenUsage,
)
from src.shared.config import get_settings

logger = logging.getLogger(__name__)


class BaseModel(ABC):
    """Abstract base class for LLM models.

    This class defines the interface that all model implementations must follow.
    """

    @abstractmethod
    async def generate(self, request: InferenceRequest) -> InferenceResponse:
        """Generate a completion from the model.

        Args:
            request: The inference request containing prompt and parameters.

        Returns:
            The inference response with generated content and usage stats.
        """
        pass


class MockModel(BaseModel):
    """Mock LLM model for testing purposes.

    This model returns predefined responses without making actual API calls.
    It simulates token usage for observability testing.
    """

    async def generate(self, request: InferenceRequest) -> InferenceResponse:
        """Generate a mock completion.

        Args:
            request: The inference request.

        Returns:
            A mock response with simulated content and usage.
        """
        logger.info(f"MockModel: Generating response for prompt length {len(request.prompt)}")

        # Simulate processing time
        await self._simulate_latency()

        # Create mock response
        mock_content = self._generate_mock_content(request.prompt)

        # Simulate token usage
        prompt_tokens = len(request.prompt.split()) * 2  # Rough approximation
        completion_tokens = len(mock_content.split()) * 2

        usage = TokenUsage(
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=prompt_tokens + completion_tokens,
        )

        logger.info(f"MockModel: Token Usage - {usage.dict()}")

        return InferenceResponse(
            content=mock_content, model="mock-model", usage=usage, metadata=request.metadata
        )

    async def _simulate_latency(self) -> None:
        """Simulate API latency."""
        import asyncio

        await asyncio.sleep(0.1)  # 100ms simulated latency

    def _generate_mock_content(self, prompt: str) -> str:
        """Generate mock content based on the prompt.

        Args:
            prompt: The input prompt.

        Returns:
            Mock generated content.
        """
        prompt_lower = prompt.lower()

        # Check if this is a critique/evaluation request
        if "evaluate" in prompt_lower and "evaluation:" in prompt_lower:
            return self._generate_mock_critique()

        # Check if this is a planning request (PlannerAgent)
        if (
            "create an outline" in prompt_lower
            or "structure for the post" in prompt_lower
            or "outline for a linkedin post" in prompt_lower
        ):
            return self._generate_mock_outline()

        # Check if this is a writing request (WriterAgent)
        if (
            "write the linkedin post" in prompt_lower
            or "create the post content" in prompt_lower
            or "based on the outline" in prompt_lower
            or "rewrite" in prompt_lower
        ):
            return self._generate_mock_linkedin_post()

        # Default: LinkedIn post content
        return self._generate_mock_linkedin_post()

    def _generate_mock_linkedin_post(self) -> str:
        """Generate a mock LinkedIn post content.

        Returns:
            Mock LinkedIn post.
        """
        import random

        hooks = [
            "🚀 The future of technology is here, and it's transforming everything.",
            "💡 I've been reflecting on the rapid changes in our industry lately.",
            "🎯 Let me share something that's been on my mind recently.",
            "✨ Here's an insight that completely changed my perspective.",
        ]

        insights = [
            "Innovation isn't just about technology—it's about solving real problems.",
            "The key to success is continuous learning and adaptation.",
            "Collaboration amplifies impact more than individual genius ever could.",
            "Data-driven decisions are only as good as the questions we ask.",
        ]

        ctas = [
            "What's your take on this? Share your thoughts below! 💬",
            "I'd love to hear your perspective. What has your experience been?",
            "Let's discuss this further. Drop your insights in the comments!",
            "Have you experienced something similar? Let's connect and chat!",
        ]

        hook = random.choice(hooks)
        insight1 = random.choice(insights)
        insight2 = random.choice([i for i in insights if i != insight1])
        cta = random.choice(ctas)

        return f"""{hook}

I've been exploring this fascinating topic, and here are my key takeaways:

✅ {insight1}

✅ {insight2}

✅ The possibilities are endless when we combine creativity with strategic thinking.

{cta}

#Innovation #Technology #Leadership #Growth #LinkedInPost"""

    def _generate_mock_critique(self) -> str:
        """Generate a mock critique evaluation response.

        Returns:
            Mock critique in JSON format.
        """
        import random

        # Randomly generate scores to simulate variability
        brand_adherence = random.randint(7, 10)
        quality = random.randint(7, 10)
        tone_length = random.randint(7, 10)
        overall_score = (brand_adherence + quality + tone_length) / 3

        approved = overall_score >= 8.0

        feedback = ""
        if not approved:
            feedback_options = [
                "The hook could be more engaging. Consider starting with a question or surprising statistic.",
                "The brand voice needs to be more prominent. Incorporate more of the brand's unique personality.",
                "The call-to-action could be stronger. Make it more specific and compelling.",
                "Consider adding more concrete examples or data to support your points.",
            ]
            feedback = random.choice(feedback_options)
        else:
            feedback = "Excellent post! Meets all criteria."

        return f"""{{
  "score": {overall_score:.1f},
  "brand_adherence": {brand_adherence},
  "quality": {quality},
  "tone_length": {tone_length},
  "feedback": "{feedback}",
  "approved": {str(approved).lower()}
}}"""

    def _generate_mock_outline(self) -> str:
        """Generate a mock outline for content planning.

        Returns:
            Mock outline structure.
        """
        return """Here's a structured outline for your LinkedIn post:

**HOOK** (First 1-2 lines):
A compelling question or statement to grab attention

**MAIN CONTENT** (3-5 key points):
1. First key insight or point
2. Second key insight with supporting detail
3. Third key insight (optional)

**CALL-TO-ACTION**:
Engage with the audience - ask a question or suggest next steps

**HASHTAGS**:
#RelevantTag1 #RelevantTag2 #RelevantTag3

This structure will ensure engagement and clarity."""


class OpenAIModel(BaseModel):
    """OpenAI LLM model implementation.

    This model makes real API calls to OpenAI's language models.
    """

    def __init__(self, api_key: str):
        """Initialize the OpenAI model.

        Args:
            api_key: OpenAI API key for authentication.
        """
        self.api_key = api_key
        self._client: ChatOpenAI | None = None

    def _get_client(self, model: str, temperature: float, max_tokens: int) -> ChatOpenAI:
        """Get or create a ChatOpenAI client.

        Args:
            model: Model identifier.
            temperature: Sampling temperature.
            max_tokens: Maximum tokens to generate.

        Returns:
            Configured ChatOpenAI client.
        """
        return ChatOpenAI(
            api_key=self.api_key, model=model, temperature=temperature, max_tokens=max_tokens
        )

    async def generate(self, request: InferenceRequest) -> InferenceResponse:
        """Generate a completion using OpenAI.

        Args:
            request: The inference request.

        Returns:
            The inference response with generated content and usage.
        """
        logger.info(f"OpenAIModel: Generating response with model {request.model}")

        start_time = time.time()

        try:
            client = self._get_client(
                model=request.model, temperature=request.temperature, max_tokens=request.max_tokens
            )

            messages = [HumanMessage(content=request.prompt)]

            response = await client.agenerate([messages])

            # Extract the generated content
            content = response.generations[0][0].text

            # Extract token usage from response metadata
            llm_output = response.llm_output or {}
            token_usage = llm_output.get("token_usage", {})

            usage = TokenUsage(
                prompt_tokens=token_usage.get("prompt_tokens", 0),
                completion_tokens=token_usage.get("completion_tokens", 0),
                total_tokens=token_usage.get("total_tokens", 0),
            )

            elapsed_time = time.time() - start_time
            logger.info(f"OpenAIModel: Token Usage - {usage.dict()}, Latency: {elapsed_time:.2f}s")

            return InferenceResponse(
                content=content, model=request.model, usage=usage, metadata=request.metadata
            )

        except Exception as e:
            logger.error(f"OpenAIModel: Error during generation - {str(e)}")
            raise


class InferenceGateway:
    """Central gateway for routing and managing LLM inference calls.

    This class provides a unified interface for making LLM calls with:
    - Model switching (mock vs real)
    - Token usage logging
    - Observability and metrics
    - Error handling

    Attributes:
        use_mock: Whether to use mock model instead of real model.
        model: The active model instance (mock or real).
    """

    def __init__(self, use_mock: bool = True, api_key: str | None = None):
        """Initialize the Inference Gateway.

        Args:
            use_mock: If True, use mock model. If False, use real OpenAI model.
            api_key: OpenAI API key (required if use_mock=False).
        """
        self.use_mock = use_mock

        if use_mock:
            logger.info("InferenceGateway: Initialized with MockModel")
            self.model = MockModel()
        else:
            if not api_key:
                raise ValueError("API key is required when not using mock model")
            logger.info("InferenceGateway: Initialized with OpenAIModel")
            self.model = OpenAIModel(api_key=api_key)

    async def generate(
        self,
        prompt: str,
        model: str = "gpt-3.5-turbo",
        temperature: float = 0.7,
        max_tokens: int = 500,
        metadata: dict | None = None,
    ) -> InferenceResponse:
        """Generate a completion through the gateway.

        This method routes the request to the appropriate model (mock or real)
        and logs token usage for observability.

        Args:
            prompt: The input prompt for the LLM.
            model: The model identifier to use.
            temperature: Sampling temperature (0.0 to 2.0).
            max_tokens: Maximum tokens to generate.
            metadata: Additional metadata for logging.

        Returns:
            The inference response with generated content and usage stats.

        Raises:
            Exception: If the generation fails.
        """
        request = InferenceRequest(
            prompt=prompt,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            metadata=metadata,
        )

        logger.info(
            f"InferenceGateway: Processing request - "
            f"Model: {model}, Temperature: {temperature}, "
            f"Max Tokens: {max_tokens}"
        )

        try:
            response = await self.model.generate(request)

            # Log token usage for observability
            logger.info(
                f"InferenceGateway: REQUEST COMPLETE - "
                f"Prompt Tokens: {response.usage.prompt_tokens}, "
                f"Completion Tokens: {response.usage.completion_tokens}, "
                f"Total Tokens: {response.usage.total_tokens}"
            )

            return response

        except Exception as e:
            logger.error(f"InferenceGateway: Generation failed - {str(e)}")
            raise

    @classmethod
    def from_settings(cls) -> "InferenceGateway":
        """Create an InferenceGateway instance from application settings.

        Returns:
            Configured InferenceGateway instance.
        """
        settings = get_settings()

        return cls(
            use_mock=settings.use_mock_model,
            api_key=settings.openai_api_key if not settings.use_mock_model else None,
        )
