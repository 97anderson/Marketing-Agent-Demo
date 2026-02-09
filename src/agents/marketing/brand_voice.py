"""Brand Voice Management Module.

This module handles loading and managing brand voice guidelines for the marketing agent.
Implements a simple RAG approach: direct file reading for small files, ChromaDB for large ones.
"""

import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class BrandVoiceManager:
    """Manages brand voice guidelines for content generation.

    This class implements a simple RAG (Retrieval-Augmented Generation) approach:
    - For small files (<10KB): Direct file reading
    - For large files (>10KB): Could use ChromaDB for chunking and retrieval

    Attributes:
        knowledge_base_dir: Directory containing brand voice files.
        max_file_size_kb: Maximum file size for direct reading (default: 10KB).
    """

    def __init__(self, knowledge_base_dir: str = "knowledge_base", max_file_size_kb: int = 10):
        """Initialize the Brand Voice Manager.

        Args:
            knowledge_base_dir: Path to directory containing brand voice files.
            max_file_size_kb: Maximum file size in KB for direct reading.
        """
        self.knowledge_base_dir = Path(knowledge_base_dir)
        self.max_file_size_kb = max_file_size_kb
        self.max_file_size_bytes = max_file_size_kb * 1024

        logger.info(f"BrandVoiceManager initialized with dir: {self.knowledge_base_dir}")

    def get_brand_voice(self, brand_id: str) -> str:
        """Get brand voice guidelines for a specific brand.

        Args:
            brand_id: The brand identifier (e.g., 'techcorp', 'ecolife').

        Returns:
            The brand voice guidelines as a string.

        Raises:
            FileNotFoundError: If brand voice file doesn't exist.
            ValueError: If brand_id is empty.
        """
        if not brand_id:
            raise ValueError("brand_id cannot be empty")

        # Normalize brand_id to lowercase
        brand_id = brand_id.lower().strip()

        # Construct file path
        file_path = self.knowledge_base_dir / f"{brand_id}_brand_voice.txt"

        if not file_path.exists():
            available_brands = self.list_available_brands()
            logger.error(f"Brand voice file not found for: {brand_id}")
            raise FileNotFoundError(
                f"Brand voice file not found for '{brand_id}'. "
                f"Available brands: {', '.join(available_brands)}"
            )

        # Check file size
        file_size = file_path.stat().st_size

        if file_size > self.max_file_size_bytes:
            logger.info(
                f"File size ({file_size} bytes) exceeds threshold, " f"using chunked retrieval"
            )
            return self._load_large_file(file_path, brand_id)
        else:
            logger.info(f"Loading brand voice directly from file: {file_path.name}")
            return self._load_small_file(file_path)

    def _load_small_file(self, file_path: Path) -> str:
        """Load brand voice from a small file directly.

        Args:
            file_path: Path to the brand voice file.

        Returns:
            The complete file content.
        """
        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()

            logger.info(f"Successfully loaded brand voice: {len(content)} characters")
            return content

        except Exception as e:
            logger.error(f"Error reading brand voice file: {str(e)}")
            raise

    def _load_large_file(self, file_path: Path, brand_id: str) -> str:
        """Load brand voice from a large file using ChromaDB for chunking.

        For files larger than the threshold, this method would:
        1. Chunk the file into smaller pieces
        2. Store in ChromaDB with embeddings
        3. Retrieve relevant chunks based on query

        Currently implements simple direct reading as files are expected to be small.

        Args:
            file_path: Path to the brand voice file.
            brand_id: Brand identifier.

        Returns:
            The file content (or relevant chunks in future implementation).
        """
        logger.warning(
            f"Large file detected ({file_path.name}). "
            f"Consider implementing ChromaDB chunking for better performance."
        )

        # For now, still read directly but log a warning
        # In production, implement proper chunking and retrieval
        return self._load_small_file(file_path)

    def list_available_brands(self) -> list[str]:
        """List all available brands in the knowledge base.

        Returns:
            List of brand identifiers.
        """
        if not self.knowledge_base_dir.exists():
            logger.warning(f"Knowledge base directory does not exist: {self.knowledge_base_dir}")
            return []

        brand_files = list(self.knowledge_base_dir.glob("*_brand_voice.txt"))
        brands = [f.stem.replace("_brand_voice", "") for f in brand_files]

        logger.info(f"Found {len(brands)} brands: {brands}")
        return brands

    def validate_brand_exists(self, brand_id: str) -> bool:
        """Check if a brand voice file exists for the given brand.

        Args:
            brand_id: The brand identifier to check.

        Returns:
            True if brand voice exists, False otherwise.
        """
        if not brand_id:
            return False

        brand_id = brand_id.lower().strip()
        file_path = self.knowledge_base_dir / f"{brand_id}_brand_voice.txt"
        return file_path.exists()

    def get_brand_summary(self, brand_id: str) -> dict[str, str]:
        """Get a summary of brand voice guidelines.

        Extracts key information from the brand voice file.

        Args:
            brand_id: The brand identifier.

        Returns:
            Dictionary with brand summary information.
        """
        try:
            content = self.get_brand_voice(brand_id)

            # Extract company overview (first few lines after header)
            lines = content.split("\n")
            overview = ""
            for i, line in enumerate(lines):
                if "Company Overview" in line and i + 1 < len(lines):
                    overview = lines[i + 1].strip()
                    break

            return {
                "brand_id": brand_id,
                "overview": overview,
                "guidelines_length": len(content),
                "available": True,
            }

        except Exception as e:
            logger.error(f"Error getting brand summary: {str(e)}")
            return {
                "brand_id": brand_id,
                "overview": "Not available",
                "guidelines_length": 0,
                "available": False,
            }
