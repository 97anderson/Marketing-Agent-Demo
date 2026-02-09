"""Unit tests for Brand Voice Manager."""

from pathlib import Path
from unittest.mock import patch

import pytest

from src.agents.marketing.brand_voice import BrandVoiceManager


@pytest.fixture
def brand_voice_manager():
    """Create a BrandVoiceManager instance for testing."""
    return BrandVoiceManager(knowledge_base_dir="knowledge_base")


def test_brand_voice_manager_initialization():
    """Test BrandVoiceManager initialization."""
    manager = BrandVoiceManager(knowledge_base_dir="test_kb", max_file_size_kb=5)

    assert manager.knowledge_base_dir == Path("test_kb")
    assert manager.max_file_size_kb == 5
    assert manager.max_file_size_bytes == 5 * 1024


def test_get_brand_voice_success(brand_voice_manager):
    """Test successfully loading brand voice."""
    # Test with techcorp (should exist in knowledge_base)
    brand_voice = brand_voice_manager.get_brand_voice("techcorp")

    assert brand_voice is not None
    assert len(brand_voice) > 0
    assert "TechCorp" in brand_voice
    assert "Brand Voice Guide" in brand_voice


def test_get_brand_voice_not_found(brand_voice_manager):
    """Test loading non-existent brand voice."""
    with pytest.raises(FileNotFoundError) as exc_info:
        brand_voice_manager.get_brand_voice("nonexistent")

    assert "not found" in str(exc_info.value)
    assert "nonexistent" in str(exc_info.value)


def test_get_brand_voice_empty_id(brand_voice_manager):
    """Test with empty brand_id."""
    with pytest.raises(ValueError) as exc_info:
        brand_voice_manager.get_brand_voice("")

    assert "cannot be empty" in str(exc_info.value)


def test_get_brand_voice_case_insensitive(brand_voice_manager):
    """Test that brand_id is case insensitive."""
    voice1 = brand_voice_manager.get_brand_voice("techcorp")
    voice2 = brand_voice_manager.get_brand_voice("TECHCORP")
    voice3 = brand_voice_manager.get_brand_voice("TechCorp")

    assert voice1 == voice2 == voice3


def test_list_available_brands(brand_voice_manager):
    """Test listing available brands."""
    brands = brand_voice_manager.list_available_brands()

    assert isinstance(brands, list)
    assert len(brands) >= 3  # We created at least 3 brands
    assert "techcorp" in brands
    assert "ecolife" in brands
    assert "financewise" in brands


def test_validate_brand_exists(brand_voice_manager):
    """Test brand existence validation."""
    assert brand_voice_manager.validate_brand_exists("techcorp") is True
    assert brand_voice_manager.validate_brand_exists("ecolife") is True
    assert brand_voice_manager.validate_brand_exists("nonexistent") is False
    assert brand_voice_manager.validate_brand_exists("") is False


def test_get_brand_summary(brand_voice_manager):
    """Test getting brand summary."""
    summary = brand_voice_manager.get_brand_summary("techcorp")

    assert isinstance(summary, dict)
    assert summary["brand_id"] == "techcorp"
    assert summary["available"] is True
    assert "overview" in summary
    assert summary["guidelines_length"] > 0


def test_get_brand_summary_not_found(brand_voice_manager):
    """Test getting summary for non-existent brand."""
    summary = brand_voice_manager.get_brand_summary("nonexistent")

    assert summary["brand_id"] == "nonexistent"
    assert summary["available"] is False
    assert summary["guidelines_length"] == 0


def test_load_small_file(brand_voice_manager):
    """Test loading a small file directly."""
    file_path = brand_voice_manager.knowledge_base_dir / "techcorp_brand_voice.txt"
    content = brand_voice_manager._load_small_file(file_path)

    assert content is not None
    assert len(content) > 0


def test_load_large_file_warning(brand_voice_manager):
    """Test that large file loading logs a warning."""
    file_path = brand_voice_manager.knowledge_base_dir / "techcorp_brand_voice.txt"

    # Mock logger to check for warning
    with patch("src.agents.marketing.brand_voice.logger") as mock_logger:
        content = brand_voice_manager._load_large_file(file_path, "techcorp")

        assert content is not None
        mock_logger.warning.assert_called_once()


def test_list_available_brands_empty_directory():
    """Test listing brands with non-existent directory."""
    manager = BrandVoiceManager(knowledge_base_dir="nonexistent_dir")
    brands = manager.list_available_brands()

    assert brands == []
