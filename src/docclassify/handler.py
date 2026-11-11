"""The Lambda entry point: checks the request, runs the steps, builds the response."""

import logging
import os
import time
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from pydantic import ValidationError

from docclassify.classifier import Classifier, KeywordClassifier
from docclassify.errors import AppError, InvalidRequest, UnsupportedDocument
from docclassify.extract import extract_text
from docclassify.models import ClassifyRequest
from docclassify.store import DocumentStore, LocalDocumentStore
from docclassify.urls import check_url

logger = logging.getLogger("docclassify")


@dataclass(frozen=True)
class Deps:
    """The outside parts the handler needs. Tests pass in fakes."""

    store: DocumentStore
    classifier: Classifier
    allowed_hosts: frozenset[str]
    clock: Callable[[], float] = field(default=time.time)


def build_deps() -> Deps:
    """Create the real parts once, from environment variables."""
    folder = Path(os.environ.get("DOCUMENT_STORE_DIR", "sample_docs"))
    max_bytes = int(os.environ.get("MAX_DOCUMENT_BYTES", "10000000"))
    hosts = os.environ.get("ALLOWED_HOSTS", "docstore.example.com")
    return Deps(
        store=LocalDocumentStore(folder, max_bytes),
        classifier=KeywordClassifier(),
        allowed_hosts=frozenset(host.strip().lower() for host in hosts.split(",") if host.strip()),
    )


def describe(exc: ValidationError) -> str:
    """Turn pydantic's error list into one short sentence for the caller."""
    problems = []
    for error in exc.errors():
        location = ".".join(str(part) for part in error["loc"]) or "request"
        problems.append(f"{location}: {error['msg']}")
    return "Invalid request. " + "; ".join(problems)


def error_response(request_id: Any, error: AppError) -> dict:
    return {
        "request_id": request_id if isinstance(request_id, str) else None,
        "status": "error",
        "error": {"code": error.code, "message": error.message, "retryable": error.retryable},
    }


def handle(event: Any, deps: Deps) -> dict:
    """Classify one document. Always returns a dictionary, never raises."""
    request_id = event.get("request_id") if isinstance(event, dict) else None
    try:
        try:
            request = ClassifyRequest.model_validate(event)
        except ValidationError as exc:
            raise InvalidRequest(describe(exc)) from exc

        check_url(request.document_url, deps.allowed_hosts, deps.clock())
        content = deps.store.fetch(request.document_url)

        warnings: list[str] = []
        try:
            text = extract_text(content, request.metadata.mime_type)
        except UnsupportedDocument:
            text = ""
            warnings.append("content_not_read")
        if not text.strip() and not warnings:
            warnings.append("no_text_found")

        result = deps.classifier.classify(text, request.metadata.file_name)
    except AppError as error:
        logger.warning("request_failed request_id=%s code=%s", request_id, error.code)
        return error_response(request_id, error)
    except Exception:
        # A bug, not a bad request. Log the full error for us, return a safe message.
        logger.exception("unexpected_error request_id=%s", request_id)
        return error_response(request_id, AppError("Something went wrong on our side."))

    return {
        "request_id": request.request_id,
        "status": "ok",
        "document_id": request.metadata.document_id,
        "category": result.category.value,
        "confidence": result.confidence,
        "classifier": result.classifier,
        "warnings": warnings,
    }


# Created once when Lambda loads this file, then reused by every request.
DEPS = build_deps()


def lambda_handler(event: Any, context: Any) -> dict:
    return handle(event, DEPS)
