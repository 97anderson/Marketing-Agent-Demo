#!/usr/bin/env python
"""Development helper script for common tasks."""

import argparse
import subprocess
import sys


def run_command(cmd, description):
    """Run a shell command and handle errors."""
    print(f"\n{'=' * 60}")
    print(f"Running: {description}")
    print(f"{'=' * 60}\n")
    
    result = subprocess.run(cmd, shell=True)
    
    if result.returncode != 0:
        print(f"\n❌ {description} failed!")
        sys.exit(1)
    
    print(f"\n✅ {description} completed successfully!")


def main():
    """Parse arguments and run commands."""
    parser = argparse.ArgumentParser(description="Development helper script")
    parser.add_argument(
        "command",
        choices=["test", "lint", "format", "evaluate", "run", "docker", "clean"],
        help="Command to run"
    )
    
    args = parser.parse_args()
    
    commands = {
        "test": ("pytest tests/ -v --cov=src --cov-report=term --cov-report=html", "Unit Tests"),
        "lint": ("ruff check src/ tests/", "Linting"),
        "format": ("ruff format src/ tests/", "Code Formatting"),
        "evaluate": ("python tests/evaluation/evaluate_agent.py", "LLM-as-a-Judge Evaluation"),
        "run": ("python run.py", "Application"),
        "docker": ("docker-compose up --build", "Docker Services"),
        "clean": ("rm -rf __pycache__ .pytest_cache .ruff_cache htmlcov .coverage evaluation_results.json && find . -type d -name __pycache__ -exec rm -rf {} +", "Cleanup")
    }
    
    if args.command in commands:
        cmd, desc = commands[args.command]
        run_command(cmd, desc)
    else:
        print(f"Unknown command: {args.command}")
        sys.exit(1)


if __name__ == "__main__":
    main()

