"""Example usage of the Marketing Agent API."""

import asyncio

import httpx


async def main():
    """Demonstrate API usage."""
    base_url = "http://localhost:8000"

    print("🚀 Marketing Agent API Demo\n")

    # 1. Health Check
    print("=" * 60)
    print("1. Health Check")
    print("=" * 60)

    async with httpx.AsyncClient() as client:
        response = await client.get(f"{base_url}/health")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}\n")

        # 2. Generate a LinkedIn Post
        print("=" * 60)
        print("2. Generate LinkedIn Post")
        print("=" * 60)

        request_data = {
            "topic": "artificial intelligence in healthcare",
            "tone": "professional",
            "max_length": 800,
        }

        print(f"Request: {request_data}\n")

        response = await client.post(f"{base_url}/generate", json=request_data, timeout=30.0)

        result = response.json()
        post = result["post"]

        print(f"Status: {response.status_code}")
        print("\nGenerated Post:")
        print("-" * 60)
        print(post["content"])
        print("-" * 60)
        print("\nMetadata:")
        print(f"  - ID: {post['id']}")
        print(f"  - Topic: {post['topic']}")
        print(f"  - Tone: {post['tone']}")
        print(f"  - Created: {post['created_at']}")
        print("\nToken Usage:")
        print(f"  - Prompt Tokens: {post['usage']['prompt_tokens']}")
        print(f"  - Completion Tokens: {post['usage']['completion_tokens']}")
        print(f"  - Total Tokens: {post['usage']['total_tokens']}\n")

        # 3. Get Post History
        print("=" * 60)
        print("3. Get Post History")
        print("=" * 60)

        response = await client.get(f"{base_url}/history?limit=5")
        history = response.json()

        print(f"Status: {response.status_code}")
        print(f"Total Posts: {history['total']}\n")

        for i, post in enumerate(history["posts"], 1):
            print(f"{i}. Topic: {post['topic']}")
            print(f"   Tone: {post['tone']}")
            print(f"   Length: {len(post['content'])} chars")
            print(f"   Created: {post['created_at']}\n")

        # 4. Get Metrics
        print("=" * 60)
        print("4. Get Metrics")
        print("=" * 60)

        response = await client.get(f"{base_url}/metrics")
        metrics = response.json()

        print(f"Status: {response.status_code}")
        print(f"Total Posts Generated: {metrics['total_posts_generated']}")
        print(f"Total Tokens Used: {metrics['total_tokens_used']}")
        print(f"Status: {metrics['status']}\n")

    print("=" * 60)
    print("✅ Demo completed successfully!")
    print("=" * 60)


if __name__ == "__main__":
    print("\nMake sure the API is running on http://localhost:8000")
    print("Start it with: docker-compose up\n")

    try:
        asyncio.run(main())
    except httpx.ConnectError:
        print("\n❌ Error: Could not connect to API")
        print("Please start the API first: docker-compose up\n")
    except Exception as e:
        print(f"\n❌ Error: {str(e)}\n")
