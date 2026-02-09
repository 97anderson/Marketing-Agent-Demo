"""Multi-Agent Flow Orchestrator.

This module orchestrates the collaboration between multiple agents to generate
high-quality LinkedIn posts through a structured workflow.
"""

import logging
from datetime import datetime

from src.agents.marketing.critique_agent import CritiqueAgent
from src.agents.marketing.planner_agent import PlannerAgent
from src.agents.marketing.writer_agent import WriterAgent
from src.gateway.inference_gateway import InferenceGateway
from src.shared.console import safe_print
from src.shared.trace_logger import ActionType, StepStatus, get_trace_logger

logger = logging.getLogger(__name__)


class MultiAgentFlow:
    """Orchestrates a multi-agent workflow for content generation.

    This class manages the collaboration between Planner, Writer, and Critique
    agents to produce high-quality, brand-consistent LinkedIn posts.

    The workflow:
    1. Planner creates an outline
    2. Writer generates the post
    3. Critique evaluates the post
    4. If rejected, Writer rewrites (loop)
    5. Return approved post

    Attributes:
        planner: The Planner Agent.
        writer: The Writer Agent.
        critique: The Critique Agent.
        max_rewrites: Maximum number of rewrite attempts.
    """

    def __init__(
        self,
        gateway: InferenceGateway,
        critique_threshold: float = 8.0,
        max_rewrites: int = 2,
    ):
        """Initialize the Multi-Agent Flow.

        Args:
            gateway: Inference Gateway instance for LLM calls.
            critique_threshold: Minimum score for approval (0-10).
            max_rewrites: Maximum number of rewrite attempts.
        """
        self.planner = PlannerAgent(gateway)
        self.writer = WriterAgent(gateway)
        self.critique = CritiqueAgent(gateway, pass_threshold=critique_threshold)
        self.max_rewrites = max_rewrites

        logger.info(
            f"MultiAgentFlow initialized with threshold={critique_threshold}, "
            f"max_rewrites={max_rewrites}"
        )

    async def generate_post(
        self,
        topic: str,
        context: str,
        brand_voice: str | None = None,
        tone: str = "professional",
        max_length: int = 500,
    ) -> dict:
        """Generate a LinkedIn post using the multi-agent workflow.

        Args:
            topic: The topic for the post.
            context: Background context from research.
            brand_voice: Optional brand voice guidelines.
            tone: Desired tone of the post.
            max_length: Maximum length in characters.

        Returns:
            Dictionary with:
                - content: The final approved post
                - outline: The outline used
                - iterations: Number of write/rewrite cycles
                - final_score: The critique score
                - workflow_summary: Summary of the agent interactions
        """
        start_time = datetime.now()
        trace = get_trace_logger()

        # Start workflow tracking
        trace.start_workflow(
            topic=topic,
            tone=tone,
            threshold=self.critique.pass_threshold,
            max_rewrites=self.max_rewrites,
            brand_voice=brand_voice is not None,
        )

        # Log workflow start
        trace.log_step(
            agent_name="MultiAgentFlow",
            action_type=ActionType.INFO,
            content=f"Starting multi-agent workflow\nTopic: {topic}\nThreshold: {self.critique.pass_threshold}/10\nMax Rewrites: {self.max_rewrites}",
            status=StepStatus.THINKING,
        )

        safe_print(f"\n{'#'*80}")
        safe_print("🚀 MULTI-AGENT WORKFLOW STARTED")
        safe_print(f"{'#'*80}")
        safe_print(f"Topic: {topic}")
        safe_print(f"Critique Threshold: {self.critique.pass_threshold}/10")
        safe_print(f"Max Rewrites: {self.max_rewrites}")
        safe_print(f"{'#'*80}\n")

        # Step 1: Planner creates outline
        logger.info("Starting Phase 1: Planning")
        outline = await self.planner.create_outline(
            topic=topic,
            context=context,
            brand_voice=brand_voice,
            tone=tone,
            max_length=max_length,
        )

        # Step 2: Writer generates initial post
        logger.info("Starting Phase 2: Writing")
        content = await self.writer.write_post(
            topic=topic,
            outline=outline,
            brand_voice=brand_voice,
            tone=tone,
            max_length=max_length,
            is_rewrite=False,
        )

        # Step 3: Critique and potential rewrites
        logger.info("Starting Phase 3: Critique and Refinement")
        iterations = 1
        final_score = 0.0
        workflow_log = []

        for attempt in range(self.max_rewrites + 1):
            # Critique the post
            approved, feedback, score = await self.critique.evaluate_post(
                content=content,
                topic=topic,
                brand_voice=brand_voice,
                tone=tone,
            )

            final_score = score

            workflow_log.append(
                {
                    "iteration": attempt + 1,
                    "action": "initial_write" if attempt == 0 else "rewrite",
                    "score": score,
                    "approved": approved,
                }
            )

            if approved:
                safe_print(f"\n{'='*80}")
                safe_print(f"✅ POST APPROVED after {iterations} iteration(s)!")
                safe_print(f"{'='*80}\n")
                logger.info(f"Post approved after {iterations} iterations")
                break

            if attempt < self.max_rewrites:
                # Need to rewrite
                safe_print(f"\n{'='*80}")
                safe_print(
                    f"🔄 Iteration {attempt + 2}/{self.max_rewrites + 1}: Requesting rewrite..."
                )
                safe_print(f"{'='*80}\n")

                logger.info(f"Iteration {attempt + 2}: Requesting rewrite")
                iterations += 1

                content = await self.writer.write_post(
                    topic=topic,
                    outline=outline,
                    brand_voice=brand_voice,
                    tone=tone,
                    max_length=max_length,
                    is_rewrite=True,
                    critique_feedback=feedback,
                )
            else:
                # Max rewrites reached
                safe_print(f"\n{'='*80}")
                safe_print(f"⚠️  Maximum rewrites ({self.max_rewrites}) reached!")
                safe_print(f"Using best version (score: {score}/10)")
                safe_print(f"{'='*80}\n")
                logger.warning(f"Maximum rewrites reached. Using score: {score}")
                break

        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

        # End workflow tracking
        trace.end_workflow(
            iterations=iterations,
            final_score=final_score,
            approved=final_score >= self.critique.pass_threshold,
            duration=duration,
        )

        # Log workflow completion
        trace.log_step(
            agent_name="MultiAgentFlow",
            action_type=ActionType.INFO,
            content=f"Workflow completed\nIterations: {iterations}\nFinal Score: {final_score}/10\nStatus: {'APPROVED' if final_score >= self.critique.pass_threshold else 'APPROVED WITH RESERVATIONS'}\nDuration: {duration:.2f}s",
            status=StepStatus.SUCCESS
            if final_score >= self.critique.pass_threshold
            else StepStatus.WARNING,
            duration=duration,
        )

        # Summary
        safe_print(f"\n{'#'*80}")
        safe_print("🏁 MULTI-AGENT WORKFLOW COMPLETED")
        safe_print(f"{'#'*80}")
        safe_print(f"Total Iterations: {iterations}")
        safe_print(f"Final Score: {final_score}/10")
        safe_print(
            f"Status: {'✅ Approved' if final_score >= self.critique.pass_threshold else '⚠️  Approved with reservations'}"
        )
        safe_print(f"Duration: {duration:.2f} seconds")
        safe_print(f"{'#'*80}\n")

        return {
            "content": content,
            "outline": outline,
            "iterations": iterations,
            "final_score": final_score,
            "workflow_summary": workflow_log,
            "duration_seconds": duration,
            "approved": final_score >= self.critique.pass_threshold,
        }
