"""Turns text into one of the six categories."""

import re
from dataclasses import dataclass
from typing import Protocol

from docclassify.models import Category


@dataclass(frozen=True)
class Classification:
    category: Category
    confidence: float
    classifier: str


class Classifier(Protocol):
    """Anything with this classify method can be used as a classifier."""

    def classify(self, text: str, file_name: str) -> Classification: ...


# English and Dutch words and phrases that point to each category, in lower case.
KEYWORDS: dict[Category, tuple[str, ...]] = {
    Category.QUOTE: ("quote", "quotation", "offerte", "prijsopgave", "valid until", "geldig tot"),
    Category.DRAWING: ("drawing", "tekening", "scale", "schaal", "floor plan", "plattegrond"),
    Category.SPECIFICATION: ("specification", "specifications", "bestek", "requirements"),
    Category.BILL_OF_QUANTITIES: (
        "bill of quantities",
        "boq",
        "staat van hoeveelheden",
        "unit price",
        "eenheidsprijs",
    ),
    Category.CONTRACT: ("contract", "agreement", "overeenkomst", "aannemingsovereenkomst"),
}


def words_of(text: str) -> list[str]:
    """Lower-case words, split on anything that is not a letter or a digit."""
    return [word for word in re.split(r"[\W_]+", text.lower()) if word]


def count_phrase(words: list[str], phrase: str) -> int:
    """How often the phrase appears as whole words in the list."""
    parts = phrase.split()
    size = len(parts)
    return sum(1 for i in range(len(words) - size + 1) if words[i : i + size] == parts)


class KeywordClassifier:
    """Counts keywords per category. Confidence is the winner's share of all hits."""

    name = "keywords"

    def classify(self, text: str, file_name: str) -> Classification:
        words = words_of(f"{file_name} {text}")
        scores = {
            category: sum(count_phrase(words, phrase) for phrase in phrases)
            for category, phrases in KEYWORDS.items()
        }
        total = sum(scores.values())
        if total == 0:
            return Classification(Category.OTHER, 0.0, self.name)
        best = max(scores, key=lambda category: scores[category])
        return Classification(best, round(scores[best] / total, 2), self.name)
