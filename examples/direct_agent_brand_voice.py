"""Example of using the Marketing Agent with Brand Voice directly (without API)."""

import asyncio

from src.agents.marketing.agent import MarketingAgent
from src.agents.marketing.models import GeneratePostRequest
from src.shared.logger import setup_logging


async def main():
    """Demonstrate direct brand voice usage with the agent."""
    # Setup logging
    setup_logging()

    print("🎨 Marketing Agent with Brand Voice - Direct Usage Demo\n")

    # Initialize the agent
    print("Initializing Marketing Agent with Brand Voice support...")
    agent = MarketingAgent()
    print("✅ Agent initialized\n")

    # List available brands
    print("=" * 80)
    print("Available Brands")
    print("=" * 80)
    brands = agent.list_available_brands()
    print(f"Found {len(brands)} brands:\n")
    for brand in brands:
        info = agent.get_brand_info(brand)
        print(f"  • {brand}: {info['overview']}")
    print()

    # Test different brand voices
    test_cases = [
        {
            "topic": "AI-powered automation",
            "brand_id": "techcorp",
            "tone": "professional",
            "max_length": 700,
        },
        {
            "topic": "reducing carbon footprint",
            "brand_id": "ecolife",
            "tone": "enthusiastic",
            "max_length": 700,
        },
        {
            "topic": "retirement planning strategies",
            "brand_id": "financewise",
            "tone": "professional",
            "max_length": 700,
        },
        {
            "topic": "remote work trends",
            "brand_id": None,  # No brand voice
            "tone": "casual",
            "max_length": 600,
        },
    ]

    for i, test_case in enumerate(test_cases, 1):
        print("=" * 80)
        brand_label = test_case["brand_id"] or "DEFAULT (No Brand Voice)"
        print(f"Test {i}: {test_case['topic']} - Brand: {brand_label}")
        print("=" * 80)

        request = GeneratePostRequest(**test_case)

        print("\nGenerating post...")
        print(f"  Topic: {request.topic}")
        print(f"  Brand: {request.brand_id or 'None'}")
        print(f"  Tone: {request.tone}")
        print(f"  Max Length: {request.max_length}\n")

        # Generate the post
        post = await agent.generate_post(request)

        print("Generated Post:")
        print("-" * 80)
        print(post.content)
        print("-" * 80)

        print("\nPost Metadata:")
        print(f"  ID: {post.id}")
        print(f"  Topic: {post.topic}")
        print(f"  Brand: {post.brand_id or 'None'}")
        print(f"  Tone: {post.tone}")
        print(f"  Length: {len(post.content)} characters")
        print(f"  Created: {post.created_at}")

        print("\nToken Usage:")
        print(f"  Prompt Tokens: {post.usage.prompt_tokens}")
        print(f"  Completion Tokens: {post.usage.completion_tokens}")
        print(f"  Total Tokens: {post.usage.total_tokens}\n")

    # Get history
    print("=" * 80)
    print("Post History")
    print("=" * 80)

    history = agent.get_history(limit=10)
    print(f"\nTotal posts in history: {len(history)}\n")

    for i, post in enumerate(history, 1):
        brand_label = post.brand_id if post.brand_id else "None"
        print(f"{i}. {post.topic} ({post.tone}) - Brand: {brand_label}")
        print(f"   Created: {post.created_at}")
        print(f"   Length: {len(post.content)} chars")
        print(f"   Tokens: {post.usage.total_tokens}\n")

    print("=" * 80)
    print("✅ Demo completed successfully!")
    print("=" * 80)
    print("\n💡 Key Features Demonstrated:")
    print("  ✓ Loading brand voice guidelines from knowledge base")
    print("  ✓ Generating content with strict brand adherence")
    print("  ✓ Comparing posts with and without brand voice")
    print("  ✓ Storing brand metadata in ChromaDB")


if __name__ == "__main__":
    asyncio.run(main())
