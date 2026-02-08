"""Inference Gateway Models.

This module defines the data models for the Inference Gateway.
"""

from pydantic import BaseModel, Field


class TokenUsage(BaseModel):
    """Token usage information from LLM calls.

    Attributes:
        prompt_tokens: Number of tokens in the prompt.
        completion_tokens: Number of tokens in the completion.
        total_tokens: Total number of tokens used.
    """

    prompt_tokens: int = Field(..., description="Number of tokens in the prompt")
    completion_tokens: int = Field(..., description="Number of tokens in the completion")
    total_tokens: int = Field(..., description="Total number of tokens used")


class InferenceRequest(BaseModel):
    """Request model for LLM inference.

    Attributes:
        prompt: The input prompt for the LLM.
        model: The model to use (e.g., 'gpt-3.5-turbo', 'gpt-4').
        temperature: Sampling temperature (0.0 to 2.0).
        max_tokens: Maximum tokens to generate.
        metadata: Additional metadata for logging.
    """

    prompt: str = Field(..., description="The input prompt for the LLM")
    model: str = Field(default="gpt-3.5-turbo", description="Model identifier")
    temperature: float = Field(default=0.7, ge=0.0, le=2.0, description="Sampling temperature")
    max_tokens: int = Field(default=500, ge=1, description="Maximum tokens to generate")
    metadata: dict[str, str] | None = Field(default=None, description="Additional metadata")


class InferenceResponse(BaseModel):
    """Response model from LLM inference.

    Attributes:
        content: The generated content from the LLM.
        model: The model that was used.
        usage: Token usage information.
        metadata: Additional metadata from the request.
    """

    content: str = Field(..., description="Generated content")
    model: str = Field(..., description="Model that was used")
    usage: TokenUsage = Field(..., description="Token usage information")
    metadata: dict[str, str] | None = Field(default=None, description="Request metadata")


class ModelType(str):
    """Supported model types."""

    MOCK = "mock"
    OPENAI = "openai"
