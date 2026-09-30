"""Security helpers for outbound integration requests."""

from urllib.parse import urlparse

from .errors import ExternalAPIError


def validate_external_url(url: str, allowed_hosts: set[str] | frozenset[str]) -> None:
    """Reject unsafe URLs before making an outbound request.

    Integrations should pass a small, explicit allow-list of official API hosts.
    This prevents an arbitrary URL from becoming an SSRF primitive.
    """
    parsed = urlparse(url)
    hostname = parsed.hostname
    if parsed.scheme != "https":
        raise ExternalAPIError("Only HTTPS URLs are allowed for external API requests.")
    if not hostname or hostname.lower() not in {host.lower() for host in allowed_hosts}:
        raise ExternalAPIError("The external API host is not allowed.")
    if parsed.username or parsed.password:
        raise ExternalAPIError("URLs containing user credentials are not allowed.")
    if parsed.fragment:
        raise ExternalAPIError("URLs containing fragments are not allowed.")
