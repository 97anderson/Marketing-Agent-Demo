# Contribution Guidelines

Thank you for considering contributing to the Marketing Agent Demo!

## How to Contribute

### Reporting Issues

- Use the GitHub issue tracker
- Describe the issue clearly
- Include steps to reproduce
- Provide system information

### Pull Requests

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass: `pytest tests/ -v`
6. Run linting: `ruff check src/ tests/`
7. Commit with clear messages
8. Push to your fork
9. Create a Pull Request

### Code Standards

- Follow PEP 8 style guide
- Use type hints for all functions
- Add docstrings (Google style)
- Write unit tests (80%+ coverage)
- Keep functions focused and small
- Use meaningful variable names

### Testing Requirements

All PRs must:
- Pass all existing tests
- Add tests for new features
- Maintain or improve coverage
- Pass the LLM-as-a-Judge evaluation

### Commit Messages

Format: `<type>(<scope>): <description>`

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `test`: Tests
- `refactor`: Code refactoring
- `chore`: Maintenance

Example: `feat(agent): add support for Twitter posts`

## Development Setup

```bash
# Clone repo
git clone <your-fork>
cd marketing-agent-demo

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run tests
pytest tests/ -v
```

## Questions?

Open an issue for discussion before starting major changes.

Thank you! 🙏

