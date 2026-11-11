"""Checks on a document URL before anything is downloaded."""

from urllib.parse import parse_qs, urlsplit

from docclassify.errors import InvalidRequest, UrlExpired, UrlNotAllowed


def check_url(url: str, allowed_hosts: frozenset[str], now: float) -> None:
    """Raise an error if the URL must not be fetched. Return nothing if it is fine."""
    parts = urlsplit(url)
    if parts.scheme != "https":
        raise UrlNotAllowed("Only https URLs are accepted.")
    if parts.username or parts.password:
        raise UrlNotAllowed("URLs that contain a user name or password are not accepted.")
    if (parts.hostname or "") not in allowed_hosts:
        raise UrlNotAllowed("This host is not on the allowed list.")

    # exp is the time the signed URL stops working, in seconds since 1 January 1970.
    expiry = parse_qs(parts.query).get("exp")
    if expiry is None:  # not all urls are signed
        return
    try:
        expires_at = int(expiry[0])
    except ValueError as exc:
        raise InvalidRequest("The exp value in the URL is not a whole number.") from exc
    if expires_at < now:
        raise UrlExpired("The URL has expired. Ask the document store for a new one.")
