#!/usr/bin/env bash
set -euo pipefail

uv sync --all-extras
uv run ruff check src/
uv run pytest tests/ -v
