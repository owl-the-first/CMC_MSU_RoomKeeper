"""Command line entry point for database initialization."""

from roomkeeper.db.init_db import create_tables
from roomkeeper.db.session import DEFAULT_DATABASE_URL


def main() -> None:
    """Create all database tables."""

    create_tables()
    print(f"Database initialized: {DEFAULT_DATABASE_URL}")