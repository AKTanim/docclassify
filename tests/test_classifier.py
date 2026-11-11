import pytest

from docclassify.classifier import KeywordClassifier, count_phrase, words_of
from docclassify.models import Category


def test_words_are_split_on_symbols():
    assert words_of("Offerte_kozijnen-fase2.PDF") == ["offerte", "kozijnen", "fase2", "pdf"]


def test_phrases_are_counted_as_whole_words():
    words = words_of("Valid until May. Valid until June. Invalid untilted.")
    assert count_phrase(words, "valid until") == 2


@pytest.mark.parametrize(
    ("text", "file_name", "expected"),
    [
        ("Prijsopgave, geldig tot 1 maart", "doc1.pdf", Category.QUOTE),
        ("Plattegrond begane grond, schaal 1:100", "A-101.pdf", Category.DRAWING),
        ("Technical requirements for the facade", "spec.pdf", Category.SPECIFICATION),
        ("Item, quantity, unit price, total", "boq.xlsx", Category.BILL_OF_QUANTITIES),
        ("This agreement is made between the parties", "doc.pdf", Category.CONTRACT),
    ],
)
def test_keywords_pick_the_category(text, file_name, expected):
    assert KeywordClassifier().classify(text, file_name).category == expected


def test_file_name_counts_as_evidence():
    result = KeywordClassifier().classify("", "Offerte_kozijnen_fase2.pdf")
    assert result.category == Category.QUOTE
    assert result.confidence == 1.0


def test_no_keywords_means_other_with_zero_confidence():
    result = KeywordClassifier().classify("Meeting notes from Tuesday", "notes.txt")
    assert result.category == Category.OTHER
    assert result.confidence == 0.0


def test_confidence_is_the_share_of_hits():
    # Two quote hits and one contract hit: 2 of 3.
    result = KeywordClassifier().classify("quote quote contract", "x.pdf")
    assert result.category == Category.QUOTE
    assert result.confidence == 0.67


def test_part_of_a_word_does_not_count():
    # "contractor" must not count as "contract".
    result = KeywordClassifier().classify("Contractor visit report", "x.pdf")
    assert result.category == Category.OTHER
