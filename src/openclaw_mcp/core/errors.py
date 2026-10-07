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

    def __init__(self, message: str, *, status_code: int | None = None) -> None:
        super().__init__(message)
        self.status_code = status_code


class RateLimitError(ExternalAPIError):
    """Raised when an external API rate limit is reached."""

    def __init__(self, message: str, *, retry_after: float | None = None) -> None:
        super().__init__(message, status_code=429)
        self.retry_after = retry_after
