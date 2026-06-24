"""Automation tasks for CMC MSU RoomKeeper project."""

from __future__ import annotations

from pathlib import Path

PROJECT_ROOT = Path(__file__).parent
SRC_DIR = PROJECT_ROOT / "src"
TESTS_DIR = PROJECT_ROOT / "tests"


def task_lint() -> dict[str, object]:
    """Run source code style checks."""

    return {
        "actions": ["python -m ruff check src tests scripts"],
        "verbosity": 2,
    }


def task_test() -> dict[str, object]:
    """Run project tests."""

    return {
        "actions": ["python -m pytest"],
        "verbosity": 2,
    }


def task_coverage() -> dict[str, object]:
    """Run tests and check coverage threshold."""

    return {
        "actions": [
            "python -m coverage run -m pytest",
            "python -m coverage report",
        ],
        "verbosity": 2,
    }


def task_wheel() -> dict[str, object]:
    """Build wheel distribution."""

    return {
        "actions": ["python -m build --wheel"],
        "verbosity": 2,
    }


def task_sdist() -> dict[str, object]:
    """Build source distribution."""

    return {
        "actions": ["python -m build --sdist"],
        "verbosity": 2,
    }


def task_build() -> dict[str, object]:
    """Build wheel and source distributions."""

    return {
        "actions": ["python -m build"],
        "verbosity": 2,
    }


def task_cleanup() -> dict[str, object]:
    """Remove generated build and coverage files."""

    return {
        "actions": [
            "rm -rf build dist *.egg-info src/*.egg-info .coverage htmlcov",
        ],
        "verbosity": 2,
    }


def task_docs() -> dict[str, object]:
    """Build HTML documentation."""

    return {
        "actions": ["python -m sphinx -b html docs docs/_build/html"],
        "verbosity": 2,
    }
