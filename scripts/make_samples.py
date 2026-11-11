"""Create the sample documents that the mock-store serves."""

from pathlib import Path

from fpdf import FPDF

FOLDER = Path("sample_docs")


def write_pdf(name: str, lines: list[str]) -> None:
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", size=12)
    for line in lines:
        pdf.cell(text=line, new_x="LMARGIN", new_y="NEXT")
    pdf.output(str(FOLDER / name))


def main() -> None:
    FOLDER.mkdir(exist_ok=True)
    write_pdf(
        "9f1c2e7a.pdf",
        ["Offerte kozijnen fase 2", "Totaal: EUR 48.250 excl. btw", "Geldig tot 31 maart 2026"],
    )
    write_pdf(
        "3b7d1a20.pdf",
        ["Aannemingsovereenkomst", "This agreement is made between the client and the builder."],
    )
    (FOLDER / "5c2e9f41.txt").write_text(
        "Staat van hoeveelheden\nItem; quantity; unit price\nMetselwerk; 120 m2; 85.00\n",
        encoding="utf-8",
    )
    print(f"Sample documents written to {FOLDER}/")


if __name__ == "__main__":
    main()
