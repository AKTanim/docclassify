"""Turns the downloaded bytes into text the classifier can read."""

import io

from pypdf import PdfReader
from pypdf.errors import PdfReadError

from docclassify.errors import UnreadableDocument, UnsupportedDocument

# Only the start of a document is needed to classify it. A limit keeps
# very long documents from slowing the service down.
MAX_TEXT_CHARS = 20_000

PDF_SIGNATURE = b"%PDF-"


def extract_text(data: bytes, mime_type: str) -> str:
    """Return the document's text, cut to MAX_TEXT_CHARS."""
    # Trust the file's first bytes over the declared type.
    if data.startswith(PDF_SIGNATURE):
        text = _pdf_text(data)
    elif mime_type.startswith("text/"):
        text = _plain_text(data)
    else:
        raise UnsupportedDocument(f"Cannot read text from type {mime_type}.")
    return text[:MAX_TEXT_CHARS]


def _plain_text(data: bytes) -> str:
    try:
        return data.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise UnreadableDocument("The text file is not valid UTF-8.") from exc


def _pdf_text(data: bytes) -> str:
    try:
        reader = PdfReader(io.BytesIO(data))
        # Many PDFs are encrypted with an empty password and open normally.
        if reader.is_encrypted and not reader.decrypt(""):
            raise UnreadableDocument("The PDF is protected with a password.")
        pages = []
        total = 0
        for page in reader.pages:
            page_text = page.extract_text() or ""
            pages.append(page_text)
            total += len(page_text)
            if total >= MAX_TEXT_CHARS:
                break
        return "\n".join(pages)
    except PdfReadError as exc:
        raise UnreadableDocument("The PDF file is damaged.") from exc
