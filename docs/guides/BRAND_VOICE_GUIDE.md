# Brand Voice Feature Documentation

## Overview

The Marketing Agent now supports **Brand Voice** - the ability to generate content that strictly adheres to specific brand guidelines using a simple RAG (Retrieval-Augmented Generation) approach.

## Features

### ✅ What's Implemented

1. **Brand Voice Manager**: RAG system for loading brand guidelines
2. **Knowledge Base**: Directory with brand voice files
3. **API Endpoints**: New endpoints for brand management
4. **Automatic Detection**: Small files (<10KB) loaded directly
5. **Future-Ready**: Architecture supports ChromaDB chunking for large files

## How It Works

### 1. RAG Implementation

```
┌─────────────────────────────────────────────────┐
│         User Request with brand_id              │
└────────────────┬────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────┐
│      Brand Voice Manager (RAG)                  │
│  ┌─────────────────────────────────────────┐   │
│  │  Check file size                        │   │
│  │  • <10KB: Direct file reading           │   │
│  │  • >10KB: ChromaDB chunking (future)    │   │
│  └─────────────────────────────────────────┘   │
└────────────────┬────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────┐
│      Load Brand Guidelines                      │
│  • Company overview                             │
│  • Tone of voice                                │
│  • Writing guidelines                           │
│  • Hashtag strategy                             │
│  • Example phrases                              │
└────────────────┬────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────┐
│    Inject into LLM Prompt                       │
│  "You MUST strictly follow these guidelines..." │
└────────────────┬────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────┐
│    Generate Brand-Consistent Content            │
└─────────────────────────────────────────────────┘
```

### 2. Brand Voice Files

Located in `knowledge_base/` directory:
- `techcorp_brand_voice.txt` - Tech company
- `ecolife_brand_voice.txt` - Sustainability brand
- `financewise_brand_voice.txt` - Financial services

Each file contains:
- Company Overview
- Brand Personality
- Tone of Voice
- Writing Guidelines (Do's & Don'ts)
- Hashtag Strategy
- Post Structure
- Example Phrases
- Signature Closing

## Usage

### API Usage

```bash
# Generate post with brand voice
curl -X POST http://localhost:8000/generate \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "artificial intelligence",
    "brand_id": "techcorp",
    "tone": "professional",
    "max_length": 800
  }'

# List available brands
curl http://localhost:8000/brands

# Get brand information
curl http://localhost:8000/brands/techcorp
```

### Python Usage

```python
from src.agents.marketing.agent import MarketingAgent
from src.agents.marketing.models import GeneratePostRequest

# Initialize agent
agent = MarketingAgent()

# Generate with brand voice
request = GeneratePostRequest(
    topic="AI innovation",
    brand_id="techcorp",  # Apply TechCorp's brand voice
    tone="professional",
    max_length=700
)

post = await agent.generate_post(request)
print(post.content)
```

## Adding New Brands

### 1. Create Brand Voice File

Create `knowledge_base/{brand_id}_brand_voice.txt`:

```markdown
# [Brand Name] Brand Voice Guide

## Company Overview
[Brief company description]

## Brand Personality
- [Trait 1]
- [Trait 2]
- [Trait 3]

## Tone of Voice
- **[Aspect]**: [Description]
- **[Aspect]**: [Description]

## Writing Guidelines

### Do:
- [Guideline 1]
- [Guideline 2]

### Don't:
- [Avoid 1]
- [Avoid 2]

## Hashtag Strategy
- #Tag1
- #Tag2

## Post Structure
1. **Hook**: [Description]
2. **Body**: [Description]
3. **CTA**: [Description]

## Example Phrases
- "[Phrase 1]"
- "[Phrase 2]"

## Signature Closing
[Your closing format]
```

### 2. Verify It Works

```bash
# Check if brand is available
curl http://localhost:8000/brands

# Test generation
curl -X POST http://localhost:8000/generate \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "test topic",
    "brand_id": "your_new_brand"
  }'
```

## Architecture Details

### BrandVoiceManager Class

```python
class BrandVoiceManager:
    """Manages brand voice guidelines with RAG approach."""
    
    def get_brand_voice(self, brand_id: str) -> str:
        """Load brand voice (direct or chunked)."""
        
    def list_available_brands(self) -> list[str]:
        """List all available brands."""
        
    def validate_brand_exists(self, brand_id: str) -> bool:
        """Check if brand exists."""
```

### File Size Thresholds

- **Small files (<10KB)**: Direct file reading
  - Fast, simple
  - Current implementation
  - Suitable for most brand guides

- **Large files (>10KB)**: ChromaDB chunking
  - Chunking into smaller pieces
  - Vector embeddings
  - Semantic retrieval
  - Future enhancement

## Examples

Run the examples to see Brand Voice in action:

```bash
# API example
python examples/brand_voice_usage.py

# Direct agent example
python examples/direct_agent_brand_voice.py
```

## Testing

```bash
# Run brand voice tests
pytest tests/unit/test_brand_voice.py -v

# Test with specific brand
pytest tests/unit/test_brand_voice.py::test_get_brand_voice_success -v
```

## Metrics

The API now tracks brand usage:

```bash
curl http://localhost:8000/metrics
```

Response:
```json
{
  "total_posts_generated": 10,
  "total_tokens_used": 5000,
  "posts_by_brand": {
    "techcorp": 4,
    "ecolife": 3,
    "financewise": 2
  },
  "available_brands": 3
}
```

## Benefits

### 1. **Consistency**
- Every post matches brand guidelines
- No manual review needed for style

### 2. **Scalability**
- Generate hundreds of posts with consistent voice
- Easy to add new brands

### 3. **Flexibility**
- Can generate with or without brand voice
- Multiple brands supported simultaneously

### 4. **Quality**
- Strict adherence to guidelines
- Professional, on-brand content

## Best Practices

### 1. Brand Voice Guidelines
- Be specific and detailed
- Include examples
- Cover edge cases
- Update regularly

### 2. File Organization
- One file per brand
- Clear naming: `{brand_id}_brand_voice.txt`
- Keep under 10KB for fast loading

### 3. Testing
- Test each brand after adding
- Compare outputs against manual examples
- Verify tone and style consistency

## Troubleshooting

### Brand Not Found
```python
FileNotFoundError: Brand voice file not found for 'mybrand'
```
**Solution**: Ensure file exists: `knowledge_base/mybrand_brand_voice.txt`

### Inconsistent Style
**Issue**: Generated content doesn't match brand voice

**Solutions**:
1. Make guidelines more explicit
2. Add more examples in the brand voice file
3. Use stricter language in the guidelines

### File Too Large
**Warning**: `File size exceeds threshold, using chunked retrieval`

**Solutions**:
1. Simplify brand guidelines (recommended)
2. Implement ChromaDB chunking (future feature)

## Future Enhancements

- [ ] ChromaDB integration for large files
- [ ] Multi-language brand voices
- [ ] Brand voice versioning
- [ ] A/B testing different brand voices
- [ ] Brand voice consistency scoring
- [ ] Auto-generate brand voice from examples

---

**Created**: February 2026
**Version**: 1.0
**Status**: Production Ready ✅

