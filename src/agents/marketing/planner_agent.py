"""Planner Agent - Generates outlines for LinkedIn posts.

This agent is responsible for creating structured outlines based on the topic,
context, and brand voice guidelines.
"""

import logging
import time

from src.gateway.inference_gateway import InferenceGateway
from src.shared.console import print_separator, safe_print
from src.shared.trace_logger import ActionType, StepStatus, get_trace_logger

logger = logging.getLogger(__name__)


class PlannerAgent:
    """Planner Agent that creates post outlines.

    This agent analyzes the topic, context, and brand guidelines to create
    a structured outline that the Writer Agent will use to create the post.

    Attributes:
        gateway: The Inference Gateway for LLM calls.
        name: Agent name for logging.
    """

    def __init__(self, gateway: InferenceGateway):
        """Initialize the Planner Agent.

        Args:
            gateway: Inference Gateway instance for LLM calls.
        """
        self.gateway = gateway
        self.name = "PlannerAgent"
        logger.info(f"{self.name} initialized")

    async def create_outline(
        self,
        topic: str,
        context: str,
        brand_voice: str | None = None,
        tone: str = "professional",
        max_length: int = 500,
    ) -> str:
        """Create a structured outline for the LinkedIn post.

        Args:
            topic: The topic for the post.
            context: Background context from research.
            brand_voice: Optional brand voice guidelines.
            tone: Desired tone of the post.
            max_length: Maximum length in characters.

        Returns:
            The outline as a string.
        """
        trace = get_trace_logger()
        start_time = time.time()

        # Log start
        trace.log_step(
            agent_name=self.name,
            action_type=ActionType.PLANNING,
            content=f"Starting outline creation\nTopic: {topic}\nTone: {tone}\nBrand Voice: {'Yes' if brand_voice else 'No'}",
            status=StepStatus.THINKING,
        )

        # Also print to console for backwards compatibility (optional)
        safe_print(f"\n{'='*80}")
        safe_print(f"🎯 {self.name}: Starting outline creation...")
        safe_print(f"{'='*80}")

        prompt = self._create_planning_prompt(topic, context, brand_voice, tone, max_length)

        logger.info(f"{self.name}: Generating outline for topic: {topic}")

        response = await self.gateway.generate(
            prompt=prompt,
            temperature=0.7,
            max_tokens=400,
            metadata={"agent": "planner", "topic": topic},
        )

        outline = response.content.strip()
        duration = time.time() - start_time

        # Log completion
        trace.log_step(
            agent_name=self.name,
            action_type=ActionType.PLANNING,
            content=f"Outline created:\n\n{outline}",
            status=StepStatus.SUCCESS,
            duration=duration,
            tokens=response.usage.total_tokens,
        )

        safe_print(f"📋 {self.name}: Outline created!")
        print_separator("-", 80)
        safe_print(outline)
        print_separator("-", 80)
        safe_print(f"Token usage: {response.usage.total_tokens} tokens")
        safe_print()

        logger.info(f"{self.name}: Outline created successfully")
        return outline

    def _create_planning_prompt(
        self, topic: str, context: str, brand_voice: str | None, tone: str, max_length: int
    ) -> str:
        """Create the planning prompt for the LLM.

        Args:
            topic: The topic for the post.
            context: Background context.
            brand_voice: Optional brand voice guidelines.
            tone: Desired tone.
            max_length: Maximum length.

        Returns:
            The formatted prompt.
        """
        brand_section = ""
        if brand_voice:
            brand_section = f"""
BRAND VOICE GUIDELINES:
{brand_voice}

You MUST consider these brand guidelines when planning the outline.
"""

        prompt = f"""You are a strategic content planner for LinkedIn posts. Your job is to create a detailed outline that a writer will follow.

TOPIC: {topic}

CONTEXT/RESEARCH:
{context}
{brand_section}
REQUIREMENTS:
- Tone: {tone}
- Target length: {max_length} characters
- Platform: LinkedIn (professional network)

Create a structured outline with:
1. Hook/Opening (1 sentence) - How to grab attention
2. Main Points (2-3 key ideas) - What to cover
3. Call-to-Action (1 sentence) - How to engage readers
4. Hashtags (3-5 relevant tags) - Which hashtags to use

Format your outline clearly with bullet points. Be specific about what each section should communicate.

OUTLINE:"""

        return prompt
