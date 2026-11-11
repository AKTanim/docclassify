"""Every error the service can return to a caller."""


class AppError(Exception):
    """Base class. Every subclass sets its own code
    and whether a retry can help."""

    code = "INTERNAL_ERROR"
    retryable = False

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


class InvalidRequest(AppError):
    code = "INVALID_REQUEST"


class DocumentNotFound(AppError):
    code = "DOCUMENT_NOT_FOUND"


class DocumentTooLarge(AppError):
    code = "DOCUMENT_TOO_LARGE"


class StoreUnavailable(AppError):
    code = "STORE_UNAVAILABLE"
    retryable = True


class UnreadableDocument(AppError):
    code = "UNREADABLE_DOCUMENT"


class UnsupportedDocument(AppError):
    # Raised by the text extractor. The service catches it and falls back
    # to the file name, so callers never receive this code.
    code = "UNSUPPORTED_DOCUMENT"


class UrlNotAllowed(AppError):
    code = "URL_NOT_ALLOWED"


class UrlExpired(AppError):
    # The caller must ask for a new URL. Sending the same one again cannot work.
    code = "URL_EXPIRED"
