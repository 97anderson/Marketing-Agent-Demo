# ARCHITECTURE SPECIFICATION: AGENTIC MESH DEMO

## 1. Project Overview
We are building a Proof of Concept (PoC) for a Scalable Agentic Architecture.
The goal is to demonstrate a "Golden Path" for developers: a pre-configured template that includes AI Agents, CI/CD, and Quality Gates.

## 2. Tech Stack
- **Language:** Python 3.11+
- **Framework:** FastAPI (for the API interface)
- **Agent Framework:** LangChain or PydanticAI (Simple implementation)
- **Database:** ChromaDB (Local vector store for memory)
- **Testing:** Pytest
- **Containerization:** Docker & Docker Compose
- **Orchestration:** Simulated Kubernetes services via Docker Compose

## 3. Architecture Components

### A. The Inference Gateway (Mock)
- A simple wrapper class that routes LLM calls.
- It must log "Token Usage" to the console (simulating observability).
- It should allow switching between "Mock Model" and "Real Model".

### B. The Agent Service ("Content-Creator")
- **Role:** Takes a topic, searches for info (simulated tool), and writes a LinkedIn post.
- **Tools:** `web_search_tool` (Simulated: returns static context).
- **Memory:** Saves the generated post to ChromaDB to remember context.
- **Endpoints:**
  - `POST /generate`: Input {topic}, Output {content, usage}.
  - `GET /history`: Returns last generated posts from Vector DB.

### C. CI/CD Pipeline (GitHub Actions)
- Linting (Ruff).
- Unit Tests (Pytest).
- **CRITICAL:** LLM-as-a-Judge Step. A script that evaluates the generated content quality.

## 4. Folder Structure (Modulith Style)
/
  /src
    /gateway       # The shared inference gateway code
    /agents
      /marketing   # The specific agent logic
    /shared        # Shared utilities (logger, db connection)
  /tests
    /unit
    /evaluation    # LLM-as-a-Judge scripts
  Dockerfile
  docker-compose.yml
  pyproject.toml   # Poetry or pip requirements

## 5. The "LLM-as-a-Judge" Requirement
Create a script `evaluate_agent.py` that:
1. Calls the agent with a test topic.
2. Uses an LLM (or mock) to score the result on: Clarity, Tone, and Length.
3. Fails the pipeline if the score is < 8/10.

## 6. Implementation Instructions for Cursor
- Use Type Hints for everything.
- Add Docstrings following Google style.
- Ensure 12-factor app principles (config via env vars).