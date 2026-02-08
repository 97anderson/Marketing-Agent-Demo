"""Pytest configuration file."""

import pytest
import sys
from pathlib import Path

# Add src directory to Python path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))


@pytest.fixture(autouse=True)
def reset_singletons():
    """Reset singleton instances between tests."""
    from src.shared.database import VectorDatabase
    
    # Reset VectorDatabase singleton
    VectorDatabase._instance = None
    
    yield
    
    # Clean up after test
    VectorDatabase._instance = None

