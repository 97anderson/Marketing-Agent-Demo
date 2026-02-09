"""Compare Single-Agent vs Multi-Agent Workflows.

This script runs the same request through both workflows to compare:
- Output quality
- Process transparency
- Token usage
- Execution time
"""

import asyncio
import sys
from pathlib import Path
from time import time

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.agents.marketing.agent import MarketingAgent
from src.agents.marketing.models import GeneratePostRequest


async def run_single_agent(topic: str, brand_id: str | None = None):
    """Run the single-agent workflow."""
    print("\n" + "=" * 100)
    print("SINGLE-AGENT WORKFLOW")
    print("=" * 100)

    agent = MarketingAgent(use_multi_agent=False)

    request = GeneratePostRequest(
        topic=topic,
        tone="professional",
        max_length=500,
        brand_id=brand_id,
    )

    start = time()
    result = await agent.generate_post(request)
    duration = time() - start

    print("\n" + "-" * 100)
    print("RESULT:")
    print("-" * 100)
    print(result.content)
    print("-" * 100)
    print(f"Duration: {duration:.2f} seconds")
    print(f"Tokens: {result.usage.get('total_tokens', 'N/A')}")
    print()

    return result, duration


async def run_multi_agent(topic: str, brand_id: str | None = None):
    """Run the multi-agent workflow."""
    print("\n" + "=" * 100)
    print("MULTI-AGENT WORKFLOW")
    print("=" * 100)

    agent = MarketingAgent(
        use_multi_agent=True,
        critique_threshold=8.0,
        max_rewrites=2,
    )

    request = GeneratePostRequest(
        topic=topic,
        tone="professional",
        max_length=500,
        brand_id=brand_id,
    )

    start = time()
    result = await agent.generate_post(request)
    duration = time() - start

    print("\n" + "-" * 100)
    print("RESULT:")
    print("-" * 100)
    print(result.content)
    print("-" * 100)
    print(f"Duration: {duration:.2f} seconds")

    if hasattr(result, "metadata") and result.metadata:
        print(f"Iterations: {result.metadata.get('iterations', 'N/A')}")
        print(f"Final Score: {result.metadata.get('final_score', 'N/A')}/10")

    print()

    return result, duration


async def compare_workflows():
    """Compare both workflows side by side."""
    topic = "The impact of remote work on team collaboration"
    brand_id = "techcorp"

    print("\n" + "#" * 100)
    print("WORKFLOW COMPARISON")
    print("#" * 100)
    print(f"\nTopic: {topic}")
    print(f"Brand: {brand_id}")
    print("\n" + "#" * 100)

    # Run both workflows
    single_result, single_duration = await run_single_agent(topic, brand_id)
    multi_result, multi_duration = await run_multi_agent(topic, brand_id)

    # Summary comparison
    print("\n" + "=" * 100)
    print("COMPARISON SUMMARY")
    print("=" * 100)

    print("\nSingle-Agent:")
    print(f"  - Duration: {single_duration:.2f}s")
    print(f"  - Tokens: {single_result.usage.get('total_tokens', 'N/A')}")
    print("  - Process: Direct generation")

    print("\nMulti-Agent:")
    print(f"  - Duration: {multi_duration:.2f}s")
    iterations = (
        multi_result.metadata.get("iterations", 1) if hasattr(multi_result, "metadata") else 1
    )
    score = (
        multi_result.metadata.get("final_score", "N/A")
        if hasattr(multi_result, "metadata")
        else "N/A"
    )
    print(f"  - Iterations: {iterations}")
    print(f"  - Final Score: {score}/10")
    print("  - Process: Plan → Write → Critique → Rewrite (if needed)")

    print("\nKey Differences:")
    print(f"  ✓ Multi-agent provides quality score: {score}/10")
    print("  ✓ Multi-agent shows agent reasoning (visible in logs)")
    print("  ✓ Multi-agent has built-in quality control")
    print(f"  ✓ Single-agent is faster: {single_duration:.2f}s vs {multi_duration:.2f}s")

    print("\n" + "=" * 100)


if __name__ == "__main__":
    asyncio.run(compare_workflows())
