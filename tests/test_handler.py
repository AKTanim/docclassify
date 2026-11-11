from docclassify.classifier import KeywordClassifier
from docclassify.handler import Deps, handle
from tests.helpers import FakeStore, make_pdf

URL = "https://docstore.example.com/f/9f1c2e7a.pdf?exp=1761663129&sig=7d1e9c42"


def event(**changes) -> dict:
    base = {
        "request_id": "req-1",
        "document_url": URL,
        "metadata": {
            "document_id": "9f1c2e7a",
            "tenant_id": "contractor-1042",
            "file_name": "Offerte_kozijnen_fase2.pdf",
            "mime_type": "application/pdf",
        },
    }
    base.update(changes)
    return base


def deps_with(documents: dict[str, bytes]) -> Deps:
    return Deps(store=FakeStore(documents), classifier=KeywordClassifier())


def test_quote_is_classified():
    deps = deps_with({URL: make_pdf("Offerte kozijnen. Geldig tot 1 april.")})
    response = handle(event(), deps)
    assert response == {
        "request_id": "req-1",
        "status": "ok",
        "document_id": "9f1c2e7a",
        "category": "quote",
        "confidence": 1.0,
        "classifier": "keywords",
        "warnings": [],
    }


def test_invalid_request_returns_a_clear_error():
    response = handle({"request_id": "req-2"}, deps_with({}))
    assert response["status"] == "error"
    assert response["request_id"] == "req-2"
    assert response["error"]["code"] == "INVALID_REQUEST"
    assert "document_url" in response["error"]["message"]
    assert response["error"]["retryable"] is False


def test_event_that_is_not_a_dictionary_is_invalid():
    response = handle("not a dict", deps_with({}))
    assert response["request_id"] is None
    assert response["error"]["code"] == "INVALID_REQUEST"


def test_missing_document_returns_not_found():
    response = handle(event(), deps_with({}))
    assert response["error"]["code"] == "DOCUMENT_NOT_FOUND"


def test_unsupported_type_falls_back_to_the_file_name():
    metadata = {
        "document_id": "d2",
        "tenant_id": "t1",
        "file_name": "plattegrond_A01.dwg",
        "mime_type": "image/vnd.dwg",
    }
    deps = deps_with({URL: b"AC1032 binary drawing"})
    response = handle(event(metadata=metadata), deps)
    assert response["category"] == "drawing"
    assert response["warnings"] == ["content_not_read"]


def test_pdf_without_text_gets_a_warning():
    deps = deps_with({URL: make_pdf("")})
    response = handle(event(), deps)
    assert response["category"] == "quote"
    assert response["warnings"] == ["no_text_found"]


class BrokenClassifier:
    def classify(self, text, file_name):
        raise RuntimeError("bug")


def test_unexpected_error_returns_internal_error():
    request = event()
    request["metadata"]["mime_type"] = "text/plain"
    deps = Deps(store=FakeStore({URL: b"hello"}), classifier=BrokenClassifier())
    response = handle(request, deps)
    assert response["error"] == {
        "code": "INTERNAL_ERROR",
        "message": "Something went wrong on our side.",
        "retryable": False,
    }
