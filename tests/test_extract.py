import pytest

from docclassify.errors import UnreadableDocument, UnsupportedDocument
from docclassify.extract import MAX_TEXT_CHARS, extract_text
from tests.helpers import make_locked_pdf, make_pdf


def test_pdf_text_is_read():
    text = extract_text(make_pdf("Offerte voor kozijnen"), "application/pdf")
    assert "Offerte voor kozijnen" in text


def test_pdf_is_detected_by_its_first_bytes():
    # The declared type is wrong, but the content is a PDF.
    text = extract_text(make_pdf("Bill of quantities"), "application/octet-stream")
    assert "Bill of quantities" in text


def test_plain_text_is_read():
    data = "Bestek: gevel geïsoleerd".encode()
    assert extract_text(data, "text/plain") == "Bestek: gevel geïsoleerd"


def test_text_is_cut_to_the_limit():
    text = extract_text(b"a" * (MAX_TEXT_CHARS + 50), "text/plain")
    assert len(text) == MAX_TEXT_CHARS


def test_invalid_utf8_is_unreadable():
    with pytest.raises(UnreadableDocument):
        extract_text(b"\xff\xfe\xfa", "text/plain")


def test_other_types_are_unsupported():
    with pytest.raises(UnsupportedDocument):
        extract_text(b"\x89PNG\r\n", "image/png")


def test_damaged_pdf_is_unreadable():
    with pytest.raises(UnreadableDocument):
        extract_text(b"%PDF-1.7 this is not really a pdf", "application/pdf")


def test_pdf_with_password_is_unreadable():
    with pytest.raises(UnreadableDocument):
        extract_text(make_locked_pdf("Secret", user_password="open-sesame"), "application/pdf")  # noqa: S106


def test_pdf_locked_only_for_editing_is_read():
    text = extract_text(make_locked_pdf("Open me", user_password=""), "application/pdf")
    assert "Open me" in text
