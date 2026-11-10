import pytest
from pydantic import ValidationError

from docclassify.models import ClassifyRequest


def valid_event() -> dict:
    return {
        "request_id": "req-1",
        "document_url": "https://docstore.example.com/f/9f1c2e7a.pdf?exp=1&sig=x",
        "metadata": {
            "document_id": "9f1c2e7a",
            "tenant_id": "contractor-1042",
            "file_name": "Offerte_kozijnen_fase2.pdf",
            "mime_type": "application/pdf",
        },
    }


def test_valid_request_is_accepted():
    request = ClassifyRequest.model_validate(valid_event())
    assert request.metadata.file_name == "Offerte_kozijnen_fase2.pdf"


def test_spaces_are_stripped():
    event = valid_event()
    event["request_id"] = "  req-1  "
    assert ClassifyRequest.model_validate(event).request_id == "req-1"


def test_unknown_fields_are_ignored():
    event = valid_event()
    request = ClassifyRequest.model_validate({**event, "priority": "high"})
    assert not hasattr(request, "priority")


@pytest.mark.parametrize(
    "metadata_change",
    [
        {"tenant_id": 1042},
        {"tenant_id": "   "},
        {"file_name": "    "},
        {"file_name": "x" * 300},
    ],
)
def test_bad_metadata_is_rejected(metadata_change):
    event = valid_event()
    data = {**event, "metadata": {**event["metadata"], **metadata_change}}
    with pytest.raises(ValidationError):
        ClassifyRequest.model_validate(data)


def test_missing_url_is_rejected():
    event = valid_event()
    data = {key: value for key, value in event.items() if key != "document_url"}
    with pytest.raises(ValidationError):
        ClassifyRequest.model_validate(data)
