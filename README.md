# Marketing Agent Demo - Agentic Architecture PoC

[![CI/CD Pipeline](https://github.com/your-org/marketing-agent-demo/workflows/CI/CD%20Pipeline/badge.svg)](https://github.com/your-org/marketing-agent-demo/actions)
[![codecov](https://codecov.io/gh/your-org/marketing-agent-demo/branch/main/graph/badge.svg)](https://codecov.io/gh/your-org/marketing-agent-demo)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 🎯 Project Overview

This is a **Proof of Concept (PoC)** for a **Scalable Agentic Architecture** that demonstrates the "Golden Path" for building AI Agent systems with production-ready infrastructure, including:

- ✅ **AI Agents** with LangChain
- ✅ **Inference Gateway** for unified LLM access
- ✅ **Vector Memory** with ChromaDB
- ✅ **Quality Gates** with LLM-as-a-Judge
- ✅ **CI/CD Pipeline** with GitHub Actions
- ✅ **Observability** with structured logging
- ✅ **Containerization** with Docker

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     FastAPI Application                      │
│  ┌────────────────────────────────────────────────────────┐ │
│  │          Marketing Agent (Content Creator)             │ │
│  │  • Searches for topic information                      │ │
│  │  • Generates LinkedIn posts                            │ │
│  │  • Stores in vector memory                             │ │
│  └────────────────────────────────────────────────────────┘ │
│  ┌────────────────────────────────────────────────────────┐ │
│  │              Inference Gateway                         │ │
│  │  • Routes LLM calls (Mock/Real)                        │ │
│  │  • Logs token usage                                    │ │
│  │  • Provides observability                              │ │
│  └────────────────────────────────────────────────────────┘ │
│  ┌────────────────────────────────────────────────────────┐ │
│  │              ChromaDB (Vector Store)                   │ │
│  │  • Stores generated posts                              │ │
│  │  • Enables semantic search                             │ │
│  │  • Persistent memory                                   │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Docker & Docker Compose
- Git

### 1. Clone the Repository

```bash
git clone https://github.com/your-org/marketing-agent-demo.git
cd marketing-agent-demo
```

### 2. Set Up Environment Variables

```bash
cp .env.example .env
# Edit .env with your configuration
```

### 3. Run with Docker Compose

```bash
docker-compose up --build
```

The API will be available at: `http://localhost:8000`

### 4. Access API Documentation

Open your browser and navigate to:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 📦 Installation (Local Development)

### Using pip

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the application
uvicorn src.agents.marketing.api:app --reload
```

### Using Poetry

```bash
# Install Poetry
curl -sSL https://install.python-poetry.org | python3 -

# Install dependencies
poetry install

# Run the application
poetry run uvicorn src.agents.marketing.api:app --reload
```

## 🧪 Testing

### Run Unit Tests

```bash
pytest tests/unit/ -v --cov=src
```

### Run LLM-as-a-Judge Evaluation

```bash
python tests/evaluation/evaluate_agent.py
```

### Run All Tests

```bash
pytest tests/ -v --cov=src --cov-report=html
```

### Run Linting

```bash
ruff check src/ tests/
ruff format src/ tests/
```

## 📚 API Endpoints

### Generate LinkedIn Post

```bash
POST /generate
```

**Request:**
```json
{
  "topic": "artificial intelligence in healthcare",
  "tone": "professional",
  "max_length": 800
}
```

**Response:**
```json
{
  "post": {
    "id": "uuid-here",
    "topic": "artificial intelligence in healthcare",
    "content": "Generated LinkedIn post content...",
    "tone": "professional",
    "usage": {
      "prompt_tokens": 150,
      "completion_tokens": 250,
      "total_tokens": 400
    },
    "created_at": "2026-02-08T10:30:00Z"
  },
  "message": "Post generated successfully"
}
```

### Get Post History

```bash
GET /history?limit=10
```

**Response:**
```json
{
  "posts": [...],
  "total": 10
}
```

### Health Check

```bash
GET /health
```

### Metrics

```bash
GET /metrics
```

## 🔧 Configuration

Configuration is managed through environment variables (12-factor app):

| Variable | Description | Default |
|----------|-------------|---------|
| `ENVIRONMENT` | Application environment | `development` |
| `LOG_LEVEL` | Logging level | `INFO` |
| `OPENAI_API_KEY` | OpenAI API key | `mock` |
| `USE_MOCK_MODEL` | Use mock LLM instead of real | `true` |
| `CHROMA_PERSIST_DIRECTORY` | ChromaDB data directory | `./data/chroma` |
| `API_HOST` | API host address | `0.0.0.0` |
| `API_PORT` | API port number | `8000` |

## 📁 Project Structure

```
marketing-agent-demo/
├── src/
│   ├── gateway/              # Inference Gateway
│   │   ├── inference_gateway.py
│   │   └── models.py
│   ├── agents/
│   │   └── marketing/        # Marketing Agent
│   │       ├── agent.py
│   │       ├── api.py
│   │       ├── models.py
│   │       └── tools.py
│   └── shared/               # Shared utilities
│       ├── config.py
│       ├── logger.py
│       └── database.py
├── tests/
│   ├── unit/                 # Unit tests
│   │   ├── test_gateway.py
│   │   ├── test_agent.py
│   │   ├── test_api.py
│   │   └── test_shared.py
│   └── evaluation/           # LLM-as-a-Judge
│       └── evaluate_agent.py
├── .github/
│   └── workflows/
│       └── ci-cd.yml         # CI/CD Pipeline
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
├── pyproject.toml
└── README.md
```

## 🔄 CI/CD Pipeline

The GitHub Actions pipeline includes:

1. **Linting**: Code quality checks with Ruff
2. **Unit Tests**: Full test suite with coverage
3. **LLM-as-a-Judge**: Quality gate for generated content
4. **Build**: Docker image build and test
5. **Integration Tests**: End-to-end API testing
6. **Security Scan**: Dependency vulnerability check
7. **Deploy**: Deployment to production (placeholder)

## 📊 LLM-as-a-Judge

The quality gate evaluates generated posts on:

- **Clarity** (1-10): Message clarity and structure
- **Tone** (1-10): Appropriateness for LinkedIn
- **Length** (1-10): Optimal length (300-1500 chars)

**Pass Threshold**: Average score ≥ 8.0/10

## 🛡️ Best Practices Implemented

- ✅ **Type Hints**: Full type annotations throughout
- ✅ **Docstrings**: Google-style documentation
- ✅ **12-Factor App**: Configuration via environment variables
- ✅ **Structured Logging**: JSON logging for production
- ✅ **Error Handling**: Comprehensive exception management
- ✅ **Testing**: 80%+ code coverage
- ✅ **Containerization**: Docker for consistent environments
- ✅ **Observability**: Token usage tracking and metrics

## 🔮 Future Enhancements

- [ ] Add more agent types (SEO, Email, etc.)
- [ ] Implement agent-to-agent communication
- [ ] Add Redis for caching
- [ ] Implement rate limiting
- [ ] Add Prometheus metrics
- [ ] Deploy to Kubernetes
- [ ] Add Grafana dashboards
- [ ] Implement A/B testing

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Contributing

Contributions are welcome! Please read our contributing guidelines before submitting PRs.

## 📧 Contact

For questions or support, please open an issue on GitHub.

---

**Built with ❤️ using FastAPI, LangChain, and ChromaDB**

