"""Demo: Multi-Agent Workflow with Brand Voice.

This example demonstrates the multi-agent workflow where:
1. PlannerAgent creates an outline
2. WriterAgent generates the post
3. CritiqueAgent evaluates and potentially rejects
4. WriterAgent rewrites if needed

Run this to see the agent collaboration in action!
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.agents.marketing.agent import MarketingAgent
from src.agents.marketing.models import GeneratePostRequest
from src.shared.console import print_separator, safe_print


async def demo_multi_agent_without_brand():
    """Demo: Multi-agent workflow without brand voice."""
    safe_print("\n" + "=" * 100)
    safe_print("DEMO 1: Multi-Agent Workflow WITHOUT Brand Voice")
    safe_print("=" * 100)

    # Initialize agent in multi-agent mode
    agent = MarketingAgent(
        use_multi_agent=True,
        critique_threshold=8.0,  # Require score of 8/10 to approve
        max_rewrites=2,  # Allow up to 2 rewrites
    )

    # Generate a post
    request = GeneratePostRequest(
        topic="The future of AI in software development",
        tone="professional",
        max_length=500,
    )

    result = await agent.generate_post(request)

    safe_print("\n" + "=" * 100)
    safe_print("FINAL RESULT")
    safe_print("=" * 100)
    safe_print(f"\nPost ID: {result.id}")
    safe_print(f"Topic: {result.topic}")
    safe_print(f"Tone: {result.tone}")
    safe_print("\nGenerated Content:")
    print_separator("-", 100)
    safe_print(result.content)
    print_separator("-", 100)

    if hasattr(result, "metadata") and result.metadata:
        safe_print("\nWorkflow Metadata:")
        safe_print(f"  - Iterations: {result.metadata.get('iterations', 'N/A')}")
        safe_print(f"  - Final Score: {result.metadata.get('final_score', 'N/A')}/10")


async def demo_multi_agent_with_brand():
    """Demo: Multi-agent workflow with brand voice."""
    safe_print("\n" + "=" * 100)
    safe_print("DEMO 2: Multi-Agent Workflow WITH Brand Voice (TechCorp)")
    safe_print("=" * 100)

    # Initialize agent in multi-agent mode
    agent = MarketingAgent(
        use_multi_agent=True,
        critique_threshold=8.5,  # Higher threshold with brand voice
        max_rewrites=2,
    )

    # Generate a post with brand voice
    request = GeneratePostRequest(
        topic="Cloud computing cost optimization strategies",
        tone="professional",
        max_length=500,
        brand_id="techcorp",  # Apply TechCorp brand voice
    )

    result = await agent.generate_post(request)

    print("\n" + "=" * 100)
    print("FINAL RESULT")
    print("=" * 100)
    print(f"\nPost ID: {result.id}")
    print(f"Topic: {result.topic}")
    print(f"Brand: {result.brand_id}")
    print(f"Tone: {result.tone}")
    print("\nGenerated Content:")
    print("-" * 100)
    print(result.content)
    print("-" * 100)

    if hasattr(result, "metadata") and result.metadata:
        print("\nWorkflow Metadata:")
        print(f"  - Iterations: {result.metadata.get('iterations', 'N/A')}")
        print(f"  - Final Score: {result.metadata.get('final_score', 'N/A')}/10")


async def demo_multi_agent_strict_brand():
    """Demo: Multi-agent workflow with strict brand requirements (likely to trigger rewrites)."""
    safe_print("\n" + "=" * 100)
    safe_print("DEMO 3: Multi-Agent Workflow with STRICT Brand Requirements (EcoLife)")
    safe_print("=" * 100)
    safe_print("This demo uses a high critique threshold to demonstrate rewrite loops")
    safe_print("=" * 100)

    # Initialize agent in multi-agent mode with very strict criteria
    agent = MarketingAgent(
        use_multi_agent=True,
        critique_threshold=9.0,  # Very high threshold - likely to trigger rewrites
        max_rewrites=3,  # Allow more rewrites
    )

    # Generate a post with brand voice
    request = GeneratePostRequest(
        topic="Sustainable packaging innovations for e-commerce",
        tone="inspirational",
        max_length=500,
        brand_id="ecolife",  # Apply EcoLife brand voice
    )

    result = await agent.generate_post(request)

    safe_print("\n" + "=" * 100)
    safe_print("FINAL RESULT")
    safe_print("=" * 100)
    safe_print(f"\nPost ID: {result.id}")
    safe_print(f"Topic: {result.topic}")
    safe_print(f"Brand: {result.brand_id}")
    safe_print(f"Tone: {result.tone}")
    safe_print("\nGenerated Content:")
    print_separator("-", 100)
    safe_print(result.content)
    print_separator("-", 100)

    if hasattr(result, "metadata") and result.metadata:
        safe_print("\nWorkflow Metadata:")
        safe_print(f"  - Iterations: {result.metadata.get('iterations', 'N/A')}")
        safe_print(f"  - Final Score: {result.metadata.get('final_score', 'N/A')}/10")
        safe_print(f"  - Approved: {result.metadata.get('final_score', 0) >= 9.0}")


async def main():
    """Run all demos."""
    safe_print("\n" + "#" * 100)
    safe_print("MULTI-AGENT WORKFLOW DEMONSTRATION")
    safe_print("#" * 100)
    safe_print(
        "\nThis demo shows how multiple agents collaborate to generate high-quality content:"
    )
    safe_print("  1. PlannerAgent - Creates a structured outline")
    safe_print("  2. WriterAgent - Writes the post based on the outline")
    safe_print("  3. CritiqueAgent - Evaluates quality and brand adherence")
    safe_print("  4. WriterAgent - Rewrites if rejected by critique")
    safe_print("\n" + "#" * 100)

    try:
        # Demo 1: Basic multi-agent workflow
        await demo_multi_agent_without_brand()

        safe_print("\n" + "=" * 100)
        input("Press Enter to continue to Demo 2...")

        # Demo 2: Multi-agent with brand voice
        await demo_multi_agent_with_brand()

        safe_print("\n" + "=" * 100)
        input("Press Enter to continue to Demo 3 (may take longer)...")

        # Demo 3: Strict criteria to demonstrate rewrites
        await demo_multi_agent_strict_brand()

        safe_print("\n" + "#" * 100)
        safe_print("ALL DEMOS COMPLETED!")
        safe_print("#" * 100)

    except FileNotFoundError as e:
        safe_print(f"\nError: {e}")
        safe_print("\nMake sure brand voice files exist in the knowledge_base/ folder.")
    except Exception as e:
        safe_print(f"\nUnexpected error: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
