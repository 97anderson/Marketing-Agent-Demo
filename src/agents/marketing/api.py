"""Marketing Agent FastAPI Application.

This module implements the REST API for the Marketing Agent service.
"""

import logging
from contextlib import asynccontextmanager

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
from src.shared.trace_logger import get_trace_logger

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

    # Initialize the agent (check if multi-agent mode is enabled)
    agent = MarketingAgent(
        use_multi_agent=settings.use_multi_agent_flow,
        critique_threshold=settings.critique_threshold,
        max_rewrites=settings.max_rewrites,
    )

    mode = "MULTI-AGENT" if settings.use_multi_agent_flow else "SINGLE-AGENT"
    logger.info(f"Marketing Agent initialized successfully in {mode} mode")
    if settings.use_multi_agent_flow:
        logger.info(
            f"Multi-agent config: threshold={settings.critique_threshold}, "
            f"max_rewrites={settings.max_rewrites}"
        )

    yield

    # Shutdown
    logger.info("Shutting down Marketing Agent API")


# Create FastAPI application
app = FastAPI(
    title="Marketing Agent API",
    description="Content-Creator Agent for generating LinkedIn posts (Single-Agent and Multi-Agent modes)",
    version="2.0.0",
    lifespan=lifespan,
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
    settings = get_settings()
    return {
        "message": "Marketing Agent API",
        "version": "2.0.0",
        "mode": "multi-agent" if settings.use_multi_agent_flow else "single-agent",
        "docs": "/docs",
        "health": "/health",
        "features": [
            "content_generation",
            "brand_voice",
            "post_history",
            "multi_agent_workflow" if settings.use_multi_agent_flow else "single_agent_workflow",
        ],
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
        "using_mock_model": settings.use_mock_model,
        "agent_mode": "multi-agent" if settings.use_multi_agent_flow else "single-agent",
        "multi_agent_config": {
            "enabled": settings.use_multi_agent_flow,
            "critique_threshold": settings.critique_threshold,
            "max_rewrites": settings.max_rewrites,
        }
        if settings.use_multi_agent_flow
        else None,
    }


@app.post(
    "/generate",
    response_model=GeneratePostResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Content Generation"],
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

        return GeneratePostResponse(post=post, message="Post generated successfully")

    except Exception as e:
        logger.error(f"Error generating post: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate post: {str(e)}",
        )


@app.get("/history", response_model=PostHistory, tags=["Content History"])
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

        return PostHistory(posts=posts, total=len(posts))

    except Exception as e:
        logger.error(f"Error retrieving history: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve history: {str(e)}",
        )


@app.get("/brands", tags=["Brand Voice"])
async def list_brands():
    """List all available brands with voice guidelines.

    Returns:
        List of available brand identifiers and their information.
    """
    try:
        brands = agent.list_available_brands()

        # Get summary for each brand
        brand_info = []
        for brand_id in brands:
            info = agent.get_brand_info(brand_id)
            brand_info.append(info)

        return {"brands": brand_info, "total": len(brands)}

    except Exception as e:
        logger.error(f"Error listing brands: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list brands: {str(e)}",
        )


@app.get("/brands/{brand_id}", tags=["Brand Voice"])
async def get_brand(brand_id: str):
    """Get information about a specific brand.

    Args:
        brand_id: The brand identifier.

    Returns:
        Brand information and summary.
    """
    try:
        info = agent.get_brand_info(brand_id)

        if not info["available"]:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Brand '{brand_id}' not found",
            )

        return info

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting brand info: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get brand info: {str(e)}",
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

        # Count posts by brand
        posts_by_brand = {}
        for post in posts:
            if post.brand_id:
                posts_by_brand[post.brand_id] = posts_by_brand.get(post.brand_id, 0) + 1

        return {
            "total_posts_generated": total_posts,
            "total_tokens_used": total_tokens,
            "posts_by_brand": posts_by_brand,
            "available_brands": len(agent.list_available_brands()),
            "status": "operational",
        }

    except Exception as e:
        logger.error(f"Error retrieving metrics: {str(e)}")
        return {
            "total_posts_generated": 0,
            "total_tokens_used": 0,
            "posts_by_brand": {},
            "status": "error",
            "error": str(e),
        }


@app.post("/report/generate", tags=["Reports"])
async def generate_html_report():
    """Generate HTML report from current trace logger.

    This endpoint generates an HTML report from the accumulated
    trace data and returns the HTML content.

    Returns:
        HTML content of the report.
    """
    try:
        logger.info("Generating HTML report from trace logger")

        trace = get_trace_logger()

        # Generate report to temporary location
        import tempfile
        from pathlib import Path

        temp_dir = Path(tempfile.gettempdir())
        report_path = temp_dir / "agent_report.html"

        # Generate without auto-open
        from src.shared.html_reporter import HTMLReporter

        reporter = HTMLReporter(trace)
        reporter.generate_report(output_path=report_path, auto_open=False)

        # Read and return HTML content
        html_content = report_path.read_text(encoding="utf-8")

        return JSONResponse(
            content={"html": html_content, "message": "Report generated successfully"},
            status_code=status.HTTP_200_OK,
        )

    except Exception as e:
        logger.error(f"Error generating report: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate report: {str(e)}",
        )


@app.get("/report/download", tags=["Reports"])
async def download_html_report():
    """Download HTML report as file.

    Returns:
        HTML file download.
    """
    try:
        import tempfile
        from pathlib import Path

        from fastapi.responses import FileResponse

        trace = get_trace_logger()

        temp_dir = Path(tempfile.gettempdir())
        report_path = temp_dir / "agent_execution_report.html"

        from src.shared.html_reporter import HTMLReporter

        reporter = HTMLReporter(trace)
        reporter.generate_report(output_path=report_path, auto_open=False)

        return FileResponse(
            path=report_path,
            media_type="text/html",
            filename="agent_execution_report.html",
        )

    except Exception as e:
        logger.error(f"Error generating report: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate report: {str(e)}",
        )


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
        content={"detail": "An unexpected error occurred", "error": str(exc)},
    )


if __name__ == "__main__":
    import uvicorn

    settings = get_settings()

    uvicorn.run(
        "src.agents.marketing.api:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.is_development,
    )
