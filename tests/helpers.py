"""Small tools shared by the tests."""

import io

from fpdf import FPDF
from pypdf import PdfReader, PdfWriter


def make_pdf(text: str) -> bytes:
    """Build a one-page PDF in memory that contains the given text."""
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", size=12)
    pdf.multi_cell(0, 10, text)
    return bytes(pdf.output())


def make_locked_pdf(text: str, user_password: str) -> bytes:
    """Build a PDF that needs user_password to open. An empty one opens freely."""
    writer = PdfWriter(clone_from=PdfReader(io.BytesIO(make_pdf(text))))
    writer.encrypt(user_password=user_password, owner_password="owner-secret")  # noqa: S106
    buffer = io.BytesIO()
    writer.write(buffer)
    return buffer.getvalue()
