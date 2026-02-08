"""Database Connection Management.

This module manages the connection to ChromaDB for vector storage.
"""

import logging
from typing import Optional

import chromadb
from chromadb.config import Settings as ChromaSettings

from src.shared.config import get_settings


logger = logging.getLogger(__name__)


class VectorDatabase:
    """Vector database manager using ChromaDB.
    
    This class provides a singleton interface to ChromaDB for storing
    and retrieving agent memory.
    
    Attributes:
        client: ChromaDB client instance.
        collection_name: Name of the default collection.
    """
    
    _instance: Optional["VectorDatabase"] = None
    
    def __init__(self, collection_name: str = "marketing_agent_memory"):
        """Initialize the vector database.
        
        Args:
            collection_name: Name of the collection to use.
        """
        settings = get_settings()
        
        logger.info(
            f"Initializing ChromaDB with persist_directory: "
            f"{settings.chroma_persist_directory}"
        )
        
        # Create persistent client
        self.client = chromadb.Client(
            ChromaSettings(
                persist_directory=settings.chroma_persist_directory,
                anonymized_telemetry=False
            )
        )
        
        self.collection_name = collection_name
        self._collection = None
        
        logger.info(f"ChromaDB initialized with collection: {collection_name}")
    
    @property
    def collection(self):
        """Get or create the collection.
        
        Returns:
            ChromaDB collection instance.
        """
        if self._collection is None:
            self._collection = self.client.get_or_create_collection(
                name=self.collection_name,
                metadata={"description": "Marketing agent generated content storage"}
            )
        return self._collection
    
    def add_document(
        self,
        document: str,
        document_id: str,
        metadata: Optional[dict] = None
    ) -> None:
        """Add a document to the vector database.
        
        Args:
            document: The document text to store.
            document_id: Unique identifier for the document.
            metadata: Optional metadata to store with the document.
        """
        try:
            self.collection.add(
                documents=[document],
                ids=[document_id],
                metadatas=[metadata] if metadata else None
            )
            logger.info(f"Document added to ChromaDB: {document_id}")
        except Exception as e:
            logger.error(f"Error adding document to ChromaDB: {str(e)}")
            raise
    
    def query_documents(
        self,
        query_text: str,
        n_results: int = 5
    ) -> dict:
        """Query documents from the vector database.
        
        Args:
            query_text: The query text to search for.
            n_results: Number of results to return.
            
        Returns:
            Query results with documents, distances, and metadata.
        """
        try:
            results = self.collection.query(
                query_texts=[query_text],
                n_results=n_results
            )
            logger.info(f"Query executed: found {len(results['documents'][0])} results")
            return results
        except Exception as e:
            logger.error(f"Error querying ChromaDB: {str(e)}")
            raise
    
    def get_all_documents(self, limit: Optional[int] = None) -> dict:
        """Get all documents from the collection.
        
        Args:
            limit: Maximum number of documents to return.
            
        Returns:
            All documents in the collection.
        """
        try:
            result = self.collection.get(
                limit=limit
            )
            logger.info(f"Retrieved {len(result['ids'])} documents")
            return result
        except Exception as e:
            logger.error(f"Error getting documents from ChromaDB: {str(e)}")
            raise
    
    def delete_collection(self) -> None:
        """Delete the entire collection.
        
        Warning: This operation cannot be undone.
        """
        try:
            self.client.delete_collection(name=self.collection_name)
            self._collection = None
            logger.warning(f"Collection deleted: {self.collection_name}")
        except Exception as e:
            logger.error(f"Error deleting collection: {str(e)}")
            raise
    
    @classmethod
    def get_instance(cls, collection_name: str = "marketing_agent_memory") -> "VectorDatabase":
        """Get or create a singleton instance of VectorDatabase.
        
        Args:
            collection_name: Name of the collection to use.
            
        Returns:
            VectorDatabase singleton instance.
        """
        if cls._instance is None:
            cls._instance = cls(collection_name=collection_name)
        return cls._instance

