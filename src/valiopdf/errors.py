"""Exception hierarchy for valiopdf.

Every error raised on purpose by the library is a subclass of :class:`ValioPdfError`.
Each class has a stable ``code`` string; the HTTP service uses it in error responses
and maps it to a status code in one place (``valiopdf.server.errors``).
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from valiopdf.render.report import RenderReport


class ValioPdfError(Exception):
    """Base class for all valiopdf errors."""

    code: str = "internal_error"

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


class RenderError(ValioPdfError):
    """Rendering HTML to PDF failed."""

    code = "render_failed"


class RenderTimeoutError(RenderError):
    """A render took longer than its timeout."""

    code = "render_timeout"

    def __init__(self, message: str, *, timeout_ms: int) -> None:
        super().__init__(message)
        self.timeout_ms = timeout_ms


class BlockedRequestError(RenderError):
    """The request guard refused a URL (SSRF protection)."""

    code = "blocked_request"

    def __init__(self, message: str, *, url: str) -> None:
        super().__init__(message)
        self.url = url


class IncompleteRenderError(RenderError):
    """A strict render found missing resources or script errors (see ``.report``)."""

    code = "render_incomplete"

    def __init__(self, message: str, *, report: RenderReport) -> None:
        super().__init__(message)
        self.report = report


class TemplateError(ValioPdfError):
    """A Jinja2 template could not be found, parsed or rendered."""

    code = "invalid_template"


class AssetError(ValioPdfError):
    """An asset bundle is invalid, e.g. a path with ``..`` or too many files."""

    code = "invalid_request"


class InvalidPdfError(ValioPdfError):
    """Input bytes could not be read as a PDF."""

    code = "invalid_pdf"


class PdfPasswordError(InvalidPdfError):
    """The PDF is password-protected and no (or the wrong) password was given."""

    code = "pdf_password"


class PdfOperationError(ValioPdfError):
    """A PDF operation got arguments it can't apply, e.g. a page out of range."""

    code = "invalid_request"


class LimitExceededError(PdfOperationError):
    """An operation's output would pass a size limit, e.g. too many pixels."""

    code = "limit_exceeded"


class SigningError(ValioPdfError):
    """Signing or reading signatures failed (bad key file, unreadable signature...)."""

    code = "signing_failed"


class SignatureInvalidatedWarning(UserWarning):
    """An operation on a signed document writes a new file, which would break its
    signatures, so the result has them removed."""


class PoolExhaustedError(ValioPdfError):
    """Too many renders are already waiting for a browser slot."""

    code = "busy"


__all__ = [
    "AssetError",
    "BlockedRequestError",
    "IncompleteRenderError",
    "InvalidPdfError",
    "LimitExceededError",
    "PdfOperationError",
    "PdfPasswordError",
    "PoolExhaustedError",
    "RenderError",
    "RenderTimeoutError",
    "SignatureInvalidatedWarning",
    "SigningError",
    "TemplateError",
    "ValioPdfError",
]


def describe_validation_errors(errors: Sequence[Mapping[str, Any]]) -> str:
    """One line from pydantic/FastAPI validation errors: "field.path: message; ...".
    Uses only each error's location and message, never its input (which may be secret)."""
    details = "; ".join(
        f"{'.'.join(str(p) for p in e['loc'] if p != 'body')}: {e['msg']}" for e in errors
    )
    return details or "invalid request"
