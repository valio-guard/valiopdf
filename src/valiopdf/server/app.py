"""The FastAPI application factory.

Run with ``valiopdf serve`` or
``uvicorn valiopdf.server.app:create_app --factory``. Settings come from
VALIOPDF_* environment variables (see docs/http-api.md).
"""

from __future__ import annotations

import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from valiopdf import __version__
from valiopdf.document.signing import SigningKey
from valiopdf.errors import SigningError
from valiopdf.render.pool import BrowserPool
from valiopdf.render.renderer import AsyncRenderer
from valiopdf.server import errors
from valiopdf.server.config import Settings
from valiopdf.server.metrics import Metrics
from valiopdf.server.middleware import BodyLimitMiddleware, RequestIdMiddleware
from valiopdf.server.routes import convert, documents, health, render

logger = logging.getLogger("valiopdf.server")


def create_app(settings: Settings | None = None, renderer: AsyncRenderer | None = None) -> FastAPI:
    """Build the app. ``renderer`` lets tests supply their own; by default one is
    created from ``settings`` and started/stopped with the app."""
    settings = settings or Settings()
    # Load signing keys and trust roots now: a bad key stops the server at startup,
    # not on the first sign request. Messages name the key, never its password.
    signing_keys: dict[str, SigningKey] = {}
    for name, config in settings.signing_keys.items():
        try:
            signing_keys[name] = SigningKey.from_pkcs12(config.pkcs12, config.read_password())
        except (OSError, SigningError) as exc:
            reason = exc.message if isinstance(exc, SigningError) else exc.strerror
            raise SigningError(f"signing key {name!r}: {reason}") from None
    trust_roots = [path.read_bytes() for path in settings.trust_root_files]
    if not logging.getLogger().handlers:
        logging.basicConfig(format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    logging.getLogger("valiopdf").setLevel(settings.log_level.upper())

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        active = renderer or AsyncRenderer(
            max_concurrency=settings.max_concurrency,
            max_queue=settings.max_queue,
            allowed_hosts=settings.allowed_host_list,
        )
        await active.start()
        app.state.renderer = active
        logger.info("valiopdf %s ready", __version__)
        try:
            yield
        finally:
            await active.close()

    app = FastAPI(
        title="valiopdf",
        version=__version__,
        summary="HTML to PDF and PDF tools.",
        lifespan=lifespan,
    )
    app.state.settings = settings
    app.state.signing_keys = signing_keys
    app.state.trust_roots = trust_roots
    app.state.renderer = None

    def current_pool() -> BrowserPool | None:
        active: AsyncRenderer | None = app.state.renderer
        return active.pool if active is not None else None

    app.state.metrics = Metrics(current_pool)
    errors.install(app)
    for module in (render, documents, convert, health):
        app.include_router(module.router)
    # Last added runs first: request ids wrap everything, including 413 responses.
    app.add_middleware(BodyLimitMiddleware, max_bytes=settings.max_body_bytes)
    app.add_middleware(RequestIdMiddleware)
    return app
