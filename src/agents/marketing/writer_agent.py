"""Writer Agent - Generates LinkedIn post content from outlines.

This agent takes an outline and creates the actual post content following
the structure and guidelines provided.
"""

import logging
import time

from src.gateway.inference_gateway import InferenceGateway
from src.shared.console import print_separator, safe_print
from src.shared.trace_logger import ActionType, StepStatus, get_trace_logger

logger = logging.getLogger(__name__)


class WriterAgent:
    """Writer Agent that creates post content from outlines.

    This agent takes the outline from the Planner and creates the actual
    LinkedIn post content, following brand guidelines strictly.

    Attributes:
        gateway: The Inference Gateway for LLM calls.
        name: Agent name for logging.
    """

    def __init__(self, gateway: InferenceGateway):
        """Initialize the Writer Agent.

        Args:
            gateway: Inference Gateway instance for LLM calls.
        """
        self.gateway = gateway
        self.name = "WriterAgent"
        logger.info(f"{self.name} initialized")

    async def write_post(
        self,
        topic: str,
        outline: str,
        brand_voice: str | None = None,
        tone: str = "professional",
        max_length: int = 500,
        is_rewrite: bool = False,
        critique_feedback: str | None = None,
    ) -> str:
        """Write the LinkedIn post based on the outline.

        Args:
            topic: The topic for the post.
            outline: The outline from the Planner.
            brand_voice: Optional brand voice guidelines.
            tone: Desired tone of the post.
            max_length: Maximum length in characters.
            is_rewrite: Whether this is a rewrite after critique.
            critique_feedback: Feedback from the Critique Agent (for rewrites).

        Returns:
            The written post content.
        """
        trace = get_trace_logger()
        start_time = time.time()

        action = "Rewriting" if is_rewrite else "Writing"
        action_type = ActionType.REWRITE if is_rewrite else ActionType.GENERATION

        # Log start
        step_content = f"{action} post for topic: {topic}"
        if is_rewrite and critique_feedback:
            step_content += f"\n\nAddressing feedback:\n{critique_feedback[:200]}..."

        trace.log_step(
            agent_name=self.name,
            action_type=action_type,
            content=step_content,
            status=StepStatus.THINKING,
        )

        safe_print(f"\n{'='*80}")
        safe_print(f"✍️  {self.name}: {action} post...")
        safe_print(f"{'='*80}")

        if is_rewrite and critique_feedback:
            safe_print("📝 Addressing critique feedback:")
            print_separator("-", 80)
            safe_print(critique_feedback)
            print_separator("-", 80)
            safe_print()

        prompt = self._create_writing_prompt(
            topic, outline, brand_voice, tone, max_length, is_rewrite, critique_feedback
        )

        logger.info(f"{self.name}: Generating post content (rewrite={is_rewrite})")

        response = await self.gateway.generate(
            prompt=prompt,
            temperature=0.7,
            max_tokens=800,
            metadata={
                "agent": "writer",
                "topic": topic,
                "is_rewrite": str(is_rewrite),
            },
        )

        content = response.content.strip()
        duration = time.time() - start_time

        # Log completion
        trace.log_step(
            agent_name=self.name,
            action_type=action_type,
            content=f"Post {'rewritten' if is_rewrite else 'written'}:\n\n{content}",
            status=StepStatus.SUCCESS,
            duration=duration,
            tokens=response.usage.total_tokens,
            length=len(content),
        )

        safe_print(f"📄 {self.name}: Post {'rewritten' if is_rewrite else 'written'}!")
        print_separator("-", 80)
        safe_print(content)
        print_separator("-", 80)
        safe_print(f"Length: {len(content)} characters")
        safe_print(f"Token usage: {response.usage.total_tokens} tokens")
        safe_print()

        logger.info(f"{self.name}: Post content generated successfully")
        return content

    def _create_writing_prompt(
        self,
        topic: str,
        outline: str,
        brand_voice: str | None,
        tone: str,
        max_length: int,
        is_rewrite: bool,
        critique_feedback: str | None,
    ) -> str:
        """Create the writing prompt for the LLM.

        Args:
            topic: The topic for the post.
            outline: The outline to follow.
            brand_voice: Optional brand voice guidelines.
            tone: Desired tone.
            max_length: Maximum length.
            is_rewrite: Whether this is a rewrite.
            critique_feedback: Feedback from critique (if rewrite).

        Returns:
            The formatted prompt.
        """
        brand_section = ""
        if brand_voice:
            brand_section = f"""
BRAND VOICE GUIDELINES (FOLLOW STRICTLY):
{brand_voice}

You MUST adhere to these brand guidelines precisely.
"""

        rewrite_section = ""
        if is_rewrite and critique_feedback:
            rewrite_section = f"""
CRITIQUE FEEDBACK (ADDRESS ALL POINTS):
{critique_feedback}

This is a rewrite. You MUST address all the critique feedback above.
"""

        action = "Rewrite" if is_rewrite else "Write"

        prompt = f"""You are a professional LinkedIn content writer. {f"{action} the following post." if is_rewrite else "Create an engaging LinkedIn post."}

TOPIC: {topic}

OUTLINE TO FOLLOW:
{outline}
{brand_section}{rewrite_section}
REQUIREMENTS:
- Tone: {tone}
- Maximum length: {max_length} characters
- Follow the outline structure precisely
- Make it engaging and professional
- Include relevant emojis if appropriate
- End with the specified call-to-action and hashtags

{action.upper()} THE POST:"""

        return prompt
