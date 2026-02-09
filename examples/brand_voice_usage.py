"""Example usage of Brand Voice with the Marketing Agent API."""

import asyncio

import httpx


async def main():
    """Demonstrate Brand Voice API usage."""
    base_url = "http://localhost:8000"

    print("🎨 Marketing Agent with Brand Voice Demo\n")

    async with httpx.AsyncClient(timeout=30.0) as client:
        # 1. List available brands
        print("=" * 70)
        print("1. List Available Brands")
        print("=" * 70)

        response = await client.get(f"{base_url}/brands")
        brands_data = response.json()

        print(f"Total Brands: {brands_data['total']}\n")
        for brand in brands_data["brands"]:
            print(f"  • {brand['brand_id']}: {brand['overview']}")
        print()

        # 2. Get specific brand info
        print("=" * 70)
        print("2. Get Brand Information")
        print("=" * 70)

        brand_id = "techcorp"
        response = await client.get(f"{base_url}/brands/{brand_id}")
        brand_info = response.json()

        print(f"Brand: {brand_info['brand_id']}")
        print(f"Overview: {brand_info['overview']}")
        print(f"Guidelines Length: {brand_info['guidelines_length']} characters\n")

        # 3. Generate posts with different brand voices
        test_cases = [
            {
                "topic": "artificial intelligence in business",
                "brand_id": "techcorp",
                "tone": "professional",
            },
            {
                "topic": "sustainable technology",
                "brand_id": "ecolife",
                "tone": "enthusiastic",
            },
            {"topic": "investing in AI stocks", "brand_id": "financewise", "tone": "professional"},
        ]

        for i, test_case in enumerate(test_cases, 1):
            print("=" * 70)
            print(f"{i+2}. Generate Post with Brand Voice: {test_case['brand_id'].upper()}")
            print("=" * 70)

            request_data = {
                "topic": test_case["topic"],
                "brand_id": test_case["brand_id"],
                "tone": test_case["tone"],
                "max_length": 800,
            }

            print(f"Topic: {request_data['topic']}")
            print(f"Brand: {request_data['brand_id']}")
            print(f"Tone: {request_data['tone']}\n")

            response = await client.post(f"{base_url}/generate", json=request_data)

            if response.status_code == 201:
                result = response.json()
                post = result["post"]

                print("Generated Post:")
                print("-" * 70)
                print(post["content"])
                print("-" * 70)
                print("\nMetadata:")
                print(f"  - ID: {post['id']}")
                print(f"  - Brand: {post['brand_id']}")
                print(f"  - Length: {len(post['content'])} characters")
                print(f"  - Tokens Used: {post['usage']['total_tokens']}\n")
            else:
                print(f"Error: {response.status_code}")
                print(response.json())
            print()

        # 4. Generate a post WITHOUT brand voice
        print("=" * 70)
        print(f"{len(test_cases)+3}. Generate Post WITHOUT Brand Voice")
        print("=" * 70)

        request_data = {"topic": "future of work", "tone": "professional", "max_length": 600}

        print(f"Topic: {request_data['topic']}")
        print("Brand: None (default style)\n")

        response = await client.post(f"{base_url}/generate", json=request_data)

        if response.status_code == 201:
            result = response.json()
            post = result["post"]

            print("Generated Post:")
            print("-" * 70)
            print(post["content"])
            print("-" * 70)
            print("\nMetadata:")
            print(f"  - ID: {post['id']}")
            print(f"  - Brand: {post['brand_id'] or 'None'}")
            print(f"  - Length: {len(post['content'])} characters\n")

        # 5. Get metrics with brand breakdown
        print("=" * 70)
        print(f"{len(test_cases)+4}. Get Metrics with Brand Breakdown")
        print("=" * 70)

        response = await client.get(f"{base_url}/metrics")
        metrics = response.json()

        print(f"Total Posts Generated: {metrics['total_posts_generated']}")
        print(f"Total Tokens Used: {metrics['total_tokens_used']}")
        print(f"Available Brands: {metrics['available_brands']}")
        print("\nPosts by Brand:")
        for brand, count in metrics["posts_by_brand"].items():
            print(f"  - {brand}: {count} post(s)")
        print()

    print("=" * 70)
    print("✅ Brand Voice Demo completed successfully!")
    print("=" * 70)


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
