# Knowledge Base - Brand Voice Guidelines

This directory contains brand voice guidelines for different companies. Each file contains comprehensive style guides that the Marketing Agent uses to generate brand-consistent content.

## Available Brands

### TechCorp
**File**: `techcorp_brand_voice.txt`
- **Industry**: Technology
- **Tone**: Professional, innovative, solution-oriented
- **Style**: Forward-thinking with data-driven insights

### EcoLife
**File**: `ecolife_brand_voice.txt`
- **Industry**: Sustainability
- **Tone**: Warm, inspiring, authentic
- **Style**: Storytelling with actionable environmental advice

### FinanceWise
**File**: `financewise_brand_voice.txt`
- **Industry**: Financial Services
- **Tone**: Professional, educational, empowering
- **Style**: Clear financial education with actionable steps

## Usage

The Marketing Agent automatically loads these guidelines when generating content with a `brand_id` parameter:

```python
request = GeneratePostRequest(
    topic="artificial intelligence",
    brand_id="techcorp"  # Uses TechCorp's brand voice
)
```

## Adding New Brands

To add a new brand voice:

1. Create a new file: `{brand_id}_brand_voice.txt`
2. Include the following sections:
   - Company Overview
   - Brand Personality
   - Tone of Voice
   - Writing Guidelines (Do's and Don'ts)
   - Hashtag Strategy
   - Post Structure
   - Example Phrases
   - Signature Closing

## File Size Considerations

- Files < 10KB: Loaded directly (current implementation)
- Files > 10KB: Should use ChromaDB chunking (future enhancement)

Current files are optimized to be under 10KB for efficient direct loading.

