"""Main entry point for running the application."""

import sys
import uvicorn

from src.shared.config import get_settings
from src.shared.logger import setup_logging


def main():
    """Run the FastAPI application."""
    # Setup logging
    setup_logging()
    
    # Get settings
    settings = get_settings()
    
    # Run the application
    uvicorn.run(
        "src.agents.marketing.api:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.is_development,
        log_level=settings.log_level.lower()
    )


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nShutting down gracefully...")
        sys.exit(0)
    except Exception as e:
        print(f"\n\nError: {str(e)}")
        sys.exit(1)

