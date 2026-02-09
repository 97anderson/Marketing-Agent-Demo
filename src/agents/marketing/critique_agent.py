"""Critique Agent - Evaluates posts against brand guidelines.

This agent reviews generated posts to ensure they meet brand voice guidelines
and quality standards. It can reject posts and provide feedback for rewrites.
"""

import json
import logging
import time

from src.gateway.inference_gateway import InferenceGateway
from src.shared.console import print_separator, safe_print
from src.shared.trace_logger import ActionType, StepStatus, get_trace_logger

logger = logging.getLogger(__name__)


class CritiqueAgent:
    """Critique Agent that evaluates posts against brand guidelines.

    This agent reviews the written post to ensure it follows brand voice
    guidelines, is appropriate in tone, and meets quality standards.

    Attributes:
        gateway: The Inference Gateway for LLM calls.
        name: Agent name for logging.
        pass_threshold: Minimum score to approve (0-10).
    """

    def __init__(self, gateway: InferenceGateway, pass_threshold: float = 8.0):
        """Initialize the Critique Agent.

        Args:
            gateway: Inference Gateway instance for LLM calls.
            pass_threshold: Minimum score (0-10) to approve the post.
        """
        self.gateway = gateway
        self.name = "CritiqueAgent"
        self.pass_threshold = pass_threshold
        logger.info(f"{self.name} initialized with threshold: {pass_threshold}")

    async def evaluate_post(
        self,
        content: str,
        topic: str,
        brand_voice: str | None = None,
        tone: str = "professional",
    ) -> tuple[bool, str, float]:
        """Evaluate the post against brand guidelines and quality standards.

        Args:
            content: The post content to evaluate.
            topic: The original topic.
            brand_voice: Optional brand voice guidelines to check against.
            tone: Expected tone.

        Returns:
            Tuple of (approved, feedback, score):
                - approved: Whether the post passes the criteria
                - feedback: Detailed feedback (empty if approved)
                - score: Overall score (0-10)
        """
        trace = get_trace_logger()
        start_time = time.time()

        # Log start
        trace.log_step(
            agent_name=self.name,
            action_type=ActionType.CRITIQUE,
            content=f"Evaluating post for topic: {topic}\nThreshold: {self.pass_threshold}/10",
            status=StepStatus.THINKING,
        )

        safe_print(f"\n{'='*80}")
        safe_print(f"🔍 {self.name}: Evaluating post...")
        safe_print(f"{'='*80}")
        safe_print(f"Pass threshold: {self.pass_threshold}/10")
        safe_print()

        prompt = self._create_critique_prompt(content, topic, brand_voice, tone)

        logger.info(f"{self.name}: Evaluating post for topic: {topic}")

        response = await self.gateway.generate(
            prompt=prompt,
            temperature=0.3,  # Lower temperature for consistent evaluation
            max_tokens=600,
            metadata={"agent": "critique", "topic": topic},
        )

        # Parse the evaluation
        evaluation = self._parse_evaluation(response.content)

        approved = evaluation["score"] >= self.pass_threshold
        score = evaluation["score"]
        feedback = evaluation["feedback"]
        duration = time.time() - start_time

        # Log result
        result_content = f"Score: {score}/10\n"
        result_content += f"Status: {'APPROVED' if approved else 'REJECTED'}\n"
        if not approved:
            result_content += f"\nFeedback:\n{feedback}"

        trace.log_step(
            agent_name=self.name,
            action_type=ActionType.CRITIQUE,
            content=result_content,
            status=StepStatus.SUCCESS if approved else StepStatus.WARNING,
            duration=duration,
            score=score,
            threshold=self.pass_threshold,
            approved=approved,
            tokens=response.usage.total_tokens,
        )

        safe_print(f"📊 {self.name}: Evaluation complete!")
        print_separator("-", 80)
        safe_print(f"Overall Score: {score}/10")
        safe_print(f"Status: {'✅ APPROVED' if approved else '❌ REJECTED'}")
        safe_print()

        if not approved:
            safe_print("📋 Feedback for Writer:")
            print_separator("-", 80)
            safe_print(feedback)
            print_separator("-", 80)
        else:
            safe_print("✓ Post meets all criteria!")

        safe_print(f"Token usage: {response.usage.total_tokens} tokens")
        safe_print()

        logger.info(f"{self.name}: Evaluation result - Score: {score}, " f"Approved: {approved}")

        return approved, feedback, score

    def _create_critique_prompt(
        self, content: str, topic: str, brand_voice: str | None, tone: str
    ) -> str:
        """Create the critique prompt for the LLM.

        Args:
            content: The post content to evaluate.
            topic: The original topic.
            brand_voice: Optional brand voice guidelines.
            tone: Expected tone.

        Returns:
            The formatted prompt.
        """
        brand_section = ""
        if brand_voice:
            brand_section = f"""
BRAND VOICE GUIDELINES TO CHECK AGAINST:
{brand_voice}

CRITICAL: Check if the post strictly follows these brand guidelines.
"""

        prompt = f"""You are a critical content reviewer for LinkedIn posts. Evaluate the following post rigorously.

ORIGINAL TOPIC: {topic}
EXPECTED TONE: {tone}
{brand_section}
POST TO EVALUATE:
---
{content}
---

Evaluate this post on the following criteria (score each 1-10):

1. BRAND ADHERENCE (if brand guidelines provided):
   - Does it follow the brand voice precisely?
   - Does it use the recommended hashtags and phrases?
   - Does it match the brand personality?

2. QUALITY:
   - Is the hook engaging?
   - Is the content well-structured?
   - Is the call-to-action clear?

3. TONE & LENGTH:
   - Is the tone appropriate?
   - Is the length suitable for LinkedIn?

Provide your evaluation in the following JSON format:
{{
  "score": <overall score 1-10>,
  "brand_adherence": <score 1-10>,
  "quality": <score 1-10>,
  "tone_length": <score 1-10>,
  "feedback": "<specific feedback on what needs improvement, be detailed>",
  "approved": <true/false based on score>
}}

Be strict. A score of 8+ means excellent quality. If score < 8, provide specific, actionable feedback.

EVALUATION:"""

        return prompt

    def _parse_evaluation(self, response_content: str) -> dict:
        """Parse the evaluation response from the LLM.

        Args:
            response_content: The raw response from the LLM.

        Returns:
            Parsed evaluation dictionary.
        """
        try:
            # Extract JSON from response
            start = response_content.find("{")
            end = response_content.rfind("}") + 1

            if start != -1 and end > start:
                json_str = response_content[start:end]
                evaluation = json.loads(json_str)

                # Calculate overall score if not provided
                if "score" not in evaluation:
                    scores = [
                        evaluation.get("brand_adherence", 7),
                        evaluation.get("quality", 7),
                        evaluation.get("tone_length", 7),
                    ]
                    evaluation["score"] = sum(scores) / len(scores)

                return evaluation

        except (json.JSONDecodeError, ValueError) as e:
            logger.warning(f"{self.name}: Failed to parse evaluation: {str(e)}")

        # Fallback: return neutral evaluation
        return {
            "score": 7.0,
            "brand_adherence": 7,
            "quality": 7,
            "tone_length": 7,
            "feedback": "Could not parse evaluation properly. Consider regenerating.",
            "approved": False,
        }
