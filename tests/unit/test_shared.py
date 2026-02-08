"""Unit tests for shared utilities."""

from unittest.mock import MagicMock, patch

import pytest

from src.shared.config import Settings, get_settings
from src.shared.database import VectorDatabase


def test_settings_defaults():
    """Test Settings has correct defaults."""
    # Clear environment variables to test defaults
    with patch.dict("os.environ", {}, clear=True):
        settings = Settings()

        assert settings.environment == "development"
        assert settings.log_level == "INFO"
        assert settings.use_mock_model is True
        assert settings.api_host == "0.0.0.0"
        assert settings.api_port == 8000


def test_settings_is_development():
    """Test is_development property."""
    settings = Settings(environment="development")
    assert settings.is_development is True

    settings = Settings(environment="production")
    assert settings.is_development is False


def test_settings_is_production():
    """Test is_production property."""
    settings = Settings(environment="production")
    assert settings.is_production is True

    settings = Settings(environment="development")
    assert settings.is_production is False


def test_get_settings_cached():
    """Test that get_settings returns cached instance."""
    settings1 = get_settings()
    settings2 = get_settings()

    assert settings1 is settings2


@pytest.fixture
def mock_chroma_client():
    """Create a mock ChromaDB client."""
    mock_client = MagicMock()
    mock_collection = MagicMock()

    mock_client.get_or_create_collection.return_value = mock_collection
    mock_collection.add = MagicMock()
    mock_collection.query = MagicMock(
        return_value={
            "documents": [["test doc"]],
            "distances": [[0.5]],
            "metadatas": [[{"topic": "test"}]],
        }
    )
    mock_collection.get = MagicMock(
        return_value={"ids": ["id1"], "documents": ["doc1"], "metadatas": [{"topic": "test"}]}
    )

    return mock_client, mock_collection


def test_vector_database_initialization(mock_chroma_client):
    """Test VectorDatabase initialization."""
    mock_client, mock_collection = mock_chroma_client

    with patch("chromadb.Client", return_value=mock_client):
        db = VectorDatabase(collection_name="test_collection")

        assert db.collection_name == "test_collection"
        assert db.client is not None


def test_vector_database_add_document(mock_chroma_client):
    """Test adding a document to VectorDatabase."""
    mock_client, mock_collection = mock_chroma_client

    with patch("chromadb.Client", return_value=mock_client):
        db = VectorDatabase()

        db.add_document(document="Test document", document_id="doc-1", metadata={"topic": "test"})

        mock_collection.add.assert_called_once()


def test_vector_database_query_documents(mock_chroma_client):
    """Test querying documents from VectorDatabase."""
    mock_client, mock_collection = mock_chroma_client

    with patch("chromadb.Client", return_value=mock_client):
        db = VectorDatabase()

        results = db.query_documents(query_text="test query", n_results=5)

        assert "documents" in results
        mock_collection.query.assert_called_once()


def test_vector_database_get_all_documents(mock_chroma_client):
    """Test getting all documents from VectorDatabase."""
    mock_client, mock_collection = mock_chroma_client

    with patch("chromadb.Client", return_value=mock_client):
        db = VectorDatabase()

        results = db.get_all_documents(limit=10)

        assert "ids" in results
        assert "documents" in results
        mock_collection.get.assert_called_once()


def test_vector_database_singleton():
    """Test VectorDatabase singleton pattern."""
    with patch("chromadb.Client"):
        db1 = VectorDatabase.get_instance()
        db2 = VectorDatabase.get_instance()

        assert db1 is db2
