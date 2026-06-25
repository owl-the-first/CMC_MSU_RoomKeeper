"""Automation tasks for CMC MSU RoomKeeper project."""

from __future__ import annotations

from pathlib import Path

PROJECT_ROOT = Path(__file__).parent
SRC_DIR = PROJECT_ROOT / "src"
TESTS_DIR = PROJECT_ROOT / "tests"


def task_lint() -> dict[str, object]:
    """Run source code style checks."""

    return {
        "actions": ["python3 -m ruff check src tests scripts"],
        "verbosity": 2,
    }


def task_test() -> dict[str, object]:
    """Run project tests."""

    return {
        "task_dep": ["i18n_compile"],
        "actions": ["python3 -m coverage run -m pytest"],
        "verbosity": 2,
    }


def task_coverage() -> dict[str, object]:
    """Run tests and check coverage threshold."""

    return {
        "task_dep": ["test"],
        "actions": ["python3 -m coverage report"],
        "verbosity": 2,
    }


def task_wheel() -> dict[str, object]:
    """Build wheel distribution."""

    return {
        "task_dep": ["i18n_compile"],
        "actions": ["python3 -m build --wheel"],
        "verbosity": 2,
    }


def task_sdist() -> dict[str, object]:
    """Build source distribution."""

    return {
        "actions": ["python3 -m build --sdist"],
        "verbosity": 2,
    }


def task_build() -> dict[str, object]:
    """Build wheel and source distributions."""

    return {
        "task_dep": ["i18n_compile"],
        "actions": ["python3 -m build"],
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
        "actions": ["python3 -m sphinx -b html docs docs/_build/html"],
        "verbosity": 2,
    }


def task_i18n_extract() -> dict[str, object]:
    """Extract translatable strings into a POT template."""

    return {
        "actions": [
            (
                "pybabel extract -F babel.cfg "
                "-o src/roomkeeper/locales/messages.pot src/roomkeeper"
            ),
        ],
        "verbosity": 2,
    }


def task_i18n_update() -> dict[str, object]:
    """Update locale catalogs from the POT template."""

    return {
        "actions": [
            (
                "pybabel update -i src/roomkeeper/locales/messages.pot "
                "-d src/roomkeeper/locales -l ru"
            ),
            (
                "pybabel update -i src/roomkeeper/locales/messages.pot "
                "-d src/roomkeeper/locales -l en"
            ),
        ],
        "verbosity": 2,
    }


def task_i18n_compile() -> dict[str, object]:
    """Compile locale catalogs to binary MO files."""

    return {
        "actions": ["pybabel compile -d src/roomkeeper/locales"],
        "verbosity": 2,
    }
