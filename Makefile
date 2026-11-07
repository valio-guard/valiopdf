.PHONY: install browser lint format typecheck test test-all check serve docker

install:
	uv sync --all-extras

browser:
	uv run playwright install chromium

lint:
	uv run ruff check .
	uv run ruff format --check .
	uv run deptry src

format:
	uv run ruff check --fix .
	uv run ruff format .

typecheck:
	uv run mypy

test:
	uv run pytest -m "not browser"

test-all:
	uv run pytest

check: lint typecheck test

serve:
	VALIOPDF_API_KEY=$${VALIOPDF_API_KEY:-dev} uv run valiopdf serve

# The image is labelled with the commit it was built from (valiopdf:<short sha>), so Valio Guard can pin an
# exact version. Uncommitted changes get a -dirty suffix: never a tag anyone would pin.
REVISION := $(shell git rev-parse HEAD)
VERSION := $(shell git rev-parse --short=7 HEAD)$(shell git diff --quiet HEAD || echo -dirty)

docker:
	docker build -t valiopdf:$(VERSION) -t valiopdf:latest --label org.opencontainers.image.revision=$(REVISION) .
	@echo "built valiopdf:$(VERSION)"

