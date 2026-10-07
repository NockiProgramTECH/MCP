"""Security helpers for outbound integration requests."""

import ipaddress
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


def validate_public_media_url(url: str) -> None:
    """Validate a public HTTPS media URL passed to Meta for server-side fetching."""
    parsed = urlparse(url)
    hostname = parsed.hostname
    if parsed.scheme != "https" or not hostname:
        raise ExternalAPIError("Media URLs must use HTTPS and include a hostname.")
    if parsed.username or parsed.password or parsed.fragment:
        raise ExternalAPIError("Media URLs cannot contain credentials or fragments.")
    if hostname.lower() in {"localhost", "localhost.localdomain"}:
        raise ExternalAPIError("Local media URLs are not allowed.")
    try:
        address = ipaddress.ip_address(hostname)
    except ValueError:
        return
    if address.is_private or address.is_loopback or address.is_link_local or address.is_reserved:
        raise ExternalAPIError("Private or reserved media URLs are not allowed.")
