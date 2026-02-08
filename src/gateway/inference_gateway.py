"""Inference Gateway Implementation.

This module provides a unified interface for routing LLM calls with observability.
It supports both mock models (for testing) and real models (OpenAI).
"""

import logging
import time
from abc import ABC, abstractmethod

from langchain.schema import HumanMessage
from langchain_openai import ChatOpenAI

from src.gateway.models import InferenceRequest, InferenceResponse, TokenUsage
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
            total_tokens=prompt_tokens + completion_tokens
        )

        logger.info(f"MockModel: Token Usage - {usage.dict()}")

        return InferenceResponse(
            content=mock_content,
            model="mock-model",
            usage=usage,
            metadata=request.metadata
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
        return (
            "🚀 This is a mock-generated LinkedIn post! 🎯\n\n"
            "I've been exploring the fascinating world of AI and technology. "
            "The rapid advancement in this field is truly remarkable. "
            "From machine learning to natural language processing, "
            "the possibilities are endless! 💡\n\n"
            "Key insights:\n"
            "✅ Innovation drives progress\n"
            "✅ Continuous learning is essential\n"
            "✅ Collaboration amplifies impact\n\n"
            "What are your thoughts on this topic? Let's discuss! 💬\n\n"
            "#AI #Technology #Innovation #LinkedInPost"
        )


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
            api_key=self.api_key,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens
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
                model=request.model,
                temperature=request.temperature,
                max_tokens=request.max_tokens
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
                total_tokens=token_usage.get("total_tokens", 0)
            )

            elapsed_time = time.time() - start_time
            logger.info(
                f"OpenAIModel: Token Usage - {usage.dict()}, "
                f"Latency: {elapsed_time:.2f}s"
            )

            return InferenceResponse(
                content=content,
                model=request.model,
                usage=usage,
                metadata=request.metadata
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
        metadata: dict | None = None
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
            metadata=metadata
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
            api_key=settings.openai_api_key if not settings.use_mock_model else None
        )
