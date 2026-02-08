#!/usr/bin/env python
"""Project verification script.

This script checks that all required files and directories are present.
"""

import os
import sys
from pathlib import Path


def check_structure():
    """Check that all required project files exist."""
    
    required_files = [
        # Root files
        "README.md",
        "QUICKSTART.md",
        "CONTRIBUTING.md",
        "LICENSE",
        "PROJECT_SUMMARY.md",
        "ARCHITECTURE_SPEC.md",
        "requirements.txt",
        "pyproject.toml",
        "docker-compose.yml",
        "Dockerfile",
        ".gitignore",
        "run.py",
        "dev.py",
        
        # Source files
        "src/__init__.py",
        "src/gateway/__init__.py",
        "src/gateway/inference_gateway.py",
        "src/gateway/models.py",
        "src/agents/__init__.py",
        "src/agents/marketing/__init__.py",
        "src/agents/marketing/agent.py",
        "src/agents/marketing/api.py",
        "src/agents/marketing/models.py",
        "src/agents/marketing/tools.py",
        "src/shared/__init__.py",
        "src/shared/config.py",
        "src/shared/logger.py",
        "src/shared/database.py",
        
        # Test files
        "tests/__init__.py",
        "tests/conftest.py",
        "tests/unit/__init__.py",
        "tests/unit/test_gateway.py",
        "tests/unit/test_agent.py",
        "tests/unit/test_api.py",
        "tests/unit/test_shared.py",
        "tests/unit/test_evaluation.py",
        "tests/evaluation/__init__.py",
        "tests/evaluation/evaluate_agent.py",
        
        # Examples
        "examples/__init__.py",
        "examples/api_usage.py",
        "examples/direct_agent.py",
        
        # CI/CD
        ".github/workflows/ci-cd.yml",
    ]
    
    required_dirs = [
        "src",
        "src/gateway",
        "src/agents",
        "src/agents/marketing",
        "src/shared",
        "tests",
        "tests/unit",
        "tests/evaluation",
        "examples",
        ".github",
        ".github/workflows",
    ]
    
    print("=" * 70)
    print("PROJECT STRUCTURE VERIFICATION")
    print("=" * 70)
    
    root_path = Path(__file__).parent
    all_good = True
    
    # Check directories
    print("\n[Directories] Checking directories...")
    missing_dirs = []
    for dir_path in required_dirs:
        full_path = root_path / dir_path
        if full_path.exists():
            print(f"  [OK] {dir_path}")
        else:
            print(f"  [MISSING] {dir_path}")
            missing_dirs.append(dir_path)
            all_good = False
    
    # Check files
    print("\n[Files] Checking files...")
    missing_files = []
    for file_path in required_files:
        full_path = root_path / file_path
        if full_path.exists():
            size = full_path.stat().st_size
            print(f"  [OK] {file_path} ({size:,} bytes)")
        else:
            print(f"  [MISSING] {file_path}")
            missing_files.append(file_path)
            all_good = False
    
    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"Total directories checked: {len(required_dirs)}")
    print(f"Total files checked: {len(required_files)}")
    
    if all_good:
        print("\n[SUCCESS] ALL CHECKS PASSED!")
        print("\nProject structure is complete and ready to use.")
        print("\n[Quick Start]")
        print("   1. docker-compose up --build")
        print("   2. Visit http://localhost:8000/docs")
        return 0
    else:
        print(f"\n[ERROR] MISSING {len(missing_dirs)} directories and {len(missing_files)} files")
        if missing_dirs:
            print(f"\nMissing directories: {', '.join(missing_dirs)}")
        if missing_files:
            print(f"\nMissing files: {', '.join(missing_files)}")
        return 1


if __name__ == "__main__":
    sys.exit(check_structure())

