"""HTML to PDF with headless Chromium."""

from __future__ import annotations

import importlib
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from valiopdf.render.guards import RequestGuard
    from valiopdf.render.pool import BrowserPool
    from valiopdf.render.renderer import AsyncRenderer
    from valiopdf.render.sync import Renderer

__all__ = ["AsyncRenderer", "BrowserPool", "Renderer", "RequestGuard"]

# Imported on first use: the proxy subprocess imports valiopdf.render._netpolicy and
# must not pay for playwright (see tests/unit/test_proxy_imports.py).
_LAZY = {
    "AsyncRenderer": "valiopdf.render.renderer",
    "BrowserPool": "valiopdf.render.pool",
    "Renderer": "valiopdf.render.sync",
    "RequestGuard": "valiopdf.render.guards",
}


def __getattr__(name: str) -> object:
    module = _LAZY.get(name)
    if module is None:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
    value = getattr(importlib.import_module(module), name)
    globals()[name] = value
    return value
