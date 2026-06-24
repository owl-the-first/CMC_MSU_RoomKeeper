"""Command line entry point for running the Telegram bot."""

from roomkeeper.bot.app import run_bot


def main() -> None:
    """Run the Telegram bot."""
    run_bot()