"""The shape of a valid request, and the list of categories."""

from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field


class Category(StrEnum):
    QUOTE = "quote"
    DRAWING = "drawing"
    SPECIFICATION = "specification"
    BILL_OF_QUANTITIES = "bill_of_quantities"
    CONTRACT = "contract"
    OTHER = "other"


class Metadata(BaseModel):
    # Ignore unknown fields, so caller can add fields without breaking us.
    # Strip spaces around text values.
    model_config = ConfigDict(extra="ignore", str_strip_whitespace=True)

    document_id: str = Field(min_length=1, max_length=200)
    tenant_id: str = Field(min_length=1, max_length=200)
    file_name: str = Field(min_length=1, max_length=255)
    mime_type: str = Field(min_length=1, max_length=100)


class ClassifyRequest(BaseModel):
    model_config = ConfigDict(extra="ignore", str_strip_whitespace=True)

    request_id: str = Field(min_length=1, max_length=100)
    document_url: str = Field(min_length=1, max_length=2000)
    metadata: Metadata
