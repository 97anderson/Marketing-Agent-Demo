#!/usr/bin/env python
"""Project Structure Verification Script.

This script verifies that all required files and directories exist
in the refactored project structure.
"""

import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def verify_structure():
    """Verify project structure."""
    print("=" * 60)
    print("PROJECT STRUCTURE VERIFICATION")
    print("=" * 60)
    print()

    # Define required structure
    required_items = {
        "Root Files": [
            "README.md",
            "CONTRIBUTING.md",
            "LICENSE",
            "requirements.txt",
            "pyproject.toml",
            "docker-compose.yml",
            "Dockerfile",
            ".gitignore",
            ".env.example",
        ],
        "Directories": [
            "src/",
            "tests/",
            "docs/",
            "scripts/",
            "examples/",
            "knowledge_base/",
        ],
        "Documentation": [
            "docs/specs/",
            "docs/guides/",
            "docs/internal/",
        ],
        "Source Code": [
            "src/gateway/",
            "src/agents/",
            "src/agents/marketing/",
            "src/shared/",
        ],
    }

    all_pass = True

    for category, items in required_items.items():
        print(f"\n{category}:")
        print("-" * 60)

        for item in items:
            path = project_root / item
            exists = path.exists()
            status = "[OK]" if exists else "[FAIL]"
            print(f"  {status} {item}")

            if not exists:
                all_pass = False

    print()
    print("=" * 60)
    if all_pass:
        print("[SUCCESS] ALL CHECKS PASSED")
    else:
        print("[ERROR] SOME CHECKS FAILED")
    print("=" * 60)
    print()

    return all_pass


def verify_imports():
    """Verify that key imports work."""
    print("=" * 60)
    print("IMPORT VERIFICATION")
    print("=" * 60)
    print()

    imports_to_test = [
        ("src.gateway.inference_gateway", "InferenceGateway"),
        ("src.agents.marketing.agent", "MarketingAgent"),
        ("src.shared.config", "get_settings"),
        ("src.shared.logger", "setup_logging"),
    ]

    all_pass = True

    for module_name, class_name in imports_to_test:
        try:
            module = __import__(module_name, fromlist=[class_name])
            getattr(module, class_name)
            print(f"  [OK] from {module_name} import {class_name}")
        except (ImportError, AttributeError) as e:
            print(f"  [FAIL] from {module_name} import {class_name}")
            print(f"     Error: {e}")
            all_pass = False

    print()
    print("=" * 60)
    if all_pass:
        print("[SUCCESS] ALL IMPORTS OK")
    else:
        print("[ERROR] SOME IMPORTS FAILED")
    print("=" * 60)
    print()

    return all_pass


def main():
    """Run all verifications."""
    structure_ok = verify_structure()
    imports_ok = verify_imports()

    if structure_ok and imports_ok:
        print("\n[SUCCESS] PROJECT VERIFICATION COMPLETE - ALL CHECKS PASSED")
        return 0
    else:
        print("\n[ERROR] PROJECT VERIFICATION FAILED")
        return 1


if __name__ == "__main__":
    sys.exit(main())
