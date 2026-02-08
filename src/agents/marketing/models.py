"""Marketing Agent Models.

This module defines the data models for the Marketing Agent.
"""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field

from src.gateway.models import TokenUsage


class GeneratePostRequest(BaseModel):
    """Request to generate a LinkedIn post.
    
    Attributes:
        topic: The topic for the post.
        tone: The desired tone (professional, casual, enthusiastic).
        max_length: Maximum length in characters.
    """
    
    topic: str = Field(..., description="Topic for the LinkedIn post")
    tone: str = Field(
        default="professional",
        description="Tone of the post (professional, casual, enthusiastic)"
    )
    max_length: int = Field(
        default=500,
        ge=100,
        le=3000,
        description="Maximum length in characters"
    )


class GeneratedPost(BaseModel):
    """A generated LinkedIn post.
    
    Attributes:
        id: Unique identifier for the post.
        topic: The topic of the post.
        content: The generated content.
        tone: The tone used.
        usage: Token usage information.
        created_at: Timestamp when the post was created.
    """
    
    id: str = Field(..., description="Unique identifier")
    topic: str = Field(..., description="Topic of the post")
    content: str = Field(..., description="Generated content")
    tone: str = Field(..., description="Tone used")
    usage: TokenUsage = Field(..., description="Token usage information")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")


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
    
    posts: List[GeneratedPost] = Field(..., description="List of generated posts")
    total: int = Field(..., description="Total number of posts")

