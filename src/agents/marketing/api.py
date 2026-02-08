"""Marketing Agent FastAPI Application.

This module implements the REST API for the Marketing Agent service.
"""

import logging
from contextlib import asynccontextmanager
from typing import List

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from src.agents.marketing.agent import MarketingAgent
from src.agents.marketing.models import (
    GeneratePostRequest,
    GeneratePostResponse,
    PostHistory,
)
from src.shared.config import get_settings
from src.shared.logger import setup_logging


# Setup logging
setup_logging()
logger = logging.getLogger(__name__)


# Global agent instance
agent: MarketingAgent = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for application startup and shutdown.
    
    Args:
        app: The FastAPI application instance.
    """
    # Startup
    global agent
    logger.info("Starting Marketing Agent API")
    
    settings = get_settings()
    logger.info(f"Environment: {settings.environment}")
    logger.info(f"Using Mock Model: {settings.use_mock_model}")
    
    # Initialize the agent
    agent = MarketingAgent()
    logger.info("Marketing Agent initialized successfully")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Marketing Agent API")


# Create FastAPI application
app = FastAPI(
    title="Marketing Agent API",
    description="Content-Creator Agent for generating LinkedIn posts",
    version="0.1.0",
    lifespan=lifespan
)


# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", tags=["Root"])
async def root():
    """Root endpoint.
    
    Returns:
        Welcome message and API information.
    """
    return {
        "message": "Marketing Agent API",
        "version": "0.1.0",
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint.
    
    Returns:
        Service health status.
    """
    settings = get_settings()
    
    return {
        "status": "healthy",
        "service": "marketing-agent",
        "environment": settings.environment,
        "using_mock_model": settings.use_mock_model
    }


@app.post(
    "/generate",
    response_model=GeneratePostResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Content Generation"]
)
async def generate_post(request: GeneratePostRequest):
    """Generate a LinkedIn post on the given topic.
    
    This endpoint:
    1. Searches for information about the topic
    2. Generates a professional LinkedIn post
    3. Saves the post to the vector database
    
    Args:
        request: The post generation request containing topic and parameters.
        
    Returns:
        The generated post with usage statistics.
        
    Raises:
        HTTPException: If post generation fails.
    """
    try:
        logger.info(f"Received request to generate post for topic: {request.topic}")
        
        # Generate the post using the agent
        post = await agent.generate_post(request)
        
        return GeneratePostResponse(
            post=post,
            message="Post generated successfully"
        )
        
    except Exception as e:
        logger.error(f"Error generating post: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate post: {str(e)}"
        )


@app.get(
    "/history",
    response_model=PostHistory,
    tags=["Content History"]
)
async def get_history(limit: int = 10):
    """Get the history of generated posts.
    
    Retrieves previously generated posts from the vector database.
    
    Args:
        limit: Maximum number of posts to return (default: 10).
        
    Returns:
        List of previously generated posts with metadata.
        
    Raises:
        HTTPException: If retrieval fails.
    """
    try:
        logger.info(f"Retrieving post history (limit: {limit})")
        
        # Get history from the agent
        posts = agent.get_history(limit=limit)
        
        return PostHistory(
            posts=posts,
            total=len(posts)
        )
        
    except Exception as e:
        logger.error(f"Error retrieving history: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve history: {str(e)}"
        )


@app.get("/metrics", tags=["Observability"])
async def get_metrics():
    """Get API metrics and statistics.
    
    Returns:
        Current metrics including total posts generated.
    """
    try:
        posts = agent.get_history(limit=None)
        total_posts = len(posts)
        
        # Calculate total token usage
        total_tokens = sum(post.usage.total_tokens for post in posts)
        
        return {
            "total_posts_generated": total_posts,
            "total_tokens_used": total_tokens,
            "status": "operational"
        }
        
    except Exception as e:
        logger.error(f"Error retrieving metrics: {str(e)}")
        return {
            "total_posts_generated": 0,
            "total_tokens_used": 0,
            "status": "error",
            "error": str(e)
        }


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler for unhandled errors.
    
    Args:
        request: The request that caused the exception.
        exc: The exception that was raised.
        
    Returns:
        JSON error response.
    """
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "An unexpected error occurred",
            "error": str(exc)
        }
    )


if __name__ == "__main__":
    import uvicorn
    
    settings = get_settings()
    
    uvicorn.run(
        "src.agents.marketing.api:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.is_development
    )

