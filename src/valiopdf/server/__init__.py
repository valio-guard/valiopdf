"""HTTP service (FastAPI). Needs the ``[server]`` extra."""

from valiopdf.server.app import create_app

__all__ = ["create_app"]
