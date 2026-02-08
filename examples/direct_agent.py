"""Example of using the Marketing Agent directly (without API)."""

import asyncio
from src.agents.marketing.agent import MarketingAgent
from src.agents.marketing.models import GeneratePostRequest
from src.shared.logger import setup_logging


async def main():
    """Demonstrate direct agent usage."""
    # Setup logging
    setup_logging()
    
    print("🤖 Marketing Agent Direct Usage Demo\n")
    
    # Initialize the agent
    print("Initializing Marketing Agent...")
    agent = MarketingAgent()
    print("✅ Agent initialized\n")
    
    # Test topics
    topics = [
        {
            "topic": "remote work productivity tips",
            "tone": "casual",
            "max_length": 600
        },
        {
            "topic": "sustainable business practices",
            "tone": "professional",
            "max_length": 800
        }
    ]
    
    # Generate posts
    for i, topic_config in enumerate(topics, 1):
        print("=" * 80)
        print(f"Test {i}: {topic_config['topic']}")
        print("=" * 80)
        
        request = GeneratePostRequest(**topic_config)
        
        print(f"\nGenerating post with tone: {request.tone}")
        print(f"Max length: {request.max_length} characters\n")
        
        # Generate the post
        post = await agent.generate_post(request)
        
        print("Generated Post:")
        print("-" * 80)
        print(post.content)
        print("-" * 80)
        
        print(f"\nPost Metadata:")
        print(f"  ID: {post.id}")
        print(f"  Topic: {post.topic}")
        print(f"  Tone: {post.tone}")
        print(f"  Length: {len(post.content)} characters")
        print(f"  Created: {post.created_at}")
        
        print(f"\nToken Usage:")
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
        print(f"{i}. {post.topic} ({post.tone})")
        print(f"   Created: {post.created_at}")
        print(f"   Length: {len(post.content)} chars")
        print(f"   Tokens: {post.usage.total_tokens}\n")
    
    print("=" * 80)
    print("✅ Demo completed successfully!")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(main())

