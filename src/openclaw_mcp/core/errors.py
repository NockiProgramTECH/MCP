"""Safe, user-facing application errors."""


class OpenClawMCPError(Exception):
    """Base class for expected errors safe to present to an MCP client."""


class ConfigurationError(OpenClawMCPError):
    """Raised when an integration is not configured."""


class AuthenticationError(OpenClawMCPError):
    """Raised when an external API rejects credentials."""


class AuthorizationError(OpenClawMCPError):
    """Raised when credentials lack a required permission."""


class ExternalAPIError(OpenClawMCPError):
    """Raised for an external API failure without exposing raw secrets."""


class RateLimitError(ExternalAPIError):
    """Raised when an external API rate limit is reached."""
