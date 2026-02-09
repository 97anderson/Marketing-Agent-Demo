"""Main entry point for running the application."""

import sys
from pathlib import Path

import uvicorn

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.shared.config import get_settings
from src.shared.logger import setup_logging


def main():
    """Run the FastAPI application."""
    # Setup logging
    setup_logging()

    # Get settings
    settings = get_settings()

    print(f"\n{'='*60}")
    print("Starting Marketing Agent API")
    print(f"{'='*60}")
    print(f"Environment: {settings.environment}")
    print(f"Mock Model: {settings.use_mock_model}")
    print(f"Host: {settings.api_host}:{settings.api_port}")
    print(f"{'='*60}\n")

    # Run the application
    uvicorn.run(
        "src.agents.marketing.api:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.is_development,
        log_level=settings.log_level.lower(),
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
