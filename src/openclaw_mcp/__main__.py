"""Command-line entry point for the OpenClaw MCP server."""

from .server import run


def main() -> None:
    """Start the MCP server using its configured transport."""
    run()


if __name__ == "__main__":
    main()
