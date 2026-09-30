from openclaw_mcp.core.errors import ExternalAPIError
from openclaw_mcp.core.security import validate_external_url, validate_public_media_url


def test_allows_https_url_on_explicit_host() -> None:
    validate_external_url("https://api.example.com/v1/items", {"api.example.com"})


def test_rejects_non_https_url() -> None:
    try:
        validate_external_url("http://api.example.com/v1/items", {"api.example.com"})
    except ExternalAPIError as exc:
        assert "HTTPS" in str(exc)
    else:
        raise AssertionError("unsafe URL was accepted")


def test_rejects_unlisted_host() -> None:
    try:
        validate_external_url("https://evil.example/v1/items", {"api.example.com"})
    except ExternalAPIError as exc:
        assert "not allowed" in str(exc)
    else:
        raise AssertionError("unlisted host was accepted")


def test_rejects_url_credentials() -> None:
    try:
        validate_external_url("https://user:password@api.example.com/items", {"api.example.com"})
    except ExternalAPIError as exc:
        assert "credentials" in str(exc)
    else:
        raise AssertionError("URL credentials were accepted")


def test_rejects_private_media_url() -> None:
    try:
        validate_public_media_url("https://10.0.0.1/media.jpg")
    except ExternalAPIError as exc:
        assert "Private" in str(exc)
    else:
        raise AssertionError("private media URL was accepted")
