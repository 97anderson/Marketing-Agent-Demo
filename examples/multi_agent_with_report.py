"""Demo: Multi-Agent Workflow with HTML Report Generation.

This example demonstrates the multi-agent workflow and generates
a beautiful HTML report at the end instead of showing logs in console.
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.agents.marketing.agent import MarketingAgent
from src.agents.marketing.models import GeneratePostRequest
from src.shared.html_reporter import generate_report
from src.shared.trace_logger import get_trace_logger


async def run_with_html_report():
    """Run multi-agent workflow and generate HTML report."""
    print("\n" + "=" * 80)
    print("MULTI-AGENT WORKFLOW WITH HTML REPORT")
    print("=" * 80)
    print("\nExecuting workflow... (logs will be in HTML report)")
    print()

    # Reset trace logger for clean execution
    trace = get_trace_logger()
    trace.reset()

    # Initialize agent in multi-agent mode
    agent = MarketingAgent(
        use_multi_agent=True,
        critique_threshold=8.0,
        max_rewrites=2,
    )

    # Generate a post
    request = GeneratePostRequest(
        topic="The future of AI in software development",
        tone="professional",
        max_length=500,
        brand_id="techcorp",  # With brand voice
    )

    print(f"[+] Generating post about: {request.topic}")
    print(f"[Brand] {request.brand_id}")
    print()

    result = await agent.generate_post(request)

    print("[OK] Post generated successfully!")
    print(f"   - ID: {result.id}")
    print(f"   - Length: {len(result.content)} characters")

    if hasattr(result, "metadata") and result.metadata:
        print(f"   - Iterations: {result.metadata.get('iterations', 'N/A')}")
        print(f"   - Final Score: {result.metadata.get('final_score', 'N/A')}/10")

    print()
    print("=" * 80)
    print("GENERATING HTML REPORT...")
    print("=" * 80)

    # Generate HTML report
    report_path = generate_report(
        trace_logger=trace,
        output_path="agent_execution_report.html",
        auto_open=True,  # Automatically open in browser
    )

    print(f"\n[*] HTML Report generated: {report_path.absolute()}")
    print("[Browser] Opening in your default browser...")
    print()

    return result


async def run_multiple_scenarios():
    """Run multiple scenarios and generate reports."""
    print("\n" + "#" * 80)
    print("MULTI-SCENARIO DEMO WITH HTML REPORTS")
    print("#" * 80)
    print()

    scenarios = [
        {
            "name": "Scenario 1: Without Brand Voice",
            "topic": "The impact of remote work on team collaboration",
            "brand_id": None,
            "file": "report_no_brand.html",
        },
        {
            "name": "Scenario 2: With TechCorp Brand",
            "topic": "Cloud computing cost optimization strategies",
            "brand_id": "techcorp",
            "file": "report_techcorp.html",
        },
        {
            "name": "Scenario 3: Strict Criteria (EcoLife)",
            "topic": "Sustainable packaging innovations",
            "brand_id": "ecolife",
            "file": "report_ecolife.html",
            "threshold": 9.0,  # Higher threshold
        },
    ]

    for i, scenario in enumerate(scenarios, 1):
        print(f"\n{'='*80}")
        print(f"{scenario['name']}")
        print(f"{'='*80}")

        # Reset trace logger
        trace = get_trace_logger()
        trace.reset()

        # Create agent
        agent = MarketingAgent(
            use_multi_agent=True,
            critique_threshold=scenario.get("threshold", 8.0),
            max_rewrites=2,
        )

        # Generate post
        request = GeneratePostRequest(
            topic=scenario["topic"],
            tone="professional",
            brand_id=scenario["brand_id"],
        )

        print(f"[+] Topic: {request.topic}")
        if request.brand_id:
            print(f"[Brand] {request.brand_id}")
        print("[...] Processing...")

        result = await agent.generate_post(request)

        print("[OK] Completed!")
        if hasattr(result, "metadata") and result.metadata:
            print(f"   Score: {result.metadata.get('final_score', 'N/A')}/10")
            print(f"   Iterations: {result.metadata.get('iterations', 'N/A')}")

        # Generate report (don't auto-open for batch)
        report_path = generate_report(
            trace_logger=trace,
            output_path=scenario["file"],
            auto_open=(i == len(scenarios)),  # Only open last one
        )

        print(f"[File] Report saved: {report_path.name}")

        if i < len(scenarios):
            print("\n[Pause] Moving to next scenario...")

    print("\n" + "#" * 80)
    print("ALL SCENARIOS COMPLETED!")
    print("#" * 80)
    print("\n[Reports] generated:")
    for scenario in scenarios:
        print(f"   - {scenario['file']}")
    print()


async def main():
    """Main entry point."""
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "--multiple":
        # Run multiple scenarios
        await run_multiple_scenarios()
    else:
        # Run single demo
        await run_with_html_report()


if __name__ == "__main__":
    asyncio.run(main())
