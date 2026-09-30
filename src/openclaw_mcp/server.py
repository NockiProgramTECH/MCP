"""MCP server construction and process entry point."""

import logging

from mcp.server.fastmcp import FastMCP

from .config import get_settings
from .core.logging import configure_logging

logger = logging.getLogger(__name__)


def create_server() -> FastMCP:
    """Build the MCP server and register the currently available tools."""
    settings = get_settings()
    server = FastMCP(
        name="openclaw-mcp",
        instructions=(
            "Secure gateway for configured OpenClaw integrations. "
            "Only use write tools when the user explicitly requests the external action."
        ),
    )

    @server.tool(description="Returns the server name and configured integration status.")
    def server_status() -> dict[str, object]:
        """Return non-sensitive startup information for connectivity checks."""
        configured = {
            "github": settings.github_token is not None,
            "linkedin": settings.linkedin_access_token is not None,
            "meta": settings.meta_access_token is not None,
            "instagram": settings.instagram_access_token is not None,
            "tiktok": settings.tiktok_access_token is not None,
        }
        return {"server": "openclaw-mcp", "version": "0.1.0", "configured": configured}

    return server


def run() -> None:
    """Configure stderr logging and run the server over MCP stdio."""
    settings = get_settings()
    configure_logging(settings.log_level)
    logger.info("Starting OpenClaw MCP server over stdio")
    create_server().run(transport="stdio")
