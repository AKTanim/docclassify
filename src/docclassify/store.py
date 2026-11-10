"""Documents come from this store. This is a mock of a real store."""

import re
from pathlib import Path, PurePosixPath
from typing import Protocol
from urllib.parse import urlsplit

from docclassify.errors import DocumentNotFound, DocumentTooLarge, StoreUnavailable

# A safe file name: starts with a letter or digit, then only letters, digits,
# dots, dashes and underscores. No slashes, so it cannot point to another folder.
SAFE_NAME = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]*")


class DocumentStore(Protocol):
    """Anything with this fetch method can be used as a store."""

    def fetch(self, url: str) -> bytes: ...


class LocalDocumentStore:
    """Mock store: serves files from a local folder.

    The last part of the URL path picks the file, so
    https://docstore.example.com/f/9f1c2e7a.pdf?exp=1&sig=x reads <folder>/9f1c2e7a.pdf.
    """

    def __init__(self, folder: Path, max_bytes: int) -> None:
        self._folder = folder
        self._max_bytes = max_bytes

    def fetch(self, url: str) -> bytes:
        name = PurePosixPath(urlsplit(url).path).name
        if not SAFE_NAME.fullmatch(name):
            raise DocumentNotFound("The store has no document at this URL.")
        file = self._folder / name
        if not file.is_file():
            raise DocumentNotFound("The store has no document at this URL.")
        try:
            size = file.stat().st_size
            if size > self._max_bytes:
                raise DocumentTooLarge(f"The document is larger than {self._max_bytes} bytes.")
            return file.read_bytes()
        except OSError as exc:
            raise StoreUnavailable("The store could not be read. Try again later.") from exc
