import pytest

from docclassify.errors import InvalidRequest, UrlExpired, UrlNotAllowed
from docclassify.urls import check_url

HOSTS = frozenset({"docstore.example.com"})
NOW = 1_800_000_000


def test_valid_url_passes():
    check_url("https://docstore.example.com/f/a.pdf?exp=1900000000&sig=x", HOSTS, NOW)


def test_url_without_expiry_passes():
    check_url("https://docstore.example.com/f/a.pdf", HOSTS, NOW)


@pytest.mark.parametrize(
    "url",
    [
        "http://docstore.example.com/f/a.pdf",
        "https://evil.example.org/f/a.pdf",
        "https://admin:secret@docstore.example.com/f/a.pdf",
        "https://localhost/f/a.pdf",
        "file:///etc/passwd",
    ],
)
def test_unsafe_urls_are_refused(url):
    with pytest.raises(UrlNotAllowed):
        check_url(url, HOSTS, NOW)


def test_expired_url_is_refused():
    with pytest.raises(UrlExpired):
        check_url("https://docstore.example.com/f/a.pdf?exp=1700000000&sig=x", HOSTS, NOW)


def test_expiry_that_is_not_a_number_is_invalid():
    with pytest.raises(InvalidRequest):
        check_url("https://docstore.example.com/f/a.pdf?exp=soon", HOSTS, NOW)
