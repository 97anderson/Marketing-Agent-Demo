# Agentic Marketing Platform - PoC

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Docker](https://img.shields.io/badge/docker-ready-blue.svg)](https://www.docker.com/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109-green.svg)](https://fastapi.tiangolo.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)

> **Production-ready multi-agent system for generating brand-aligned LinkedIn content with LLM-powered critique and RAG-based brand voice.**

---

## 🎯 Overview

This Proof-of-Concept demonstrates a scalable agentic architecture for automated content generation. The system uses a **multi-agent workflow** where specialized AI agents collaborate to plan, write, and critique LinkedIn posts while maintaining strict brand voice adherence.

### Key Features

- **🤖 Multi-Agent Workflow**: Planner → Writer → Critic agents working in sequence
- **🎨 Brand Voice RAG**: Retrieval-Augmented Generation for consistent brand identity
- **🔄 Self-Critique Loop**: Automatic rewriting based on quality feedback (configurable threshold)
- **📊 HTML Reporting**: Beautiful timeline reports of agent reasoning and decisions
- **🚀 Inference Gateway**: Unified LLM interface with token tracking and mock support
- **🐳 Docker-Ready**: Full containerization with Docker Compose
- **✅ LLM-as-a-Judge**: Automated quality evaluation pipeline

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     FastAPI Application                      │
│                    (Port 8000)                               │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
         ┌──────────────────────────────┐
         │   Marketing Agent            │
         │   (Orchestrator)             │
         └──────────┬───────────────────┘
                    │
      ┌─────────────┼─────────────┐
      │             │             │
      ▼             ▼             ▼
┌──────────┐  ┌──────────┐  ┌──────────┐
│ Planner  │  │  Writer  │  │ Critique │
│  Agent   │─>│  Agent   │─>│  Agent   │
└──────────┘  └────┬─────┘  └────┬─────┘
                   │             │
                   └──────┬──────┘
                          │ (Rewrite Loop)
                          ▼
              ┌────────────────────┐
              │ Inference Gateway  │
              │  (LLM Abstraction) │
              └─────────┬──────────┘
                        │
        ┌───────────────┼───────────────┐
        ▼               ▼               ▼
  ┌─────────┐    ┌──────────┐    ┌──────────┐
  │ OpenAI  │    │   Mock   │    │ ChromaDB │
  │  API    │    │  Model   │    │ (Memory) │
  └─────────┘    └──────────┘    └──────────┘
```

**Data Flow:**
1. User provides topic + brand ID
2. **PlannerAgent** creates structured outline
3. **WriterAgent** generates post with brand voice
4. **CritiqueAgent** evaluates quality (score 0-10)
5. If score < threshold: Writer rewrites (max 2 rewrites)
6. System returns final post + metadata

---

## 📁 Project Structure

```
Marketing-Agent-Demo/
├── src/                          # Source code
│   ├── gateway/                  # Inference Gateway (LLM abstraction)
│   │   ├── inference_gateway.py  # Main gateway logic
│   │   └── models.py             # Pydantic models
│   ├── agents/                   # Agent implementations
│   │   └── marketing/            # Marketing agent module
│   │       ├── agent.py          # Orchestrator
│   │       ├── planner_agent.py  # Outline generation
│   │       ├── writer_agent.py   # Content creation
│   │       ├── critique_agent.py # Quality evaluation
│   │       ├── multi_agent_flow.py # Workflow coordinator
│   │       ├── brand_voice.py    # RAG for brand guidelines
│   │       ├── tools.py          # Agent tools
│   │       ├── models.py         # Data models
│   │       └── api.py            # FastAPI endpoints
│   └── shared/                   # Shared utilities
│       ├── config.py             # Configuration (12-factor)
│       ├── logger.py             # Structured logging
│       ├── database.py           # ChromaDB wrapper
│       ├── trace_logger.py       # Agent execution tracking
│       └── html_reporter.py      # Report generation
│
├── tests/                        # Test suite
│   ├── unit/                     # Unit tests
│   └── evaluation/               # LLM-as-a-Judge
│       └── evaluate_agent.py
│
├── docs/                         # Documentation
│   ├── specs/                    # Technical specifications
│   ├── guides/                   # User guides
│   └── internal/                 # Development logs
│
├── examples/                     # Usage examples
│   ├── direct_agent.py           # Direct agent usage
│   ├── api_usage.py              # API client example
│   └── multi_agent_demo.py       # Multi-agent demo
│
├── knowledge_base/               # Brand voice guidelines
│   ├── techcorp_brand_voice.txt
│   ├── ecolife_brand_voice.txt
│   └── financewise_brand_voice.txt
│
├── scripts/                      # Utility scripts
│   ├── run.py                    # Application runner
│   ├── dev.py                    # Development helper
│   └── verify_project.py         # Structure verification
│
├── .github/workflows/            # CI/CD pipeline
│   └── ci-cd.yml                 # GitHub Actions
│
├── docker-compose.yml            # Docker Compose configuration
├── Dockerfile                    # Container definition
├── requirements.txt              # Python dependencies
├── pyproject.toml                # Project metadata
├── .env.example                  # Environment template
├── .gitignore                    # Git ignore rules
├── LICENSE                       # MIT License
├── CONTRIBUTING.md               # Contribution guidelines
└── README.md                     # This file
```

---

## 🚀 Quick Start

### Prerequisites

- **Python 3.11+**
- **Docker & Docker Compose** (recommended)
- **Git**

### Option 1: Docker (Recommended)

```bash
# 1. Clone the repository
git clone https://github.com/97anderson/Marketing-Agent-Demo.git
cd Marketing-Agent-Demo

# 2. Copy environment template
cp .env.example .env

# 3. Start services
docker-compose up --build

# 4. Access the API
curl http://localhost:8000/health
```

**The API will be available at:** `http://localhost:8000`  
**Interactive docs:** `http://localhost:8000/docs`

### Option 2: Local Development

```bash
# 1. Clone and setup
git clone https://github.com/97anderson/Marketing-Agent-Demo.git
cd Marketing-Agent-Demo

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Setup environment
cp .env.example .env
# Edit .env with your settings

# 5. Run the application
python scripts/run.py

# Or use the dev helper
python scripts/dev.py run
```

---

## 💡 Usage Examples

### Generate a LinkedIn Post via API

```bash
curl -X POST http://localhost:8000/generate \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "The future of AI in software development",
    "tone": "professional",
    "brand_id": "techcorp"
  }'
```

**Response:**
```json
{
  "post": {
    "id": "uuid-here",
    "topic": "The future of AI in software development",
    "content": "🚀 AI is transforming how we build software...",
    "tone": "professional",
    "brand_id": "techcorp",
    "metadata": {
      "workflow": "multi-agent",
      "iterations": 2,
      "final_score": 8.5,
      "workflow_summary": "[...]"
    }
  },
  "message": "Post generated successfully"
}
```

### Direct Agent Usage (Python)

```python
import asyncio
from src.agents.marketing.agent import MarketingAgent
from src.gateway.inference_gateway import InferenceGateway

async def main():
    gateway = InferenceGateway.from_settings()
    agent = MarketingAgent(gateway)
    
    result = await agent.generate_post(
        topic="Sustainable tech practices",
        tone="inspirational",
        brand_id="ecolife"
    )
    
    print(f"Generated Post:\n{result.content}")
    print(f"Score: {result.metadata['final_score']}")
    print(f"Iterations: {result.metadata['iterations']}")

asyncio.run(main())
```

### View Execution Report

```bash
# Generate a post and download the HTML report
curl -o report.html http://localhost:8000/report/download

# Open in browser
open report.html  # macOS
start report.html # Windows
xdg-open report.html # Linux
```

---

## 🎨 Brand Voice System

The platform uses **RAG (Retrieval-Augmented Generation)** to maintain consistent brand identity:

1. **Add Brand Guidelines:** Create a `.txt` file in `knowledge_base/`
2. **Use in Requests:** Pass `brand_id` parameter (filename without extension)
3. **Automatic Injection:** System loads guidelines and injects into LLM prompts
4. **Critic Validation:** CritiqueAgent verifies brand adherence

**Example Brand File** (`knowledge_base/mycompany_brand_voice.txt`):
```
Brand Name: MyCompany
Voice: Professional yet approachable
Tone: Confident, data-driven
Key Phrases: "innovation-first", "customer-centric"
Hashtags: #MyCompanyInnovation #TechLeadership
```

**Usage:**
```bash
curl -X POST http://localhost:8000/generate \
  -d '{"topic": "...", "brand_id": "mycompany"}'
```

---

## ⚙️ Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `ENVIRONMENT` | Environment (development/production) | `development` |
| `USE_MOCK_MODEL` | Use mock LLM instead of OpenAI | `true` |
| `OPENAI_API_KEY` | OpenAI API key | `mock` |
| `USE_MULTI_AGENT_FLOW` | Enable multi-agent workflow | `true` |
| `CRITIQUE_THRESHOLD` | Minimum score to approve (0-10) | `8.0` |
| `MAX_REWRITES` | Maximum rewrite attempts | `2` |
| `API_HOST` | API host | `0.0.0.0` |
| `API_PORT` | API port | `8000` |

### Switching to Real OpenAI

1. Get an API key from [OpenAI](https://platform.openai.com/)
2. Update `.env`:
   ```bash
   USE_MOCK_MODEL=false
   OPENAI_API_KEY=sk-your-actual-key-here
   ```
3. Restart the application

---

## 🧪 Development

### Run Tests

```bash
# All tests
python scripts/dev.py test

# With coverage report
pytest tests/ -v --cov=src --cov-report=html
open htmlcov/index.html
```

### Code Quality

```bash
# Lint
python scripts/dev.py lint

# Format
python scripts/dev.py format

# Full check
ruff check src/ tests/ && ruff format src/ tests/
```

### LLM-as-a-Judge Evaluation

```bash
python scripts/dev.py evaluate

# Or directly
python tests/evaluation/evaluate_agent.py
```

---

## 📊 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check + system status |
| `/generate` | POST | Generate LinkedIn post |
| `/report/download` | GET | Download HTML execution report |
| `/metrics` | GET | System metrics |
| `/brands` | GET | List available brands |
| `/docs` | GET | Interactive API documentation |

**Full API Documentation:** Visit `http://localhost:8000/docs` when running.

---

## 🔬 Advanced Features

### Multi-Agent Workflow

The system orchestrates three specialized agents:

1. **PlannerAgent**: Creates structured outlines with hooks, key points, CTAs
2. **WriterAgent**: Generates content following the outline and brand voice
3. **CritiqueAgent**: Evaluates quality on 3 dimensions (brand adherence, quality, tone)

**Workflow Logic:**
```python
outline = planner.create_outline(topic)
post = writer.write_post(outline, brand_voice)
approved, feedback, score = critique.evaluate(post)

while not approved and iterations < MAX_REWRITES:
    post = writer.rewrite(post, feedback)
    approved, feedback, score = critique.evaluate(post)

return post, metadata
```

### HTML Reporting

Every agent execution generates a visual timeline report showing:
- Agent decisions and reasoning
- Iteration history (initial write + rewrites)
- Quality scores per iteration
- Time and cost metrics
- Final approval decision

**Features:**
- Dark mode design (Tailwind CSS)
- Expandable step details
- Color-coded statuses
- Copy-paste friendly metadata

---

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](./CONTRIBUTING.md) for guidelines.

### Development Workflow

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests and linting
5. Commit with conventional commits (`feat:`, `fix:`, `docs:`, etc.)
6. Push and create a Pull Request

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](./LICENSE) file for details.

---

## 🙏 Acknowledgments

- Built with [FastAPI](https://fastapi.tiangolo.com/)
- Powered by [LangChain](https://www.langchain.com/)
- Styled with [Tailwind CSS](https://tailwindcss.com/)
- Vector storage by [ChromaDB](https://www.trychroma.com/)

---

## 📚 Documentation

- **Quick Start Guide:** [docs/guides/QUICKSTART.md](./docs/guides/QUICKSTART.md)
- **Brand Voice Setup:** [docs/guides/BRAND_VOICE_GUIDE.md](./docs/guides/BRAND_VOICE_GUIDE.md)
- **Multi-Agent System:** [docs/guides/MULTI_AGENT_GUIDE.md](./docs/guides/MULTI_AGENT_GUIDE.md)
- **HTML Reporting:** [docs/guides/HTML_REPORT_GUIDE.md](./docs/guides/HTML_REPORT_GUIDE.md)
- **Docker Guide:** [docs/guides/DOCKER_DEMO_GUIDE.md](./docs/guides/DOCKER_DEMO_GUIDE.md)
- **Architecture Spec:** [docs/specs/ARCHITECTURE_SPEC.md](./docs/specs/ARCHITECTURE_SPEC.md)

---

## 🐛 Known Issues & Roadmap

- [ ] Add support for more LLM providers (Anthropic, Cohere)
- [ ] Implement streaming responses
- [ ] Add multi-language support
- [ ] Create web UI for content generation
- [ ] Add more sophisticated RAG (semantic search over brand docs)
- [ ] Implement agent memory/context preservation
- [ ] Add A/B testing for different agent prompts

---

## 📞 Support

- **Issues:** [GitHub Issues](https://github.com/97anderson/Marketing-Agent-Demo/issues)
- **Discussions:** [GitHub Discussions](https://github.com/97anderson/Marketing-Agent-Demo/discussions)
- **Email:** your-email@example.com

---

<p align="center">
  By Anderson Jimenez - Solutions Architect and AI Developer
</p>

<p align="center">
  <sub>This is a Proof-of-Concept for demonstration purposes.</sub>
</p>
