"""valiopdf: HTML to PDF conversion and PDF tools, powered by headless Chromium."""

from __future__ import annotations

import importlib
from importlib.metadata import PackageNotFoundError, version
from typing import TYPE_CHECKING

from valiopdf.errors import (
    AssetError,
    BlockedRequestError,
    IncompleteRenderError,
    InvalidPdfError,
    LimitExceededError,
    PdfOperationError,
    PdfPasswordError,
    PoolExhaustedError,
    RenderError,
    RenderTimeoutError,
    SignatureInvalidatedWarning,
    SigningError,
    TemplateError,
    ValioPdfError,
)

if TYPE_CHECKING:
    from valiopdf.document import PdfDocument
    from valiopdf.document.forms import FormField
    from valiopdf.document.signing import (
        SignatureBox,
        SignatureInfo,
        SigningKey,
        signature_problems,
    )
    from valiopdf.options import HeaderFooter, Margins, RenderOptions, Viewport
    from valiopdf.render import AsyncRenderer, BrowserPool, Renderer, RequestGuard
    from valiopdf.render.auth import Cookie, RenderAuth, StorageState
    from valiopdf.render.report import FailedRequest, HttpError, RenderReport

try:
    __version__ = version("valiopdf")
except PackageNotFoundError:  # running from a source tree without installing
    __version__ = "0.0.0"

__all__ = [
    "AssetError",
    "AsyncRenderer",
    "BlockedRequestError",
    "BrowserPool",
    "Cookie",
    "FailedRequest",
    "FormField",
    "HeaderFooter",
    "HttpError",
    "IncompleteRenderError",
    "InvalidPdfError",
    "LimitExceededError",
    "Margins",
    "PdfDocument",
    "PdfOperationError",
    "PdfPasswordError",
    "PoolExhaustedError",
    "RenderAuth",
    "RenderError",
    "RenderOptions",
    "RenderReport",
    "RenderTimeoutError",
    "Renderer",
    "RequestGuard",
    "SignatureBox",
    "SignatureInfo",
    "SignatureInvalidatedWarning",
    "SigningError",
    "SigningKey",
    "StorageState",
    "TemplateError",
    "ValioPdfError",
    "Viewport",
    "__version__",
    "signature_problems",
]

# Imported on first use: the per-render proxy process imports valiopdf.errors (and so
# this package) and must not pay for pikepdf, playwright or pydantic
# (see tests/unit/test_proxy_imports.py).
_LAZY = {
    "PdfDocument": "valiopdf.document",
    "FormField": "valiopdf.document.forms",
    "SignatureBox": "valiopdf.document.signing",
    "SignatureInfo": "valiopdf.document.signing",
    "SigningKey": "valiopdf.document.signing",
    "signature_problems": "valiopdf.document.signing",
    "HeaderFooter": "valiopdf.options",
    "Margins": "valiopdf.options",
    "RenderOptions": "valiopdf.options",
    "Viewport": "valiopdf.options",
    "AsyncRenderer": "valiopdf.render",
    "BrowserPool": "valiopdf.render",
    "Renderer": "valiopdf.render",
    "RequestGuard": "valiopdf.render",
    "Cookie": "valiopdf.render.auth",
    "RenderAuth": "valiopdf.render.auth",
    "StorageState": "valiopdf.render.auth",
    "FailedRequest": "valiopdf.render.report",
    "HttpError": "valiopdf.render.report",
    "RenderReport": "valiopdf.render.report",
}


def __getattr__(name: str) -> object:
    module = _LAZY.get(name)
    if module is None:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
    value = getattr(importlib.import_module(module), name)
    globals()[name] = value
    return value
