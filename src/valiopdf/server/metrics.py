"""Prometheus metrics, on a registry per app (so tests can build many apps)."""

from __future__ import annotations

from collections.abc import Callable, Iterator

from prometheus_client import CollectorRegistry, Histogram
from prometheus_client.core import GaugeMetricFamily, Metric
from prometheus_client.registry import Collector

from valiopdf.render.pool import BrowserPool


class _PoolCollector(Collector):
    def __init__(self, get_pool: Callable[[], BrowserPool | None]) -> None:
        self._get_pool = get_pool

    def collect(self) -> Iterator[Metric]:
        pool = self._get_pool()
        if pool is None:
            return
        for name, doc, value in (
            ("valiopdf_renders_active", "Renders running now.", pool.active),
            ("valiopdf_renders_waiting", "Renders waiting for a browser slot.", pool.waiting),
            ("valiopdf_renders_total", "Renders finished since start.", pool.renders),
            ("valiopdf_browser_launches_total", "Chromium launches.", pool.launches),
            (
                "valiopdf_browser_restarts_total",
                "Chromium relaunches after a crash.",
                pool.restarts,
            ),
        ):
            yield GaugeMetricFamily(name, doc, value=value)


class Metrics:
    def __init__(self, get_pool: Callable[[], BrowserPool | None]) -> None:
        self.registry = CollectorRegistry()
        self.render_seconds = Histogram(
            "valiopdf_render_seconds",
            "Time to render a PDF, by source.",
            ["source"],
            registry=self.registry,
            buckets=(0.25, 0.5, 1, 2, 5, 10, 20, 30, 60, 120),
        )
        self.registry.register(_PoolCollector(get_pool))
