"""Marketing Agent Implementation.

This module implements the Content-Creator agent for generating LinkedIn posts.
"""

import logging
import uuid
from datetime import datetime

from src.agents.marketing.models import GeneratedPost, GeneratePostRequest
from src.agents.marketing.tools import WebSearchTool
from src.gateway.inference_gateway import InferenceGateway
from src.shared.database import VectorDatabase


logger = logging.getLogger(__name__)


class MarketingAgent:
    """Content-Creator Agent for generating LinkedIn posts.

    This agent:
    - Takes a topic as input
    - Searches for information using simulated tools
    - Generates a LinkedIn post using the Inference Gateway
    - Saves the post to ChromaDB for memory

    Attributes:
        gateway: The Inference Gateway for LLM calls.
        search_tool: The web search tool for gathering context.
        database: The vector database for storing generated posts.
    """

    def __init__(
        self,
        gateway: InferenceGateway | None = None,
        database: VectorDatabase | None = None
    ):
        """Initialize the Marketing Agent.

        Args:
            gateway: Inference Gateway instance (creates default if None).
            database: Vector database instance (creates default if None).
        """
        self.gateway = gateway or InferenceGateway.from_settings()
        self.search_tool = WebSearchTool()
        self.database = database or VectorDatabase.get_instance()

        logger.info("MarketingAgent initialized")

    async def generate_post(
        self,
        request: GeneratePostRequest
    ) -> GeneratedPost:
        """Generate a LinkedIn post on the given topic.

        This method:
        1. Searches for information about the topic
        2. Constructs a prompt with the context
        3. Calls the LLM through the Inference Gateway
        4. Saves the result to ChromaDB

        Args:
            request: The post generation request.

        Returns:
            The generated post with metadata.
        """
        logger.info(f"Generating post for topic: {request.topic}")

        # Step 1: Search for information
        search_results = await self.search_tool.search(request.topic)

        # Step 2: Build context from search results
        context = self._build_context(search_results)

        # Step 3: Create the prompt
        prompt = self._create_prompt(
            topic=request.topic,
            context=context,
            tone=request.tone,
            max_length=request.max_length
        )

        # Step 4: Generate content using the Inference Gateway
        logger.info("Calling Inference Gateway for content generation")
        response = await self.gateway.generate(
            prompt=prompt,
            temperature=0.7,
            max_tokens=800,
            metadata={
                "agent": "marketing_agent",
                "topic": request.topic,
                "tone": request.tone
            }
        )

        # Step 5: Create the post object
        post_id = str(uuid.uuid4())
        post = GeneratedPost(
            id=post_id,
            topic=request.topic,
            content=response.content,
            tone=request.tone,
            usage=response.usage,
            created_at=datetime.utcnow()
        )

        # Step 6: Save to ChromaDB for memory
        self._save_to_memory(post)

        logger.info(f"Post generated successfully with ID: {post_id}")
        return post

    def _build_context(self, search_results: list) -> str:
        """Build context string from search results.

        Args:
            search_results: List of web search results.

        Returns:
            Formatted context string.
        """
        context_parts = []

        for result in search_results:
            context_parts.append(
                f"- {result.title}\n  {result.snippet}\n  Source: {result.url}"
            )

        return "\n\n".join(context_parts)

    def _create_prompt(
        self,
        topic: str,
        context: str,
        tone: str,
        max_length: int
    ) -> str:
        """Create the prompt for the LLM.

        Args:
            topic: The topic for the post.
            context: Background context from search.
            tone: Desired tone of the post.
            max_length: Maximum length in characters.

        Returns:
            The formatted prompt.
        """
        prompt = f"""You are a professional LinkedIn content creator. Your task is to write an engaging LinkedIn post.

Topic: {topic}

Background Information:
{context}

Requirements:
- Tone: {tone}
- Maximum length: {max_length} characters
- Include relevant hashtags
- Make it engaging and professional
- Use emojis sparingly and appropriately
- Structure: Hook, main content, call-to-action

Write a compelling LinkedIn post that will drive engagement:"""

        return prompt

    def _save_to_memory(self, post: GeneratedPost) -> None:
        """Save the generated post to ChromaDB.

        Args:
            post: The generated post to save.
        """
        try:
            metadata = {
                "topic": post.topic,
                "tone": post.tone,
                "created_at": post.created_at.isoformat(),
                "prompt_tokens": post.usage.prompt_tokens,
                "completion_tokens": post.usage.completion_tokens,
                "total_tokens": post.usage.total_tokens
            }

            self.database.add_document(
                document=post.content,
                document_id=post.id,
                metadata=metadata
            )

            logger.info(f"Post saved to ChromaDB: {post.id}")

        except Exception as e:
            logger.error(f"Failed to save post to memory: {str(e)}")
            # Don't fail the request if memory save fails

    def get_history(self, limit: int = 10) -> list[GeneratedPost]:
        """Get the history of generated posts from ChromaDB.

        Args:
            limit: Maximum number of posts to return.

        Returns:
            List of previously generated posts.
        """
        logger.info(f"Retrieving post history (limit: {limit})")

        try:
            results = self.database.get_all_documents(limit=limit)

            posts = []

            # Convert ChromaDB results to GeneratedPost objects
            for i, doc_id in enumerate(results["ids"]):
                metadata = results["metadatas"][i] if results["metadatas"] else {}
                document = results["documents"][i] if results["documents"] else ""

                # Reconstruct the post
                post = GeneratedPost(
                    id=doc_id,
                    topic=metadata.get("topic", "Unknown"),
                    content=document,
                    tone=metadata.get("tone", "professional"),
                    usage={
                        "prompt_tokens": metadata.get("prompt_tokens", 0),
                        "completion_tokens": metadata.get("completion_tokens", 0),
                        "total_tokens": metadata.get("total_tokens", 0)
                    },
                    created_at=datetime.fromisoformat(
                        metadata.get("created_at", datetime.utcnow().isoformat())
                    )
                )

                posts.append(post)

            logger.info(f"Retrieved {len(posts)} posts from history")
            return posts

        except Exception as e:
            logger.error(f"Failed to retrieve post history: {str(e)}")
            return []
