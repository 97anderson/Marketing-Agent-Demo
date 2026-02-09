"""Marketing Agent Models.

This module defines the data models for the Marketing Agent.
"""

from datetime import datetime

from pydantic import BaseModel, Field

from src.gateway.models import TokenUsage


class GeneratePostRequest(BaseModel):
    """Request to generate a LinkedIn post.

    Attributes:
        topic: The topic for the post.
        tone: The desired tone (professional, casual, enthusiastic).
        max_length: Maximum length in characters.
        brand_id: Optional brand identifier for brand voice guidelines.
    """

    topic: str = Field(..., min_length=1, description="Topic for the LinkedIn post")
    tone: str = Field(
        default="professional", description="Tone of the post (professional, casual, enthusiastic)"
    )
    max_length: int = Field(
        default=500, ge=100, le=3000, description="Maximum length in characters"
    )
    brand_id: str | None = Field(
        default=None,
        description="Brand identifier for applying brand voice guidelines (e.g., 'techcorp', 'ecolife')",
    )


class GeneratedPost(BaseModel):
    """A generated LinkedIn post.

    Attributes:
        id: Unique identifier for the post.
        topic: The topic of the post.
        content: The generated content.
        tone: The tone used.
        brand_id: The brand identifier used (if any).
        usage: Token usage information.
        created_at: Timestamp when the post was created.
        metadata: Optional metadata about the generation process (e.g., multi-agent workflow info).
    """

    id: str = Field(..., description="Unique identifier")
    topic: str = Field(..., description="Topic of the post")
    content: str = Field(..., description="Generated content")
    tone: str = Field(..., description="Tone used")
    brand_id: str | None = Field(default=None, description="Brand identifier used")
    usage: TokenUsage = Field(..., description="Token usage information")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    metadata: dict | None = Field(
        default=None,
        description="Optional metadata (e.g., workflow type, iterations, scores)",
    )


class GeneratePostResponse(BaseModel):
    """Response from post generation.

    Attributes:
        post: The generated post.
        message: Status message.
    """

    post: GeneratedPost = Field(..., description="The generated post")
    message: str = Field(default="Post generated successfully", description="Status message")


class PostHistory(BaseModel):
    """History of generated posts.

    Attributes:
        posts: List of generated posts.
        total: Total number of posts.
    """

    posts: list[GeneratedPost] = Field(..., description="List of generated posts")
    total: int = Field(..., description="Total number of posts")
