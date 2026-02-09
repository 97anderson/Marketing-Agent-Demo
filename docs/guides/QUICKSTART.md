# How to Run the Marketing Agent Demo

This guide will walk you through running the Marketing Agent Demo locally.

## Option 1: Docker Compose (Recommended)

This is the easiest way to run the entire stack.

### Steps:

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd marketing-agent-demo
   ```

2. **Create environment file**
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` if needed. Default values work for development.

3. **Start the services**
   ```bash
   docker-compose up --build
   ```

4. **Access the API**
   - API: http://localhost:8000
   - Swagger Docs: http://localhost:8000/docs
   - Health Check: http://localhost:8000/health

5. **Test the API**
   ```bash
   # Generate a LinkedIn post
   curl -X POST http://localhost:8000/generate \
     -H "Content-Type: application/json" \
     -d '{
       "topic": "artificial intelligence",
       "tone": "professional",
       "max_length": 500
     }'
   
   # Get post history
   curl http://localhost:8000/history
   ```

6. **Stop the services**
   ```bash
   docker-compose down
   ```

## Option 2: Local Development

Run the application directly on your machine.

### Prerequisites:
- Python 3.11+
- pip or Poetry

### Steps:

1. **Clone and navigate**
   ```bash
   git clone <repository-url>
   cd marketing-agent-demo
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   
   # On Windows:
   venv\Scripts\activate
   
   # On Mac/Linux:
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Create environment file**
   ```bash
   cp .env.example .env
   ```

5. **Run the application**
   ```bash
   uvicorn src.agents.marketing.api:app --reload --host 0.0.0.0 --port 8000
   ```

6. **Access the API**
   - http://localhost:8000/docs

## Option 3: Run Tests

### Unit Tests
```bash
pytest tests/unit/ -v
```

### LLM-as-a-Judge Evaluation
```bash
python tests/evaluation/evaluate_agent.py
```

### Run All Tests with Coverage
```bash
pytest tests/ -v --cov=src --cov-report=html
```

View coverage report: Open `htmlcov/index.html` in your browser.

### Linting
```bash
# Check code
ruff check src/ tests/

# Format code
ruff format src/ tests/
```

## Troubleshooting

### Port 8000 already in use
```bash
# Change the port in .env
API_PORT=8001

# Or stop the conflicting service
lsof -ti:8000 | xargs kill -9  # Mac/Linux
```

### Docker issues
```bash
# Clean up Docker
docker-compose down -v
docker system prune -a

# Rebuild from scratch
docker-compose up --build --force-recreate
```

### ChromaDB connection issues
```bash
# Delete the database and restart
rm -rf ./data/chroma
docker-compose up --build
```

## Using the API

### Example Requests

**Generate a post:**
```bash
curl -X POST http://localhost:8000/generate \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "remote work productivity",
    "tone": "casual",
    "max_length": 800
  }'
```

**Get history:**
```bash
curl http://localhost:8000/history?limit=5
```

**Health check:**
```bash
curl http://localhost:8000/health
```

**Metrics:**
```bash
curl http://localhost:8000/metrics
```

## Next Steps

- Check the [README.md](README.md) for full documentation
- Explore the API at http://localhost:8000/docs
- Review the code in `src/` directory
- Run the evaluation script to see LLM-as-a-Judge in action
- Customize the agent for your use case

## Need Help?

- Check the logs: `docker-compose logs -f`
- Review environment variables in `.env`
- Open an issue on GitHub

